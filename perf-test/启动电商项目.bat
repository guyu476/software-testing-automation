@echo off
title ecommerce-demo dev server - keep this window open
set "PATH=C:\Windows\System32;C:\Windows;C:\Windows\System32\Wbem;C:\Program Files\nodejs;C:\Program Files\Java\jdk-21.0.10\bin"
cd /d D:\ecommerce-demo
"C:\Program Files\nodejs\node.exe" "D:\ecommerce-demo\node_modules\next\dist\bin\next" dev -p 3000
pause
