@echo off
echo Flushing Database... 


call venv\Scripts\activate.bat
echo Creating new migrations...

python manage.py flush


echo Database cleaned. 
pause
