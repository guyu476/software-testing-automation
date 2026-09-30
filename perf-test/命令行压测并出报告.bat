@echo off
title JMeter CLI Load Test
chcp 65001 >nul 2>&1

REM ============================================================
REM  JMeter command line load test + auto HTML report
REM  PATH is fully hardcoded because the system PATH on this
REM  machine is broken (C:\Windows\System32 is missing from it),
REM  and jmeter.bat resolves BOTH findstr and java from PATH.
REM ============================================================

set "PATH=C:\Windows\System32;C:\Windows;C:\Windows\System32\Wbem;C:\Windows\System32\WindowsPowerShell\v1.0;C:\Program Files\Java\jdk-21.0.10\bin"
set "JAVA_HOME=C:\Program Files\Java\jdk-21.0.10"

set "JM=D:\selenium\jmeter\bin\jmeter.bat"
set "JMX=D:\selenium\perf-test\new_bird_压测版.jmx"
set "JTL=D:\selenium\perf-test\results\cli-20260928-020920.jtl"
set "REP=D:\selenium\perf-test\results\cli-report-20260928-020920"
set "JMLOG=D:\selenium\perf-test\results\cli-20260928-020920.log"

echo.
echo   ============================================
echo    JMeter    : %JM%
echo    Plan      : %JMX%
echo    Result    : %JTL%
echo    Report    : %REP%
echo   ============================================
echo.

if not exist "%JM%"  ( echo [FAIL] jmeter.bat not found & goto :end )
if not exist "%JMX%" ( echo [FAIL] test plan not found & goto :end )

echo [1/2] Running load test in CLI mode (no GUI)...
echo       Watch the "summary" line below for live results.
echo.
call "%JM%" -n -t "%JMX%" -l "%JTL%" -e -o "%REP%" -j "%JMLOG%"
set RC=%errorlevel%

echo.
echo [2/2] Done. ExitCode=%RC%

if exist "%REP%\index.html" (
  echo [ OK ] HTML report generated.
  echo        Opening it in your browser...
  start "" "%REP%\index.html"
) else (
  echo [FAIL] No report generated. Check the log:
  echo        %JMLOG%
)

:end
echo.
echo Press any key to close this window...
pause >nul