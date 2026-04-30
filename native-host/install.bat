@echo off
setlocal
REM SOTA Chaser - Native Messaging Host Registration
REM Run this script once to register the native messaging host with Chrome.
REM
REM Usage:
REM   install.bat EXTENSION_ID
REM
REM If no extension ID is passed, the script asks for it interactively.

set "HOST_NAME=com.sotachaser.bridge"
set "MANIFEST_PATH=%~dp0com.sotachaser.bridge.json"
set "BRIDGE_PATH=%~dp0bridge.bat"
set "REG_KEY=HKCU\Software\Google\Chrome\NativeMessagingHosts\%HOST_NAME%"
set "EXTENSION_ID=%~1"

echo.
echo SOTA Chaser - Native Messaging Host Installer
echo ===============================================
echo.

if "%EXTENSION_ID%"=="" (
    set /p EXTENSION_ID=Chrome extension ID:
)

if "%EXTENSION_ID%"=="" (
    echo.
    echo FAILED: Extension ID is required.
    echo Open chrome://extensions, enable Developer mode, and copy the ID for SOTA Chaser.
    echo.
    pause
    exit /b 1
)

echo Manifest path: %MANIFEST_PATH%
echo Bridge path:   %BRIDGE_PATH%
echo Registry key:  %REG_KEY%
echo Extension ID:  %EXTENSION_ID%
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command "$manifest = [ordered]@{ name = $env:HOST_NAME; description = 'SOTA Chaser - native messaging bridge for Chrome'; path = $env:BRIDGE_PATH; type = 'stdio'; allowed_origins = @('chrome-extension://' + $env:EXTENSION_ID + '/') }; $manifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $env:MANIFEST_PATH -Encoding ASCII"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo FAILED: Could not write native messaging manifest.
    echo.
    pause
    exit /b 1
)

REG ADD "%REG_KEY%" /ve /t REG_SZ /d "%MANIFEST_PATH%" /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS: Native messaging host registered.
    echo.
    echo Restart Chrome or reload the extension, then try Test Connection again.
) else (
    echo.
    echo FAILED: Could not write registry key. Try running as administrator.
)

echo.
pause
