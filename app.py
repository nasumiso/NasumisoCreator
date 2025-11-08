#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nasumiso LoRA Training Assistant - Gradio WebUI (簡易版)

なすみそLoRA学習アシスタントツール
"""

import json
import logging
import os
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import gradio as gr

PROJECT_ROOT = Path(__file__).parent
DEFAULT_TAGGED_DIR = PROJECT_ROOT / "projects/nasumiso_v1/3_tagged"

# 既存スクリプトをimport
sys.path.append(str(PROJECT_ROOT))
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

def parse_image_map(json_str: Optional[str]) -> Dict[str, str]:
    """JSON文字列から画像マップを復元"""
    if not json_str:
        return {}
    try:
        data = json.loads(json_str)
        if isinstance(data, dict):
            return {str(k): str(v) for k, v in data.items()}
    except json.JSONDecodeError:
        logger.warning("画像マップのJSON解析に失敗しました")
    return {}


def launch_app_with_port_retry(
    app: gr.Blocks,
    host: str = "127.0.0.1",
    preferred_port: int = 7861,
    max_attempts: int = 20
):
    """
    Gradioのポート競合を検出したら自動で次のポートを試行する
    """
    env_port = os.getenv("GRADIO_SERVER_PORT")
    ports_to_try = []

    if env_port:
        try:
            ports_to_try.append(int(env_port))
        except ValueError:
            logger.warning(f"GRADIO_SERVER_PORT の値 '{env_port}' を整数として解釈できません")

    ports_to_try.extend(preferred_port + offset for offset in range(max_attempts))

    tried = set()
    last_error = None

    for port in ports_to_try:
        if port in tried:
            continue
        tried.add(port)

        logger.info(f"Gradioをポート{port}で起動します...")
        try:
            app.launch(
                server_name=host,
                server_port=port,
                share=False,
                show_error=True,
                show_api=False,
                inbrowser=True  # ブラウザを自動で開く
            )
            return
        except OSError as e:
            logger.warning(f"ポート{port}で起動できませんでした: {e}")
            last_error = e
            continue

    if last_error:
        raise RuntimeError(
            f"❌ 指定ポートでアプリを起動できませんでした: {sorted(tried)}"
        ) from last_error
    raise RuntimeError("❌ アプリ起動に必要なポート候補がありません")


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


# ==================== タグ編集ロジック ====================

def resolve_tagged_folder(tagged_folder: str = None) -> Path:
    """タグ付きフォルダのパスを解決"""
    if tagged_folder and str(tagged_folder).strip():
        return Path(tagged_folder).expanduser()
    return DEFAULT_TAGGED_DIR


def resolve_image_path(
    image_name: str,
    tagged_folder: str = None,
    image_map: Optional[Dict[str, str]] = None
) -> Optional[Path]:
    """画像名とフォルダ情報から実際のPathを取得"""
    if not image_name:
        return None

    if image_map and image_name in image_map:
        return Path(image_map[image_name])

    folder = resolve_tagged_folder(tagged_folder)
    return folder / image_name


def load_tagged_images(tagged_folder: str = None):
    """
    タグ付き画像の一覧を取得

    Args:
        tagged_folder: タグ付き画像フォルダのパス

    Returns:
        画像パスのリスト
    """
    try:
        tagged_folder = resolve_tagged_folder(tagged_folder)

        if not tagged_folder.exists():
            logger.warning(f"タグ付き画像フォルダが存在しません: {tagged_folder}")
            return []

        # 画像ファイルを取得（_jp.txt は除外）
        image_extensions = {'.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'}
        image_files = sorted([
            str(f) for f in tagged_folder.iterdir()
            if f.is_file() and f.suffix in image_extensions
        ])

        return image_files

    except Exception as e:
        logger.exception("画像一覧取得でエラー発生")
        return []


def load_tags_for_image(image_path: str) -> str:
    """
    画像に対応するタグファイルを読み込む

    Args:
        image_path: 画像ファイルのパス

    Returns:
        タグ文字列（カンマ区切り）
    """
    try:
        if not image_path:
            return ""

        img_path = Path(image_path)
        txt_path = img_path.with_suffix('.txt')

        if not txt_path.exists():
            return ""

        tags = txt_path.read_text(encoding='utf-8').strip()
        return tags

    except Exception as e:
        logger.exception(f"タグ読み込みでエラー発生: {image_path}")
        return f"❌ エラー: {str(e)}"


def save_tags_for_image(image_path: str, tags: str) -> str:
    """
    画像のタグを保存

    Args:
        image_path: 画像ファイルのパス
        tags: タグ文字列（カンマ区切り）

    Returns:
        結果メッセージ
    """
    try:
        if not image_path:
            return "❌ 画像が選択されていません"

        img_path = Path(image_path)
        txt_path = img_path.with_suffix('.txt')

        # タグを保存
        txt_path.write_text(tags.strip(), encoding='utf-8')

        logger.info(f"タグ保存完了: {txt_path.name}")
        return f"✅ タグを保存しました: {img_path.name}"

    except Exception as e:
        logger.exception(f"タグ保存でエラー発生: {image_path}")
        return f"❌ エラー: {str(e)}"


def get_selected_image_info(gallery_images, evt: gr.SelectData):
    """
    ギャラリーで選択された画像の情報を取得

    Args:
        gallery_images: ギャラリーの画像リスト
        evt: 選択イベント

    Returns:
        選択された画像のパス、タグ、画像名
    """
    try:
        if not gallery_images or evt.index < 0 or evt.index >= len(gallery_images):
            return "", "", "📝 画像を選択してください"

        selected_image_path = gallery_images[evt.index]
        tags = load_tags_for_image(selected_image_path)
        image_name = Path(selected_image_path).name

        return selected_image_path, tags, f"📝 {image_name} のタグを編集"

    except Exception as e:
        logger.exception("画像選択でエラー発生")
        return "", "", "❌ エラーが発生しました"


def add_batch_tag(
    tag_to_add: str,
    selected_images: list,
    tagged_folder: str = None,
    image_map_json: Optional[str] = None
) -> str:
    """
    選択した画像に一括でタグを追加

    Args:
        tag_to_add: 追加するタグ
        selected_images: 選択された画像名のリスト
        tagged_folder: タグ付き画像フォルダ
        image_map: 画像名とフルパスのマップ

    Returns:
        結果メッセージ
    """
    try:
        if not tag_to_add or not tag_to_add.strip():
            return "❌ タグを入力してください"

        if not selected_images:
            return "❌ 画像を選択してください"

        tag_to_add = tag_to_add.strip()
        success_count = 0

        image_map = parse_image_map(image_map_json)

        for image_name in selected_images:
            image_path = resolve_image_path(image_name, tagged_folder, image_map)

            if not image_path or not image_path.exists():
                continue

            current_tags = load_tags_for_image(str(image_path))

            # タグが既に存在するかチェック
            tags_list = [t.strip() for t in current_tags.split(',') if t.strip()]

            if tag_to_add not in tags_list:
                tags_list.append(tag_to_add)
                new_tags = ', '.join(tags_list)
                save_tags_for_image(str(image_path), new_tags)
                success_count += 1

        return f"✅ {success_count}枚の画像に「{tag_to_add}」を追加しました"

    except Exception as e:
        logger.exception("一括タグ追加でエラー発生")
        return f"❌ エラー: {str(e)}"


def get_initial_image_choices():
    """
    タグ付き画像の初期選択肢を取得（UI構築時用）

    Returns:
        画像名のリスト
    """
    try:
        image_paths = load_tagged_images()
        if not image_paths:
            return []
        # ファイル名のみを返す
        return [Path(p).name for p in image_paths]
    except Exception as e:
        logger.exception("画像選択肢取得でエラー発生")
        return []


def on_image_select(image_name: str, tagged_folder: str = None):
    """
    Dropdownで選択された画像の情報を取得

    Args:
        image_name: 選択された画像名

    Returns:
        tuple: (画像パスまたは空文字列, タグ文字列)
    """
    try:
        if not image_name:
            return "", ""

        folder = resolve_tagged_folder(tagged_folder)
        image_path = folder / image_name

        if not image_path.exists():
            logger.warning(f"画像が見つかりません: {image_path}")
            return "", "❌ 画像が見つかりません"

        # タグを読み込む
        tags = load_tags_for_image(str(image_path))

        return str(image_path), tags

    except Exception as e:
        logger.exception("画像選択でエラー発生")
        return "", f"❌ エラー: {str(e)}"


def save_current_tags(
    image_name: str,
    tags: str,
    tagged_folder: str = None,
    image_map_json: Optional[str] = None
) -> str:
    """
    現在選択中の画像のタグを保存

    Args:
        image_name: 画像名
        tags: タグ文字列

    Returns:
        結果メッセージ
    """
    try:
        if not image_name:
            return "❌ 画像が選択されていません"

        image_map = parse_image_map(image_map_json)
        image_path = resolve_image_path(image_name, tagged_folder, image_map)

        if not image_path:
            return "❌ 画像が選択されていません"

        if not image_path.exists():
            return "❌ 画像が見つかりません"

        # タグを保存
        result = save_tags_for_image(str(image_path), tags)
        return result

    except Exception as e:
        logger.exception("タグ保存でエラー発生")
        return f"❌ エラー: {str(e)}"


def refresh_tag_editor_data(tagged_folder: str):
    """
    タグ編集タブのデータを再読み込み

    Args:
        tagged_folder: タグ付き画像フォルダ

    Returns:
        Dropdown更新、チェックボックス更新、画像、タグ、見出し、画像マップ、ステータスメッセージ
    """
    try:
        folder = resolve_tagged_folder(tagged_folder)
        image_paths = load_tagged_images(str(folder))
        image_map = {Path(p).name: p for p in image_paths}
        image_names = list(image_map.keys())

        first_name = image_names[0] if image_names else None
        if first_name:
            preview = image_map[first_name]
            tags = load_tags_for_image(preview)
            header = f"📝 {first_name} のタグを編集"
            status = f"📁 {len(image_names)}枚の画像を読み込みました"
        else:
            preview = None
            tags = ""
            header = "📝 画像を選択してください"
            status = "❗ タグ付き画像が見つかりません"

        image_map_json = json.dumps(image_map, ensure_ascii=False)

        return (
            gr.update(choices=image_names, value=first_name),
            gr.update(choices=image_names, value=[]),
            gr.update(value=preview),
            gr.update(value=tags),
            gr.update(value=header),
            image_map_json,
            status
        )

    except Exception as e:
        logger.exception("タグ一覧再読み込みでエラー発生")
        return (
            gr.update(),
            gr.update(),
            gr.update(value=None),
            gr.update(value=""),
            gr.update(value="❌ エラーが発生しました"),
            "{}",
            f"❌ エラー: {str(e)}"
        )


def handle_image_selection(
    image_name: str,
    tagged_folder: str,
    image_map_json: Optional[str]
):
    """
    ドロップダウン変更時にプレビューとタグを更新
    """
    try:
        if not image_name:
            return (
                gr.update(value=None),
                "",
                "📝 画像を選択してください"
            )

        image_map = parse_image_map(image_map_json)
        image_path = resolve_image_path(image_name, tagged_folder, image_map)

        if not image_path or not image_path.exists():
            return (
                gr.update(value=None),
                "",
                "❌ 画像が見つかりません"
            )

        tags = load_tags_for_image(str(image_path))
        header = f"📝 {image_name} のタグを編集"
        return (
            gr.update(value=str(image_path)),
            tags,
            header
        )

    except Exception as e:
        logger.exception("画像選択更新でエラー発生")
        return (
            gr.update(value=None),
            f"❌ エラー: {str(e)}",
            "❌ エラーが発生しました"
        )


def initialize_ui(input_folder: str):
    """
    UI初期化時の処理

    Args:
        input_folder: デフォルトの入力フォルダ

    Returns:
        画像情報、画像選択肢（リスト）
    """
    # タブ1の画像情報を取得
    image_info = get_image_info(input_folder)

    # タブ2の画像選択肢を取得
    image_choices = get_initial_image_choices()

    return image_info, image_choices


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

                # イベントハンドラ: 変換処理
                process_btn.click(
                    fn=process_image_pipeline,
                    inputs=[input_folder],
                    outputs=[progress_output]
                )

            # タブ2: タグ編集
            with gr.Tab("🏷️ タグ編集"):
                gr.Markdown("## タグ編集")

                with gr.Row():
                    tagged_folder_input = gr.Textbox(
                        label="タグ付き画像フォルダ",
                        value="projects/nasumiso_v1/3_tagged",
                        placeholder="projects/nasumiso_v1/3_tagged",
                        scale=4
                    )
                    refresh_tags_btn = gr.Button("🔄 再読み込み", scale=1)
                    open_tagged_folder_btn = gr.Button("📂 フォルダを開く", scale=1)

                tag_section_header = gr.Markdown("📝 画像を選択してください")

                with gr.Row():
                    image_dropdown = gr.Dropdown(
                        label="画像を選択",
                        choices=[],
                        value=None,
                        interactive=True
                    )
                    reload_tags_btn = gr.Button("↺ タグ再読み込み")

                with gr.Row():
                    image_preview = gr.Image(
                        label="プレビュー",
                        type="filepath",
                        interactive=False
                    )
                    tag_editor = gr.Textbox(
                        label="タグ（カンマ区切り）",
                        lines=10,
                        placeholder="例: masterpiece, best quality",
                        show_label=True
                    )

                save_tags_btn = gr.Button("💾 タグを保存", variant="primary")

                with gr.Accordion("一括タグ操作", open=False):
                    batch_tag_input = gr.Textbox(
                        label="追加するタグ",
                        placeholder="例: nasumiso_style"
                    )
                    batch_image_selector = gr.CheckboxGroup(
                        label="対象画像（複数選択可）",
                        choices=[],
                        interactive=True
                    )
                    batch_add_btn = gr.Button("➕ タグを一括追加")

                tag_action_status = gr.Markdown("")
                image_map_state = gr.Textbox(
                    value="{}",
                    label="__image_map_state",
                    visible=False
                )

                refresh_outputs = [
                    image_dropdown,
                    batch_image_selector,
                    image_preview,
                    tag_editor,
                    tag_section_header,
                    image_map_state,
                    tag_action_status
                ]

                refresh_tags_btn.click(
                    fn=refresh_tag_editor_data,
                    inputs=[tagged_folder_input],
                    outputs=refresh_outputs
                )
                tagged_folder_input.submit(
                    fn=refresh_tag_editor_data,
                    inputs=[tagged_folder_input],
                    outputs=refresh_outputs
                )
                tagged_folder_input.change(
                    fn=refresh_tag_editor_data,
                    inputs=[tagged_folder_input],
                    outputs=refresh_outputs
                )
                open_tagged_folder_btn.click(
                    fn=open_folder_in_explorer,
                    inputs=[tagged_folder_input],
                    outputs=None
                )

                image_dropdown.change(
                    fn=handle_image_selection,
                    inputs=[image_dropdown, tagged_folder_input, image_map_state],
                    outputs=[image_preview, tag_editor, tag_section_header]
                )
                reload_tags_btn.click(
                    fn=handle_image_selection,
                    inputs=[image_dropdown, tagged_folder_input, image_map_state],
                    outputs=[image_preview, tag_editor, tag_section_header]
                )

                save_tags_btn.click(
                    fn=save_current_tags,
                    inputs=[image_dropdown, tag_editor, tagged_folder_input, image_map_state],
                    outputs=[tag_action_status]
                )

                batch_add_btn.click(
                    fn=add_batch_tag,
                    inputs=[batch_tag_input, batch_image_selector, tagged_folder_input, image_map_state],
                    outputs=[tag_action_status]
                )

        app.load(
            fn=refresh_tag_editor_data,
            inputs=[tagged_folder_input],
            outputs=refresh_outputs
        )

        gr.Markdown("---")
        gr.Markdown("Made with ❤️ for Nasumiso")

    return app


if __name__ == "__main__":
    logger.info("Nasumiso LoRA Training Assistant 起動中...")

    app = create_ui()
    launch_app_with_port_retry(app, host="127.0.0.1")
