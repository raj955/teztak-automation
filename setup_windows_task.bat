@echo off
echo ================================================
echo    TezTak - Windows Task Scheduler Setup
echo ================================================
echo.

REM Get current directory
set SCRIPT_DIR=%~dp0
set PYTHON_PATH=python
set SCHEDULER_PATH=%SCRIPT_DIR%scheduler.py

echo Script folder: %SCRIPT_DIR%
echo.

REM Create scheduled task - runs at startup and daily
schtasks /create /tn "TezTak_Scheduler" /tr "%PYTHON_PATH% %SCHEDULER_PATH%" /sc ONSTART /ru "%USERNAME%" /f

if %errorlevel% == 0 (
    echo ✅ Task created! Scheduler ab PC start hone pe automatically chalega.
) else (
    echo ⚠️ Admin rights chahiye. Right-click karke "Run as Administrator" se chalao.
)

echo.
echo Ab scheduler manually start karne ke liye:
echo python scheduler.py
echo.
pause
