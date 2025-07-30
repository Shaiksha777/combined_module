@echo off
cd /d "C:\Users\Shaiksha\Desktop\phase1_project"

REM (Optional) Activate virtual environment if used
call venv\Scripts\activate

REM Set Flask environment variables
set FLASK_APP=app.py
set FLASK_ENV=development

REM Start the server
start http://127.0.0.1:5000
flask run

pause
