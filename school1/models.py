from django.db import models


class Department(models.Model):
    STATUS_DEPARTMENT=[
        ('Active','Active'),
        ('InActive','InActive'),
        ]
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    head_of_department=models.CharField(max_length=100, blank=True)
    email=models.EmailField(blank=True)
    phone=models.CharField(max_length=100, blank=True)
    office_location=models.CharField(max_length=100, blank=True)
    established_date=models.DateField(null=True, blank=True)
    status=models.CharField(max_length=100,choices=STATUS_DEPARTMENT, blank=True)
    website=models.URLField(blank=True)
    office_extension=models.CharField(max_length=20, blank=True)
    total_staff=models.PositiveIntegerField(default=0)
    budget=models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    def __str__(self):
        return f"{self.code} - {self.name}"


class Student(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=30, unique=True, null=True, blank=True)
    age = models.PositiveIntegerField()
    email = models.EmailField(unique=True)
    course = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    guardian_name = models.CharField(max_length=100, blank=True)
    guardian_phone = models.CharField(max_length=20, blank=True)
    admission_date = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.roll_number} - {self.name}"


class Teacher(models.Model):
    FirstName = models.CharField(max_length=100, null=True, blank=True)
    LastName = models.CharField(max_length=100, null=True, blank=True)
    DateofBirth = models.DateField(null=True, blank=True)
    Email = models.EmailField(null=True, blank=True)
    PhoneNumber = models.CharField(max_length=100, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    Address = models.TextField(blank=True)
    ProfilePhoto = models.FileField(upload_to='teachers/', blank=True)
    Qualification = models.CharField(max_length=100, null=True, blank=True)
    Specialization = models.CharField(max_length=100, null=True, blank=True)
    Gender = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return " ".join(part for part in [self.FirstName, self.LastName] if part) or "Unnamed teacher"


class Course(models.Model):
    course_name=models.CharField(max_length=100)
    course_code=models.CharField(max_length=20, unique=True)
    description=models.TextField(blank=True)
    duration=models.CharField(max_length=50)
    department=models.ForeignKey(Department,on_delete=models.SET_NULL,null=True,blank=True)
    teacher=models.ForeignKey(Teacher,on_delete=models.CASCADE)
    def __str__(self): return f"{self.course_code} - {self.course_name}"


class Classroom(models.Model):
    class_name=models.CharField(max_length=50)
    section=models.CharField(max_length=10)
    room_number=models.CharField(max_length=20)
    teacher=models.ForeignKey(Teacher,on_delete=models.SET_NULL,null=True,blank=True)
    def __str__(self): return f"{self.class_name} - {self.section}"


class Exam(models.Model):
    exam_name=models.CharField(max_length=100)
    classroom=models.ForeignKey(Classroom,on_delete=models.CASCADE)
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    exam_date=models.DateField()
    total_marks=models.IntegerField()
    passing_marks=models.IntegerField()
    def __str__(self): return f"{self.exam_name} - {self.course}"


class SubjectAssignment(models.Model):
    classroom=models.ForeignKey(Classroom,on_delete=models.CASCADE)
    student=models.ForeignKey(Student,on_delete=models.CASCADE,null=True,blank=True)
    courses=models.ManyToManyField(Course)
    def __str__(self): return f"{self.classroom} - {self.student or 'All students'}"


class ClassTeacherAssignment(models.Model):
    classroom=models.OneToOneField(Classroom,on_delete=models.CASCADE)
    teacher=models.ForeignKey(Teacher,on_delete=models.CASCADE)
    effective_date=models.DateField()
    def __str__(self): return f"{self.classroom} - {self.teacher}"


class Grade(models.Model):
    name=models.CharField(max_length=10)
    classroom=models.ForeignKey(Classroom,on_delete=models.CASCADE,null=True,blank=True)
    remarks=models.CharField(max_length=100,blank=True)
    minimum_marks=models.PositiveIntegerField()
    maximum_marks=models.PositiveIntegerField()
    def __str__(self): return f"{self.name} ({self.minimum_marks}-{self.maximum_marks}%)"


class ExamComment(models.Model):
    STATUS_CHOICES=[('Active','Active'),('Inactive','Inactive')]
    title=models.CharField(max_length=150)
    comment=models.TextField()
    status=models.CharField(max_length=10,choices=STATUS_CHOICES,default='Active')
    def __str__(self): return self.title


class Mark(models.Model):
    STATUS_CHOICES=[('Active','Active'),('Inactive','Inactive')]
    student=models.ForeignKey(Student,on_delete=models.CASCADE)
    exam=models.ForeignKey(Exam,on_delete=models.CASCADE)
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    marks_obtained=models.DecimalField(max_digits=7,decimal_places=2)
    status=models.CharField(max_length=10,choices=STATUS_CHOICES,default='Active')
    remarks=models.CharField(max_length=200,blank=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['student','exam','course'],name='unique_student_exam_course_mark')]
    def __str__(self): return f"{self.student} - {self.exam.exam_name}: {self.marks_obtained}"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Leave', 'Leave'),
        ('Late', 'Late'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-id']
        constraints = [
            models.UniqueConstraint(fields=['student', 'date'], name='unique_student_attendance_per_day'),
        ]

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"


class Notice(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    published_on = models.DateField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')

    class Meta:
        ordering = ['-published_on', '-id']

    def __str__(self):
        return self.title


class Finance(models.Model):
    FEE_TYPE_CHOICES = [
        ('Tuition', 'Tuition'),
        ('Transport', 'Transport'),
        ('Exam', 'Exam'),
        ('Library', 'Library'),
        ('Hostel', 'Hostel'),
        ('Other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
        ('Partial', 'Partial'),
        ('Overdue', 'Overdue'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('Cash', 'Cash'),
        ('Bank', 'Bank'),
        ('Online', 'Online'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    fee_type = models.CharField(max_length=100, choices=FEE_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES)
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHOD_CHOICES)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.name} - {self.fee_type} - {self.status}"

class Employee(models.Model):

    SHIFT_CHOICE=[
        ('Morning','Morning'),
        ('Evening','Evening'),
    ]

    GENDER_CHOICES = [
    ('Male','Male'),
    ('Female','Female')
]
    
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)
    gender=models.CharField(max_length=100,choices=GENDER_CHOICES)
    date_of_birth=models.DateField()
    email=models.EmailField()
    phone=models.CharField(max_length=100)
    address=models.TextField()
    salary=models.DecimalField(max_digits=10,decimal_places=2)
    hire_date=models.DateField()
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    CNIC=models.CharField(max_length=100,unique=True)
    shift = models.CharField(max_length=20,choices=SHIFT_CHOICE)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class EmployeePayroll(models.Model):
    STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
    ]
    
    
    employee=models.ForeignKey(Employee,on_delete=models.CASCADE)
    month = models.CharField(max_length=20)
    year = models.IntegerField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Pending'
    )
    remarks = models.TextField(blank=True)
    def save(self, *args, **kwargs):
        self.net_salary = (
            self.basic_salary +
            self.allowance +
            self.bonus -
            self.deduction
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee} - {self.month} {self.year}" 


LIBRARY_STATUS=[('Active','Active'),('Inactive','Inactive')]

class LibraryBookType(models.Model):
    name=models.CharField(max_length=80,unique=True); status=models.CharField(max_length=10,choices=LIBRARY_STATUS,default='Active')
    def __str__(self): return self.name

class BookCategory(models.Model):
    name=models.CharField(max_length=100); code=models.CharField(max_length=20,unique=True)
    parent=models.ForeignKey('self',on_delete=models.SET_NULL,null=True,blank=True)
    status=models.CharField(max_length=10,choices=LIBRARY_STATUS,default='Active')
    def __str__(self): return f"{self.parent} / {self.name}" if self.parent else self.name

class BookLanguage(models.Model):
    name=models.CharField(max_length=50,unique=True); status=models.CharField(max_length=10,choices=LIBRARY_STATUS,default='Active')
    def __str__(self): return self.name

class BookAuthor(models.Model):
    name=models.CharField(max_length=120); email=models.EmailField(blank=True); phone=models.CharField(max_length=30,blank=True); country=models.CharField(max_length=80,blank=True); status=models.CharField(max_length=10,choices=LIBRARY_STATUS,default='Active')
    def __str__(self): return self.name

class BookPublisher(models.Model):
    name=models.CharField(max_length=120); email=models.EmailField(blank=True); phone=models.CharField(max_length=30,blank=True); website=models.URLField(blank=True); address=models.CharField(max_length=200,blank=True); city=models.CharField(max_length=80,blank=True); country=models.CharField(max_length=80,blank=True); status=models.CharField(max_length=10,choices=LIBRARY_STATUS,default='Active')
    def __str__(self): return self.name

class BookEdition(models.Model):
    name=models.CharField(max_length=80,unique=True); status=models.CharField(max_length=10,choices=LIBRARY_STATUS,default='Active')
    def __str__(self): return self.name

class LibraryBook(models.Model):
    title=models.CharField(max_length=180); code=models.CharField(max_length=30,unique=True)
    book_type=models.ForeignKey(LibraryBookType,on_delete=models.PROTECT); category=models.ForeignKey(BookCategory,on_delete=models.PROTECT); language=models.ForeignKey(BookLanguage,on_delete=models.PROTECT)
    publisher=models.ForeignKey(BookPublisher,on_delete=models.SET_NULL,null=True,blank=True); edition=models.ForeignKey(BookEdition,on_delete=models.SET_NULL,null=True,blank=True); authors=models.ManyToManyField(BookAuthor,blank=True)
    keywords=models.CharField(max_length=250,blank=True); status=models.CharField(max_length=10,choices=LIBRARY_STATUS,default='Active')
    def __str__(self): return f"{self.code} - {self.title}"

class BookCopy(models.Model):
    CONDITION_CHOICES=[('New','New'),('Normal','Normal'),('Damaged','Damaged')]; COPY_STATUS=[('Available','Available'),('Reserved','Reserved'),('Issued','Issued'),('Lost','Lost'),('Discarded','Discarded')]
    code=models.CharField(max_length=40,unique=True); book=models.ForeignKey(LibraryBook,on_delete=models.CASCADE); price=models.DecimalField(max_digits=10,decimal_places=2,default=0); arrival_date=models.DateField(); condition=models.CharField(max_length=10,choices=CONDITION_CHOICES,default='New'); status=models.CharField(max_length=10,choices=COPY_STATUS,default='Available')
    def __str__(self): return f"{self.code} - {self.book.title}"

class BookReservation(models.Model):
    STATUS_CHOICES=[('Active','Active'),('Fulfilled','Fulfilled'),('Cancelled','Cancelled')]
    copy=models.ForeignKey(BookCopy,on_delete=models.CASCADE); student=models.ForeignKey(Student,on_delete=models.CASCADE,null=True,blank=True); employee=models.ForeignKey(Employee,on_delete=models.CASCADE,null=True,blank=True); reservation_date=models.DateField(); status=models.CharField(max_length=10,choices=STATUS_CHOICES,default='Active')
    def __str__(self): return f"{self.copy} - {self.student or self.employee}"

class BookIssue(models.Model):
    STATUS_CHOICES=[('Issued','Issued'),('Returned','Returned'),('Overdue','Overdue')]
    copy=models.ForeignKey(BookCopy,on_delete=models.CASCADE); student=models.ForeignKey(Student,on_delete=models.CASCADE,null=True,blank=True); employee=models.ForeignKey(Employee,on_delete=models.CASCADE,null=True,blank=True); issue_date=models.DateField(); due_date=models.DateField(); returned_date=models.DateField(null=True,blank=True); status=models.CharField(max_length=10,choices=STATUS_CHOICES,default='Issued')
    def __str__(self): return f"{self.copy} - {self.student or self.employee} ({self.status})"

class PettyCashCategory(models.Model):
    TYPE_CHOICES=[
        ("Receipt","Receipt"),
        ("Expense","Expense"),
        ("Both","Receipt/Expense"),
    ]
    STATUS_CHOICES=[
            ("Active","Active"),
            ("Inactive","Inactive"),
        ]
    name=models.CharField(max_length=120)
    parent=models.ForeignKey('self',on_delete=models.SET_NULL,null=True,blank=True)
    transaction_type=models.CharField(max_length=10,choices=TYPE_CHOICES,default="Both")
    status=models.CharField(max_length=10,choices=STATUS_CHOICES,default="Active")
    class Meta:
        verbose_name_plural="Petty cash categories"
    def __str__(self):
        if self.parent:
            return f"{self.parent}->{self.name}"
        return self.name

class PettyCashTransaction(models.Model):
    TYPE_CHOICES = [
        ("Receipt", "Receipt"),
        ("Expense", "Expense"),
    ]

    PAYMENT_MODES = [
        ("Cash", "Cash"),
        ("Bank Transfer", "Bank Transfer"),
        ("Cheque", "Cheque"),
        ("Online", "Online"),
    ]

    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Inactive", "Inactive"),
    ]
    transaction_type=models.CharField(max_length=10,choices=TYPE_CHOICES,)
    category=models.ForeignKey(PettyCashCategory,on_delete=models.PROTECT,)
    title=models.CharField(max_length=160)
    amount=models.DecimalField( max_digits=12,decimal_places=2,)
    payment_mode = models.CharField( max_length=20,choices=PAYMENT_MODES,)
    transaction_date = models.DateField()
    party_person = models.CharField(max_length=150,blank=True,)
    comments = models.TextField(blank=True)
    invoice = models.FileField(upload_to="petty_cash/invoices/", blank=True,)
    status = models.CharField(max_length=10,choices=STATUS_CHOICES,default="Active",)
    department=models.ForeignKey(Department,on_delete=models.SET_NULL,null=True,blank=True,verbose_name="School/Department")
    employee = models.ForeignKey(Employee,on_delete=models.SET_NULL,null=True,blank=True,)
    student = models.ForeignKey(Student,on_delete=models.SET_NULL,null=True, blank=True,)
    class Meta:
        ordering = ["-transaction_date", "-id"]

    def __str__(self):
        return (
            f"{self.transaction_type}: "
            f"{self.title} ({self.amount})"
        )


INVENTORY_STATUS = [
    ("Active", "Active"),
    ("Inactive", "Inactive"),
]


class InventoryCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    status = models.CharField(max_length=10, choices=INVENTORY_STATUS, default="Active")

    def __str__(self):
        return self.name


class InventoryBrand(models.Model):
    name = models.CharField(max_length=120, unique=True)
    status = models.CharField(max_length=10, choices=INVENTORY_STATUS, default="Active")

    def __str__(self):
        return self.name


class InventorySupplier(models.Model):
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=INVENTORY_STATUS, default="Active")

    def __str__(self):
        return self.name


class InventoryAttribute(models.Model):
    name = models.CharField(max_length=120)
    value = models.CharField(max_length=120)
    status = models.CharField(max_length=10, choices=INVENTORY_STATUS, default="Active")

    def __str__(self):
        return f"{self.name}: {self.value}"


class InventoryItem(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(InventoryCategory, on_delete=models.SET_NULL, null=True, blank=True)
    brand = models.ForeignKey(InventoryBrand, on_delete=models.SET_NULL, null=True, blank=True)
    supplier = models.ForeignKey(InventorySupplier, on_delete=models.SET_NULL, null=True, blank=True)
    unit = models.CharField(max_length=30, default="pcs")
    quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=0)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=INVENTORY_STATUS, default="Active")

    def __str__(self):
        return f"{self.code} - {self.name}"


class InventoryRecord(models.Model):
    RECORD_TYPES = [
        ("Inventory", "Inventory"),
        ("Transfer", "Transfer"),
        ("Adjustment", "Adjustment"),
    ]

    record_type = models.CharField(max_length=20, choices=RECORD_TYPES)
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    date = models.DateField()
    reference = models.CharField(max_length=100, blank=True)
    remarks = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=INVENTORY_STATUS, default="Active")

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.record_type}: {self.item} ({self.quantity})"
    
