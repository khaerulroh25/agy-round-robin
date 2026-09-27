$targetDir = "$env:LOCALAPPDATA\agy\bin"
if (-not (Test-Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
}

Copy-Item -Path "$PSScriptRoot\agy_rr.py", "$PSScriptRoot\agy-rr.bat", "$PSScriptRoot\agy-rr.ps1" -Destination $targetDir -Force

Write-Host "========================================================" -ForegroundColor Green
Write-Host "  Instalasi AGY Round-Robin Berhasil!" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host "Folder tujuan: $targetDir"
Write-Host ""
Write-Host "Langkah selanjutnya di terminal:"
Write-Host "1. Ketik 'agy-rr add' untuk login akun 1" -ForegroundColor Yellow
Write-Host "2. Ketik 'agy-rr add' untuk login akun 2, dst." -ForegroundColor Yellow
Write-Host "3. Ketik 'agy-rr usage' untuk cek kuota." -ForegroundColor Cyan
