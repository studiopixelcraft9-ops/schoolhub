from datetime import date, time
from decimal import Decimal

from django.core.management.base import BaseCommand

from school1.models import (
    Attendance, BookAuthor, BookCategory, BookCopy, BookEdition, BookIssue,
    BookLanguage, BookPublisher, BookReservation, Classroom,
    ClassTeacherAssignment, Course, Department, Employee, EmployeePayroll,
    Exam, ExamComment, Finance, Grade, LibraryBook, LibraryBookType, Mark,
    Notice, PettyCashCategory, PettyCashTransaction, Student, SubjectAssignment, Teacher,
)


class Command(BaseCommand):
    help = "Create reusable mock data for every SchoolHub module."

    def handle(self, *args, **options):
        departments = []
        for index, name in enumerate(["Computer Science", "Business Administration", "Science"], 1):
            department, _ = Department.objects.update_or_create(
                code=f"D{index:02}",
                defaults={
                    "name": name, "description": f"{name} academic department",
                    "head_of_department": ["Dr. Sara Khan", "Prof. Ahmed Ali", "Dr. Hina Noor"][index - 1],
                    "email": f"department{index}@schoolhub.test", "phone": f"0300-00000{index}",
                    "office_location": f"Block {chr(64 + index)}", "established_date": date(2018, index, 1),
                    "status": "Active", "website": "https://example.com", "office_extension": f"10{index}",
                    "total_staff": 12 + index, "budget": Decimal("750000.00") + index * 50000,
                },
            )
            departments.append(department)

        teachers = []
        teacher_rows = [
            ("Ayesha", "Malik", "ayesha@schoolhub.test", "Mathematics"),
            ("Usman", "Farooq", "usman@schoolhub.test", "Computer Science"),
            ("Fatima", "Zahid", "fatima@schoolhub.test", "English"),
        ]
        for index, (first, last, email, specialization) in enumerate(teacher_rows):
            teacher, _ = Teacher.objects.update_or_create(
                Email=email,
                defaults={"FirstName": first, "LastName": last, "DateofBirth": date(1985 + index, 4, 10),
                          "PhoneNumber": f"0311-10000{index}", "department": departments[index],
                          "Address": "Lahore, Pakistan", "Qualification": "Masters",
                          "Specialization": specialization, "Gender": "Female" if index != 1 else "Male"},
            )
            teachers.append(teacher)

        courses = []
        for index, (name, code) in enumerate([("Python Programming", "CS101"), ("Business Studies", "BA101"), ("General Science", "SC101")]):
            course, _ = Course.objects.update_or_create(
                course_code=code,
                defaults={"course_name": name, "description": f"Introduction to {name}", "duration": "1 Year",
                          "department": departments[index], "teacher": teachers[index]},
            )
            courses.append(course)

        classrooms = []
        for index, name in enumerate(["Grade 8", "Grade 9", "Grade 10"]):
            room, _ = Classroom.objects.update_or_create(
                class_name=name, section="A",
                defaults={"room_number": f"R-{101 + index}", "teacher": teachers[index]},
            )
            classrooms.append(room)

        students = []
        student_rows = [("Ali Raza", "S001", "ali.raza@schoolhub.test"), ("Mariam Khan", "S002", "mariam@schoolhub.test"), ("Hamza Noor", "S003", "hamza@schoolhub.test"), ("Zoya Ahmed", "S004", "zoya@schoolhub.test"), ("Bilal Shah", "S005", "bilal@schoolhub.test")]
        for index, (name, roll, email) in enumerate(student_rows):
            student, _ = Student.objects.update_or_create(
                roll_number=roll,
                defaults={"name": name, "age": 13 + index % 3, "email": email,
                          "course": courses[index % 3].course_name, "department": departments[index % 3],
                          "gender": "Female" if name.split()[0] in ["Mariam", "Zoya"] else "Male",
                          "date_of_birth": date(2011 - index % 3, 5, 10), "guardian_name": f"Guardian of {name}",
                          "guardian_phone": f"0322-20000{index}", "admission_date": date(2025, 8, 1),
                          "address": "Lahore, Pakistan"},
            )
            students.append(student)

        exams = []
        for index, title in enumerate(["First Term", "Mid Term", "Final Term"]):
            exam, _ = Exam.objects.update_or_create(
                exam_name=title, classroom=classrooms[index], course=courses[index],
                defaults={"exam_date": date(2026, 9 + index, 10), "total_marks": 100, "passing_marks": 40},
            )
            exams.append(exam)

        for index, student in enumerate(students):
            Attendance.objects.update_or_create(
                student=student, date=date(2026, 8, 14),
                defaults={"teacher": teachers[index % 3], "status": ["Present", "Present", "Late", "Absent", "Leave"][index],
                          "check_in_time": time(8, 5 + index), "check_out_time": time(14, 0), "remarks": "Mock attendance"},
            )
            Finance.objects.update_or_create(
                student=student, fee_type="Tuition", due_date=date(2026, 8, 10),
                defaults={"amount": Decimal("15000.00"), "paid_date": date(2026, 8, 8) if index < 3 else None,
                          "status": "Paid" if index < 3 else "Unpaid", "payment_method": "Bank", "remarks": "August tuition"},
            )

        for index, title in enumerate(["Parent Teacher Meeting", "Final Exam Schedule", "Independence Day Holiday"]):
            Notice.objects.update_or_create(title=title, defaults={"message": f"Mock notice: {title}", "published_on": date(2026, 8, 10 + index), "priority": ["Medium", "High", "Low"][index]})

        employees = []
        for index, (first, last, cnic) in enumerate([("Noman", "Iqbal", "35202-1000001-1"), ("Sana", "Javed", "35202-1000002-2"), ("Kamran", "Akhtar", "35202-1000003-3")]):
            employee, _ = Employee.objects.update_or_create(
                CNIC=cnic,
                defaults={"first_name": first, "last_name": last, "gender": "Female" if first == "Sana" else "Male",
                          "date_of_birth": date(1990 + index, 2, 15), "email": f"{first.lower()}@schoolhub.test",
                          "phone": f"0333-30000{index}", "address": "Lahore, Pakistan", "salary": Decimal("55000.00") + index * 5000,
                          "hire_date": date(2024, 1 + index, 5), "department": departments[index], "shift": "Morning"},
            )
            employees.append(employee)
            EmployeePayroll.objects.update_or_create(
                employee=employee, month="August", year=2026,
                defaults={"basic_salary": employee.salary, "allowance": Decimal("5000.00"), "bonus": Decimal("2000.00"),
                          "deduction": Decimal("1000.00"), "net_salary": employee.salary + 6000,
                          "payment_date": date(2026, 8, 5), "payment_status": "Paid", "remarks": "August payroll"},
            )

        for index, room in enumerate(classrooms):
            ClassTeacherAssignment.objects.update_or_create(classroom=room, defaults={"teacher": teachers[index], "effective_date": date(2026, 8, 1)})
            assignment, _ = SubjectAssignment.objects.get_or_create(classroom=room, student=None)
            assignment.courses.set(courses)

        for index, (name, minimum, maximum, remarks) in enumerate([("A", 85, 100, "Excellent"), ("B", 70, 84, "Good"), ("C", 55, 69, "Satisfactory"), ("D", 40, 54, "Needs improvement")]):
            Grade.objects.update_or_create(name=name, classroom=None, defaults={"minimum_marks": minimum, "maximum_marks": maximum, "remarks": remarks})

        for title, text in [("Excellent progress", "[NAME] has shown excellent progress."), ("Keep improving", "[NAME] should keep practicing regularly."), ("Good participation", "[NAME] participates well in class.")]:
            ExamComment.objects.update_or_create(title=title, defaults={"comment": text, "status": "Active"})

        for index, student in enumerate(students):
            for exam in exams:
                Mark.objects.update_or_create(
                    student=student, exam=exam, course=exam.course,
                    defaults={"marks_obtained": Decimal(str(58 + index * 7)), "status": "Active", "remarks": "Mock result"},
                )

        book_type, _ = LibraryBookType.objects.update_or_create(name="Book", defaults={"status": "Active"})
        category, _ = BookCategory.objects.update_or_create(code="GEN", defaults={"name": "General Knowledge", "status": "Active"})
        language, _ = BookLanguage.objects.update_or_create(name="English", defaults={"status": "Active"})
        BookLanguage.objects.update_or_create(name="Urdu", defaults={"status": "Active"})
        author, _ = BookAuthor.objects.update_or_create(name="Stephen R. Covey", defaults={"email": "author@schoolhub.test", "country": "United States", "status": "Active"})
        publisher, _ = BookPublisher.objects.update_or_create(name="SchoolHub Press", defaults={"email": "publisher@schoolhub.test", "city": "Lahore", "country": "Pakistan", "status": "Active"})
        edition, _ = BookEdition.objects.update_or_create(name="2026 Edition", defaults={"status": "Active"})
        library_books = []
        for index, (title, code) in enumerate([("General Knowledge", "BK-001"), ("Python for Students", "BK-002"), ("The Seven Habits", "BK-003")], 1):
            book, _ = LibraryBook.objects.update_or_create(code=code, defaults={"title": title, "book_type": book_type, "category": category, "language": language, "publisher": publisher, "edition": edition, "keywords": "education school knowledge", "status": "Active"})
            book.authors.set([author])
            library_books.append(book)
            for copy_index in range(1, 3):
                BookCopy.objects.update_or_create(code=f"{code}-{copy_index:03}", defaults={"book": book, "price": Decimal("850.00") + index * 100, "arrival_date": date(2026, 8, 14), "condition": "New", "status": "Available"})

        reserved_copy = BookCopy.objects.get(code="BK-001-001")
        BookReservation.objects.update_or_create(copy=reserved_copy, student=students[0], defaults={"employee": None, "reservation_date": date(2026, 8, 14), "status": "Active"})
        reserved_copy.status = "Reserved"; reserved_copy.save(update_fields=["status"])
        issued_copy = BookCopy.objects.get(code="BK-002-001")
        BookIssue.objects.update_or_create(copy=issued_copy, student=students[1], defaults={"employee": None, "issue_date": date(2026, 8, 10), "due_date": date(2026, 8, 24), "status": "Issued"})
        issued_copy.status = "Issued"; issued_copy.save(update_fields=["status"])

        receipt_category, _ = PettyCashCategory.objects.update_or_create(name="School Funds", parent=None, defaults={"transaction_type": "Receipt", "status": "Active"})
        expense_category, _ = PettyCashCategory.objects.update_or_create(name="Stationery", parent=None, defaults={"transaction_type": "Expense", "status": "Active"})
        PettyCashCategory.objects.update_or_create(name="Books", parent=expense_category, defaults={"transaction_type": "Expense", "status": "Active"})
        PettyCashTransaction.objects.update_or_create(transaction_type="Receipt", title="Campus donation", transaction_date=date(2026, 8, 15), defaults={"category": receipt_category, "amount": Decimal("50000.00"), "payment_mode": "Bank Transfer", "department": departments[0], "party_person": "Community donor", "comments": "Mock receipt", "status": "Active"})
        PettyCashTransaction.objects.update_or_create(transaction_type="Expense", title="Office stationery", transaction_date=date(2026, 8, 15), defaults={"category": expense_category, "amount": Decimal("12500.00"), "payment_mode": "Cash", "department": departments[0], "employee": employees[0], "comments": "Mock expense", "status": "Active"})

        models = [Department, Teacher, Student, Course, Classroom, Exam, Attendance, Finance, Notice, Employee, EmployeePayroll, SubjectAssignment, ClassTeacherAssignment, Grade, ExamComment, Mark, LibraryBookType, BookCategory, BookLanguage, BookAuthor, BookPublisher, BookEdition, LibraryBook, BookCopy, BookReservation, BookIssue, PettyCashCategory, PettyCashTransaction]
        self.stdout.write(self.style.SUCCESS("Mock data seeded successfully."))
        for model in models:
            self.stdout.write(f"{model.__name__}: {model.objects.count()}")
