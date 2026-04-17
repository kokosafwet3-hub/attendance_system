from django.contrib import admin
from .models import Student, Lecture, Attendance, Level, Doctor
from openpyxl import Workbook
from django.http import HttpResponse


# =========================
# تصدير Excel
# =========================
def export_to_excel(modeladmin, request, queryset):
    wb = Workbook()
    ws = wb.active
    ws.title = "Attendance"

    # العناوين
    ws.append(["كود الطالب", "الاسم","الفرقة", "المحاضرة", "IP", "وقت الدخول"])

    # البيانات
    for record in queryset:
        ws.append([
            record.student.student_id,
            record.student.name,
            str(record.student.level) if record.student.level else "",
            record.lecture.name,
            record.device_ip,
            record.created_at.replace(tzinfo=None)
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=attendance.xlsx'

    wb.save(response)
    return response

export_to_excel.short_description = "تصدير الحضور إلى Excel"


# =========================
# Attendance Admin
# =========================
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'lecture', 'device_ip', 'created_at')
    list_filter = ('lecture',)
    actions = [export_to_excel]


# =========================
# Inline جوه المحاضرة
# =========================
class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0
    readonly_fields = ('student', 'device_ip', 'created_at')
    can_delete = False


# =========================
# Lecture Admin
# =========================
class LectureAdmin(admin.ModelAdmin):
    list_display = ('name', 'date')
    inlines = [AttendanceInline]


# =========================
# Student Admin
# =========================
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'name', 'level')


# =========================
# تسجيل في Admin
# =========================
admin.site.register(Student, StudentAdmin)
admin.site.register(Lecture, LectureAdmin)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(Level)
admin.site.register(Doctor)
