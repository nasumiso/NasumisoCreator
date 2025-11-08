#!/bin/bash
# Nasumiso LoRA Training Assistant 停止スクリプト

echo "🛑 Nasumiso LoRA Training Assistant を停止中..."

# ポート7861を使用しているプロセスを停止
PORT_PID=$(lsof -ti:7861)

if [ -z "$PORT_PID" ]; then
    echo "✅ 実行中のプロセスはありません"
else
    kill $PORT_PID 2>/dev/null
    sleep 1

    # まだ生きている場合は強制終了
    if lsof -ti:7861 >/dev/null 2>&1; then
        echo "⚠️  通常終了に失敗したため、強制終了します..."
        kill -9 $PORT_PID 2>/dev/null
    fi

    echo "✅ プロセスを停止しました (PID: $PORT_PID)"
fi
