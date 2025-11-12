from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple


@dataclass
class TagEditorRefreshResult:
    """結果データ（UI 側で Gradio コンポーネントにマッピング）"""

    image_paths: List[str]
    selected_image_name: str
    tags: str
    header_text: str
    status_text: str
    image_map: Dict[str, str]
    selected_index: Optional[int]
    error_message: Optional[str] = None


@dataclass
class GallerySelectionResult:
    """ギャラリー選択イベントの結果"""

    tags: str
    header_text: str
    image_name: str

    def as_tuple(self) -> Tuple[str, str, str]:
        return self.tags, self.header_text, self.image_name


class TagEditorService:
    """タグ編集関連のビジネスロジック"""

    IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG"}

    def __init__(self, default_tagged_dir: Path, logger: Optional[logging.Logger] = None):
        self.default_tagged_dir = Path(default_tagged_dir)
        self.logger = logger or logging.getLogger(__name__)

    def parse_image_map(self, json_str: Optional[str]) -> Dict[str, str]:
        if not json_str:
            return {}
        try:
            data = json.loads(json_str)
            if isinstance(data, dict):
                return {str(k): str(v) for k, v in data.items()}
        except json.JSONDecodeError:
            self.logger.warning("画像マップのJSON解析に失敗しました")
        return {}

    def resolve_tagged_folder(self, tagged_folder: Optional[Sequence[str] | str | Path]) -> Path:
        if not tagged_folder:
            return self.default_tagged_dir
        if isinstance(tagged_folder, (list, tuple)):
            tagged_folder = tagged_folder[0] if tagged_folder else None
        if tagged_folder and str(tagged_folder).strip():
            return Path(tagged_folder).expanduser()
        return self.default_tagged_dir

    def resolve_image_path(
        self,
        image_name: str,
        tagged_folder: Optional[str] = None,
        image_map: Optional[Dict[str, str]] = None,
    ) -> Optional[Path]:
        if not image_name:
            return None
        if image_map and image_name in image_map:
            return Path(image_map[image_name])
        folder = self.resolve_tagged_folder(tagged_folder)
        return folder / image_name

    def load_tagged_images(self, tagged_folder: Optional[str | Path] = None) -> List[str]:
        try:
            folder = self.resolve_tagged_folder(tagged_folder)
            if not folder.exists():
                self.logger.warning(f"タグ付き画像フォルダが存在しません: {folder}")
                return []
            image_files = sorted(
                str(f)
                for f in folder.iterdir()
                if f.is_file() and f.suffix in self.IMAGE_EXTENSIONS
            )
            return image_files
        except Exception as exc:
            self.logger.exception("画像一覧取得でエラー発生")
            return []

    def load_tags_for_image(self, image_path: str) -> str:
        try:
            if not image_path:
                return ""
            img_path = Path(image_path)
            txt_path = img_path.with_suffix(".txt")
            if not txt_path.exists():
                return ""
            return txt_path.read_text(encoding="utf-8").strip()
        except Exception as exc:
            self.logger.exception(f"タグ読み込みでエラー発生: {image_path}")
            return f"❌ エラー: {exc}"

    def save_tags_for_image(self, image_path: str, tags: str) -> str:
        try:
            if not image_path:
                return "❌ 画像が選択されていません"
            img_path = Path(image_path)
            txt_path = img_path.with_suffix(".txt")
            txt_path.write_text(tags.strip(), encoding="utf-8")
            self.logger.info(f"タグ保存完了: {txt_path.name}")
            return f"✅ タグを保存しました: {img_path.name}"
        except Exception as exc:
            self.logger.exception(f"タグ保存でエラー発生: {image_path}")
            return f"❌ エラー: {exc}"

    def save_current_tags(
        self,
        image_name: str,
        tags: str,
        tagged_folder: Optional[str] = None,
        image_map_json: Optional[str] = None,
    ) -> str:
        try:
            if not image_name:
                return "❌ 画像が選択されていません"
            image_map = self.parse_image_map(image_map_json)
            image_path = self.resolve_image_path(image_name, tagged_folder, image_map)
            if not image_path:
                return "❌ 画像が選択されていません"
            if not image_path.exists():
                return "❌ 画像が見つかりません"
            return self.save_tags_for_image(str(image_path), tags)
        except Exception as exc:
            self.logger.exception("タグ保存でエラー発生")
            return f"❌ エラー: {exc}"

    def refresh_tag_editor_data(self, tagged_folder: Optional[str]) -> TagEditorRefreshResult:
        try:
            image_paths = self.load_tagged_images(tagged_folder)
            image_map = {Path(p).name: p for p in image_paths}
            if image_paths:
                first_path = image_paths[0]
                first_name = Path(first_path).name
                tags = self.load_tags_for_image(first_path)
                header = f"📝 {first_name} のタグを編集"
                status = f"📁 {len(image_paths)}枚の画像を読み込みました"
                selected_index = 0
            else:
                first_name = ""
                tags = ""
                header = "📝 画像を選択してください"
                status = "❗ タグ付き画像が見つかりません"
                selected_index = None
            return TagEditorRefreshResult(
                image_paths=image_paths,
                selected_image_name=first_name,
                tags=tags,
                header_text=header,
                status_text=status,
                image_map=image_map,
                selected_index=selected_index,
            )
        except Exception as exc:
            self.logger.exception("タグ一覧再読み込みでエラー発生")
            return TagEditorRefreshResult(
                image_paths=[],
                selected_image_name="",
                tags="",
                header_text="❌ エラーが発生しました",
                status_text=f"❌ エラー: {exc}",
                image_map={},
                selected_index=None,
                error_message=str(exc),
            )

    def handle_gallery_selection(
        self,
        gallery_images: Optional[Sequence[str]],
        selected_index: Optional[int],
    ) -> GallerySelectionResult:
        try:
            if (
                not gallery_images
                or selected_index is None
                or selected_index < 0
                or selected_index >= len(gallery_images)
            ):
                return GallerySelectionResult("", "📝 画像を選択してください", "")

            selected_image_path = gallery_images[selected_index]
            tags = self.load_tags_for_image(selected_image_path)
            image_name = Path(selected_image_path).name
            header = f"📝 {image_name} のタグを編集"
            return GallerySelectionResult(tags, header, image_name)
        except Exception as exc:
            self.logger.exception("Gallery選択でエラー発生")
            return GallerySelectionResult(f"❌ エラー: {exc}", "❌ エラーが発生しました", "")
