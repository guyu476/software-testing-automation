@echo off
title JMeter plan 2 - public target httpbingo.org
set "PATH=C:\Windows\System32;C:\Windows;C:\Windows\System32\Wbem;C:\Program Files\Java\jdk-21.0.10\bin"
set "JAVA_HOME=C:\Program Files\Java\jdk-21.0.10"
call "D:\selenium\jmeter\bin\jmeter.bat" -t "D:\selenium\perf-test\02_latency_breakdown.jmx"
pause
