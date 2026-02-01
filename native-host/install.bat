@echo off
REM SOTA Hunter - Native Messaging Host Registration
REM Run this script once to register the native messaging host with Chrome.
REM
REM After loading the extension in Chrome, update two things:
REM   1. The "allowed_origins" in com.sotahunter.bridge.json with your extension ID
REM   2. The "path" in com.sotahunter.bridge.json if needed (default assumes this location)

set MANIFEST_PATH=%~dp0com.sotahunter.bridge.json
set REG_KEY=HKCU\Software\Google\Chrome\NativeMessagingHosts\com.sotahunter.bridge

echo.
echo SOTA Hunter - Native Messaging Host Installer
echo ===============================================
echo.
echo Manifest path: %MANIFEST_PATH%
echo Registry key:  %REG_KEY%
echo.

REG ADD "%REG_KEY%" /ve /t REG_SZ /d "%MANIFEST_PATH%" /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS: Native messaging host registered.
    echo.
    echo Next steps:
    echo   1. Load the extension in Chrome: chrome://extensions ^> Load unpacked ^> select extension/ folder
    echo   2. Copy the extension ID from Chrome
    echo   3. Edit com.sotahunter.bridge.json and replace EXTENSION_ID_HERE with your extension ID
    echo   4. Verify the "path" in com.sotahunter.bridge.json points to bridge.bat
) else (
    echo.
    echo FAILED: Could not write registry key. Try running as administrator.
)

echo.
pause
