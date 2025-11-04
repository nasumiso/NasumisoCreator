@echo off
echo ====================================
echo Stable Diffusion WebUI ã»ããã¢ãã
echo ãªã¹ã¿ããã¯ãªã¨ã¤ã¿ã¼
echo ====================================
echo.

REM åæ¡ä»¶ãã§ãã¯
echo [1/4] åæ¡ä»¶ãã§ãã¯ãã¦ãã¾ã...
echo.

REM Pythonã®ãã§ãã¯
python --version >nul 2>&1
if errorlevel 1 (
    echo [ã¨ã©ã¼] Pythonãã¤ã³ã¹ãã¼ã«ããã¦ãã¾ãã
    echo.
    echo ä»¥ä¸ã®URLããPython 3.10.11ãã¦ã³ã­ã¼ããã¦ã¤ã³ã¹ãã¼ã«ãã¦ãã ããï¼
    echo https://www.python.org/downloads/release/python-31011/
    echo.
    echo ã¤ã³ã¹ãã¼ã«æã®æ³¨æç¹ï¼
    echo - å¿ãããAdd Python to PATHãã«ãã§ãã¯ãå¥ãã¦ãã ãã
    echo - ã¤ã³ã¹ãã¼ã«å¾ãPCãåèµ·åãã¦ãã ãã
    echo.
    pause
    exit /b 1
)

echo [OK] Python ãè¦ã¤ããã¾ãã
python --version
echo.

REM Gitã®ãã§ãã¯
git --version >nul 2>&1
if errorlevel 1 (
    echo [ã¨ã©ã¼] Gitãã¤ã³ã¹ãã¼ã«ããã¦ãã¾ãã
    echo.
    echo ä»¥ä¸ã®URLããGit for Windowsãã¦ã³ã­ã¼ããã¦ã¤ã³ã¹ãã¼ã«ãã¦ãã ããï¼
    echo https://git-scm.com/download/win
    echo.
    echo ã¤ã³ã¹ãã¼ã«å¾ãPCãåèµ·åãã¦ãã ãã
    echo.
    pause
    exit /b 1
)

echo [OK] Git ãè¦ã¤ããã¾ãã
git --version
echo.

REM ã¤ã³ã¹ãã¼ã«åã®ç¢ºèª
set "INSTALL_DIR=%USERPROFILE%\Documents\stable-diffusion-webui"
echo [2/4] ã¤ã³ã¹ãã¼ã«åãç¢ºèªãã¦ãã¾ã...
echo ã¤ã³ã¹ãã¼ã«åï¼ %INSTALL_DIR%
echo.

if exist "%INSTALL_DIR%" (
    echo [è­¦å] ã¤ã³ã¹ãã¼ã«åã«æ¢ã«ãã©ã«ããå­å¨ãã¾ã
    echo æ¢å­ã®ãã©ã«ããåé¤ãã¦æ°è¦ã¤ã³ã¹ãã¼ã«ãã¾ããï¼
    echo.
    echo Yï¼ åé¤ãã¦æ°è¦ã¤ã³ã¹ãã¼ã«
    echo Nï¼ ã­ã£ã³ã»ã«
    echo.
    choice /C YN /N /M "é¸æãã¦ãã ãã (Y/N): "
    if errorlevel 2 (
        echo.
        echo ã­ã£ã³ã»ã«ãã¾ãã
        pause
        exit /b 0
    )
    echo.
    echo æ¢å­ã®ãã©ã«ããåé¤ãã¦ãã¾ã...
    rmdir /s /q "%INSTALL_DIR%"
)

REM WebUIã®ã¯ã­ã¼ã³
echo [3/4] Stable Diffusion WebUIãã¦ã³ã­ã¼ããã¦ãã¾ã...
echo ï¼æ°åããããå ´åãããã¾ãï¼
echo.

git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git "%INSTALL_DIR%"
if errorlevel 1 (
    echo.
    echo [ã¨ã©ã¼] ã¦ã³ã­ã¼ãã«å¤±æãã¾ãã
    echo ã¤ã³ã¿ã¼ãããæ¥ç¶ãç¢ºèªãã¦ãã ãã
    pause
    exit /b 1
)

echo.
echo [OK] ã¦ã³ã­ã¼ããå®äºãã¾ãã
echo.

REM å®äºã¡ãã»ã¼ã¸
echo [4/4] ã»ããã¢ãããå®äºãã¾ããï¼
echo.
echo ============================================================
echo æ¬¡ã®ã¹ããã
echo ============================================================
echo.
echo 1. ã¢ãã«ãã¡ã¤ã«ãä»¥ä¸ã®ãã©ã«ãã«é ç½®ãã¦ãã ããï¼
echo.
echo    ãã¼ã¹ã¢ãã«ã
echo    %INSTALL_DIR%\models\Stable-diffusion\
echo    â anything-v5.safetensors ãé ç½®
echo.
echo    ãLoRAã¢ãã«ã
echo    %INSTALL_DIR%\models\Lora\
echo    â nasumiso_v1.safetensors ãé ç½®
echo.
echo 2. ã¢ãã«ãã¡ã¤ã«ã®é ç½®ãå®äºãããã
echo    ãã¦ã³ã­ãªãã¯ãã¦èµ·åãã¦ãã ããï¼
echo.
echo    %INSTALL_DIR%\webui-user.bat
echo.
echo    åååèµ·åæã¯ä¾å­é¢ä¿ã®ã¤ã³ã¹ãã¼ã«ã«10ï½20åããããã¾ãã
echo.
echo 3. ãã©ã¦ã¶ã§ http://127.0.0.1:7860/ ã«ã¢ã¯ã»ã¹ãã¾ãã
echo.
echo ============================================================
echo.
echo ãã¹ã¯ãããã«ã·ã§ã¼ãã«ããä½æããå ´åã¯ã
echo create_shortcut.bat ãå®è¡ãã¦ãã ããã
echo.
echo è©³ããæé ã¯ docs\setup_windows.md ãåç§ãã¦ãã ããã
echo.
pause
