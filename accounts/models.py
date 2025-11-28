from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone = models.PositiveIntegerField(max_length=15, blank=True)
    address = models.CharField(blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'user_type']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.user_type})"

class Class(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Classes"
    
    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.CharField(blank=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class TeacherSubject(models.Model):
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'teacher'})
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['teacher', 'subject', 'class_assigned']
    
    def __str__(self):
        return f"{self.teacher.get_full_name()} - {self.subject.name} - {self.class_assigned.name}"

class StudentClass(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'student'})
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['student', 'class_assigned']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.class_assigned.name}"
    
class StudentSubject(models.Model):
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['student_class', 'subject']
    
    def __str__(self):
        return f"{self.student_class.student.get_full_name()} - {self.subject.name}"
