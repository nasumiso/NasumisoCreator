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
APP_STATE_FILE = PROJECT_ROOT / "app_state.json"

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


def load_app_state() -> Dict:
    """
    アプリケーション状態を読み込む
    
    Returns:
        Dict: アプリケーション状態（存在しない場合はデフォルト値）
    """
    default_state = {
        "image_preparation": {
            "folder_paths": [
                "projects/nasumiso_v1/1_raw_images",
                "",
                ""
            ],
            "additional_tags": [
                "",
                "",
                ""
            ]
        },
        "tag_editor": {
            "last_tagged_folder": "projects/nasumiso_v1/3_tagged"
        }
    }
    
    if APP_STATE_FILE.exists():
        try:
            with open(APP_STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
                logger.info(f"アプリ状態を読み込みました: {APP_STATE_FILE}")
                return state
        except Exception as e:
            logger.warning(f"状態ファイル読み込みエラー: {e}")
            return default_state
    
    return default_state


def save_app_state(state: Dict) -> None:
    """
    アプリケーション状態を保存する
    
    Args:
        state: 保存するアプリケーション状態
    """
    try:
        with open(APP_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
            logger.info(f"アプリ状態を保存しました: {APP_STATE_FILE}")
    except Exception as e:
        logger.error(f"状態ファイル保存エラー: {e}")

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
        Gallery更新、画像パスリスト、タグ、見出し、選択画像名、画像マップ、ステータスメッセージ
    """
    try:
        folder = resolve_tagged_folder(tagged_folder)
        image_paths = load_tagged_images(str(folder))
        image_map = {Path(p).name: p for p in image_paths}

        if image_paths:
            # 最初の画像を選択
            first_path = image_paths[0]
            first_name = Path(first_path).name
            tags = load_tags_for_image(first_path)
            header = f"📝 {first_name} のタグを編集"
            status = f"📁 {len(image_paths)}枚の画像を読み込みました"
        else:
            first_name = ""
            tags = ""
            header = "📝 画像を選択してください"
            status = "❗ タグ付き画像が見つかりません"

        image_map_json = json.dumps(image_map, ensure_ascii=False)

        return (
            gr.update(value=image_paths, selected_index=0 if image_paths else None),  # Gallery更新（最初の画像を選択）
            image_paths,  # 画像パスリスト（Stateとして保存）
            gr.update(value=tags),  # タグエディタ
            gr.update(value=header),  # ヘッダー
            first_name,  # 選択された画像名
            image_map_json,  # 画像マップ
            gr.update(value=status)  # ステータスメッセージ
        )

    except Exception as e:
        logger.exception("タグ一覧再読み込みでエラー発生")
        return (
            gr.update(value=[]),
            [],
            gr.update(value=""),
            gr.update(value="❌ エラーが発生しました"),
            "",
            "{}",
            gr.update(value=f"❌ エラー: {str(e)}")
        )


def handle_gallery_selection(
    gallery_images: list,
    evt: gr.SelectData
):
    """
    Gallery選択時にタグを更新

    Args:
        gallery_images: Galleryに表示されている画像パスのリスト
        evt: 選択イベント（evt.indexに選択されたインデックス）

    Returns:
        tuple: (タグ文字列, ヘッダー, 選択された画像名)
    """
    try:
        if not gallery_images or evt.index < 0 or evt.index >= len(gallery_images):
            return (
                "",
                "📝 画像を選択してください",
                ""
            )

        selected_image_path = gallery_images[evt.index]
        tags = load_tags_for_image(selected_image_path)
        image_name = Path(selected_image_path).name
        header = f"📝 {image_name} のタグを編集"

        return (
            tags,
            header,
            image_name
        )

    except Exception as e:
        logger.exception("Gallery選択でエラー発生")
        return (
            f"❌ エラー: {str(e)}",
            "❌ エラーが発生しました",
            ""
        )


# ==================== 画像処理ロジック ====================

def process_image_pipeline(
    input_folder_1: str, input_folder_2: str, input_folder_3: str,
    additional_tags_1: str = "", additional_tags_2: str = "", additional_tags_3: str = "",
    progress=gr.Progress()
) -> str:
    """
    画像前処理パイプラインを実行（複数フォルダ統合対応）

    Args:
        input_folder_1-3: 入力フォルダのパス（空の場合はスキップ）
        additional_tags_1-3: 各フォルダの追加タグ（カンマ区切り）
        progress: Gradio進捗オブジェクト

    Returns:
        処理結果のメッセージ（完了後に一度だけ表示）
    """
    output_messages = []

    def add_message(msg):
        """メッセージを追加"""
        output_messages.append(msg)

    try:
        # 入力フォルダとタグのペアを収集（空でないもののみ）
        folder_configs = []
        for idx, (folder_path, tags) in enumerate([
            (input_folder_1, additional_tags_1),
            (input_folder_2, additional_tags_2),
            (input_folder_3, additional_tags_3)
        ], start=1):
            if folder_path and folder_path.strip():
                path = Path(folder_path)
                if path.exists() and path.is_dir():
                    folder_configs.append({
                        'index': idx,
                        'path': path,
                        'tags': tags.strip()
                    })
                elif path.exists():
                    add_message(f"⚠️ フォルダ{idx}: パスがディレクトリではありません: {folder_path}")
                else:
                    add_message(f"⚠️ フォルダ{idx}: フォルダが存在しません: {folder_path}")

        if not folder_configs:
            return "❌ エラー: 有効な入力フォルダが指定されていません"

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
        add_message(f"📁 処理対象フォルダ: {len(folder_configs)}個")
        for config in folder_configs:
            add_message(f"  フォルダ{config['index']}: {config['path']}")
            if config['tags']:
                add_message(f"    追加タグ: {config['tags']}")
        add_message("")

        # 各フォルダから画像ファイルを収集
        image_list = []  # [(画像パス, フォルダindex, 追加タグ), ...]
        for config in folder_configs:
            folder_images = get_image_files(config['path'])
            for img_path in folder_images:
                image_list.append((img_path, config['index'], config['tags']))
            add_message(f"  フォルダ{config['index']}: {len(folder_images)}枚")

        total_images = len(image_list)

        if total_images == 0:
            add_message("❌ エラー: 画像ファイルが見つかりません")
            return "\n".join(output_messages)

        add_message(f"📊 合計画像数: {total_images}枚")
        add_message("")

        # ==================== ステップ1: 画像のリサイズと統合連番リネーム ====================
        logger.info(f"ステップ1開始: prepare_images (統合 -> {processed_dir})")
        add_message("📝 ステップ1: 画像のリサイズと統合連番リネーム（512x512）")
        add_message(f"  出力: {processed_dir}")
        add_message("")

        success_count = 0
        skip_count = 0

        for idx, (image_path, folder_idx, _) in enumerate(image_list, start=1):
            # 進捗バー更新（ステップ1は全体の0〜30%）
            progress_ratio = (idx / total_images) * 0.3
            progress(progress_ratio, desc=f"ステップ1: {idx}/{total_images}枚 リサイズ中...")

            try:
                with Image.open(image_path) as img:
                    if img.mode not in ('RGB', 'RGBA'):
                        img = img.convert('RGB')

                    processed = resize_and_crop(img, 512)
                    output_filename = f"img{idx-1:03d}.png"  # 0から始まる連番
                    output_path = processed_dir / output_filename
                    processed.save(output_path, 'PNG', optimize=True)

                    add_message(f"  ✓ [{idx}/{total_images}] フォルダ{folder_idx}: {image_path.name} → {output_filename}")
                    success_count += 1

            except Exception as e:
                add_message(f"  ✗ [{idx}/{total_images}] フォルダ{folder_idx}: {image_path.name}: エラー - {e}")
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

        # ==================== ステップ3: 共通タグ + 各フォルダ固有タグ追加 ====================
        logger.info(f"ステップ3開始: add_common_tag ({tagged_dir})")

        add_message("📝 ステップ3: 共通タグ + フォルダ固有タグ追加")
        add_message(f"  対象: {tagged_dir}")
        add_message("")

        txt_files = sorted(tagged_dir.glob('*.txt'))
        txt_files = [f for f in txt_files if not f.name.endswith('_jp.txt')]

        added_count = 0
        for txt_idx, txt_file in enumerate(txt_files, start=1):
            # 進捗バー更新（ステップ3は全体の80〜100%）
            progress_ratio = 0.8 + (txt_idx / len(txt_files)) * 0.2
            progress(progress_ratio, desc=f"ステップ3: {txt_idx}/{len(txt_files)}個 共通タグ追加中...")

            # ファイル名から元の画像インデックスを取得（img000.txt → 0）
            try:
                img_index = int(txt_file.stem.replace('img', ''))
            except ValueError:
                logger.warning(f"ファイル名から番号を抽出できません: {txt_file.name}")
                continue

            # 対応する元画像の情報を取得
            if img_index < len(image_list):
                _, folder_idx, folder_tags = image_list[img_index]
            else:
                logger.warning(f"画像インデックス{img_index}が範囲外です")
                continue

            # タグリストの作成（固定タグ + フォルダ固有タグ）
            tags_to_add = ["nasumiso_style"]
            if folder_tags:
                # カンマ区切りで分割し、前後の空白を削除
                extra_tags = [tag.strip() for tag in folder_tags.split(',') if tag.strip()]
                tags_to_add.extend(extra_tags)

            # 各タグを順番に追加
            for tag in tags_to_add:
                added = add_tag_to_file(txt_file, tag=tag, position="start", backup=False)
                if added:
                    added_count += 1

        add_message(f"✅ ステップ3完了: {added_count}個のタグを追加")
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

def select_folder_with_dialog(initial_dir: str = None) -> str:
    """
    システム標準のフォルダ選択ダイアログを表示
    
    macOS: osascriptを使用
    その他: tkinterを使用（インストールされている場合）
    
    Args:
        initial_dir: 初期表示ディレクトリ（省略時はプロジェクトルート）
    
    Returns:
        str: 選択されたフォルダパス（キャンセル時は空文字列）
    """
    import subprocess
    import sys
    
    try:
        # 初期ディレクトリの設定
        if initial_dir and Path(initial_dir).exists():
            init_path = str(Path(initial_dir).resolve())
        else:
            init_path = str(PROJECT_ROOT.resolve())
        
        # macOSの場合: osascriptを使用
        if sys.platform == "darwin":
            try:
                # AppleScriptでフォルダ選択ダイアログを表示
                script = f'''
                tell application "System Events"
                    activate
                    set theFolder to choose folder with prompt "フォルダを選択してください" default location POSIX file "{init_path}"
                    return POSIX path of theFolder
                end tell
                '''
                
                result = subprocess.run(
                    ["osascript", "-e", script],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5分でタイムアウト
                )
                
                if result.returncode == 0:
                    selected_folder = result.stdout.strip()
                    if selected_folder:
                        # 末尾のスラッシュを削除
                        selected_folder = selected_folder.rstrip('/')
                        selected_path = Path(selected_folder)
                        
                        # プロジェクトルート配下の場合は相対パスに
                        try:
                            rel_path = selected_path.relative_to(PROJECT_ROOT)
                            return str(rel_path)
                        except ValueError:
                            # プロジェクトルート外の場合は絶対パスを返す
                            return str(selected_path)
                
                return ""
            
            except Exception as e:
                logger.error(f"osascriptエラー: {e}")
                return ""
        
        # その他のOS: tkinterを試行
        else:
            try:
                import tkinter as tk
                from tkinter import filedialog
                
                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                
                selected_folder = filedialog.askdirectory(
                    title="フォルダを選択",
                    initialdir=init_path
                )
                
                root.destroy()
                
                if selected_folder:
                    selected_path = Path(selected_folder)
                    try:
                        rel_path = selected_path.relative_to(PROJECT_ROOT)
                        return str(rel_path)
                    except ValueError:
                        return str(selected_path)
                
                return ""
            
            except ImportError:
                logger.error("tkinterがインストールされていません")
                return ""
    
    except Exception as e:
        logger.error(f"フォルダ選択ダイアログエラー: {e}")
        return ""



def save_folder_and_tags_state(folder_1: str, folder_2: str, folder_3: str, 
                                tags_1: str, tags_2: str, tags_3: str) -> None:
    """
    フォルダパスと追加タグを状態ファイルに保存
    
    Args:
        folder_1-3: 各行のフォルダパス
        tags_1-3: 各行の追加タグ
    """
    state = {
        "image_preparation": {
            "folder_paths": [folder_1, folder_2, folder_3],
            "additional_tags": [tags_1, tags_2, tags_3]
        },
        "tag_editor": {
            "last_tagged_folder": "projects/nasumiso_v1/3_tagged"
        }
    }
    save_app_state(state)

def create_ui():
    """Gradio UIを作成"""

    # アプリ状態を読み込み
    app_state = load_app_state()
    folder_paths = app_state.get("image_preparation", {}).get("folder_paths", ["projects/nasumiso_v1/1_raw_images", "", ""])
    additional_tags = app_state.get("image_preparation", {}).get("additional_tags", ["", "", ""])
    last_tagged_folder = app_state.get("tag_editor", {}).get("last_tagged_folder", "projects/nasumiso_v1/3_tagged")

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

                gr.Markdown("### 入力フォルダ一覧")

                # テーブルヘッダー
                with gr.Row():
                    with gr.Column(scale=6):
                        gr.Markdown("**フォルダパス**")
                    with gr.Column(scale=1):
                        gr.Markdown("**画像枚数**")
                    with gr.Column(scale=2):
                        gr.Markdown("**追加タグ**")
                    with gr.Column(scale=1):
                        gr.Markdown("**操作**")

                # 行1: メインの入力フォルダ
                with gr.Row():
                    with gr.Column(scale=5):
                        input_folder_1_btn = gr.Button(
                            value=folder_paths[0] or "projects/nasumiso_v1/1_raw_images",
                            variant="secondary",
                            size="sm",
                            elem_classes="folder-path-button"
                        )
                        input_folder_1 = gr.Textbox(
                            label="",
                            value=folder_paths[0] or "projects/nasumiso_v1/1_raw_images",
                            visible=False
                        )
                    open_btn_1 = gr.Button("📂", scale=1, min_width=40)
                    image_count_btn_1 = gr.Button(
                        value="-",
                        scale=1
                    )
                    additional_tags_1 = gr.Textbox(
                        label="",
                        value=additional_tags[0],
                        placeholder="タグ1, タグ2, ...",
                        scale=2,
                        show_label=False
                    )

                # 行2: 将来用フォルダ
                with gr.Row():
                    with gr.Column(scale=5):
                        input_folder_2_btn = gr.Button(
                            value=folder_paths[1] or "クリックしてフォルダを選択",
                            variant="secondary",
                            size="sm",
                            elem_classes="folder-path-button"
                        )
                        input_folder_2 = gr.Textbox(
                            label="",
                            value=folder_paths[1] or "",
                            visible=False
                        )
                    open_btn_2 = gr.Button("📂", scale=1, min_width=40)
                    image_count_btn_2 = gr.Button(
                        value="-",
                        scale=1
                    )
                    additional_tags_2 = gr.Textbox(
                        label="",
                        value=additional_tags[1],
                        placeholder="タグ1, タグ2, ...",
                        scale=2,
                        show_label=False
                    )

                # 行3: 将来用フォルダ
                with gr.Row():
                    with gr.Column(scale=5):
                        input_folder_3_btn = gr.Button(
                            value=folder_paths[2] or "クリックしてフォルダを選択",
                            variant="secondary",
                            size="sm",
                            elem_classes="folder-path-button"
                        )
                        input_folder_3 = gr.Textbox(
                            label="",
                            value=folder_paths[2] or "",
                            visible=False
                        )
                    open_btn_3 = gr.Button("📂", scale=1, min_width=40)
                    image_count_btn_3 = gr.Button(
                        value="-",
                        scale=1
                    )
                    additional_tags_3 = gr.Textbox(
                        label="",
                        value=additional_tags[2],
                        placeholder="タグ1, タグ2, ...",
                        scale=2,
                        show_label=False
                    )

                # 共通の詳細表示エリア（コメントアウト）
                # gr.Markdown("---")
                # selected_folder_label = gr.Markdown("📋 **選択中のフォルダ**: なし")
                #
                # file_list_display = gr.Textbox(
                #     label="📁 画像ファイル一覧",
                #     value="フォルダの画像枚数をクリックすると、ファイル一覧が表示されます",
                #     lines=12,
                #     max_lines=12,
                #     interactive=False,
                #     autoscroll=False
                # )
                #
                # gr.Markdown("---")

                # 変換開始ボタン（全体で1つ）
                process_btn = gr.Button("🚀 変換開始", variant="primary", size="lg")

                progress_output = gr.Textbox(
                    label="進捗状況",
                    lines=15,
                    max_lines=20,
                    interactive=False,
                    autoscroll=True
                )

                # イベントハンドラ: フォルダパス変更時（画像枚数ボタンを更新）
                def update_count_button(path):
                    if not path or not Path(path).exists():
                        return gr.update(value="-")
                    info = get_image_info(path)
                    count_text = info.split('\n')[0].split(': ')[1] if ': ' in info.split('\n')[0] else "-"
                    return gr.update(value=count_text)

                input_folder_1.change(
                    fn=update_count_button,
                    inputs=[input_folder_1],
                    outputs=[image_count_btn_1]
                )
                input_folder_2.change(
                    fn=update_count_button,
                    inputs=[input_folder_2],
                    outputs=[image_count_btn_2]
                )
                input_folder_3.change(
                    fn=update_count_button,
                    inputs=[input_folder_3],
                    outputs=[image_count_btn_3]
                )

                # イベントハンドラ: 画像枚数ボタンクリック時（詳細情報を表示）- コメントアウト
                # def show_file_details(path):
                #     if not path or not Path(path).exists():
                #         return (
                #             "📋 **選択中のフォルダ**: なし",
                #             "フォルダが指定されていません"
                #         )
                #     info = get_image_info(path)
                #     label = f"📋 **選択中のフォルダ**: {path}"
                #     return (label, info)
                #
                # image_count_btn_1.click(
                #     fn=show_file_details,
                #     inputs=[input_folder_1],
                #     outputs=[selected_folder_label, file_list_display]
                # )
                # image_count_btn_2.click(
                #     fn=show_file_details,
                #     inputs=[input_folder_2],
                #     outputs=[selected_folder_label, file_list_display]
                # )
                # image_count_btn_3.click(
                #     fn=show_file_details,
                #     inputs=[input_folder_3],
                #     outputs=[selected_folder_label, file_list_display]
                # )

                # イベントハンドラ: フォルダ選択（tkinter版）
                def browse_folder_1(current_path):
                    """行1のフォルダ選択"""
                    selected = select_folder_with_dialog(current_path)
                    if selected:
                        logger.info(f"フォルダ選択: {selected} (行1)")
                        return gr.update(value=selected), gr.update(value=selected)
                    return gr.update(), gr.update()

                def browse_folder_2(current_path):
                    """行2のフォルダ選択"""
                    selected = select_folder_with_dialog(current_path)
                    if selected:
                        logger.info(f"フォルダ選択: {selected} (行2)")
                        return gr.update(value=selected), gr.update(value=selected)
                    return gr.update(), gr.update()

                def browse_folder_3(current_path):
                    """行3のフォルダ選択"""
                    selected = select_folder_with_dialog(current_path)
                    if selected:
                        logger.info(f"フォルダ選択: {selected} (行3)")
                        return gr.update(value=selected), gr.update(value=selected)
                    return gr.update(), gr.update()

                # イベントハンドラ: フォルダパスボタンクリック時にフォルダ選択
                input_folder_1_btn.click(
                    fn=browse_folder_1,
                    inputs=[input_folder_1],
                    outputs=[input_folder_1, input_folder_1_btn],
                    show_progress=False
                )
                input_folder_2_btn.click(
                    fn=browse_folder_2,
                    inputs=[input_folder_2],
                    outputs=[input_folder_2, input_folder_2_btn],
                    show_progress=False
                )
                input_folder_3_btn.click(
                    fn=browse_folder_3,
                    inputs=[input_folder_3],
                    outputs=[input_folder_3, input_folder_3_btn],
                    show_progress=False
                )

                # イベントハンドラ: フォルダを開く
                open_btn_1.click(
                    fn=open_folder_in_explorer,
                    inputs=[input_folder_1],
                    outputs=None
                )
                open_btn_2.click(
                    fn=open_folder_in_explorer,
                    inputs=[input_folder_2],
                    outputs=None
                )
                open_btn_3.click(
                    fn=open_folder_in_explorer,
                    inputs=[input_folder_3],
                    outputs=None
                )

                # イベントハンドラ: 状態保存（フォルダパスまたはタグ変更時）
                def save_state_handler(f1, f2, f3, t1, t2, t3):
                    """フォルダパスと追加タグの変更を保存"""
                    save_folder_and_tags_state(f1, f2, f3, t1, t2, t3)

                # フォルダパス変更時に状態保存
                for folder_input in [input_folder_1, input_folder_2, input_folder_3]:
                    folder_input.change(
                        fn=save_state_handler,
                        inputs=[input_folder_1, input_folder_2, input_folder_3,
                               additional_tags_1, additional_tags_2, additional_tags_3],
                        outputs=None,
                        show_progress=False
                    )

                # 追加タグ変更時に状態保存
                for tags_input in [additional_tags_1, additional_tags_2, additional_tags_3]:
                    tags_input.change(
                        fn=save_state_handler,
                        inputs=[input_folder_1, input_folder_2, input_folder_3,
                               additional_tags_1, additional_tags_2, additional_tags_3],
                        outputs=None,
                        show_progress=False
                    )

                # イベントハンドラ: 変換処理（複数フォルダ対応）
                process_btn.click(
                    fn=process_image_pipeline,
                    inputs=[
                        input_folder_1, input_folder_2, input_folder_3,
                        additional_tags_1, additional_tags_2, additional_tags_3
                    ],
                    outputs=[progress_output]
                )

            # タブ2: タグ編集
            with gr.Tab("🏷️ タグ編集"):
                gr.Markdown("## タグ編集")

                with gr.Row():
                    tagged_folder_input = gr.Textbox(
                        label="タグ付き画像フォルダ",
                        value=last_tagged_folder,
                        placeholder="projects/nasumiso_v1/3_tagged",
                        scale=4
                    )
                    refresh_tags_btn = gr.Button("🔄 再読み込み", scale=1)
                    open_tagged_folder_btn = gr.Button("📂 フォルダを開く", scale=1)

                tag_section_header = gr.Markdown("📝 画像を選択してください")

                with gr.Row():
                    # 左側: Galleryでサムネイル表示（縦一列）
                    with gr.Column(scale=1):
                        image_gallery = gr.Gallery(
                            label="画像一覧（クリックで選択）",
                            value=[],
                            columns=10,
                            rows=1,
                            height="auto",
                            object_fit="contain",
                            show_label=True
                        )

                    # 右側: タグ編集エリア
                    with gr.Column(scale=1):
                        tag_editor = gr.Textbox(
                            label="タグ（カンマ区切り）",
                            lines=8,
                            placeholder="例: masterpiece, best quality, 1girl, solo",
                            show_label=True
                        )
                        save_tags_btn = gr.Button("💾 タグを保存", variant="primary", size="lg")

                # TODO: 一括タグ操作機能（未実装）
                # with gr.Accordion("一括タグ操作", open=False):
                #     gr.Markdown("""
                #     ### 使い方
                #     1. 下のチェックボックスで対象画像を複数選択
                #     2. 追加するタグを入力
                #     3. 「一括追加」ボタンをクリック
                #     """)
                #     batch_tag_input = gr.Textbox(
                #         label="追加するタグ",
                #         placeholder="例: nasumiso_style"
                #     )
                #
                #     batch_image_selector = gr.CheckboxGroup(
                #         label="対象画像（複数選択可）",
                #         choices=[],
                #         value=[],
                #         info="チェックしたすべての画像にタグを追加します"
                #     )
                #
                #     batch_add_btn = gr.Button("➕ 選択した画像にタグを一括追加", variant="secondary", size="lg")

                tag_action_status = gr.Markdown("")

                # Hidden states
                gallery_images_state = gr.State(value=[])
                selected_image_name_state = gr.State(value="")
                image_map_state = gr.Textbox(
                    value="{}",
                    label="__image_map_state",
                    visible=False
                )

                refresh_outputs = [
                    image_gallery,
                    gallery_images_state,
                    tag_editor,
                    tag_section_header,
                    selected_image_name_state,
                    image_map_state,
                    tag_action_status
                ]

                # イベントハンドラ: フォルダ再読み込み
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

                # イベントハンドラ: Gallery選択
                image_gallery.select(
                    fn=handle_gallery_selection,
                    inputs=[gallery_images_state],
                    outputs=[tag_editor, tag_section_header, selected_image_name_state]
                )

                # イベントハンドラ: タグ保存
                save_tags_btn.click(
                    fn=save_current_tags,
                    inputs=[selected_image_name_state, tag_editor, tagged_folder_input, image_map_state],
                    outputs=[tag_action_status]
                )

                # TODO: 未実装 - 一括タグ追加機能のイベントハンドラ
                # 以下のコンポーネントが未定義のためコメントアウト:
                # - batch_gallery (Gallery)
                # - batch_selected_indices_state (State)
                # - update_batch_selection (関数)
                # - add_batch_tag_from_indices (関数)

                # # イベントハンドラ: 一括タグ追加用のGallery更新とリセット
                # def reset_batch_selection_and_update_gallery(paths):
                #     return gr.update(value=paths), [], "💡 一括追加したい画像をクリックして選択してください"
                #
                # refresh_tags_btn.click(
                #     fn=reset_batch_selection_and_update_gallery,
                #     inputs=[gallery_images_state],
                #     outputs=[batch_gallery, batch_selected_indices_state, tag_action_status]
                # )
                # tagged_folder_input.change(
                #     fn=reset_batch_selection_and_update_gallery,
                #     inputs=[gallery_images_state],
                #     outputs=[batch_gallery, batch_selected_indices_state, tag_action_status]
                # )
                #
                # # イベントハンドラ: 一括操作用Gallery選択（トグル動作）
                # batch_gallery.select(
                #     fn=update_batch_selection,
                #     inputs=[batch_selected_indices_state],
                #     outputs=[batch_selected_indices_state, tag_action_status]
                # )
                #
                # # イベントハンドラ: 一括タグ追加ボタン
                # batch_add_btn.click(
                #     fn=add_batch_tag_from_indices,
                #     inputs=[batch_tag_input, batch_selected_indices_state, gallery_images_state],
                #     outputs=[tag_action_status]
                # )

        # アプリロード時の初期化
        app.load(
            fn=refresh_tag_editor_data,
            inputs=[tagged_folder_input],
            outputs=refresh_outputs
        )

        # 画像準備タブ：画像枚数の初期化
        def init_image_counts(path1, path2, path3):
            """起動時に各フォルダの画像枚数を取得"""
            count1 = update_count_button(path1)
            count2 = update_count_button(path2)
            count3 = update_count_button(path3)
            return count1, count2, count3

        app.load(
            fn=init_image_counts,
            inputs=[input_folder_1, input_folder_2, input_folder_3],
            outputs=[image_count_btn_1, image_count_btn_2, image_count_btn_3]
        )

        gr.Markdown("---")
        gr.Markdown("Made with ❤️ for Nasumiso")

    return app


if __name__ == "__main__":
    logger.info("Nasumiso LoRA Training Assistant 起動中...")

    app = create_ui()
    launch_app_with_port_retry(app, host="127.0.0.1")
