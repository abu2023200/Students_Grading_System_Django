from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Class, Subject, TeacherSubject, StudentClass, StudentSubject

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'user_type', 'phone', 'address')

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'phone', 'address')

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['name', 'description']

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'description']

class TeacherSubjectForm(forms.ModelForm):
    class Meta:
        model = TeacherSubject
        fields = ['teacher', 'subject', 'class_assigned']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = CustomUser.objects.filter(user_type='teacher')

class StudentClassForm(forms.ModelForm):
    class Meta:
        model = StudentClass
        fields = ['student', 'class_assigned']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = CustomUser.objects.filter(user_type='student')

 