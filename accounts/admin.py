from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Class, Subject, TeacherSubject, StudentClass, StudentSubject

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'user_type', 'is_active']
    list_filter = ['user_type', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone', 'address')}),
    )

admin.site.register(Class)
admin.site.register(Subject)
admin.site.register(TeacherSubject)
admin.site.register(StudentClass)
admin.site.register(StudentSubject)
