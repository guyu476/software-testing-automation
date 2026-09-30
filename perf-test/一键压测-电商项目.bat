@echo off
chcp 65001 >nul
setlocal
title Load test - ecommerce-demo
set "PATH=C:\Windows\System32;C:\Windows;C:\Windows\System32\Wbem"
set "PYTHONIOENCODING=utf-8"
set "PYTHONUTF8=1"
"C:\Users\Lenovo\AppData\Local\Programs\Python\Python313\python.exe" "D:\selenium\perf-test\run_loadtest.py"
echo.
pause
