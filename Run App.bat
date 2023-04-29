@echo off

echo Waiting for Anonymous User to be created...
call venv\Scripts\activate.bat

start /wait python Anonymous_User.py

echo Starting Django server...

python manage.py runserver

pause
