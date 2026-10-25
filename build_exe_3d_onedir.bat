@echo off
chcp 65001 >nul
echo ================================================
echo   BUILDING EnglishTutor3D - BAN FOLDER (du phong)
echo   Chi dung khi ban onefile bi loi voi Ursina.
echo   File ra: dist\EnglishTutor3D\EnglishTutor3D.exe
echo ================================================
pip show pyinstaller >nul 2>&1
if errorlevel 1 pip install pyinstaller
pip install -r "%~dp0requirements.txt"
pyinstaller --noconfirm --onedir --windowed ^
    --name "EnglishTutor3D" ^
    --hidden-import "ursina" ^
    --hidden-import "speech_recognition" ^
    --hidden-import "pyttsx3" ^
    --hidden-import "pyaudio" ^
    --collect-all "ursina" ^
    --collect-all "speech_recognition" ^
    avatar3d.py
echo.
echo   Xong! Chay: dist\EnglishTutor3D\EnglishTutor3D.exe
pause
