@echo off
chcp 65001 >nul
echo ================================================
echo   BUILDING EnglishTutor3D - 1 FILE EXE
echo   Giong kieu QuantResearchLab: 1 file Application
echo   duy nhat, nhap dup la chay, khong can folder dist.
echo   Chay 1 lan tren Windows, file ra la:
echo   dist\EnglishTutor3D.exe
echo ================================================
pip show pyinstaller >nul 2>&1
if errorlevel 1 pip install pyinstaller
pip install -r "%~dp0requirements.txt"
pyinstaller --noconfirm EnglishTutor3D.spec
copy /y "%~dp0dist\EnglishTutor3D.exe" "%~dp0EnglishTutor3D.exe" >nul
echo.
echo   Xong! File chay 1 click, 1 file duy nhat:
echo   dist\EnglishTutor3D.exe
echo   Copy file nay ra Desktop la xong, khong can copy ca folder.
echo   Luu y: lan dau chay se cham hon 1 chut vi exe tu giai nen,
echo   va Windows co the hoi cho phep mic - bam Allow.
echo   Neu ban onefile nay loi voi Ursina, chay
echo   build_exe_3d_onedir.bat de ve ban folder cu, on dinh hon.
pause
