@echo off
chcp 65001 >nul
echo ====================================================
echo        DANG PUSH CODE LEN GITHUB
echo ====================================================
echo.
git push -u origin main
echo.
if %errorlevel% equ 0 (
    echo [THANH CONG] Code da duoc day len GitHub thanh cong!
) else (
    echo [THAT BAI] Co loi xay ra. Vui long kiem tra lai.
)
echo.
pause
