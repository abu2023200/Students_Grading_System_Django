from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Admin URLs
    path('accounts/CustomUser/', views.manage_users, name='manage_users'),
    path('accounts/CustomUser/add/', views.add_user, name='add_user'),
    path('accounts/CustomUser/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('CustomUser/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    
    path('accounts/class/', views.manage_classes, name='manage_classes'),
    path('accounts/class/add/', views.add_class, name='add_class'),
    path('class/edit/<int:class_id>/', views.edit_class, name='edit_class'),
    path('class/delete/<int:class_id>/', views.delete_class, name='delete_class'),

    path('accounts/subjects/', views.manage_subjects, name='manage_subjects'),
    path('accounts/subjects/add/', views.add_subject, name='add_subject'),
    path('accounts/subjects/edit/<int:subject_id>/', views.edit_subject, name='edit_subject'),
    path('subject/delete/<int:subject_id>/', views.delete_subject, name='delete_subject'),

    
    path('accounts/teacher-assignments/', views.manage_teacher_assignments, name='manage_teacher_assignments'),
    path('accounts/assign-teacher/', views.assign_teacher_subject, name='assign_teacher_subject'),
    path('assignments/edit/<int:assignment_id>/', views.edit_teacher_assignment, name='edit_teacher_assignment'),
    path('assignments/delete/<int:assignment_id>/', views.delete_teacher_assignment, name='delete_teacher_assignment'),
    path('teacher-assignments/<int:teacher_id>/', views.teacher_assignments_detail, name='teacher_assignments_detail'),
    
    path('accounts/student-assignments/', views.manage_student_assignments, name='manage_student_assignments'),
    path('accounts/assign-student/', views.assign_student_class, name='assign_student_class'),
    path('student-assignments/edit/<int:assignment_id>/', views.edit_student_assignment, name='edit_student_assignment'),
    path('student-assignments/delete/<int:assignment_id>/', views.delete_student_assignment, name='delete_student_assignment'),
    path('assign-student/', views.assign_student_subject, name='assign_student_subject'),
]
