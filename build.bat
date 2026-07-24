@echo off
chcp 65001 >nul
title PPRCheat Builder

echo.
echo [1/3] Очистка кэша и старой сборки...
flet clean

echo.
echo [2/3] Сборка нового приложения...
flet build windows

echo.
echo [3/3] Сборка установщика...
iscc inno_setup/setup.iss

echo.
echo ========================================
echo Готово!
echo ========================================
pause