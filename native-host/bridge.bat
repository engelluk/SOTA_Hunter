@echo off
setlocal

set "LOCAL_PYTHON=%LOCALAPPDATA%\Programs\Python\Python310\python.exe"

if exist "%LOCAL_PYTHON%" (
    "%LOCAL_PYTHON%" "%~dp0bridge.py"
    exit /b %ERRORLEVEL%
)

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py -3 "%~dp0bridge.py"
    exit /b %ERRORLEVEL%
)

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python "%~dp0bridge.py"
    exit /b %ERRORLEVEL%
)

>&2 echo Python was not found. Install Python or update native-host\bridge.bat.
exit /b 1
