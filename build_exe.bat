@echo off
chcp 65001 >nul
echo ========================================
echo   BUILDING English AI Tutor - 1 FILE EXE
echo   File ra: dist\EnglishTutor.exe (1 file duy nhat)
echo ========================================
pip show pyinstaller >nul 2>&1
if errorlevel 1 pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed ^
    --name "EnglishTutor" ^
    --hidden-import "customtkinter" ^
    --hidden-import "speech_recognition" ^
    --hidden-import "pyttsx3" ^
    --collect-all "customtkinter" ^
    main.py
echo.
echo   Xong! Chay: dist\EnglishTutor.exe
pause
