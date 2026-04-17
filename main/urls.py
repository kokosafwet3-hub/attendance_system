from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('lectures/', views.lectures_page, name='lectures_page'),

    path('lecture/<int:lecture_id>/', views.lecture_detail, name='lecture_detail'),
    path('lecture/<int:lecture_id>/attendance/', views.mark_attendance, name='mark_attendance'),
    path('lecture/<int:lecture_id>/qr/', views.generate_qr, name='generate_qr'),
       path('lecture/<int:lecture_id>/export/', views.export_lecture_excel, name='export_lecture_excel'),
       path('levels/', views.select_level, name='select_level'),
       path('lectures/level/<int:level_id>/', views.lectures_page, name='lectures_by_level'),
]