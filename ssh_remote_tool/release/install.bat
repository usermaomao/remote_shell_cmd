@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    SSH Remote Tool - Installer
echo ========================================
echo.

set "INSTALL_DIR=%USERPROFILE%\SSH_Remote_Tool"
set "SHORTCUT=%USERPROFILE%\Desktop\SSH_Remote_Tool.lnk"

echo Installing to: %INSTALL_DIR%
echo.

REM Create installation directory
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy files
echo Copying program files...
copy "SSH_Remote_Tool.exe" "%INSTALL_DIR%\" >nul
if errorlevel 1 (
    echo Error: Cannot copy program files
    pause
    exit /b 1
)

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%INSTALL_DIR%\SSH_Remote_Tool.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'SSH Remote Tool'; $Shortcut.Save()"

if exist "%SHORTCUT%" (
    echo Installation completed!
    echo.
    echo Program installed to: %INSTALL_DIR%
    echo Desktop shortcut created
    echo.
    echo You can:
    echo 1. Double-click desktop shortcut to start
    echo 2. Or run directly: %INSTALL_DIR%\SSH_Remote_Tool.exe
) else (
    echo Program installed successfully, but shortcut creation failed
    echo Please run manually: %INSTALL_DIR%\SSH_Remote_Tool.exe
)

echo.
pause
