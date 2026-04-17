from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import HttpResponse
from django.contrib import messages
from .models import Student, Lecture, Attendance
from .forms import StudentForm
import qrcode
from io import BytesIO
from openpyxl import Workbook


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
def home(request):
    today = timezone.now().date()
    lectures = Lecture.objects.filter(date__gte=today).order_by('date')
    return render(request, 'main/home.html', {'lectures': lectures})

# =========================
# اختيار الفرقة 
# =========================
def select_level(request):
    return render(request, 'main/select_level.html')

# =========================
# تفاصيل المحاضرة
# =========================
def lecture_detail(request, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id)
    return render(request, 'main/lecture_detail.html', {'lecture': lecture})


# =========================
# تسجيل الحضور
# =========================
def mark_attendance(request, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id)

    if request.method == 'POST':
        student_id = request.POST.get('student_id')

        device_ip = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        try:
            student = Student.objects.get(student_id=student_id)
        except Student.DoesNotExist:
            messages.error(request, "الطالب غير موجود ❌")
            return redirect('mark_attendance', lecture_id=lecture.id)

        if Attendance.already_registered(student, lecture, device_ip):
            messages.warning(request, "تم تسجيل حضورك من هذا الجهاز بالفعل ✅")
            return redirect('mark_attendance', lecture_id=lecture.id)

        Attendance.objects.create(
            student=student,
            lecture=lecture,
            device_ip=device_ip,
            user_agent=user_agent
        )

        messages.success(request, f"تم تسجيل حضورك يا {student.name} ✅")
        return redirect('mark_attendance', lecture_id=lecture.id)

    return render(request, 'main/mark_attendance.html', {'lecture': lecture})


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

    server_ip = request.get_host().split(':')[0] # 192.168.1.5
    qr.add_data(f'http://{server_ip}:8000/lecture/{lecture.id}/attendance/')

    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')

    buffer = BytesIO()
    img.save(buffer)

    return HttpResponse(buffer.getvalue(), content_type='image/png')


# =========================
# صفحة عرض كل المحاضرات
# =========================
def lectures_page(request, level_id=None):
    if level_id:
        lectures = Lecture.objects.filter(level__level_name__contains=level_id).order_by('-date')
    else:
        lectures = Lecture.objects.all().order_by('-date')

    return render(request, 'main/lectures.html', {'lectures': lectures})


# =========================
# Export Excel per Lecture (ADMIN ONLY)
# =========================
def export_lecture_excel(request, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id)
    records = Attendance.objects.filter(lecture=lecture)

    wb = Workbook()
    ws = wb.active
    ws.title = "Attendance"

    ws.append(["كود الطالب", "الاسم", "IP", "الوقت"])

    for record in records:
        ws.append([
            record.student.student_id,
            record.student.name,
            record.device_ip,
            record.created_at.replace(tzinfo=None)
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=lecture_{lecture.id}.xlsx'

    wb.save(response)
    return response