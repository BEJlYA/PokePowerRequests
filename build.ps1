Write-Host "`n[1/3] Очистка кэша..." -ForegroundColor Yellow
flet clean

Write-Host "`n[2/3] Сборка приложения..." -ForegroundColor Yellow
flet build windows

Write-Host "`n[3/3] Сборка установщика..." -ForegroundColor Yellow
iscc inno_setup/setup.iss

Write-Host "`nГотово!" -ForegroundColor Green