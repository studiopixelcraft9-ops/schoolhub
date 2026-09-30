import calendar

from django.db import transaction
from django.db.models import Avg, Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import AttendanceForm, ClassroomForm, ClassTeacherAssignmentForm, CourseForm, DepartmentForm, EmployeeForm, EmployeePayrollForm, ExamCommentForm, ExamForm, FinanceForm, GradeForm, MarkForm, NoticeForm, StudentForm, SubjectAssignmentForm, TeacherForm
from .models import Attendance, Classroom, ClassTeacherAssignment, Course, Department, Employee, EmployeePayroll, Exam, ExamComment, Finance, Grade, Mark, Notice, Student, SubjectAssignment, Teacher
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    today = timezone.localdate()
    weekday_order = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    attendance_totals = {
        item["status"]: item["count"]
        for item in Attendance.objects.values("status").annotate(count=Count("id"))
    }
    finance_paid_total = Finance.objects.filter(status="Paid").aggregate(total=Sum("amount"))["total"] or 0
    finance_pending_total = Finance.objects.exclude(status="Paid").aggregate(total=Sum("amount"))["total"] or 0
    month_calendar = calendar.Calendar(firstweekday=6).monthdayscalendar(today.year, today.month)
    calendar_week = next((week for week in month_calendar if today.day in week), month_calendar[0] if month_calendar else [])
    calendar_days = []
    for index, day in enumerate(calendar_week):
        calendar_days.append(
            {
                "label": ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"][index],
                "day": day,
                "is_today": day == today.day,
                "is_empty": day == 0,
            }
        )

    recent_activity = []
    for student in Student.objects.order_by("-id")[:2]:
        recent_activity.append(
            {
                "title": f"{student.name} was added",
                "detail": f"Student record created for {student.course}",
                "meta": student.roll_number or student.email,
            }
        )
    for finance in Finance.objects.select_related("student").order_by("-id")[:2]:
        recent_activity.append(
            {
                "title": f"{finance.student.name} finance updated",
                "detail": f"{finance.fee_type} fee marked {finance.status}",
                "meta": f"{finance.amount}",
            }
        )
    recent_activity = recent_activity[:4]

    context = {
        'department_count': Department.objects.count(),
        'student_count': Student.objects.count(),
        'teacher_count': Teacher.objects.count(),
        'employee_count': Employee.objects.count(),
        'attendance_count': Attendance.objects.count(),
        'finance_count': Finance.objects.count(),
        'notice_count': Notice.objects.count(),
        'course_count': Course.objects.count(),
        'classroom_count': Classroom.objects.count(),
        'exam_count': Exam.objects.count(),
        'payroll_count': EmployeePayroll.objects.count(),
        'present_count': attendance_totals.get('Present', 0),
        'absent_count': attendance_totals.get('Absent', 0),
        'leave_count': attendance_totals.get('Leave', 0),
        'late_count': attendance_totals.get('Late', 0),
        'active_student_percent': min(100, 40 + Student.objects.count() * 3),
        'finance_paid_total': finance_paid_total,
        'finance_pending_total': finance_pending_total,
        'today': today,
        'calendar_month_year': today.strftime("%B %Y"),
        'calendar_days': calendar_days,
        'message_teachers': Teacher.objects.order_by('-id')[:4],
        'student_activity': Student.objects.order_by('-id')[:4],
        'recent_activity': recent_activity,
        'recent_students': Student.objects.order_by('-id')[:5],
        'recent_departments': Department.objects.order_by('-id')[:5],
        'recent_teachers': Teacher.objects.order_by('-id')[:5],
        'recent_courses': Course.objects.select_related('department', 'teacher').order_by('-id')[:5],
        'recent_classrooms': Classroom.objects.select_related('teacher').order_by('-id')[:5],
        'recent_exams': Exam.objects.select_related('course', 'classroom').order_by('-id')[:5],
        'recent_attendance': Attendance.objects.select_related('student').order_by('-id')[:5],
        'recent_finances': Finance.objects.select_related('student').order_by('-id')[:5],
        'recent_notices': Notice.objects.order_by('-id')[:5],
    }
    return render(request, 'school1/dashboard.html', context)

@login_required
def department_list(request):
    departments = Department.objects.all().order_by('name')
    return render(request, 'school1/department/department_list.html', {'departments': departments})

@login_required
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('department_list')
    else:
        form = DepartmentForm()
    return render(request, 'school1/department/department_form.html', {'form': form, 'title': 'Add Department'})

@login_required
def department_update(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            return redirect('department_list')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'school1/department/department_form.html', {'form': form, 'title': 'Update Department'})

@login_required
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        department.delete()
        return redirect('department_list')
    return render(request, 'school1/department/department_delete.html', {'department': department})

@login_required
def course_list(request):
    courses = Course.objects.select_related('department', 'teacher').order_by('course_name')
    return render(request, 'school1/course/course_list.html', {'courses': courses})

@login_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'school1/course/course_form.html', {'form': form, 'title': 'Add Course'})

@login_required
def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'school1/course/course_form.html', {'form': form, 'title': 'Update Course'})

@login_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        return redirect('course_list')
    return render(request, 'school1/course/course_delete.html', {'course': course})

@login_required
def classroom_list(request):
    classrooms = Classroom.objects.select_related('teacher').order_by('class_name', 'section')
    return render(request, 'school1/classroom/classroom_list.html', {'classrooms': classrooms})

@login_required
def classroom_create(request):
    if request.method == 'POST':
        form = ClassroomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('classroom_list')
    else:
        form = ClassroomForm()
    return render(request, 'school1/classroom/classroom_form.html', {'form': form, 'title': 'Add Classroom'})

@login_required
def classroom_update(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    if request.method == 'POST':
        form = ClassroomForm(request.POST, instance=classroom)
        if form.is_valid():
            form.save()
            return redirect('classroom_list')
    else:
        form = ClassroomForm(instance=classroom)
    return render(request, 'school1/classroom/classroom_form.html', {'form': form, 'title': 'Update Classroom'})

@login_required
def classroom_delete(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    if request.method == 'POST':
        classroom.delete()
        return redirect('classroom_list')
    return render(request, 'school1/classroom/classroom_delete.html', {'classroom': classroom})

@login_required
def exam_list(request):
    exams = Exam.objects.select_related('course', 'classroom').order_by('-exam_date', 'exam_name')
    return render(request, 'school1/exam/exam_list.html', {'exams': exams})

@login_required
def exam_create(request):
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('exam_list')
    else:
        form = ExamForm()
    return render(request, 'school1/exam/exam_form.html', {'form': form, 'title': 'Add Exam'})

@login_required
def exam_update(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            return redirect('exam_list')
    else:
        form = ExamForm(instance=exam)
    return render(request, 'school1/exam/exam_form.html', {'form': form, 'title': 'Update Exam'})

@login_required
def exam_delete(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if request.method == 'POST':
        exam.delete()
        return redirect('exam_list')
    return render(request, 'school1/exam/exam_delete.html', {'exam': exam})


EXAM_TOOL_CONFIG = {
    'subjects-assignment': ('Subjects Assignment', '🧪', 'Assign subjects to students and classes.'),
    'class-teachers': ('Class Teachers', '🧑‍🏫', 'Assign teachers to classes and sections.'),
    'grades': ('Grades', '📝', 'Create and manage grade ranges.'),
    'comments': ('Comments', '📖', 'Manage reusable report-card comments.'),
    'marks': ('Marks', '📋', 'Search and enter student marks.'),
    'report-cards': ('Report Cards', '📄', 'Find and prepare student report cards.'),
    'analysis': ('Analysis', '📊', 'Review examination performance.'),
}

EXAM_TOOL_MODELS = {
    'subjects-assignment': (SubjectAssignment, SubjectAssignmentForm),
    'class-teachers': (ClassTeacherAssignment, ClassTeacherAssignmentForm),
    'grades': (Grade, GradeForm),
    'comments': (ExamComment, ExamCommentForm),
    'marks': (Mark, MarkForm),
}


@login_required
def exam_tool(request, tool):
    if tool not in EXAM_TOOL_CONFIG:
        from django.http import Http404
        raise Http404('Exam category not found')

    title, icon, description = EXAM_TOOL_CONFIG[tool]
    form = None
    records = None
    editing = None

    if tool in EXAM_TOOL_MODELS:
        model, form_class = EXAM_TOOL_MODELS[tool]
        edit_id = request.GET.get('edit')
        if edit_id:
            editing = get_object_or_404(model, pk=edit_id)
        form = form_class(request.POST or None, instance=editing)
        if request.method == 'POST' and form.is_valid():
            form.save()
            return redirect(request.path)
        records = model.objects.all().order_by('-id')

    selected_exam = request.GET.get('exam')
    selected_student = request.GET.get('student')
    mark_results = Mark.objects.select_related('student', 'exam', 'course').order_by('student__name')
    if selected_exam:
        mark_results = mark_results.filter(exam_id=selected_exam)
    if selected_student:
        mark_results = mark_results.filter(student_id=selected_student)

    context = {
        'tool': tool,
        'title': title,
        'icon': icon,
        'description': description,
        'students': Student.objects.order_by('name'),
        'teachers': Teacher.objects.order_by('FirstName', 'LastName'),
        'classrooms': Classroom.objects.order_by('class_name', 'section'),
        'courses': Course.objects.order_by('course_name'),
        'exams': Exam.objects.select_related('course', 'classroom').order_by('-exam_date'),
        'form': form,
        'records': records,
        'editing': editing,
        'mark_results': mark_results,
        'analysis': mark_results.aggregate(average=Avg('marks_obtained'), total=Count('id')),
    }
    return render(request, 'school1/exam_tools/exam_tool.html', context)


@login_required
def exam_tool_delete(request, tool, pk):
    if tool not in EXAM_TOOL_MODELS:
        from django.http import Http404
        raise Http404('Exam category not found')
    if request.method == 'POST':
        model, _ = EXAM_TOOL_MODELS[tool]
        get_object_or_404(model, pk=pk).delete()
    return redirect('exam_tool', tool=tool)


"""
LIBRARY_TOOL_CONFIG = {
    'navigator': ('Library Navigator', 'Search the complete book catalogue.'),
    'book-types': ('Book Types', 'Manage library material types.'),
    'categories': ('Book Categories', 'Organize books into categories.'),
    'languages': ('Book Languages', 'Manage supported book languages.'),
    'authors': ('Authors', 'Manage author contact information.'),
    'publishers': ('Publishers', 'Manage book publishers.'),
    'editions': ('Book Editions', 'Manage publication editions.'),
    'books': ('Books', 'Manage catalogue titles and metadata.'),
    'copies': ('Book Copies', 'Manage physical copies and availability.'),
    'reservations': ('Reservations', 'Reserve available copies.'),
    'issues': ('Issue Books', 'Issue books to students or employees.'),
    'returns': ('Book Returns', 'Return currently issued books.'),
    'reports': ('Library Reports', 'Review library inventory and circulation.'),
}

LIBRARY_CRUD = {
    'book-types': (LibraryBookType, LibraryBookTypeForm),
    'categories': (BookCategory, BookCategoryForm),
    'languages': (BookLanguage, BookLanguageForm),
    'authors': (BookAuthor, BookAuthorForm),
    'publishers': (BookPublisher, BookPublisherForm),
    'editions': (BookEdition, BookEditionForm),
    'books': (LibraryBook, LibraryBookForm),
    'copies': (BookCopy, BookCopyForm),
    'reservations': (BookReservation, BookReservationForm),
    'issues': (BookIssue, BookIssueForm),
}


@login_required
def library_tool(request, tool):
    if tool not in LIBRARY_TOOL_CONFIG:
        from django.http import Http404
        raise Http404('Library category not found')
    title, description = LIBRARY_TOOL_CONFIG[tool]
    form = records = editing = None
    query = request.GET.get('q', '').strip()

    if tool in LIBRARY_CRUD:
        model, form_class = LIBRARY_CRUD[tool]
        if request.GET.get('edit'):
            editing = get_object_or_404(model, pk=request.GET['edit'])
        form = form_class(request.POST or None, instance=editing)
        if request.method == 'POST' and form.is_valid():
            with transaction.atomic():
                saved = form.save()
                if tool == 'reservations' and saved.status == 'Active':
                    saved.copy.status = 'Reserved'; saved.copy.save(update_fields=['status'])
                if tool == 'issues' and saved.status == 'Issued':
                    saved.copy.status = 'Issued'; saved.copy.save(update_fields=['status'])
            return redirect(request.path)
        records = model.objects.all().order_by('-id')

    books = LibraryBook.objects.select_related('book_type', 'category', 'language', 'publisher', 'edition').prefetch_related('authors')
    if query:
        books = books.filter(Q(title__icontains=query) | Q(code__icontains=query) | Q(keywords__icontains=query))
    issued = BookIssue.objects.filter(status__in=['Issued', 'Overdue']).select_related('copy__book', 'student', 'employee')
    context = {
        'tool': tool, 'title': title, 'description': description, 'form': form,
        'records': records, 'editing': editing, 'books': books.order_by('title'),
        'issued': issued, 'query': query,
        'stats': {'books': LibraryBook.objects.count(), 'copies': BookCopy.objects.count(),
                  'available': BookCopy.objects.filter(status='Available').count(), 'issued': issued.count(),
                  'reserved': BookReservation.objects.filter(status='Active').count()},
    }
    return render(request, 'school1/library/library_tool.html', context)


@login_required
def library_delete(request, tool, pk):
    if tool in LIBRARY_CRUD and request.method == 'POST':
        model, _ = LIBRARY_CRUD[tool]
        get_object_or_404(model, pk=pk).delete()
    return redirect('library_tool', tool=tool)


@login_required
def library_return(request, pk):
    issue = get_object_or_404(BookIssue, pk=pk, status__in=['Issued', 'Overdue'])
    if request.method == 'POST':
        with transaction.atomic():
            issue.status = 'Returned'; issue.returned_date = timezone.localdate(); issue.save()
            issue.copy.status = 'Available'; issue.copy.save(update_fields=['status'])
    return redirect('library_returns')

"""

@login_required
def student_list(request):
    students = Student.objects.all().order_by('name')
    return render(request, 'school1/student/student_list.html', {'students': students})

@login_required
def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form = StudentForm()
    return render(request, 'school1/student/student_form.html', {'form': form, 'title': 'Add Student'})

@login_required
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form = StudentForm(instance=student)
    return render(request, 'school1/student/student_form.html', {'form': form, 'title': 'Update Student'})

@login_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        return redirect('student_list')
    return render(request, 'school1/student/student_delete.html', {'student': student})

@login_required
def teacher_list(request):
    teachers = Teacher.objects.all().order_by('FirstName', 'LastName')
    return render(request, 'school1/teacher/teacher_list.html', {'teachers': teachers})

@login_required
def teacher_create(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('teacher_list')
    else:
        form = TeacherForm()
    return render(request, 'school1/teacher/teacher_form.html', {'form': form, 'title': 'Add Teacher'})

@login_required
def teacher_update(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            form.save()
            return redirect('teacher_list')
    else:
        form = TeacherForm(instance=teacher)
    return render(request, 'school1/teacher/teacher_form.html', {'form': form, 'title': 'Update Teacher'})

@login_required
def teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        teacher.delete()
        return redirect('teacher_list')
    return render(request, 'school1/teacher/teacher_delete.html', {'teacher': teacher})

@login_required
def Attendance_list(request):
    attendance_records = Attendance.objects.select_related('student', 'teacher')
    return render(request, 'school1/attendance/attendance_list.html', {'attendance_records': attendance_records})

@login_required
def Attendance_create(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('Attendance_list')
    else:
        form = AttendanceForm()
    return render(request, 'school1/attendance/attendance_form.html', {'form': form, 'title': 'Add Attendance'})

@login_required
def Attendance_update(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            return redirect('Attendance_list')
    else:
        form = AttendanceForm(instance=attendance)
    return render(request, 'school1/attendance/attendance_form.html', {'form': form, 'title': 'Update Attendance'})

@login_required
def Attendance_delete(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        attendance.delete()
        return redirect('Attendance_list')
    return render(request, 'school1/attendance/attendance_delete.html', {'attendance': attendance})

@login_required
def notice_list(request):
    notices = Notice.objects.all()
    return render(request, 'school1/notice/notice_list.html', {'notices': notices})

@login_required
def notice_create(request):
    if request.method == 'POST':
        form = NoticeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('notice_list')
    else:
        form = NoticeForm()
    return render(request, 'school1/notice/notice_form.html', {'form': form, 'title': 'Add Notice'})

@login_required
def notice_update(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    if request.method == 'POST':
        form = NoticeForm(request.POST, instance=notice)
        if form.is_valid():
            form.save()
            return redirect('notice_list')
    else:
        form = NoticeForm(instance=notice)
    return render(request, 'school1/notice/notice_form.html', {'form': form, 'title': 'Update Notice'})

@login_required
def notice_delete(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    if request.method == 'POST':
        notice.delete()
        return redirect('notice_list')
    return render(request, 'school1/notice/notice_delete.html', {'notice': notice})
@login_required
def finance_list(request):
    finances = Finance.objects.select_related('student').order_by('-id')
    return render(request, 'school1/finance/finance_list.html', {'finances': finances})

@login_required
def finance_create(request):
    if request.method == 'POST':
        form = FinanceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('finance_list')
    else:
        form = FinanceForm()
    return render(request, 'school1/finance/finance_form.html', {'form': form, 'title': 'Add Finance'})
@login_required
def finance_update(request, pk):
    finance = get_object_or_404(Finance, pk=pk)
    if request.method == 'POST':
        form = FinanceForm(request.POST, instance=finance)
        if form.is_valid():
            form.save()
            return redirect('finance_list')
    else:
        form = FinanceForm(instance=finance)
    return render(request, 'school1/finance/finance_form.html', {'form': form, 'title': 'Update Finance'})
@login_required
def finance_delete(request, pk):
    finance = get_object_or_404(Finance, pk=pk)
    if request.method == 'POST':
        finance.delete()
        return redirect('finance_list')
    return render(request, 'school1/finance/finance_delete.html', {'finance': finance})


@login_required
def employee_list(request):
    employees = Employee.objects.select_related('department').order_by('first_name', 'last_name')
    return render(request, 'school1/employee/employee_list.html', {'employees': employees})


@login_required
def employee_create(request):
    form = EmployeeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('employee_list')
    return render(request, 'school1/employee/employee_form.html', {'form': form, 'title': 'Add Employee'})


@login_required
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    form = EmployeeForm(request.POST or None, instance=employee)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('employee_list')
    return render(request, 'school1/employee/employee_form.html', {'form': form, 'title': 'Update Employee'})


@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        return redirect('employee_list')
    return render(request, 'school1/employee/employee_delete.html', {'employee': employee})


@login_required
def employee_payroll_list(request):
    payrolls = EmployeePayroll.objects.select_related('employee').order_by('-year', '-id')
    return render(request, 'school1/employee_payroll/employee_payroll_list.html', {'payrolls': payrolls})


@login_required
def employee_payroll_create(request):
    form = EmployeePayrollForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('employee_payroll_list')
    return render(request, 'school1/employee_payroll/employee_payroll_form.html', {'form': form, 'title': 'Add Employee Payroll'})


@login_required
def employee_payroll_update(request, pk):
    payroll = get_object_or_404(EmployeePayroll, pk=pk)
    form = EmployeePayrollForm(request.POST or None, instance=payroll)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('employee_payroll_list')
    return render(request, 'school1/employee_payroll/employee_payroll_form.html', {'form': form, 'title': 'Update Employee Payroll'})


@login_required
def employee_payroll_delete(request, pk):
    payroll = get_object_or_404(EmployeePayroll, pk=pk)
    if request.method == 'POST':
        payroll.delete()
        return redirect('employee_payroll_list')
    return render(request, 'school1/employee_payroll/employee_payroll_delete.html', {'payroll': payroll})


"""
def _petty_type(value):
    from django.http import Http404
    if value not in ('Receipt', 'Expense'):
        raise Http404('Invalid transaction type')
    return value


@login_required
def petty_category_list(request):
    categories = PettyCashCategory.objects.select_related('parent').order_by('name')
    return render(request, 'school1/petty_cash/petty_cash.html', {'page': 'categories', 'title': 'Petty Cash Categories', 'records': categories})


@login_required
def petty_category_form(request, pk=None):
    record = get_object_or_404(PettyCashCategory, pk=pk) if pk else None
    form = PettyCashCategoryForm(request.POST or None, instance=record)
    if request.method == 'POST' and form.is_valid():
        form.save(); return redirect('petty_category_list')
    return render(request, 'school1/petty_cash/petty_cash.html', {'page': 'category_form', 'title': 'Edit Category' if record else 'New Category', 'form': form})


@login_required
def petty_category_delete(request, pk):
    if request.method == 'POST':
        get_object_or_404(PettyCashCategory, pk=pk).delete()
    return redirect('petty_category_list')


@login_required
def petty_transaction_list(request, transaction_type):
    transaction_type = _petty_type(transaction_type)
    records = PettyCashTransaction.objects.filter(transaction_type=transaction_type).select_related('category', 'department', 'employee', 'student')
    start, end, category = request.GET.get('start_date'), request.GET.get('end_date'), request.GET.get('category')
    if start: records = records.filter(transaction_date__gte=start)
    if end: records = records.filter(transaction_date__lte=end)
    if category: records = records.filter(category_id=category)
    total = records.aggregate(total=Sum('amount'))['total'] or 0
    return render(request, 'school1/petty_cash/petty_cash.html', {'page': 'transactions', 'title': f'{transaction_type}s', 'transaction_type': transaction_type, 'records': records, 'total': total, 'categories': PettyCashCategory.objects.filter(status='Active', transaction_type__in=[transaction_type, 'Both'])})


@login_required
def petty_transaction_form(request, transaction_type, pk=None):
    transaction_type = _petty_type(transaction_type)
    record = get_object_or_404(PettyCashTransaction, pk=pk, transaction_type=transaction_type) if pk else None
    form = PettyCashTransactionForm(request.POST or None, request.FILES or None, instance=record, transaction_type=transaction_type)
    if request.method == 'POST' and form.is_valid():
        form.save(); return redirect('petty_transaction_list', transaction_type=transaction_type)
    return render(request, 'school1/petty_cash/petty_cash.html', {'page': 'transaction_form', 'title': f'Edit {transaction_type}' if record else f'New {transaction_type}', 'transaction_type': transaction_type, 'form': form})


@login_required
def petty_transaction_delete(request, transaction_type, pk):
    transaction_type = _petty_type(transaction_type)
    if request.method == 'POST':
        get_object_or_404(PettyCashTransaction, pk=pk, transaction_type=transaction_type).delete()
    return redirect('petty_transaction_list', transaction_type=transaction_type)


@login_required
def petty_reports(request):
    records = PettyCashTransaction.objects.filter(status='Active').select_related('category', 'department')
    start, end, category, kind = request.GET.get('start_date'), request.GET.get('end_date'), request.GET.get('category'), request.GET.get('transaction_type')
    if start: records = records.filter(transaction_date__gte=start)
    if end: records = records.filter(transaction_date__lte=end)
    if category: records = records.filter(category_id=category)
    if kind in ('Receipt', 'Expense'): records = records.filter(transaction_type=kind)
    receipts = records.filter(transaction_type='Receipt').aggregate(total=Sum('amount'))['total'] or 0
    expenses = records.filter(transaction_type='Expense').aggregate(total=Sum('amount'))['total'] or 0
    return render(request, 'school1/petty_cash/petty_cash.html', {'page': 'reports', 'title': 'Petty Cash Reports', 'records': records, 'receipt_total': receipts, 'expense_total': expenses, 'balance': receipts-expenses, 'categories': PettyCashCategory.objects.filter(status='Active')})


def _inventory_page(request, page, title, subtitle, tiles=None):
    return render(
        request,
        'school1/inventory/inventory.html',
        {
            'page': page,
            'title': title,
            'subtitle': subtitle,
            'tiles': tiles or [],
        },
    )


@login_required
def inventory_dashboard(request):
    return _inventory_page(
        request,
        'dashboard',
        'Inventory',
        'Inventory module',
        [
            ('Categories', 'inventory_category_list'),
            ('Brands', 'inventory_brand_list'),
            ('Suppliers', 'inventory_supplier_list'),
            ('Attributes', 'inventory_attribute_list'),
            ('Items', 'inventory_item_list'),
            ('Inventory', 'inventory_record_list'),
            ('Transfers', 'inventory_transfer_list'),
            ('Adjustments', 'inventory_adjustment_list'),
            ('Reports', 'inventory_reports'),
        ],
    )


@login_required
def inventory_category_list(request):
    records = InventoryCategory.objects.all().order_by('name')
    return _inventory_page(request, 'categories', 'Categories', 'Category list page', [('New Category', 'inventory_category_create')])


@login_required
def inventory_category_create(request):
    form = InventoryCategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('inventory_category_list')
    return render(request, 'school1/inventory/inventory.html', {'page': 'category_form', 'title': 'New Category', 'form': form})


@login_required
def inventory_category_update(request, pk):
    record = get_object_or_404(InventoryCategory, pk=pk)
    form = InventoryCategoryForm(request.POST or None, instance=record)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('inventory_category_list')
    return render(request, 'school1/inventory/inventory.html', {'page': 'category_form', 'title': 'Edit Category', 'form': form, 'record': record})


@login_required
def inventory_category_delete(request, pk):
    if request.method == 'POST':
        get_object_or_404(InventoryCategory, pk=pk).delete()
    return redirect('inventory_category_list')


@login_required
def inventory_brand_list(request):
    records = InventoryBrand.objects.all().order_by('name')
    return render(request, 'school1/inventory/inventory.html', {'page': 'brands', 'title': 'Brands', 'records': records})


@login_required
def inventory_brand_create(request):
    form = InventoryBrandForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('inventory_brand_list')
    return render(request, 'school1/inventory/inventory.html', {'page': 'brand_form', 'title': 'New Brand', 'form': form})


@login_required
def inventory_brand_update(request, pk):
    record = get_object_or_404(InventoryBrand, pk=pk)
    form = InventoryBrandForm(request.POST or None, instance=record)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('inventory_brand_list')
    return render(request, 'school1/inventory/inventory.html', {'page': 'brand_form', 'title': 'Edit Brand', 'form': form, 'record': record})


@login_required
def inventory_brand_delete(request, pk):
    if request.method == 'POST':
        get_object_or_404(InventoryBrand, pk=pk).delete()
    return redirect('inventory_brand_list')


@login_required
def inventory_supplier_list(request):
    records = InventorySupplier.objects.all().order_by('name')
    return render(request, 'school1/inventory/inventory.html', {'page': 'suppliers', 'title': 'Suppliers', 'records': records})


@login_required
def inventory_supplier_create(request):
    form = InventorySupplierForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('inventory_supplier_list')
    return render(request, 'school1/inventory/inventory.html', {'page': 'supplier_form', 'title': 'New Supplier', 'form': form})


@login_required
def inventory_supplier_update(request, pk):
    record = get_object_or_404(InventorySupplier, pk=pk)
    form = InventorySupplierForm(request.POST or None, instance=record)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('inventory_supplier_list')
    return render(request, 'school1/inventory/inventory.html', {'page': 'supplier_form', 'title': 'Edit Supplier', 'form': form, 'record': record})


@login_required
def inventory_supplier_delete(request, pk):
    if request.method == 'POST':
        get_object_or_404(InventorySupplier, pk=pk).delete()
    return redirect('inventory_supplier_list')


@login_required
def inventory_attribute_list(request):
    records = InventoryAttribute.objects.all().order_by('name')
    return render(request, 'school1/inventory/inventory.html', {'page': 'attributes', 'title': 'Attributes', 'records': records})


@login_required
def inventory_attribute_create(request):
    form = InventoryAttributeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('inventory_attribute_list')
    return render(request, 'school1/inventory/inventory.html', {'page': 'attribute_form', 'title': 'New Attribute', 'form': form})


@login_required
def inventory_attribute_update(request, pk):
    record = get_object_or_404(InventoryAttribute, pk=pk)
    form = InventoryAttributeForm(request.POST or None, instance=record)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('inventory_attribute_list')
    return render(request, 'school1/inventory/inventory.html', {'page': 'attribute_form', 'title': 'Edit Attribute', 'form': form, 'record': record})


@login_required
def inventory_attribute_delete(request, pk):
    if request.method == 'POST':
        get_object_or_404(InventoryAttribute, pk=pk).delete()
    return redirect('inventory_attribute_list')


@login_required
def inventory_item_list(request):
    records = InventoryItem.objects.select_related('category', 'brand', 'supplier').order_by('name')
    return render(request, 'school1/inventory/inventory.html', {'page': 'items', 'title': 'Items', 'records': records})


@login_required
def inventory_item_create(request):
    form = InventoryItemForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('inventory_item_list')
    return render(request, 'school1/inventory/inventory.html', {'page': 'item_form', 'title': 'New Item', 'form': form})


@login_required
def inventory_item_update(request, pk):
    record = get_object_or_404(InventoryItem, pk=pk)
    form = InventoryItemForm(request.POST or None, instance=record)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('inventory_item_list')
    return render(request, 'school1/inventory/inventory.html', {'page': 'item_form', 'title': 'Edit Item', 'form': form, 'record': record})


@login_required
def inventory_item_delete(request, pk):
    if request.method == 'POST':
        get_object_or_404(InventoryItem, pk=pk).delete()
    return redirect('inventory_item_list')


@login_required
def inventory_record_list(request, record_type='Inventory'):
    records = InventoryRecord.objects.filter(record_type=record_type).select_related('item').order_by('-date', '-id')
    return render(request, 'school1/inventory/inventory.html', {'page': 'records', 'title': record_type, 'record_type': record_type, 'records': records})


@login_required
def inventory_record_create(request):
    form = InventoryRecordForm(request.POST or None, initial={'record_type': 'Inventory'})
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('inventory_record_list')
    return render(request, 'school1/inventory/inventory.html', {'page': 'record_form', 'title': 'New Inventory', 'record_type': 'Inventory', 'form': form})


@login_required
def inventory_record_update(request, pk):
    record = get_object_or_404(InventoryRecord, pk=pk)
    form = InventoryRecordForm(request.POST or None, instance=record)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('inventory_record_list')
    return render(request, 'school1/inventory/inventory.html', {'page': 'record_form', 'title': 'Edit Record', 'form': form, 'record': record})


@login_required
def inventory_record_delete(request, pk):
    if request.method == 'POST':
        get_object_or_404(InventoryRecord, pk=pk).delete()
    return redirect('inventory_record_list')


@login_required
def inventory_transfer_list(request):
    records = InventoryRecord.objects.filter(record_type='Transfer').select_related('item').order_by('-date', '-id')
    return render(request, 'school1/inventory/inventory.html', {'page': 'records', 'title': 'Transfers', 'record_type': 'Transfer', 'records': records})


@login_required
def inventory_transfer_create(request):
    form = InventoryRecordForm(request.POST or None, initial={'record_type': 'Transfer'})
    if request.method == 'POST' and form.is_valid():
        record = form.save(commit=False)
        record.record_type = 'Transfer'
        record.save()
        return redirect('inventory_transfer_list')
    return render(request, 'school1/inventory/inventory.html', {'page': 'record_form', 'title': 'New Transfer', 'form': form, 'record_type': 'Transfer'})


@login_required
def inventory_transfer_update(request, pk):
    record = get_object_or_404(InventoryRecord, pk=pk, record_type='Transfer')
    form = InventoryRecordForm(request.POST or None, instance=record)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('inventory_transfer_list')
    return render(request, 'school1/inventory/inventory.html', {'page': 'record_form', 'title': 'Edit Transfer', 'form': form, 'record': record, 'record_type': 'Transfer'})


@login_required
def inventory_transfer_delete(request, pk):
    if request.method == 'POST':
        get_object_or_404(InventoryRecord, pk=pk, record_type='Transfer').delete()
    return redirect('inventory_transfer_list')


@login_required
def inventory_adjustment_list(request):
    records = InventoryRecord.objects.filter(record_type='Adjustment').select_related('item').order_by('-date', '-id')
    return render(request, 'school1/inventory/inventory.html', {'page': 'records', 'title': 'Adjustments', 'record_type': 'Adjustment', 'records': records})


@login_required
def inventory_adjustment_create(request):
    form = InventoryRecordForm(request.POST or None, initial={'record_type': 'Adjustment'})
    if request.method == 'POST' and form.is_valid():
        record = form.save(commit=False)
        record.record_type = 'Adjustment'
        record.save()
        return redirect('inventory_adjustment_list')
    return render(request, 'school1/inventory/inventory.html', {'page': 'record_form', 'title': 'New Adjustment', 'form': form, 'record_type': 'Adjustment'})


@login_required
def inventory_adjustment_update(request, pk):
    record = get_object_or_404(InventoryRecord, pk=pk, record_type='Adjustment')
    form = InventoryRecordForm(request.POST or None, instance=record)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('inventory_adjustment_list')
    return render(request, 'school1/inventory/inventory.html', {'page': 'record_form', 'title': 'Edit Adjustment', 'form': form, 'record': record, 'record_type': 'Adjustment'})


@login_required
def inventory_adjustment_delete(request, pk):
    if request.method == 'POST':
        get_object_or_404(InventoryRecord, pk=pk, record_type='Adjustment').delete()
    return redirect('inventory_adjustment_list')


@login_required
def inventory_reports(request):
    records = InventoryItem.objects.select_related('category', 'brand', 'supplier').order_by('name')
    low_stock = records.filter(quantity__lte=0)
    return render(request, 'school1/inventory/inventory.html', {'page': 'reports', 'title': 'Reports', 'items': records, 'low_stock': low_stock})
"""
