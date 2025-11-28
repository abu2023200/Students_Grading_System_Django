from django.db import models
from accounts.models import CustomUser, Subject, StudentClass, StudentSubject

class Grade(models.Model):
    
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'student'})
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'teacher'}, related_name='grades_given')
    test_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    exam_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'subject']
    
    def save(self, *args, **kwargs):
        self.total_score = self.test_score + self.exam_score
        super().save(*args, **kwargs)
     
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.subject.name} - {self.total_score}"

class Comment(models.Model):
    COMMENT_TYPE_CHOICES = [
        ('teacher_to_student', 'Teacher to Student'),
        ('student_to_teacher', 'Student to Teacher'),
    ]
    
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_comments')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_comments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    comment_type = models.CharField(max_length=20, choices=COMMENT_TYPE_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sender.get_full_name()} to {self.receiver.get_full_name()} - {self.subject.name}"

class StudentResult(models.Model):
    student = models.OneToOneField(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'student'})
    total_subjects = models.IntegerField(default=0)
    total_score = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    average_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    academic_year = models.CharField(max_length=20, default='2023-2024')
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_result(self):
        grades = Grade.objects.filter(student=self.student)
        if grades.exists():
            self.total_subjects = grades.count()
            self.total_score = sum(grade.total_score for grade in grades)
            self.average_score = self.total_score / self.total_subjects if self.total_subjects > 0 else 0
        self.save()
    
    def __str__(self):
        return f"{self.student.get_full_name()}"


class SchoolSettings(models.Model):
    name = models.CharField(max_length=100, default="My School")
    logo = models.ImageField(upload_to='school_logos/', null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "School Settings"
    
    def __str__(self):
        return self.name