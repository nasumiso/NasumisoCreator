from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Protocol, Sequence

from PIL import Image

from scripts.add_common_tag import add_tag_to_file
from scripts.auto_caption import WD14Tagger
from scripts.prepare_images import get_image_files, resize_and_crop


class ProgressReporter(Protocol):
    def __call__(self, value: float, desc: str = ...) -> None:  # pragma: no cover - Protocol definition
        ...


@dataclass
class FolderConfig:
    index: int
    path: Path
    tags: str


def run_image_preparation_pipeline(
    folders: Sequence[dict],
    project_root: Path,
    progress: Optional[ProgressReporter] = None,
    logger: Optional[logging.Logger] = None,
) -> str:
    """
    画像前処理パイプラインを実行し、ログ文字列を返す
    """
    logger = logger or logging.getLogger(__name__)
    output_messages: List[str] = []

    def add_message(msg: str) -> None:
        output_messages.append(msg)

    def update_progress(value: float, desc: str) -> None:
        if progress is None:
            return
        try:
            progress(value, desc=desc)
        except TypeError:
            progress(value)

    try:
        folder_configs: List[FolderConfig] = []
        for idx, folder_dict in enumerate(folders, start=1):
            folder_path = folder_dict.get("path", "").strip()
            tags = folder_dict.get("tags", "").strip()

            if not folder_path:
                continue

            path = Path(folder_path)
            if path.exists() and path.is_dir():
                folder_configs.append(FolderConfig(index=idx, path=path, tags=tags))
            elif path.exists():
                add_message(f"⚠️ フォルダ{idx}: パスがディレクトリではありません: {folder_path}")
            else:
                add_message(f"⚠️ フォルダ{idx}: フォルダが存在しません: {folder_path}")

        if not folder_configs:
            return "❌ エラー: 有効な入力フォルダが指定されていません"

        processed_dir = project_root / "projects/nasumiso_v1/2_processed"
        tagged_dir = project_root / "projects/nasumiso_v1/3_tagged"
        processed_dir.mkdir(parents=True, exist_ok=True)
        tagged_dir.mkdir(parents=True, exist_ok=True)

        add_message("=" * 60)
        add_message("🎨 Nasumiso LoRA Training Assistant - 画像前処理パイプライン")
        add_message("=" * 60)
        add_message("")
        add_message(f"📁 処理対象フォルダ: {len(folder_configs)}個")
        for config in folder_configs:
            add_message(f"  フォルダ{config.index}: {config.path}")
            if config.tags:
                add_message(f"    追加タグ: {config.tags}")
        add_message("")

        image_list = []
        for config in folder_configs:
            folder_images = get_image_files(config.path)
            for img_path in folder_images:
                image_list.append((img_path, config.index, config.tags))
            add_message(f"  フォルダ{config.index}: {len(folder_images)}枚")

        total_images = len(image_list)
        if total_images == 0:
            add_message("❌ エラー: 画像ファイルが見つかりません")
            return "\n".join(output_messages)

        add_message(f"📊 合計画像数: {total_images}枚")
        add_message("")

        logger.info("ステップ1開始: prepare_images (統合 -> %s)", processed_dir)
        add_message("📝 ステップ1: 画像のリサイズと統合連番リネーム（512x512）")
        add_message(f"  出力: {processed_dir}")
        add_message("")

        success_count = 0
        skip_count = 0
        processed_output_paths = []  # ステップ1で生成したファイルパスを記録
        for idx, (image_path, folder_idx, _) in enumerate(image_list, start=1):
            progress_ratio = (idx / total_images) * 0.3
            update_progress(progress_ratio, desc=f"ステップ1: {idx}/{total_images}枚 リサイズ中...")
            try:
                with Image.open(image_path) as img:
                    if img.mode not in ("RGB", "RGBA"):
                        img = img.convert("RGB")
                    processed = resize_and_crop(img, 512)
                    output_filename = f"img{idx-1:03d}.png"
                    output_path = processed_dir / output_filename
                    processed.save(output_path, "PNG", optimize=True)
                    add_message(f"  ✓ [{idx}/{total_images}] フォルダ{folder_idx}: {image_path.name} → {output_filename}")
                    processed_output_paths.append(output_path)  # 成功したファイルを記録
                    success_count += 1
            except Exception as exc:  # pylint: disable=broad-except
                add_message(f"  ✗ [{idx}/{total_images}] フォルダ{folder_idx}: {image_path.name}: エラー - {exc}")
                skip_count += 1

        add_message("")
        add_message(f"✅ ステップ1完了: {success_count}枚成功, {skip_count}枚スキップ")
        add_message("")
        if success_count == 0:
            add_message("❌ エラー: 画像が1枚も処理できませんでした")
            return "\n".join(output_messages)

        logger.info("ステップ2開始: auto_caption (%s -> %s)", processed_dir, tagged_dir)
        add_message("📝 ステップ2: WD14 Taggerで自動タグ付け（しきい値: 0.35）")
        add_message(f"  入力: {processed_dir}")
        add_message(f"  出力: {tagged_dir}")
        add_message("")

        add_message("  モデルをロード中...")
        tagger = WD14Tagger(threshold=0.35, use_coreml=False)
        add_message("  ✓ モデルロード完了")
        add_message("")

        # ステップ1で生成した画像のみを処理対象とする
        processed_images = processed_output_paths
        success_count2 = 0
        skip_count2 = 0

        for idx, image_path in enumerate(processed_images, start=1):
            progress_ratio = 0.3 + (idx / len(processed_images)) * 0.5 if processed_images else 0.3
            update_progress(progress_ratio, desc=f"ステップ2: {idx}/{len(processed_images)}枚 タグ付け中...")
            try:
                tags = tagger.predict_tags_only(image_path)
                tag_string = ", ".join(tags)
                output_image = tagged_dir / image_path.name
                output_txt = tagged_dir / f"{image_path.stem}.txt"
                shutil.copy2(image_path, output_image)
                output_txt.write_text(tag_string, encoding="utf-8")
                add_message(f"  ✓ [{idx}/{len(processed_images)}] {image_path.name} ({len(tags)}個のタグ)")
                success_count2 += 1
            except Exception as exc:  # pylint: disable=broad-except
                add_message(f"  ✗ [{idx}/{len(processed_images)}] {image_path.name}: エラー - {exc}")
                skip_count2 += 1

        add_message("")
        add_message(f"✅ ステップ2完了: {success_count2}枚成功, {skip_count2}枚スキップ")
        add_message("")
        if success_count2 == 0:
            add_message("❌ エラー: タグ付けが1枚もできませんでした")
            return "\n".join(output_messages)

        logger.info("ステップ3開始: add_common_tag (%s)", tagged_dir)
        add_message("📝 ステップ3: 共通タグ + フォルダ固有タグ追加")
        add_message(f"  対象: {tagged_dir}")
        add_message("")

        txt_files = sorted(f for f in tagged_dir.glob("*.txt") if not f.name.endswith("_jp.txt"))
        added_count = 0
        for txt_idx, txt_file in enumerate(txt_files, start=1):
            progress_ratio = 0.8 + (txt_idx / len(txt_files)) * 0.2 if txt_files else 0.8
            update_progress(progress_ratio, desc=f"ステップ3: {txt_idx}/{len(txt_files)}個 共通タグ追加中...")
            try:
                img_index = int(txt_file.stem.replace("img", ""))
            except ValueError:
                logger.warning("ファイル名から番号を抽出できません: %s", txt_file.name)
                continue

            if img_index < len(image_list):
                _, folder_idx, folder_tags = image_list[img_index]
            else:
                logger.warning("画像インデックス%sが範囲外です", img_index)
                continue

            tags_to_add = ["nasumiso_style"]
            if folder_tags:
                extra_tags = [tag.strip() for tag in folder_tags.split(",") if tag.strip()]
                tags_to_add.extend(extra_tags)

            for tag in tags_to_add:
                added = add_tag_to_file(txt_file, tag=tag, position="start", backup=False)
                if added:
                    added_count += 1

        add_message(f"✅ ステップ3完了: {added_count}個のタグを追加")
        add_message("")

        update_progress(1.0, desc="完了!")
        add_message("=" * 60)
        add_message("🎉 パイプライン完了！")
        add_message(f"📁 出力フォルダ: {tagged_dir}")
        add_message(f"📊 処理結果: {success_count2}枚の画像を処理しました")
        add_message("=" * 60)

        logger.info("画像前処理パイプライン完了")
        return "\n".join(output_messages)

    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("画像処理パイプラインでエラー発生")
        add_message("")
        add_message(f"❌ エラーが発生しました: {exc}")
        return "\n".join(output_messages)
