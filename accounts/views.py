from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.db.models import Count
from .models import CustomUser, Class, Subject, TeacherSubject, StudentClass, StudentSubject
from .forms import CustomUserCreationForm, UserUpdateForm, ClassForm, SubjectForm, TeacherSubjectForm, StudentClassForm

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password')
    return render(request, 'registration/login.html')

def custom_logout(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    context = {}
    if request.user.user_type == 'admin':
        context.update({
            'total_students': CustomUser.objects.filter(user_type='student').count(),
            'total_teachers': CustomUser.objects.filter(user_type='teacher').count(),
            'total_classes': Class.objects.count(),
            'total_subjects': Subject.objects.count(),
        })
    elif request.user.user_type == 'teacher':
        context.update({
            'assigned_subjects': TeacherSubject.objects.filter(teacher=request.user),
        })
    elif request.user.user_type == 'student':
        try:
            student_class = StudentClass.objects.get(student=request.user)
            # Get all subjects taught in this class by any teacher
            subjects_in_class = TeacherSubject.objects.filter(
                class_assigned=student_class.class_assigned
            ).select_related('subject').distinct()
            
            context.update({
                'student_class': student_class,
                'subjects_in_class': subjects_in_class,  # Changed from 'subjects'
            })
        except StudentClass.DoesNotExist:
            context['student_class'] = None
    
    return render(request, 'dashboard.html', context)

# Admin Views
@login_required
def manage_users(request):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    users = CustomUser.objects.all().order_by('-date_joined')
    return render(request, 'admin/manage_users.html', {'users': users})

@login_required
def add_user(request):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully')
            return redirect('manage_users')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'admin/add_user.html', {'form': form})

@login_required
def edit_user(request, user_id):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully')
            return redirect('manage_users')
    else:
        form = UserUpdateForm(instance=user)
    
    return render(request, 'admin/edit_user.html', {'form': form, 'user': user})

@login_required
def delete_user(request, user_id):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully')
        return redirect('manage_users')
    
    return render(request, 'admin/delete_user.html', {'user': user})

@login_required
def manage_classes(request):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    classes = Class.objects.all().order_by('name')
    return render(request, 'admin/manage_classes.html', {'classes': classes})

@login_required
def add_class(request):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class created successfully')
            return redirect('manage_classes')
    else:
        form = ClassForm()
    
    return render(request, 'admin/add_class.html', {'form': form})


@login_required
def edit_class(request, class_id):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    classes = get_object_or_404(Class, id=class_id)
    if request.method == 'POST':
        form = ClassForm(request.POST, instance=classes)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class updated successfully')
            return redirect('manage_subjects')
    else:
        form = ClassForm(instance=classes)
    
    return render(request, 'admin/edit_class.html', {
        'form': form,
        'classes': classes
    })

@login_required
def delete_class(request, class_id):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    class_obj = get_object_or_404(Class, id=class_id)
    if request.method == 'POST':
        class_obj.delete()
        messages.success(request, 'Class deleted successfully')
        return redirect('manage_classes')
    
    return render(request, 'admin/confirm_delete.html', {'class_obj': class_obj})

@login_required
def manage_subjects(request):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    subjects = Subject.objects.all().order_by('name')
    return render(request, 'admin/manage_subjects.html', {'subjects': subjects})

@login_required
def add_subject(request):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject created successfully')
            return redirect('manage_subjects')
    else:
        form = SubjectForm()
    
    return render(request, 'admin/add_subject.html', {'form': form})


@login_required
def edit_subject(request, subject_id):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    subject = get_object_or_404(Subject, id=subject_id)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject updated successfully')
            return redirect('manage_subjects')
    else:
        form = SubjectForm(instance=subject)
    
    return render(request, 'admin/edit_subject.html', {
        'form': form,
        'subject': subject
    })


@login_required
def delete_subject(request, subject_id):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    subject_obj = get_object_or_404(Subject, id=subject_id)
    if request.method == 'POST':
        subject_obj.delete()
        messages.success(request, 'Subject deleted successfully')
        return redirect('manage_subjects')
    
    return render(request, 'admin/confirm_delete.html', {'class_obj': subject_obj})


@login_required
def assign_teacher_subject(request):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = TeacherSubjectForm(request.POST)
        if form.is_valid():
            # Check if this subject-class combination already has a teacher
            subject = form.cleaned_data['subject']
            class_assigned = form.cleaned_data['class_assigned']
            
            if TeacherSubject.objects.filter(
                subject=subject, 
                class_assigned=class_assigned
            ).exists():
                messages.error(request, 'This subject already has a teacher assigned in this class')
            else:
                form.save()
                messages.success(request, 'Teacher assigned to subject successfully')
                return redirect('manage_teacher_assignments')
    else:
        form = TeacherSubjectForm()
    
    return render(request, 'admin/assign_teacher_subject.html', {'form': form})

@login_required
def teacher_assignments_detail(request, teacher_id):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    teacher = get_object_or_404(CustomUser, id=teacher_id, user_type='teacher')
    assignments = TeacherSubject.objects.filter(teacher=teacher).order_by('class_assigned__name')
    
    return render(request, 'admin/teacher_assignments_detail.html', {
        'teacher': teacher,
        'assignments': assignments
    })

@login_required
def manage_teacher_assignments(request):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    # Get distinct teachers with their assignment counts
    teachers = CustomUser.objects.filter(
        user_type='teacher',
        teachersubject__isnull=False
    ).annotate(
        total_subjects=Count('teachersubject')
    ).order_by('first_name')
    
    return render(request, 'admin/manage_teacher_assignments.html', {
        'teachers': teachers
    })

@login_required
def edit_teacher_assignment(request, assignment_id):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    assignment = get_object_or_404(TeacherSubject, id=assignment_id)
    if request.method == 'POST':
        form = TeacherSubjectForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assignment updated successfully')
            return redirect('manage_teacher_assignments')
    else:
        form = TeacherSubjectForm(instance=assignment)
    
    return render(request, 'admin/edit_teacher_assignment.html', {
        'form': form,
        'assignment': assignment
    })


@login_required
def delete_teacher_assignment(request, assignment_id):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    assignment = get_object_or_404(TeacherSubject, id=assignment_id)
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'Assignment deleted successfully')
        return redirect('manage_teacher_assignments')
    
    return render(request, 'admin/confirm_delete_assignment.html', {
        'assignment': assignment
    })

@login_required
def assign_student_class(request):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = StudentClassForm(request.POST)
        if form.is_valid():
            student = form.cleaned_data['student']
            
            # Check if student is already assigned to any class
            if StudentClass.objects.filter(student=student).exists():
                messages.error(request, 'This student is already assigned to a class')
            else:
                form.save()
                messages.success(request, 'Student assigned to class successfully')
                return redirect('manage_student_assignments')
    else:
        form = StudentClassForm()
    
    return render(request, 'admin/assign_student_class.html', {'form': form})

@login_required
def manage_student_assignments(request):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    assignments = StudentClass.objects.all().order_by('student__first_name')
    return render(request, 'admin/manage_student_assignments.html', {'assignments': assignments})

@login_required
def edit_student_assignment(request, assignment_id):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    assignment = get_object_or_404(StudentClass, id=assignment_id)
    if request.method == 'POST':
        form = StudentClassForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assignment updated successfully')
            return redirect('manage_student_assignments')
    else:
        form = StudentClassForm(instance=assignment)
    
    return render(request, 'admin/edit_student_assignment.html', {
        'form': form,
        'assignment': assignment
    })

@login_required
def delete_student_assignment(request, assignment_id):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    assignment = get_object_or_404(StudentClass, id=assignment_id)
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'Assignment deleted successfully')
        return redirect('manage_student_assignments')
    
    return render(request, 'admin/confirm_delete_student_assignment.html', {
        'assignment': assignment
    })

@login_required
def assign_student_subject(request):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    if request.method == 'POST':
        student_id = request.POST.get('student')
        class_id = request.POST.get('class_assigned')
        
        # Get all subjects taught in this class by teachers
        subjects = TeacherSubject.objects.filter(
            class_assigned_id=class_id
        ).values_list('subject', flat=True).distinct()
        
        # Assign all these subjects to the student
        student_class, created = StudentClass.objects.get_or_create(
            student_id=student_id,
            class_assigned_id=class_id
        )
        
        # Create StudentSubject records for each subject
        for subject_id in subjects:
            StudentSubject.objects.get_or_create(
                student_class=student_class,
                subject_id=subject_id
            )
        
        messages.success(request, 'Student assigned to class and all subjects successfully')
        return redirect('manage_student_assignments')
    
    # For GET request, show form to select student and class only
    form = StudentClassForm()
    return render(request, 'admin/assign_student_subject.html', {'form': form})