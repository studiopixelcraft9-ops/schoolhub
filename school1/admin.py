from django.contrib import admin

from .models import Attendance, Classroom, Course, Department, Employee, EmployeePayroll, Exam, Finance, Notice, Student, Teacher


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'head_of_department', 'email', 'phone', 'office_location', 'status', 'total_staff')
    search_fields = ('code', 'name')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'course_name', 'department', 'teacher', 'duration')
    search_fields = ('course_code', 'course_name', 'department__name')
    list_filter = ('department',)


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('class_name', 'section', 'room_number', 'teacher')
    search_fields = ('class_name', 'section', 'room_number')


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('exam_name', 'course', 'classroom', 'exam_date', 'total_marks', 'passing_marks')
    list_filter = ('exam_date', 'course')
    search_fields = ('exam_name', 'course__course_name', 'classroom__class_name')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'name', 'department', 'course', 'gender', 'guardian_phone')
    search_fields = ('roll_number', 'name', 'email', 'course', 'guardian_name', 'department__name')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('FirstName', 'LastName', 'department', 'Email', 'PhoneNumber', 'Qualification')
    search_fields = ('FirstName', 'LastName', 'Email', 'Specialization', 'department__name')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'teacher', 'date', 'status')
    list_filter = ('status', 'date')
    search_fields = ('student__name', 'teacher__FirstName', 'teacher__LastName')


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'published_on')
    list_filter = ('priority', 'published_on')
    search_fields = ('title', 'message')

@admin.register(Finance)
class FinanceAdmin(admin.ModelAdmin):
     list_display = ('student', 'fee_type', 'status','remarks', 'paid_date', 'due_date')
     list_filter = ('status', 'payment_method')
     search_fields = ('student__name', 'remarks')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'CNIC', 'department', 'salary', 'shift')
    list_filter = ('shift', 'department', 'gender')
    search_fields = ('first_name', 'last_name', 'CNIC', 'email', 'department__name')


@admin.register(EmployeePayroll)
class EmployeePayrollAdmin(admin.ModelAdmin):
    list_display = ('employee', 'month', 'year', 'basic_salary', 'net_salary', 'payment_date', 'payment_status')
    list_filter = ('payment_status', 'year', 'month')
    search_fields = ('employee__first_name', 'employee__last_name', 'remarks')
    readonly_fields = ('net_salary',)
