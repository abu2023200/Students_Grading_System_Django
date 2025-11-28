from django.urls import path
from . import views

urlpatterns = [
    # Teacher URLs
    path('teacher/', views.teacher_grades, name='teacher_grades'),
    path('teacher/add/', views.add_grade, name='add_grade'),
    path('teacher/add/<int:class_id>/<int:subject_id>/', views.add_grade, name='add_grade_for_class_subject'),
    path('teacher/assign-grade/', views.teacher_assigned_classes_subjects, name='teacher_assigned_classes'),
    path('teacher/edit/<int:grade_id>/', views.edit_grade, name='edit_grade'),
    path('teacher/delete/<int:grade_id>/', views.delete_grade, name='delete_grade'),
    path('student-grades/<int:student_id>/', views.student_grades_detail, name='student_grades_detail'),
    
    # Student URLs
    path('student/results/', views.student_results, name='student_results'),
    path('student/download-pdf/', views.download_result_pdf, name='download_result_pdf'),
    
    # Comments
    path('comments/', views.comments, name='comments'),
    path('comments/add/', views.add_comment, name='add_comment'),
    
    # Admin URLs
    path('admin/results/', views.admin_student_results, name='admin_student_results'),
    path('subjects/<int:subject_id>/grades/', views.subject_grades, name='subject_grades'),
    path('admin/student/<int:student_id>/grades/', views.admin_student_grades, name='admin_student_grades'),
    path('admin/student/<int:student_id>/download-pdf/', views.admin_download_student_pdf, name='admin_download_student_pdf'),
     
]
