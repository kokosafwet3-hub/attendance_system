from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# =========================
# Student
# =========================
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  
    name = models.CharField(max_length=100)
    student_id = models.IntegerField()
    level = models.ForeignKey(Level, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

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
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='absent')

    device_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('student', 'lecture')

    def __str__(self):
        return f"{self.student.name} - {self.lecture.name} - {self.status}"