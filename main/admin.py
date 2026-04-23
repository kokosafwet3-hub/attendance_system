from django.contrib import admin
from .models import Student, Lecture, Attendance, Level, Doctor
from openpyxl import Workbook
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages


class MyAdminSite(admin.AdminSite):
    site_header = "نظام تسجيل الحضور"
    site_title = "لوحة التحكم"

# =========================
# تصدير Excel
# =========================
def export_to_excel(modeladmin, request, queryset):
    wb = Workbook()
    ws = wb.active
    ws.title = "Attendance"

    # العناوين
    ws.append(["كود الطالب", "الاسم", "الفرقة", "المحاضرة", "الحالة", "وقت التسجيل"])

    # البيانات
    for record in queryset:
       status_ar = "حاضر" if record.status == "present" else "غياب"
       ws.append([
       record.student.student_id,
       record.student.name,
       str(record.student.level),
       record.lecture.name,
       status_ar,
     record.created_at.replace(tzinfo=None) if record.status == "present" else ""
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
    list_display = ('student', 'lecture', 'status_colored', 'created_at')
    list_filter = ('lecture', 'status')
    actions = [
        export_to_excel,       
        'mark_as_present',
        'mark_as_absent',
        'delete_last_records'
    ]

    def status_colored(self, obj):
        if obj.status == 'present':
            return format_html('<span style="color:lightgreen; font-weight:bold;">● Present</span>')
        return format_html('<span style="color:#ff6b6b; font-weight:bold;">● Absent</span>')

    status_colored.short_description = "الحالة"
    def mark_as_present(self, request, queryset):
     queryset.update(status='present')

    mark_as_present.short_description = "تحديد كـ حاضر"

def mark_as_absent(self, request, queryset):
    queryset.update(status='absent')

mark_as_absent.short_description = "تحديد كـ غياب"


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

    
class MyAdminSite(admin.AdminSite):
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('clear-recent/', self.admin_view(self.clear_recent), name='clear_recent'),
        ]
        return custom_urls + urls
    
    def clear_recent(self, request):
        from django.contrib.admin.models import LogEntry
        LogEntry.objects.all().delete()
        messages.success(request, 'تم مسح آخر الإجراءات ✅')
        return redirect('/admin/')

admin_site = MyAdminSite(name='myadmin')



# =========================
# تسجيل في Admin
# =========================
admin.site.register(Student, StudentAdmin)
admin.site.register(Lecture, LectureAdmin)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(Level)
admin.site.register(Doctor)

