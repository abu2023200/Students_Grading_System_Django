from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import Image
from .models import SchoolSettings
from reportlab.lib import colors
from django.db.models import Count
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io

from .models import Grade, Comment, StudentResult
from .forms import GradeForm, CommentForm
from accounts.models import CustomUser, Subject, TeacherSubject, StudentClass, StudentSubject

# Teacher Views
@login_required
def teacher_grades(request):
    if request.user.user_type != 'teacher':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    # Get students in classes where teacher is assigned
    students = CustomUser.objects.filter(
        user_type='student',
        studentclass__isnull=False,
        studentclass__class_assigned__teachersubject__teacher=request.user
    ).distinct().prefetch_related(
        'studentclass_set',
        'grade_set'
    ).order_by('first_name')
    
    # Prepare student data with accurate counts
    student_data = []
    for student in students:
        try:
            student_class = student.studentclass_set.first()
            if not student_class:
                continue
                
            # Get subjects teacher teaches in this class
            teacher_subjects = TeacherSubject.objects.filter(
                teacher=request.user,
                class_assigned=student_class.class_assigned
            ).values_list('subject', flat=True)
            
            # Count grades for these subjects
            graded_count = student.grade_set.filter(
                teacher=request.user,
                subject__in=teacher_subjects
            ).count()
            
            student_data.append({
                'id': student.id,
                'full_name': student.get_full_name(),
                'graded_subjects': graded_count,
                'class_name': student_class.class_assigned.name
            })
        except Exception:
            continue
    
    return render(request, 'grades/teacher_grades.html', {
        'students': student_data
    })


@login_required
def teacher_assigned_classes_subjects(request):
    if request.user.user_type != 'teacher':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    # Get all unique classes assigned to this teacher with their subjects
    teacher_assignments = TeacherSubject.objects.filter(
        teacher=request.user
    ).select_related('class_assigned', 'subject')
    
    # Organize by class
    class_data = []
    for assignment in teacher_assignments:
        class_obj = assignment.class_assigned
        subject = assignment.subject
        
        # Find or create class entry
        class_entry = next((c for c in class_data if c['class_id'] == class_obj.id), None)
        if not class_entry:
            class_entry = {
                'class_id': class_obj.id,
                'class_name': class_obj.name,
                'subjects': []
            }
            class_data.append(class_entry)
        
        # Add subject if not already present
        if not any(s['id'] == subject.id for s in class_entry['subjects']):
            class_entry['subjects'].append({
                'id': subject.id,
                'name': subject.name
            })
    
    return render(request, 'grades/teacher_assigned_classes_subjects.html', {
        'class_data': class_data
    })


@login_required
def add_grade(request, class_id=None, subject_id=None):
    if request.user.user_type != 'teacher':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = GradeForm(request.POST, teacher=request.user)
        if form.is_valid():
            grade = form.save(commit=False)
            grade.teacher = request.user
            grade.save()
            
            # Update student result
            student_result, created = StudentResult.objects.get_or_create(student=grade.student)
            student_result.calculate_result()
            
            messages.success(request, 'Grade added successfully')
            return redirect('teacher_grades')
    else:
        form = GradeForm(teacher=request.user)
        
        # If specific class and subject are provided
        if class_id and subject_id:
            try:
                # Verify this teacher is actually assigned to this class and subject
                TeacherSubject.objects.get(
                    teacher=request.user,
                    class_assigned_id=class_id,
                    subject_id=subject_id
                )
                
                # Filter the form
                form.fields['subject'].queryset = Subject.objects.filter(id=subject_id)
                form.fields['student'].queryset = CustomUser.objects.filter(
                    user_type='student',
                    studentclass__class_assigned_id=class_id
                )
                
                # Set initial subject
                form.initial['subject'] = subject_id
            except TeacherSubject.DoesNotExist:
                messages.error(request, 'You are not assigned to teach this subject in this class')
                return redirect('teacher_assigned_classes_subjects')
    
    return render(request, 'grades/add_grade.html', {
        'form': form,
        'class_id': class_id,
        'subject_id': subject_id
    })


@login_required
def student_grades_detail(request, student_id):
    if request.user.user_type != 'teacher':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    student = get_object_or_404(CustomUser, id=student_id, user_type='student')
    
    # Get the student's class
    try:
        student_class = StudentClass.objects.get(student=student)
    except StudentClass.DoesNotExist:
        messages.error(request, 'Student is not assigned to any class')
        return redirect('teacher_grades')
    
    # Get subjects the teacher is assigned to teach in this class
    teacher_subjects = TeacherSubject.objects.filter(
        teacher=request.user,
        class_assigned=student_class.class_assigned
    ).values_list('subject', flat=True)
    
    # Get grades for these specific subjects
    grades = Grade.objects.filter(
        teacher=request.user,
        student=student,
        subject__in=teacher_subjects
    ).order_by('subject__name')
    
    return render(request, 'grades/student_grades_detail.html', {
        'student': student,
        'grades': grades,
        'student_class': student_class
    })

@login_required
def edit_grade(request, grade_id):
    if request.user.user_type != 'teacher':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    grade = get_object_or_404(Grade, id=grade_id, teacher=request.user)
    
    if request.method == 'POST':
        form = GradeForm(request.POST, instance=grade, teacher=request.user)
        if form.is_valid():
            form.save()
            
            # Update student result
            student_result, created = StudentResult.objects.get_or_create(student=grade.student)
            student_result.calculate_result()
            
            messages.success(request, 'Grade updated successfully')
            return redirect('teacher_grades')
    else:
        form = GradeForm(instance=grade, teacher=request.user)
        # Make student and subject fields read-only
        form.fields['student'].disabled = True
        form.fields['subject'].disabled = True
    
    return render(request, 'grades/edit_grade.html', {
        'form': form,
        'grade': grade,
        'editing': True  # Add this context variable
    })

@login_required
def delete_grade(request, grade_id):
    if request.user.user_type != 'teacher':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    grade = get_object_or_404(Grade, id=grade_id, teacher=request.user)
    
    if request.method == 'POST':
        student = grade.student
        grade.delete()
        
        # Update student result
        student_result, created = StudentResult.objects.get_or_create(student=student)
        student_result.calculate_result()
        
        messages.success(request, 'Grade deleted successfully')
        return redirect('teacher_grades')
    
    return render(request, 'grades/delete_grade.html', {'grade': grade})
    

# Student Views
@login_required
def student_results(request):
    if request.user.user_type !='student':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    grades = Grade.objects.filter(student=request.user,).order_by('subject__name')
    student_result, created = StudentResult.objects.get_or_create(student=request.user)
    if created or not grades.exists():
        student_result.calculate_result()
    
    return render(request, 'grades/student_results.html', {
        'grades': grades,
        'student_result': student_result
    })

@login_required
def download_result_pdf(request):
    if request.user.user_type != 'student':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{request.user.get_full_name()}_transcript.pdf"'
    
    # Create the PDF object
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    # Container for the 'Flowable' objects
    elements = []

    # School Logo and Name
    try:
        settings = SchoolSettings.objects.first()
        if settings:
            # Create a table for logo and school name
            header_table_data = []
            if settings.logo:
                try:
                    logo = Image(settings.logo.path, width=2*inch, height=1*inch)
                    header_table_data.append([logo])
                except:
                    header_table_data.append([''])  # Empty cell if logo fails
            
            # Add school name
            school_name_style = ParagraphStyle(
                'SchoolName',
                parent=getSampleStyleSheet()['Heading2'],
                fontSize=14,
                alignment=1,  # Center
                spaceAfter=10
            )
            school_name = Paragraph(settings.name, school_name_style)
            header_table_data.append([school_name])
            
            # Create header table
            header_table = Table(header_table_data, colWidths=[2*inch, 4*inch])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(header_table)
            elements.append(Spacer(1, 20))
    except Exception as e:
        print(f"Error loading school settings: {e}")
    
    # The rest of your original code remains exactly the same...
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1,  # Center alignment
    )
    
    # Add title
    title = Paragraph("STUDENT RESULT", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Student information
    student_info = [
        ['Student Name:', request.user.get_full_name()],
        ['Student ID:', str(request.user.id)],
        ['Email:', request.user.email],
    ]
    
    try:
        student_class = StudentClass.objects.get(student=request.user)
        student_info.append(['Class:', student_class.class_assigned.name])
    except StudentClass.DoesNotExist:
        student_info.append(['Class:', 'Not Assigned'])
    
    info_table = Table(student_info, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 20))
    
    # Grades table
    grades = Grade.objects.filter(student=request.user).order_by('subject__name')
    subject_count = grades.count()

    if grades.exists():
        grade_data = [['Subject', 'Test Score', 'Exam Score', 'Total Score']]
        
        for grade in grades:
            grade_data.append([
                grade.subject.name,
                str(grade.test_score),
                str(grade.exam_score),
                str(grade.total_score),
            ])
        
        # Add summary row
        student_result, created = StudentResult.objects.get_or_create(student=request.user)
        student_result.calculate_result()
        
        grade_data.append(['', '', '', ''])  # Empty row
        grade_data.append(['SUMMARY', '', '', ''])
        grade_data.append(['Total Subjects:', str(student_result.total_subjects), '', ''])
        grade_data.append(['Average Score:', str(round(student_result.average_score, 2)), '', ''])
         
        last_subject_row = subject_count   
        empty_row = subject_count + 1      
        summary_start = subject_count + 2 

        grade_table = Table(grade_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch])
        grade_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 1), (-1, last_subject_row), colors.beige),
            ('BACKGROUND', (0, empty_row), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, summary_start), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, last_subject_row), 1, colors.black),
        ]))
        
        elements.append(grade_table)
    else:
        no_grades = Paragraph("No grades available", styles['Normal'])
        elements.append(no_grades)
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response

# Comment Views
@login_required
def comments(request):
    if request.user.user_type == 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    sent_comments = Comment.objects.filter(sender=request.user)
    received_comments = Comment.objects.filter(receiver=request.user)
    
    return render(request, 'grades/comments.html', {
        'sent_comments': sent_comments,
        'received_comments': received_comments
    })

@login_required
def admin_download_student_pdf(request, student_id):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    student = get_object_or_404(CustomUser, id=student_id, user_type='student')
    
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{student.get_full_name()}_transcript.pdf"'
    
    # Create the PDF object
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    # Container for the 'Flowable' objects
    elements = []

    # School Logo and Name
    try:
        settings = SchoolSettings.objects.first()
        if settings:
            # Create a table for logo and school name
            header_table_data = []
            if settings.logo:
                try:
                    logo = Image(settings.logo.path, width=2*inch, height=1*inch)
                    header_table_data.append([logo])
                except:
                    header_table_data.append([''])  # Empty cell if logo fails
            
            # Add school name
            school_name_style = ParagraphStyle(
                'SchoolName',
                parent=getSampleStyleSheet()['Heading2'],
                fontSize=14,
                alignment=1,  # Center
                spaceAfter=10
            )
            school_name = Paragraph(settings.name, school_name_style)
            header_table_data.append([school_name])
            
            # Create header table
            header_table = Table(header_table_data, colWidths=[2*inch, 4*inch])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(header_table)
            elements.append(Spacer(1, 20))
    except Exception as e:
        print(f"Error loading school settings: {e}")
    
    # Rest of your original code remains exactly the same...
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1,  # Center alignment
    )
    
    # Add title
    title = Paragraph("OFFICIAL STUDENT RESULT", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Student information
    student_info = [
        ['Student Name:', student.get_full_name()],
        ['Student ID:', str(student.id)],
        ['Email:', student.email],
    ]
    
    try:
        student_class = StudentClass.objects.get(student=student)
        student_info.append(['Class:', student_class.class_assigned.name])
    except StudentClass.DoesNotExist:
        student_info.append(['Class:', 'Not Assigned'])
    
    info_table = Table(student_info, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 20))
    
    # Grades table
    grades = Grade.objects.filter(student=student).order_by('subject__name')
    student_result = StudentResult.objects.get(student=student)
    
    if grades.exists():
        grade_data = [['Subject', 'Test Score', 'Exam Score', 'Total Score']]
        
        for grade in grades:
            grade_data.append([
                grade.subject.name,
                f"{grade.test_score}",
                f"{grade.exam_score}",
                f"{grade.total_score}",
             ])
        
        # Add summary row
        grade_data.append(['', '', '', ''])  # Empty row
        grade_data.append(['SUMMARY', '', '', ''])
        grade_data.append(['Total Subjects:', str(student_result.total_subjects), '', ''])
        grade_data.append(['Average Score:', f"{student_result.average_score:.2f}%", '', ''])
        
        grade_table = Table(grade_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch])
        grade_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 1), (-1, -5), colors.beige),
            ('BACKGROUND', (0, -4), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -4), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -5), 1, colors.black),
        ]))
        
        elements.append(grade_table)
    else:
        no_grades = Paragraph("No grades available for this student", styles['Normal'])
        elements.append(no_grades)
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response

@login_required
def add_comment(request):
    if request.user.user_type == 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CommentForm(request.POST, sender=request.user)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.sender = request.user
            
            if request.user.user_type == 'teacher':
                comment.comment_type = 'teacher_to_student'
            else:
                comment.comment_type = 'student_to_teacher'
            
            comment.save()
            messages.success(request, 'Comment sent successfully')
            return redirect('comments')
    else:
        form = CommentForm(sender=request.user)
    
    return render(request, 'grades/add_comment.html', {'form': form})

# Admin Views
@login_required
def admin_student_results(request):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    students = CustomUser.objects.filter(user_type='student')
    student_results = []
    
    for student in students:
        grades = Grade.objects.filter(student=student)
        student_result, created = StudentResult.objects.get_or_create(student=student)
        if created or grades.exists():
            student_result.calculate_result()
        
        student_results.append({
            'student': student,
            'result': student_result,
            'grades': grades
        })
    
    return render(request, 'grades/admin_student_results.html', {'student_results': student_results})


@login_required
def admin_student_grades(request, student_id):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    student = get_object_or_404(CustomUser, id=student_id, user_type='student')
    grades = Grade.objects.filter(student=student).order_by('subject__name')
    student_result = get_object_or_404(StudentResult, student=student)
    
    return render(request, 'grades/admin_student_grades.html', {
        'student': student,
        'grades': grades,
        'student_result': student_result
    })


@login_required
def subject_grades(request, subject_id):
    if request.user.user_type not in ['student', 'admin']:
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    subject = get_object_or_404(Subject, id=subject_id)
    grades = Grade.objects.filter(
        student=request.user,
        subject=subject
    ).order_by('-created_at')
    
    return render(request, 'grades/subject_grades.html', {
        'subject': subject,
        'grades': grades
    })