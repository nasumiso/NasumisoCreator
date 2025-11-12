from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

DEFAULT_TAGGED_FOLDER = "projects/nasumiso_v1/3_tagged"


@dataclass
class FolderEntry:
    path: str = ""
    tags: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FolderEntry":
        return cls(
            path=str(data.get("path", "") or ""),
            tags=str(data.get("tags", "") or "")
        )

    def to_dict(self) -> Dict[str, str]:
        return {"path": self.path, "tags": self.tags}


@dataclass
class ImagePreparationState:
    folders: List[FolderEntry] = field(default_factory=lambda: [FolderEntry()])

    @classmethod
    def from_dict(cls, data: Dict[str, Any], logger: Optional[logging.Logger] = None) -> "ImagePreparationState":
        folders_raw = data.get("folders")
        folders: List[FolderEntry] = []

        if isinstance(folders_raw, Sequence):
            folders = [FolderEntry.from_dict(item) for item in folders_raw if isinstance(item, dict)]

        if not folders:
            folder_paths = data.get("folder_paths")
            additional_tags = data.get("additional_tags")
            if isinstance(folder_paths, Sequence) or isinstance(additional_tags, Sequence):
                paths = list(folder_paths) if isinstance(folder_paths, Sequence) else []
                tags = list(additional_tags) if isinstance(additional_tags, Sequence) else []
                max_len = max(len(paths), len(tags), 1)
                for idx in range(max_len):
                    path = paths[idx] if idx < len(paths) else ""
                    tag = tags[idx] if idx < len(tags) else ""
                    if path or tag:
                        folders.append(FolderEntry(path=path, tags=tag))
                if not folders:
                    folders.append(FolderEntry())
                if logger:
                    logger.info("app_state.json を新形式(folders)にマイグレーションしました")

        if not folders:
            folders = [FolderEntry()]

        return cls(folders=folders)

    def to_dict(self) -> Dict[str, Any]:
        return {"folders": [folder.to_dict() for folder in self.folders]}


@dataclass
class TagEditorState:
    last_tagged_folder: str = DEFAULT_TAGGED_FOLDER

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TagEditorState":
        folder = data.get("last_tagged_folder", DEFAULT_TAGGED_FOLDER)
        return cls(last_tagged_folder=str(folder or DEFAULT_TAGGED_FOLDER))

    def to_dict(self) -> Dict[str, str]:
        return {"last_tagged_folder": self.last_tagged_folder}


@dataclass
class AppState:
    image_preparation: ImagePreparationState = field(default_factory=ImagePreparationState)
    tag_editor: TagEditorState = field(default_factory=TagEditorState)

    @classmethod
    def from_dict(cls, data: Dict[str, Any], logger: Optional[logging.Logger] = None) -> "AppState":
        image_prep_data = data.get("image_preparation", {})
        tag_editor_data = data.get("tag_editor", {})
        image_prep_state = ImagePreparationState.from_dict(image_prep_data, logger=logger)
        tag_editor_state = TagEditorState.from_dict(tag_editor_data)
        return cls(image_preparation=image_prep_state, tag_editor=tag_editor_state)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "image_preparation": self.image_preparation.to_dict(),
            "tag_editor": self.tag_editor.to_dict()
        }


def load_app_state(path: Path, logger: Optional[logging.Logger] = None) -> AppState:
    default_state = AppState()
    if not path.exists():
        return default_state

    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        state = AppState.from_dict(data, logger=logger)
        if logger:
            logger.info("アプリ状態を読み込みました: %s", path)
        # 旧形式から新形式に変換済みなら保存
        if data != state.to_dict():
            save_app_state(state, path, logger=logger)
        return state
    except Exception as exc:  # pylint: disable=broad-except
        if logger:
            logger.warning("状態ファイル読み込みエラー: %s", exc)
        return default_state


def save_app_state(state: AppState, path: Path, logger: Optional[logging.Logger] = None) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(state.to_dict(), fh, indent=2, ensure_ascii=False)
        if logger:
            logger.info("アプリ状態を保存しました: %s", path)
    except Exception as exc:  # pylint: disable=broad-except
        if logger:
            logger.error("状態ファイル保存エラー: %s", exc)

