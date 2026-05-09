from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
import datetime
from django.http import HttpResponse
from django.contrib import messages
from .models import Student, Lecture, Attendance, Level, Department
from .forms import StudentForm
import qrcode
from io import BytesIO
from openpyxl import Workbook
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect




# =========================
# Helper: Get Client IP
# =========================
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# =========================
# الصفحة الرئيسية
# =========================
@login_required
def home(request):
    today = timezone.now().date()
    lectures = Lecture.objects.filter(date__gte=today).order_by('date')
    return render(request, 'main/home.html', {'lectures': lectures})

# =========================
# اختيار الفرقة 
# =========================
@login_required
def select_level(request, department_id):
    department = get_object_or_404(Department, id=department_id)

    levels = Level.objects.filter(Department=department)

    return render(request, 'main/select_level.html', {
        'department': department,
        'levels': levels
    })

# =========================
# تفاصيل المحاضرة
# =========================
@login_required
def lecture_detail(request, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id)

    students = Student.objects.filter(level=lecture.level)

    for student in students:
        Attendance.objects.get_or_create(
            student=student,
            lecture=lecture,
            defaults={'status': 'absent'}
        )

    return render(request, 'main/lecture_detail.html', {'lecture': lecture})


# =========================
# تسجيل الحضور
# =========================
@login_required
def mark_attendance(request, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id)

    if not hasattr(request.user, 'student'):
        messages.error(request, "هذا الحساب ليس طالب ❌")
        return redirect('login')

    student = request.user.student
    
    # ✅ الحل: return جوه الـ if
    if student.level != lecture.level or student.level.Department != lecture.level.Department:
        messages.error(request, "هذه المحاضرة ليست مخصصة لك ❌")
        return redirect('student_home')

    device_ip = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    attendance, created = Attendance.objects.get_or_create(
        student=student,
        lecture=lecture,
        defaults={'status': 'absent'}
    )

    if attendance.status == 'present':
        messages.warning(request, "تم تسجيل حضورك بالفعل ✅")
    else:
        attendance.status = 'present'
        attendance.device_ip = device_ip
        attendance.user_agent = user_agent
        attendance.marked_at = timezone.now()
        attendance.save()
        messages.success(request, f"تم تسجيل حضورك يا {student.name} ✅")

    return render(request, 'main/mark_attendance.html', {
        'lecture': lecture,
        'already_marked': not created   
    })


# =========================
# توليد QR Code لكل محاضرة
# =========================
def generate_qr(request, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id)

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5
    )

    base_url = request.build_absolute_uri(f'/lecture/{lecture.id}/attendance/')
    qr.add_data(base_url)

    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')

    buffer = BytesIO()
    img.save(buffer)

    return HttpResponse(buffer.getvalue(), content_type='image/png')


# =========================
# صفحة عرض كل المحاضرات
# =========================
@login_required
def lectures_page(request, level_id):
    today = datetime.date.today()

    lectures = Lecture.objects.filter(
        level_id=level_id,
        date=today
    ).order_by('start_time')

    return render(request, 'main/lectures.html', {
        'lectures': lectures
    })
# =========================
# Export Excel per Lecture (ADMIN ONLY)
# =========================
def export_lecture_excel(request, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id)
    records = Attendance.objects.filter(lecture=lecture)

    wb = Workbook()
    ws = wb.active
    ws.title = "Attendance"

    
    ws.append(["كود الطالب", "الاسم", "الفرقة", "المحاضرة", "الحالة", "وقت التسجيل", "IP الجهاز"])

    for record in records:
        status_ar = "حاضر" if record.status == "present" else "غياب"
        ws.append([
            record.student.student_id,
            record.student.name,
            str(record.student.level),
            record.lecture.name,
            status_ar,
            record.marked_at.replace(tzinfo=None) if record.status == "present" else "",
            record.device_ip if record.status == "present" else ""  
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=lecture_{lecture.id}.xlsx'

    wb.save(response)
    return response

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        role = request.POST.get("role")

        user = authenticate(request, username=username, password=password)

        print("USER:", user)
        print("ROLE:", role)

        if user is None:
            messages.error(request, "Incorrect username or password")
            return redirect('login')   

        login(request, user)

        
        if role == "admin":
            if user.is_superuser:
                return redirect('/admin/')
            else:
                messages.error(request, "You're not an admin")
                return redirect('login')   

        # 🟢 Student
        elif role == "student":
            if hasattr(user, 'student'):
                return redirect('student_home')
            else:
                messages.error(request, "You're not a student.")
                return redirect('login')

        # 🟢 Doctor
        elif role == "doctor":
            if hasattr(user, 'doctor'):
                return redirect('home')
            else:
                messages.error(request, "You're not a doctor.")
                return redirect('login')

        # 🟢 لو محددش role
        messages.error(request, "Select user role")
        return redirect('login')

    return render(request, "main/login.html")

@login_required
def student_home(request):
    student = request.user.student
    today = datetime.date.today()

    lectures = Lecture.objects.filter(
        level=student.level,
        date=today
    )

    lectures_data = []
    has_warning = False

    for lecture in lectures:
        total_lectures = Lecture.objects.filter(
            name=lecture.name,
            level=student.level
        ).count()

        present_count = Attendance.objects.filter(
            student=student,
            lecture__name=lecture.name,
            lecture__level=student.level,
            status='present'
        ).count()

        percentage = (present_count / total_lectures * 100) if total_lectures > 0 else 100
        warn = total_lectures >= 5 and percentage < 50

        if warn:
            has_warning = True

        lectures_data.append({
            'lecture': lecture,
            'warn': warn,
            'percentage': round(percentage, 1),
        })

    return render(request, 'main/student_home.html', {
        'lectures_data': lectures_data,
        'has_warning': has_warning,
    })

@login_required
def student_lecture(request, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id)
    student = request.user.student

    # 🔒 حماية: الطالب لازم يكون من نفس الفرقة والقسم
    if student.level != lecture.level or student.level.Department != lecture.level.Department:
        messages.error(request, "غير مصرح لك بدخول هذه المحاضرة ❌")
        return redirect('student_home')

    # 🟢 كل محاضرات نفس المادة داخل نفس الفرقة والقسم
    total_lectures = Lecture.objects.filter(
        name=lecture.name,
        level=student.level
    ).count()

    # 🟢 عدد حضور الطالب لنفس المادة
    present_count = Attendance.objects.filter(
        student=student,
        lecture__name=lecture.name,
        lecture__level=student.level,
        status='present'
    ).count()

    # 🟢 نسبة الحضور
    if total_lectures > 0:
        percentage = (present_count / total_lectures) * 100
    else:
        percentage = 0

    # ✅ الرسالة تظهر بس لو في 5 محاضرات على الأقل والنسبة أقل من 50%
    warning = total_lectures >= 5 and percentage < 50

    return render(request, 'main/student_lecture.html', {
        'lecture': lecture,
        'warning': warning,
        'percentage': round(percentage, 1)
    })

@login_required
def scan_qr(request,lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id)
    return render(request,'main/scan_qr.html',{'lecture': lecture})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def qr_page(request, lecture_id):
    lecture = Lecture.objects.get(id=lecture_id)

    return render(request, "main/qr_page.html", {
        "qr_code_url": f"/lecture/{lecture.id}/qr/"
    })

@login_required
def lectures_view(request):
    return render(request, "lectures.html", {
        "show_home": True,
        "home_url": "/home/"
    })

@login_required
def student_scan(request):
    return render(request, "scan.html", {
        "show_home": True,
        "home_url": "/student-home/"
    })

@login_required
def select_department(request):
    departments =  Department.objects.all()

    return render(request, 'main/select_department.html', {
        'departments': departments
    })

def faq_view(request):
    return render(request, 'main/faq.html')
