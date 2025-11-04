@echo off
echo ====================================
echo ãã¹ã¯ãããã·ã§ã¼ãã«ããä½æ
echo ãªã¹ã¿ããã¯ãªã¨ã¤ã¿ã¼
echo ====================================
echo.

set "INSTALL_DIR=%USERPROFILE%\Documents\stable-diffusion-webui"
set "SHORTCUT=%USERPROFILE%\Desktop\Stable Diffusion WebUI.lnk"

REM ã¤ã³ã¹ãã¼ã«åã®ç¢ºèª
if not exist "%INSTALL_DIR%\webui-user.bat" (
    echo [ã¨ã©ã¼] Stable Diffusion WebUIãè¦ã¤ããã¾ãã
    echo.
    echo åã« setup_windows.bat ãå®è¡ãã¦ã»ããã¢ãããå®äºãã¦ãã ããã
    echo.
    pause
    exit /b 1
)

REM ã·ã§ã¼ãã«ããä½æ
echo ãã¹ã¯ãããã«ã·ã§ã¼ãã«ãããä½æãã¦ãã¾ã...
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = '%INSTALL_DIR%\webui-user.bat'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.IconLocation = '%INSTALL_DIR%\webui-user.bat'; $s.Save()"

if errorlevel 1 (
    echo.
    echo [ã¨ã©ã¼] ã·ã§ã¼ãã«ããã®ä½æã«å¤±æãã¾ãã
    pause
    exit /b 1
)

echo.
echo [OK] ãã¹ã¯ãããã«ã·ã§ã¼ãã«ãããä½æãã¾ãã
echo.
echo ã·ã§ã¼ãã«ããåï¼ Stable Diffusion WebUI
echo.
echo ãã®ã·ã§ã¼ãã«ãããããã«ã¯ãªãã¯ãããã¨ã§ã
echo Stable Diffusion WebUIãèµ·åã§ãã¾ãã
echo.
pause
