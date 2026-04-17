from django.db import models
from django.utils import timezone


# =========================
# Level
# =========================
class Level(models.Model):
    level_name = models.CharField(max_length=50)

    def __str__(self):
        return self.level_name


# =========================
# Doctor
# =========================
class Doctor(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# =========================
# Student
# =========================
class Student(models.Model):
    name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=50, unique=True)
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.student_id})"


# =========================
# Lecture
# =========================
class Lecture(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True)  

    def __str__(self):
        return f"{self.name} - {self.date}"


# =========================
# Attendance
# =========================
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    device_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('student', 'lecture', 'device_ip')

    def __str__(self):
        return f"{self.student.name} - {self.lecture.name} - {self.device_ip}"

    @staticmethod
    def already_registered(student, lecture, device_ip=None):
        qs = Attendance.objects.filter(student=student, lecture=lecture)
        if device_ip:
            qs = qs.filter(device_ip=device_ip)
        return qs.exists()