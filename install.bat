@echo off
setlocal
echo ========================================================
echo   Instalasi AGY Round-Robin Multi-Akun ke Komputer Ini
echo ========================================================

set "TARGET_DIR=%LOCALAPPDATA%\agy\bin"

if not exist "%TARGET_DIR%" (
    mkdir "%TARGET_DIR%"
)

copy /Y "%~dp0agy_rr.py" "%TARGET_DIR%\" >nul
copy /Y "%~dp0agy-rr.bat" "%TARGET_DIR%\" >nul
copy /Y "%~dp0agy-rr.ps1" "%TARGET_DIR%\" >nul

echo.
echo [OK] Berhasil terpasang ke: %TARGET_DIR%
echo.
echo Sekarang Anda bisa menjalankan perintah 'agy-rr' dari terminal mana pun!
echo Langkah selanjutnya:
echo 1. Ketik 'agy-rr add' untuk menambahkan akun pertama Anda.
echo 2. Ketik 'agy-rr add' lagi untuk akun kedua, dst.
echo 3. Ketik 'agy-rr usage' untuk cek kuota semua akun.
echo ========================================================
pause
