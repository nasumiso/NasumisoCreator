#!/bin/bash
# Nasumiso LoRA Training Assistant 起動スクリプト (Mac/Linux用)

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

# 仮想環境の確認
if [ ! -d ".venv" ]; then
    echo "❌ エラー: 仮想環境が見つかりません"
    echo "以下のコマンドで仮想環境を作成してください:"
    echo "  python3 -m venv .venv"
    echo "  source .venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# 仮想環境を有効化
echo "🔧 仮想環境を有効化中..."
source .venv/bin/activate

# 依存パッケージの確認
if ! python -c "import gradio" 2>/dev/null; then
    echo "⚠️  警告: Gradioがインストールされていません"
    echo "依存パッケージをインストール中..."
    pip install -r requirements.txt
fi

# アプリケーション起動
echo "🚀 Nasumiso LoRA Training Assistant を起動中..."
echo "📍 http://127.0.0.1:7861 でアクセスできます"
echo "🛑 終了するには Ctrl+C を押してください"
echo ""

python app.py
