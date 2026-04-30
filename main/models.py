from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# =========================
# Department (القسم)
# =========================
class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم القسم")

    class Meta:
        verbose_name = "قسم"
        verbose_name_plural = "الأقسام"

    def __str__(self):
        return self.name


# =========================
# Level (المستوى)
# =========================
class Level(models.Model):
    level_name = models.CharField(max_length=50, verbose_name="المستوى")
    Department = models.ForeignKey(
        Department, on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='levels',
        verbose_name="القسم"
    )

    class Meta:
        verbose_name = "مستوى"
        verbose_name_plural = "المستويات"

    def __str__(self):
        if self.Department:
            return f"{self.Department.name} - {self.level_name}"
        return self.level_name


# =========================
# Doctor
# =========================
class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name="الاسم")

    class Meta:
        verbose_name = "دكتور"
        verbose_name_plural = "الدكاترة"

    def __str__(self):
        return self.name


# =========================
# Student
# =========================
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name="الاسم")
    student_id = models.IntegerField(verbose_name="كود الطالب")
    level = models.ForeignKey(
        Level, on_delete=models.CASCADE,
        related_name='students',
        verbose_name="المستوى"
    )

    class Meta:
        verbose_name = "طالب"
        verbose_name_plural = "الطلاب"

    def __str__(self):
        return f"{self.name} ({self.student_id})"


# =========================
# Lecture
# =========================
class Lecture(models.Model):
    name = models.CharField(max_length=200, verbose_name="اسم المادة")
    date = models.DateField(verbose_name="التاريخ")
    start_time = models.TimeField(verbose_name="وقت البداية")
    end_time = models.TimeField(null=True, blank=True, verbose_name="وقت النهاية")
    doctor = models.ForeignKey(
        Doctor, on_delete=models.SET_NULL, null=True,
        related_name='lectures',
        verbose_name="الدكتور"
    )
    level = models.ForeignKey(
        Level, on_delete=models.SET_NULL, null=True,
        related_name='lectures',
        verbose_name="المستوى"
    )

    class Meta:
        verbose_name = "محاضرة"
        verbose_name_plural = "المحاضرات"

    def __str__(self):
        return f"{self.name} - {self.date}"


# =========================
# Attendance
# =========================
class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'حاضر'),
        ('absent', 'غائب'),
    ]

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name="الطالب"
    )
    lecture = models.ForeignKey(
        Lecture, on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name="المحاضرة"
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES,
        default='absent', verbose_name="الحالة"
    )
    device_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP الجهاز")
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="وقت التسجيل")
    marked_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت مسح QR")  # ✅ جديد

    class Meta:
        unique_together = ('student', 'lecture')
        verbose_name = "حضور"
        verbose_name_plural = "سجلات الحضور"

    def __str__(self):
        return f"{self.student.name} - {self.lecture.name} - {self.get_status_display()}"
