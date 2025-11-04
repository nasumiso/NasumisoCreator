@echo off
echo ====================================
echo デスクトップショートカット作成
echo なすみそクリエイター
echo ====================================
echo.

set "INSTALL_DIR=%USERPROFILE%\Documents\stable-diffusion-webui"
set "SHORTCUT=%USERPROFILE%\Desktop\Stable Diffusion WebUI.lnk"

REM インストール先の確認
if not exist "%INSTALL_DIR%\webui-user.bat" (
    echo [エラー] Stable Diffusion WebUIが見つかりません
    echo.
    echo 先に setup_windows.bat を実行してセットアップを完了してください。
    echo.
    pause
    exit /b 1
)

REM ショートカット作成
echo デスクトップにショートカットを作成しています...
powershell -ExecutionPolicy Bypass -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = '%INSTALL_DIR%\webui-user.bat'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.Save()"

if errorlevel 1 (
    echo.
    echo [エラー] ショートカットの作成に失敗しました
    pause
    exit /b 1
)

echo.
echo [OK] デスクトップにショートカットを作成しました
echo.
echo ショートカット名: Stable Diffusion WebUI
echo.
echo このショートカットをダブルクリックすることで、
echo Stable Diffusion WebUIを起動できます。
echo.
pause
