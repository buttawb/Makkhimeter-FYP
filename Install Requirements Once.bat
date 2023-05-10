@echo off

set VENV_DIR=venv

if exist %VENV_DIR% (
  echo Awaking PYTHON...
  call %VENV_DIR%\Scripts\activate.bat
) else (
  echo Creating virtual environment...
  python -m venv %VENV_DIR%
  echo Virtual environment created.
  echo Awaking PYTHON...
  call %VENV_DIR%\Scripts\activate.bat
)



echo Installing dependencies...

pip install -r requirements.txt
echo Requirements installation completed.
pause
