from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.admin.models import LogEntry
from django.contrib.auth.decorators import user_passes_test


def clear_recent(request):
    LogEntry.objects.all().delete()
    return redirect('/admin/')

clear_recent = user_passes_test(lambda u: u.is_superuser)(clear_recent)

urlpatterns = [
    path('admin/clear-recent/', clear_recent, name='clear_recent'),
    path('admin/', admin.site.urls),
    path('', include('main.urls')),  
]
