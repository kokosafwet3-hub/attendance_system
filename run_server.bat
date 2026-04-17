@echo off
cd /d %~dp0

echo ===============================
echo Starting Django Server...
echo ===============================

for /f "tokens=2 delims=:" %%f in ('ipconfig ^| findstr /c:"IPv4"') do (
    set ip=%%f
)

set ip=%ip: =%

echo.
echo افتح الموقع من الجهاز:
echo http://127.0.0.1:8000

echo.
echo افتح من الموبايل:
echo http://%ip%:8000

echo ===============================

python manage.py runserver 0.0.0.0:8000

pause