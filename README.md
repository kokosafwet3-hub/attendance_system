#  نظام تسجيل الحضور — MCI Attendance System

---

##  نبذة عن المشروع
نظام ويب لتسجيل حضور الطلاب عن طريق QR Code، مبني بـ Django ويدعم 3 أدوار:
- **Admin** — إدارة الدكاترة والطلاب والمحاضرات والمستويات
- **Doctor** — عرض المحاضرات وتوليد QR Code
- **Student** — مسح QR Code وتسجيل الحضور

---

##  المتطلبات
- Python 3.10+
- MySQL Server
- pip

---

##  خطوات التشغيل

### 1) تثبيت المكتبات
افتح CMD داخل فولدر المشروع واكتب:

```bash
pip install -r requirements.txt
```

أو اضغط دبل كليك على:
```
install.bat
```

---

### 2) إعداد قاعدة البيانات

افتح MySQL وشغّل:
```sql
CREATE DATABASE attendance_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

تأكد إن بيانات الاتصال في `settings.py` صح:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'attendance_system',
        'USER': 'root',
        'PASSWORD': 'root123',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

---

### 3) تطبيق الـ Migrations
```bash
python manage.py migrate
```

---

### 4) إنشاء حساب Admin
```bash
python manage.py createsuperuser
```
اتبع التعليمات وأدخل username وpassword.

---

### 5) تشغيل السيرفر

🔹 **الطريقة السهلة:**
```
run_server.bat
```

🔹 **أو من CMD:**
```bash
python manage.py runserver 0.0.0.0:8000
```

---

##  فتح الموقع

### من نفس الجهاز:
```
http://127.0.0.1:8000
```

### لوحة الـ Admin:
```
http://127.0.0.1:8000/admin
```

### من الموبايل (نفس الشبكة):
1. اعرف الـ IP:
```bash
ipconfig
```
2. افتح في المتصفح:
```
http://192.168.x.x:8000
```
> استبدل `x.x` بالـ IP الحقيقي بتاع جهازك

---

##  الأدوار والصلاحيات

| الدور | الصفحة الرئيسية | الصلاحيات |
|-------|----------------|-----------|
| Admin | `/admin` | إضافة وتعديل وحذف كل البيانات |
| Doctor | `/home` | عرض المحاضرات وتوليد QR |
| Student | `/student-home` | مسح QR وتسجيل الحضور |

---

##  هيكل المشروع

```
attendance_system/
│
├── main/
│   ├── static/main/css/
│   │   ├──style.css
│   │   ├──custom.css
│   │   └── images/logo.png
│   ├── templates/main/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── home.html
│   │   ├── select_level.html
│   │   ├── lectures.html
│   │   ├── lecture_detail.html
│   │   ├── qr_page.html
│   │   ├── student_home.html
│   │   ├── student_lecture.html
│   │   ├── scan_qr.html
│   │   └── mark_attendance.html
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── attendance_system/
│   ├── settings.py
│   └── urls.py
│
├── requirements.txt
├── manage.py
├── install.bat
└── run_server.bat
```

---

##  ملاحظات مهمة

- الموبايل والكمبيوتر لازم يكونوا على **نفس شبكة WiFi**
- لو الموقع مش بيفتح على الموبايل:
  - ✔ افتح الـ **Firewall** على port 8000
- لو اتغير الـ IP:
  - ✔ استخدم الـ IP الجديد بس — مش محتاج تعديل في المشروع
- الـ `DEBUG = True` للتطوير بس — لا ترفعه على سيرفر حقيقي

---

##  تشغيل سريع (ملخص)

```
1. install.bat          ← تثبيت المكتبات
2. إنشاء قاعدة البيانات في MySQL
3. python manage.py migrate
4. python manage.py createsuperuser
5. run_server.bat       ← تشغيل المشروع
```

---

## 🛠️ المكتبات المستخدمة

| المكتبة | الاستخدام |
|---------|-----------|
| Django | الـ Framework الأساسي |
| mysqlclient | الاتصال بـ MySQL |
| qrcode | توليد QR Code |
| Pillow | معالجة الصور |
| django-jazzmin | تحسين شكل لوحة الـ Admin |

---

>  لأي مشكلة في التشغيل تأكد أولاً إن MySQL شغال وبيانات الاتصال صح في `settings.py`
