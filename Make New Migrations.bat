@echo off
echo Deleting old migrations...

del db.sqlite3
del Droso\migrations\0001_initial.py


call venv\Scripts\activate.bat
echo Creating new migrations...



python manage.py makemigrations 
python manage.py migrate 


echo Database refurbished. 
pause
