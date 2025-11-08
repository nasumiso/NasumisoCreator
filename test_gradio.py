#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最小構成のGradioテストアプリ
"""

import gradio as gr

def greet(name):
    """簡単な挨拶関数"""
    return f"Hello {name}!"

# Gradio UI
demo = gr.Interface(
    fn=greet,
    inputs=gr.Textbox(label="お名前を入力", placeholder="なすみそ"),
    outputs=gr.Textbox(label="挨拶"),
    title="Gradio テストアプリ",
    description="最小構成のGradioアプリケーション"
)

if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=7861,
        share=False
    )
