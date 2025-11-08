#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nasumiso LoRA Training Assistant - Gradio WebUI (簡易版)

なすみそLoRA学習アシスタントツール
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

import gradio as gr

# ログ設定
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

log_file = LOG_DIR / f"nasumiso_trainer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# ==================== Gradio UI ====================

def create_ui():
    """Gradio UIを作成"""

    with gr.Blocks(title="Nasumiso LoRA Training Assistant", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 🎨 Nasumiso LoRA Training Assistant")
        gr.Markdown("なすみそLoRA学習アシスタントツール（テスト版）")

        gr.Markdown("## ✅ Gradio環境構築成功！")
        gr.Markdown("""
        環境が正常に構築されました。以下の依存関係で動作しています:
        - Python 3.9.6
        - Gradio 4.44.1
        - huggingface-hub 0.36.0 (Gradio互換性のため < 1.0)
        - onnxruntime 1.19.2

        次のステップ: 段階的に機能を追加していきます。
        """)

        with gr.Tabs():
            with gr.Tab("テスト"):
                name_input = gr.Textbox(label="お名前を入力", placeholder="なすみそ")
                greet_btn = gr.Button("挨拶する", variant="primary")
                output = gr.Textbox(label="結果")

                def greet(name):
                    return f"Hello {name}! Gradioは正常に動作しています！"

                greet_btn.click(fn=greet, inputs=[name_input], outputs=[output])

        gr.Markdown("---")
        gr.Markdown("Made with ❤️ for Nasumiso")

    return app


if __name__ == "__main__":
    logger.info("Nasumiso LoRA Training Assistant 起動中...")

    app = create_ui()
    app.launch(
        server_name="127.0.0.1",
        server_port=7861,
        share=False,
        show_error=True,
        inbrowser=True  # ブラウザを自動で開く
    )
