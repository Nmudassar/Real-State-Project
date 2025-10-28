@echo off
cd /d "%~dp0"   
call .my-env/Scripts/activate.bat
python src/main.py 