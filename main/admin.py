from django.contrib import admin
from .models import Student, Lecture, Attendance, Level, Doctor, Department
from openpyxl import Workbook
from django.http import HttpResponse
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.models import Group



# =========================
# تصدير Excel
# =========================
def export_to_excel(modeladmin, request, queryset):
    wb = Workbook()
    ws = wb.active
    ws.title = "Attendance"
    
    # ✅ أضفنا عمود IP
    ws.append(["كود الطالب", "الاسم", "الفرقة", "المحاضرة", "الحالة", "وقت التسجيل", "IP الجهاز"])

    for record in queryset:
        status_ar = "حاضر" if record.status == "present" else "غياب"
        ws.append([
            record.student.student_id,
            record.student.name,
            str(record.student.level),
            record.lecture.name,
            status_ar,
            record.created_at.replace(tzinfo=None) if record.created_at else "",
            record.device_ip if record.status == "present" else ""  # ✅ الـ IP
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
    list_filter = ('lecture__level__Department', 'lecture__level', 'lecture', 'status')
    search_fields = ('student__name', 'student__student_id', 'lecture__name')
    actions = [export_to_excel, 'mark_as_present', 'mark_as_absent']

    def status_colored(self, obj):
        if obj.status == 'present':
            color = 'lightgreen'
            text = '● حاضر'
        else:
            color = '#ff6b6b'
            text = '● غائب'
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}</span>',
            color, text
        )
    status_colored.short_description = "الحالة"

    def mark_as_present(self, request, queryset):
        queryset.update(status='present')
    mark_as_present.short_description = "تحديد كـ حاضر"

    def mark_as_absent(self, request, queryset):
        queryset.update(status='absent')
    mark_as_absent.short_description = "تحديد كـ غائب"


# =========================
# Inline الحضور جوه المحاضرة
# =========================
class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0
    readonly_fields = ('student', 'status_colored', 'device_ip', 'created_at')
    fields = ('student', 'status_colored', 'device_ip', 'created_at')
    can_delete = False

    def status_colored(self, obj):
        if obj.status == 'present':
            return format_html(
                '<span style="color:lightgreen; font-weight:bold;">● حاضر</span>'
            )
        return format_html(
            '<span style="color:#ff6b6b; font-weight:bold;">● غائب</span>'
        )
    status_colored.short_description = "الحالة"


# =========================
# Lecture Admin — منظم تحت Department → Level
# =========================
class LectureAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_Department', 'get_level', 'date', 'start_time', 'doctor')
    list_filter = ('level__Department', 'level', 'doctor', 'date')
    search_fields = ('name', 'doctor__name')
    inlines = [AttendanceInline]

    # تنظيم الـ form
    fieldsets = (
        ('بيانات المحاضرة', {
            'fields': ('name', 'doctor', 'level', 'date', 'start_time', 'end_time')
        }),
    )

    def get_Department(self, obj):
        if obj.level and obj.level.Department:
            return obj.level.Department.name
        return '-'
    get_Department.short_description = "القسم"
    get_Department.admin_order_field = 'level__Department'

    def get_level(self, obj):
        if obj.level:
            return obj.level.level_name
        return '-'
    get_level.short_description = "المستوى"
    get_level.admin_order_field = 'level'


# =========================
# Student Inline جوه المستوى
# =========================
class StudentInline(admin.TabularInline):
    model = Student
    extra = 0
    fields = ('student_id', 'name', 'user')
    readonly_fields = ('user',)
    show_change_link = True


# =========================
# Level Admin — جوه القسم
# =========================
class LevelInline(admin.TabularInline):
    model = Level
    extra = 0
    fields = ('level_name',)
    show_change_link = True


# =========================
# Level Admin — صفحة مستقلة
# =========================
class LevelAdmin(admin.ModelAdmin):
    list_display = ('level_name', 'Department', 'get_students_count', 'get_lectures_count')
    list_filter = ('Department',)
    search_fields = ('level_name',)
    inlines = [StudentInline]

    def get_students_count(self, obj):
        return obj.students.count()
    get_students_count.short_description = "عدد الطلاب"

    def get_lectures_count(self, obj):
        return obj.lectures.count()
    get_lectures_count.short_description = "عدد المحاضرات"


# =========================
# Department Admin — الأقسام
# =========================
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_levels_count', 'get_students_count')
    search_fields = ('name',)
    inlines = [LevelInline]

    def get_levels_count(self, obj):
        return obj.levels.count()
    get_levels_count.short_description = "عدد المستويات"

    def get_students_count(self, obj):
        total = sum(level.students.count() for level in obj.levels.all())
        return total
    get_students_count.short_description = "إجمالي الطلاب"


# =========================
# Student Admin
# =========================
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'name', 'get_Department', 'level')
    list_filter = ('level__Department', 'level')
    search_fields = ('name', 'student_id')

    def get_Department(self, obj):
        if obj.level and obj.level.Department:
            return obj.level.Department.name
        return '-'
    get_Department.short_description = "القسم"


# =========================
# Doctor Admin — مع المواد والحضور
# =========================
class DoctorLectureInline(admin.TabularInline):
    model = Lecture
    extra = 0
    fields = ('name', 'level', 'date', 'start_time', 'attendance_count')
    readonly_fields = ('attendance_count',)
    show_change_link = True

    def attendance_count(self, obj):
        if obj.pk:
            present = obj.attendances.filter(status='present').count()
            total = obj.attendances.count()
            return format_html(
                '<span style="color:lightgreen; font-weight:bold;">{}</span> / {}',
                present, total
            )
        return '-'
    attendance_count.short_description = "الحضور / الكل"


class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_lectures_count', 'user')
    search_fields = ('name',)
    inlines = [DoctorLectureInline]

    def get_lectures_count(self, obj):
        return obj.lectures.count()
    get_lectures_count.short_description = "عدد المحاضرات"


# =========================
# تسجيل في Admin
# =========================
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Level, LevelAdmin)
admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Lecture, LectureAdmin)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.unregister(Group)