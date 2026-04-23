from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('home/', views.home, name='home'),
    path('lectures/', views.lectures_page, name='lectures_page'),

    path('lecture/<int:lecture_id>/', views.lecture_detail, name='lecture_detail'),
    path('lecture/<int:lecture_id>/attendance/', views.mark_attendance, name='mark_attendance'),
    path('lecture/<int:lecture_id>/qr/', views.generate_qr, name='generate_qr'),
       path('lecture/<int:lecture_id>/export/', views.export_lecture_excel, name='export_lecture_excel'),
       path('levels/', views.select_level, name='select_level'),
       path('lectures/level/<int:level_id>/', views.lectures_page, name='lectures_by_level'),
       path('login/', views.login_view, name='login'),
       path('student-home/', views.student_home, name='student_home'),
       path('student/lecture/<int:lecture_id>/', views.student_lecture, name='student_lecture'),
       path('scan/<int:lecture_id>/', views.scan_qr, name='scan_qr'),
       path('logout/', views.logout_view, name='logout'),
       path('lecture/<int:lecture_id>/qr-page/', views.qr_page, name='qr_page'),
       
]