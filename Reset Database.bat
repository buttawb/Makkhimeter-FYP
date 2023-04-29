@echo off
echo Flushing Database... 


call venv\Scripts\activate.bat

python manage.py flush


echo Database cleaned. 
pause
