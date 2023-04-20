@echo off
echo Installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt
echo Requirements installation completed.
pause
