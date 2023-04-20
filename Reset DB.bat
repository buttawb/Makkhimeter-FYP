@echo off
echo Flushing database...

call venv\Scripts\activate.bat
python manage.py flush
echo Database flush completed.
pause
