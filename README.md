Grading System Overview

This document provides a simple, non-technical explanation of the Grading System application.

What is this System?

This is a School Grading and Management System built as a web application. Its primary purpose is to manage student, teacher, and class information, record academic grades, and generate student results.

It acts as a central hub for all academic data within a school environment.

Key Features

The system is designed to handle three main types of users, each with specific permissions and functions:

User Role
Primary Responsibilities
Key Actions
Admin
Full control over the system and data.
Manage all users (students, teachers, admins), classes, and subjects.
Teacher
Responsible for teaching and grading.
View assigned classes and subjects, enter grades (test and exam scores) for students, and communicate with students via comments.
Student
Primary recipient of academic services.
View their assigned classes and subjects, check their individual grades, and see their overall academic results.


How Does it Work?

The system is built on a robust and popular web framework called Django (using the Python programming language).

1.
Data Management: The Admin sets up the school structure by creating Classes and Subjects, and then assigning Teachers to subjects and Students to classes.

2.
Grading: Teachers log in and enter two types of scores for each student in their assigned subjects: a Test Score and an Exam Score. The system automatically calculates the Total Score for the subject.

3.
Results: The system compiles all the subject grades to calculate a student's Total Score and Average Score across all their subjects, providing a comprehensive academic result.

4.
Communication: Teachers and students can send private Comments to each other regarding specific subjects.

Technical Details (For Developers)

•
Framework: Django (Python)

•
Database: Uses a local db.sqlite3 file by default.

•
Key Modules:

•
accounts: Manages user roles (Admin, Teacher, Student), classes, and subject assignments.

•
grades: Handles the core logic for recording grades, calculating results, and managing comments.



•
Dependencies: Requires Python packages like Django, reportlab (for generating reports), and Pillow (for image handling).

In short, this system is a complete, role-based application for managing the academic records and communication of a school.

