@echo off
chcp 65001 >nul
title English AI Tutor - 3D Avatar
cd /d "%~dp0"

echo ========================================================
echo        ENGLISH AI TUTOR - 3D AVATAR & VOICE CHAT
echo ========================================================

:: 1) Uu tien chay truc tiep bang Python (nhanh nhat, on dinh, khong bi cache exe cu)
python --version >nul 2>&1
if not errorlevel 1 (
    echo [*] Dang khoi chay Avatar 3D bang Python...
    echo [*] Bam [Start] tren man hinh de bat dau tro chuyen.
    echo [*] Co the noi truc tiep vao Mic hoac go vao o nhap ben duoi.
    python avatar3d.py
    if not errorlevel 1 exit /b 0
)

:: 2) Neu khong co Python, chay bang file EXE da dong goi
if exist "%~dp0EnglishTutor3D.exe" (
    echo [*] Dang mo file EnglishTutor3D.exe...
    start "" "%~dp0EnglishTutor3D.exe"
    exit /b 0
)

if exist "%~dp0dist\EnglishTutor3D.exe" (
    echo [*] Dang mo file dist\EnglishTutor3D.exe...
    start "" "%~dp0dist\EnglishTutor3D.exe"
    exit /b 0
)

echo [!] Khong tim thay Python hoac file exe.
pause
exit /b 1
