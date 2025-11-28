from django import forms
from .models import Grade, Comment
from accounts.models import Class, CustomUser, Subject, TeacherSubject

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['student', 'subject', 'test_score', 'exam_score']
        widgets = {
            'test_score': forms.NumberInput(attrs={'min': 0, 'max': 100, 'step': 0.01}),
            'exam_score': forms.NumberInput(attrs={'min': 0, 'max': 100, 'step': 0.01}),
        }
    
    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        
        if teacher:
            # For existing instances (editing), lock student and subject
            if self.instance and self.instance.pk:
                self.fields['student'].disabled = True
                self.fields['subject'].disabled = True
                # Set querysets to only include the current student/subject
                self.fields['student'].queryset = CustomUser.objects.filter(
                    id=self.instance.student.id,
                    user_type='student'
                )
                self.fields['subject'].queryset = Subject.objects.filter(
                    id=self.instance.subject.id
                )
            else:
                # For new grades, use the existing filtering logic
                teacher_subjects = TeacherSubject.objects.filter(teacher=teacher)
                subject_ids = teacher_subjects.values_list('subject_id', flat=True)
                self.fields['subject'].queryset = Subject.objects.filter(id__in=subject_ids)
                
                class_ids = teacher_subjects.values_list('class_assigned_id', flat=True)
                from accounts.models import StudentClass
                student_class_ids = StudentClass.objects.filter(
                    class_assigned_id__in=class_ids
                ).values_list('student_id', flat=True)
                self.fields['student'].queryset = CustomUser.objects.filter(
                    id__in=student_class_ids, 
                    user_type='student'
                )
                                    
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['receiver', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        sender = kwargs.pop('sender', None)
        super().__init__(*args, **kwargs)
        
        if sender:
            if sender.user_type == 'teacher':
                # Teachers can comment to students they teach
                teacher_subjects = TeacherSubject.objects.filter(teacher=sender)
                class_ids = teacher_subjects.values_list('class_assigned_id', flat=True)
                from accounts.models import StudentClass
                student_ids = StudentClass.objects.filter(class_assigned_id__in=class_ids).values_list('student_id', flat=True)
                self.fields['receiver'].queryset = CustomUser.objects.filter(id__in=student_ids, user_type='student')
                
                subject_ids = teacher_subjects.values_list('subject_id', flat=True)
                self.fields['subject'].queryset = Subject.objects.filter(id__in=subject_ids)
                
            elif sender.user_type == 'student':
                # Students can comment to their teachers
                try:
                    from accounts.models import StudentClass, StudentSubject
                    student_class = StudentClass.objects.get(student=sender)
 
                    teacher_subjects = TeacherSubject.objects.filter(class_assigned=student_class.class_assigned)
                    subject_ids = teacher_subjects.values_list('subject_id', flat=True)
                    
                    teacher_ids = TeacherSubject.objects.filter(
                        subject_id__in=subject_ids,
                        class_assigned=student_class.class_assigned
                    ).values_list('teacher_id', flat=True)
                    
                    self.fields['receiver'].queryset = CustomUser.objects.filter(id__in=teacher_ids, user_type='teacher')
                    self.fields['subject'].queryset = Subject.objects.filter(id__in=subject_ids)
                except:
                    self.fields['receiver'].queryset = CustomUser.objects.none()
                    self.fields['subject'].queryset = Subject.objects.none()
