#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nasumiso LoRA Training Assistant - Gradio WebUI (簡易版)

なすみそLoRA学習アシスタントツール
"""

import logging
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import gradio as gr

# 既存スクリプトをimport
sys.path.append(str(Path(__file__).parent))
from scripts.prepare_images import resize_and_crop, get_image_files
from scripts.auto_caption import WD14Tagger
from scripts.add_common_tag import add_tag_to_file
from PIL import Image
import shutil

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


# ==================== ユーティリティ関数 ====================

def open_folder_in_explorer(folder_path: str):
    """
    フォルダをFinder/Explorerで開く

    Args:
        folder_path: フォルダのパス
    """
    try:
        path = Path(folder_path)

        if not path.exists():
            logger.warning(f"フォルダが存在しません: {folder_path}")
            return

        if not path.is_dir():
            logger.warning(f"パスがディレクトリではありません: {folder_path}")
            return

        # プラットフォームに応じてコマンドを実行
        system = platform.system()

        if system == "Darwin":  # macOS
            subprocess.run(["open", str(path)])
        elif system == "Windows":
            subprocess.run(["explorer", str(path)])
        else:  # Linux
            subprocess.run(["xdg-open", str(path)])

    except Exception as e:
        logger.exception("フォルダを開く際にエラー発生")


def get_image_info(folder_path: str) -> str:
    """
    フォルダ内の画像情報を取得

    Args:
        folder_path: フォルダのパス

    Returns:
        画像枚数と一覧を含む文字列
    """
    try:
        path = Path(folder_path)

        if not path.exists():
            return "❌ フォルダが存在しません"

        if not path.is_dir():
            return "❌ パスがディレクトリではありません"

        # 画像ファイルを取得
        image_extensions = {'.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'}
        image_files = sorted([
            f for f in path.iterdir()
            if f.is_file() and f.suffix in image_extensions
        ])

        count = len(image_files)

        if count == 0:
            return "📁 画像ファイル: 0枚\n\n画像ファイルが見つかりません"

        # 画像枚数と一覧を1つの文字列にまとめる
        details = []
        details.append(f"📁 画像ファイル: {count}枚")
        details.append("")
        details.append("📋 画像ファイル一覧:")
        details.append("-" * 50)
        for idx, img_file in enumerate(image_files, start=1):
            file_size = img_file.stat().st_size / 1024  # KB
            details.append(f"{idx:2d}. {img_file.name} ({file_size:.1f} KB)")

        return "\n".join(details)

    except Exception as e:
        logger.exception("画像情報取得でエラー発生")
        return f"❌ エラー: {str(e)}"


# ==================== 画像処理ロジック ====================

def process_image_pipeline(input_folder: str, progress=gr.Progress()) -> str:
    """
    画像前処理パイプラインを実行（プログレスバーのみリアルタイム更新）

    Args:
        input_folder: 入力フォルダのパス
        progress: Gradio進捗オブジェクト

    Returns:
        処理結果のメッセージ（完了後に一度だけ表示）
    """
    output_messages = []

    def add_message(msg):
        """メッセージを追加"""
        output_messages.append(msg)

    try:
        input_path = Path(input_folder)

        # 入力フォルダの存在確認
        if not input_path.exists():
            return f"❌ エラー: 入力フォルダが存在しません: {input_folder}"

        if not input_path.is_dir():
            return f"❌ エラー: 入力パスがディレクトリではありません: {input_folder}"

        # プロジェクトルートを取得
        project_root = Path(__file__).parent
        processed_dir = project_root / "projects/nasumiso_v1/2_processed"
        tagged_dir = project_root / "projects/nasumiso_v1/3_tagged"

        # 出力ディレクトリ作成
        processed_dir.mkdir(parents=True, exist_ok=True)
        tagged_dir.mkdir(parents=True, exist_ok=True)

        add_message("=" * 60)
        add_message("🎨 Nasumiso LoRA Training Assistant - 画像前処理パイプライン")
        add_message("=" * 60)
        add_message("")

        # 画像ファイルを取得
        image_files = get_image_files(input_path)
        total_images = len(image_files)

        if total_images == 0:
            add_message("❌ エラー: 画像ファイルが見つかりません")
            return "\n".join(output_messages)

        add_message(f"📁 対象画像: {total_images}枚")
        add_message("")

        # ==================== ステップ1: 画像のリサイズと連番リネーム ====================
        logger.info(f"ステップ1開始: prepare_images ({input_path} -> {processed_dir})")
        add_message("📝 ステップ1: 画像のリサイズと連番リネーム（512x512）")
        add_message(f"  入力: {input_path}")
        add_message(f"  出力: {processed_dir}")
        add_message("")

        success_count = 0
        skip_count = 0

        for idx, image_path in enumerate(image_files, start=1):
            # 進捗バー更新（ステップ1は全体の0〜30%）
            progress_ratio = (idx / total_images) * 0.3
            progress(progress_ratio, desc=f"ステップ1: {idx}/{total_images}枚 リサイズ中...")

            try:
                with Image.open(image_path) as img:
                    if img.mode not in ('RGB', 'RGBA'):
                        img = img.convert('RGB')

                    processed = resize_and_crop(img, 512)
                    output_filename = f"img{idx:03d}.png"
                    output_path = processed_dir / output_filename
                    processed.save(output_path, 'PNG', optimize=True)

                    add_message(f"  ✓ [{idx}/{total_images}] {image_path.name} → {output_filename}")
                    success_count += 1

            except Exception as e:
                add_message(f"  ✗ [{idx}/{total_images}] {image_path.name}: エラー - {e}")
                skip_count += 1

        add_message("")
        add_message(f"✅ ステップ1完了: {success_count}枚成功, {skip_count}枚スキップ")
        add_message("")

        if success_count == 0:
            add_message("❌ エラー: 画像が1枚も処理できませんでした")
            return "\n".join(output_messages)

        # ==================== ステップ2: WD14 Taggerで自動タグ付け ====================
        logger.info(f"ステップ2開始: auto_caption ({processed_dir} -> {tagged_dir})")
        add_message("📝 ステップ2: WD14 Taggerで自動タグ付け（しきい値: 0.35）")
        add_message(f"  入力: {processed_dir}")
        add_message(f"  出力: {tagged_dir}")
        add_message("")

        # WD14 Taggerを初期化
        add_message("  モデルをロード中...")
        tagger = WD14Tagger(threshold=0.35, use_coreml=False)
        add_message("  ✓ モデルロード完了")
        add_message("")

        # 処理済み画像を取得
        processed_images = get_image_files(processed_dir)
        success_count2 = 0
        skip_count2 = 0

        for idx, image_path in enumerate(processed_images, start=1):
            # 進捗バー更新（ステップ2は全体の30〜80%）
            progress_ratio = 0.3 + (idx / len(processed_images)) * 0.5
            progress(progress_ratio, desc=f"ステップ2: {idx}/{len(processed_images)}枚 タグ付け中...")

            try:
                tags = tagger.predict_tags_only(image_path)
                tag_string = ", ".join(tags)

                output_image = tagged_dir / image_path.name
                output_txt = tagged_dir / f"{image_path.stem}.txt"

                shutil.copy2(image_path, output_image)
                output_txt.write_text(tag_string, encoding="utf-8")

                add_message(f"  ✓ [{idx}/{len(processed_images)}] {image_path.name} ({len(tags)}個のタグ)")
                success_count2 += 1

            except Exception as e:
                add_message(f"  ✗ [{idx}/{len(processed_images)}] {image_path.name}: エラー - {e}")
                skip_count2 += 1

        add_message("")
        add_message(f"✅ ステップ2完了: {success_count2}枚成功, {skip_count2}枚スキップ")
        add_message("")

        if success_count2 == 0:
            add_message("❌ エラー: タグ付けが1枚もできませんでした")
            return "\n".join(output_messages)

        # ==================== ステップ3: 共通タグ追加（nasumiso_style） ====================
        logger.info(f"ステップ3開始: add_common_tag ({tagged_dir})")
        add_message("📝 ステップ3: 共通タグ追加（nasumiso_style）")
        add_message(f"  対象: {tagged_dir}")
        add_message("")

        txt_files = sorted(tagged_dir.glob('*.txt'))
        txt_files = [f for f in txt_files if not f.name.endswith('_jp.txt')]

        added_count = 0
        for idx, txt_file in enumerate(txt_files, start=1):
            # 進捗バー更新（ステップ3は全体の80〜100%）
            progress_ratio = 0.8 + (idx / len(txt_files)) * 0.2
            progress(progress_ratio, desc=f"ステップ3: {idx}/{len(txt_files)}個 共通タグ追加中...")

            added = add_tag_to_file(txt_file, tag="nasumiso_style", position="start", backup=False)
            if added:
                added_count += 1

        add_message(f"✅ ステップ3完了: {added_count}個のファイルにタグを追加")
        add_message("")

        # 完了メッセージ
        progress(1.0, desc="完了!")
        add_message("=" * 60)
        add_message("🎉 パイプライン完了！")
        add_message(f"📁 出力フォルダ: {tagged_dir}")
        add_message(f"📊 処理結果: {success_count2}枚の画像を処理しました")
        add_message("=" * 60)

        logger.info("画像前処理パイプライン完了")

        return "\n".join(output_messages)

    except Exception as e:
        logger.exception("画像処理パイプラインでエラー発生")
        add_message("")
        add_message(f"❌ エラーが発生しました: {str(e)}")
        return "\n".join(output_messages)


# ==================== Gradio UI ====================

def create_ui():
    """Gradio UIを作成"""

    with gr.Blocks(title="Nasumiso LoRA Training Assistant", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 🎨 Nasumiso LoRA Training Assistant")
        gr.Markdown("なすみそLoRA学習アシスタントツール")

        with gr.Tabs():
            # タブ1: 画像準備
            with gr.Tab("📁 画像準備"):
                gr.Markdown("""
                ## 画像前処理パイプライン
                1. 画像のリサイズと連番リネーム（512x512）
                2. WD14 Taggerで自動タグ付け（しきい値: 0.35）
                3. 共通タグ追加（nasumiso_style）
                """)

                with gr.Row():
                    input_folder = gr.Textbox(
                        label="入力フォルダ",
                        value="projects/nasumiso_v1/1_raw_images",
                        placeholder="projects/nasumiso_v1/1_raw_images",
                        scale=4
                    )
                    open_folder_btn = gr.Button("📂 フォルダを開く", scale=1)

                with gr.Accordion("📁 画像ファイル情報", open=False):
                    image_info_output = gr.Textbox(
                        label="",
                        lines=12,
                        max_lines=20,
                        interactive=False,
                        show_label=False
                    )

                with gr.Row():
                    process_btn = gr.Button("🚀 変換開始", variant="primary", size="lg")

                progress_output = gr.Textbox(
                    label="進捗状況",
                    lines=15,
                    max_lines=20,
                    interactive=False
                )

                # イベントハンドラ: フォルダを開く
                open_folder_btn.click(
                    fn=open_folder_in_explorer,
                    inputs=[input_folder],
                    outputs=None
                )

                # イベントハンドラ: 画像情報を取得（フォルダパス変更時）
                input_folder.change(
                    fn=get_image_info,
                    inputs=[input_folder],
                    outputs=[image_info_output]
                )

                # イベントハンドラ: 初期ロード時に画像情報を取得
                app.load(
                    fn=get_image_info,
                    inputs=[input_folder],
                    outputs=[image_info_output]
                )

                # イベントハンドラ: 変換処理
                process_btn.click(
                    fn=process_image_pipeline,
                    inputs=[input_folder],
                    outputs=[progress_output]
                )

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
