@echo off
chcp 65001 >nul
echo ====================================
echo Stable Diffusion WebUI セットアップ
echo なすみそクリエイター
echo ====================================
echo.

REM 前提条件チェック
echo [1/4] 前提条件をチェックしています...
echo.

REM Pythonのチェック
python --version >nul 2>&1
if errorlevel 1 (
    echo [エラー] Pythonがインストールされていません
    echo.
    echo 以下のURLからPython 3.10.11をダウンロードしてインストールしてください：
    echo https://www.python.org/downloads/release/python-31011/
    echo.
    echo インストール時の注意点：
    echo - 必ず「Add Python to PATH」にチェックを入れてください
    echo - インストール後、PCを再起動してください
    echo.
    pause
    exit /b 1
)

echo [OK] Python が見つかりました
python --version
echo.

REM Gitのチェック
git --version >nul 2>&1
if errorlevel 1 (
    echo [エラー] Gitがインストールされていません
    echo.
    echo 以下のURLからGit for Windowsをダウンロードしてインストールしてください：
    echo https://git-scm.com/download/win
    echo.
    echo インストール後、PCを再起動してください
    echo.
    pause
    exit /b 1
)

echo [OK] Git が見つかりました
git --version
echo.

REM インストール先の確認
set "INSTALL_DIR=%USERPROFILE%\Documents\stable-diffusion-webui"
echo [2/4] インストール先を確認しています...
echo インストール先: %INSTALL_DIR%
echo.

if exist "%INSTALL_DIR%" (
    echo [警告] インストール先に既にフォルダが存在します
    echo 既存のフォルダを削除して新規インストールしますか？
    echo.
    echo Y: 削除して新規インストール
    echo N: キャンセル
    echo.
    choice /C YN /N /M "選択してください (Y/N): "
    if errorlevel 2 (
        echo.
        echo キャンセルしました
        pause
        exit /b 0
    )
    echo.
    echo 既存のフォルダを削除しています...
    rmdir /s /q "%INSTALL_DIR%"
)

REM WebUIのクローン
echo [3/4] Stable Diffusion WebUIをダウンロードしています...
echo （数分かかる場合があります）
echo.

git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git "%INSTALL_DIR%"
if errorlevel 1 (
    echo.
    echo [エラー] ダウンロードに失敗しました
    echo インターネット接続を確認してください
    pause
    exit /b 1
)

echo.
echo [OK] ダウンロードが完了しました
echo.

REM 完了メッセージ
echo [4/4] セットアップが完了しました！
echo.
echo ============================================================
echo 次のステップ
echo ============================================================
echo.
echo 1. モデルファイルを以下のフォルダに配置してください：
echo.
echo    【ベースモデル】
echo    %INSTALL_DIR%\models\Stable-diffusion\
echo    → anything-v5.safetensors を配置
echo.
echo    【LoRAモデル】
echo    %INSTALL_DIR%\models\Lora\
echo    → nasumiso_v1.safetensors を配置
echo.
echo 2. モデルファイルの配置が完了したら、以下のファイルを
echo    ダブルクリックして起動してください：
echo.
echo    %INSTALL_DIR%\webui-user.bat
echo.
echo    初回起動時は依存関係のインストールに10〜20分かかります。
echo.
echo 3. ブラウザで http://127.0.0.1:7860/ にアクセスします。
echo.
echo ============================================================
echo.
echo デスクトップにショートカットを作成する場合は、
echo create_shortcut.bat を実行してください。
echo.
echo 詳しい手順は docs\setup_windows.md を参照してください。
echo.
pause
