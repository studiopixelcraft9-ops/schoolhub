from django import forms

from .models import Attendance, BookAuthor, BookCategory, BookCopy, BookEdition, BookIssue, BookLanguage, BookPublisher, BookReservation, Classroom, ClassTeacherAssignment, Course, Department, Employee, EmployeePayroll, Exam, ExamComment, Finance, Grade, LibraryBook, LibraryBookType, Mark, Notice, Student, SubjectAssignment, Teacher,PettyCashCategory,PettyCashTransaction, InventoryCategory, InventoryBrand, InventorySupplier, InventoryAttribute, InventoryItem, InventoryRecord


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = [
            'name',
            'code',
            'description',
            'head_of_department',
            'email',
            'phone',
            'office_location',
            'established_date',
            'status',
            'website',
            'office_extension',
            'total_staff',
            'budget',
        ]
        widgets = {
            'established_date': forms.DateInput(attrs={'type': 'date'}),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course_name', 'course_code', 'description', 'duration', 'department', 'teacher']


class ClassroomForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ['class_name', 'section', 'room_number', 'teacher']


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['exam_name', 'classroom', 'course', 'exam_date', 'total_marks', 'passing_marks']
        widgets = {
            'exam_date': forms.DateInput(attrs={'type': 'date'}),
        }


class SubjectAssignmentForm(forms.ModelForm):
    class Meta:
        model = SubjectAssignment
        fields = ['classroom', 'student', 'courses']
        widgets = {'courses': forms.CheckboxSelectMultiple()}


class ClassTeacherAssignmentForm(forms.ModelForm):
    class Meta:
        model = ClassTeacherAssignment
        fields = ['classroom', 'teacher', 'effective_date']
        widgets = {'effective_date': forms.DateInput(attrs={'type': 'date'})}


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['classroom', 'name', 'remarks', 'minimum_marks', 'maximum_marks']

    def clean(self):
        cleaned = super().clean()
        minimum = cleaned.get('minimum_marks')
        maximum = cleaned.get('maximum_marks')
        if minimum is not None and maximum is not None and minimum > maximum:
            raise forms.ValidationError('Minimum marks cannot be greater than maximum marks.')
        if maximum is not None and maximum > 100:
            raise forms.ValidationError('Maximum marks cannot be greater than 100.')
        return cleaned


class ExamCommentForm(forms.ModelForm):
    class Meta:
        model = ExamComment
        fields = ['title', 'comment', 'status']


class MarkForm(forms.ModelForm):
    class Meta:
        model = Mark
        fields = ['student', 'exam', 'course', 'marks_obtained', 'status', 'remarks']

    def clean(self):
        cleaned = super().clean()
        exam = cleaned.get('exam')
        marks = cleaned.get('marks_obtained')
        if exam and marks is not None and marks > exam.total_marks:
            raise forms.ValidationError(f'Marks cannot exceed the exam total of {exam.total_marks}.')
        return cleaned


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'name',
            'roll_number',
            'age',
            'email',
            'course',
            'department',
            'gender',
            'date_of_birth',
            'guardian_name',
            'guardian_phone',
            'admission_date',
            'address',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'admission_date': forms.DateInput(attrs={'type': 'date'}),
        }


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = [
            'FirstName',
            'LastName',
            'DateofBirth',
            'Email',
            'PhoneNumber',
            'department',
            'Address',
            'ProfilePhoto',
            'Qualification',
            'Specialization',
            'Gender',
        ]
        widgets = {
            'DateofBirth': forms.DateInput(attrs={'type': 'date'}),
        }


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = [
            'student',
            'teacher',
            'date',
            'status',
            'check_in_time',
            'check_out_time',
            'remarks',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'check_in_time': forms.TimeInput(attrs={'type': 'time'}),
            'check_out_time': forms.TimeInput(attrs={'type': 'time'}),
        }


class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'message', 'published_on', 'priority']
        widgets = {
            'published_on': forms.DateInput(attrs={'type': 'date'}),
        }


class FinanceForm(forms.ModelForm):
    class Meta:
        model = Finance
        fields = ['student', 'fee_type', 'amount', 'due_date', 'paid_date', 'status', 'payment_method', 'remarks']
        widgets = {
            'paid_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }



class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'gender', 'date_of_birth', 'email', 'phone', 'address', 'salary', 'hire_date', 'department', 'CNIC', 'shift']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
        }


class EmployeePayrollForm(forms.ModelForm):
    class Meta:
        model = EmployeePayroll
        fields = ['employee', 'month', 'year', 'basic_salary', 'allowance', 'bonus', 'deduction', 'payment_date', 'payment_status', 'remarks']
        widgets = {'payment_date': forms.DateInput(attrs={'type': 'date'})}


