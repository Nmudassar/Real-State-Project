@echo off
cd /d "%~dp0"   
call .my-env/Scripts/activate.bat
python main.py 