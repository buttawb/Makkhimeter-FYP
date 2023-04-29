@echo off
echo Creating Special User...
call venv\Scripts\activate.bat

python manage.py createsuperuser


pause
