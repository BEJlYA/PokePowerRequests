@echo off
chcp 65001 >nul
title PPRCheat Builder

echo.
echo [1/2] Сборка Windows приложения...
flet build windows
iscc inno_setup/setup.iss

echo.
echo [2/2] Сборка Android приложения...
flet build apk --arch arm64-v8a --org com.belisor
if exist "build\apk\PPRCheat.apk" (
    copy /Y "build\apk\PPRCheat.apk" "PPRCheat.apk"
    echo APK успешно перемещен в корень проекта.
) else (
    echo [ОШИБКА] Файл build\apk\PPRCheat.apk не найден!
)

echo.
echo ========================================
echo Готово!
echo ========================================
pause