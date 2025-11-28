from django.contrib import admin
from .models import Grade, Comment, StudentResult, SchoolSettings


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'teacher', 'test_score', 'exam_score', 'total_score']
    list_filter = ['subject', 'teacher']
    search_fields = ['student__first_name', 'student__last_name', 'subject__name']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'subject', 'comment_type', 'created_at']
    list_filter = ['comment_type', 'created_at']
    search_fields = ['sender__first_name', 'receiver__first_name', 'subject__name']

@admin.register(StudentResult)
class StudentResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'total_subjects', 'average_score', 'updated_at']
    list_filter = ['academic_year']
    search_fields = ['student__first_name', 'student__last_name']


@admin.register(SchoolSettings)
class SchoolSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Only allow one settings instance
        return not SchoolSettings.objects.exists()