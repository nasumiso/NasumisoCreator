#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共通タグの一括追加スクリプト

機能:
- 指定したタグを全てのタグファイルの先頭（または末尾）に追加
- すでに存在するタグはスキップ
- バックアップ作成オプション
"""

import argparse
import sys
from pathlib import Path
from typing import List


def add_tag_to_file(
    txt_path: Path,
    tag: str,
    position: str = "start",
    backup: bool = False
) -> bool:
    """
    タグファイルに共通タグを追加

    Args:
        txt_path: タグファイルのパス
        tag: 追加するタグ
        position: 追加位置（"start" または "end"）
        backup: バックアップを作成するか

    Returns:
        追加されたかどうか
    """
    # 既存のタグを読み込み
    content = txt_path.read_text(encoding='utf-8')
    tags = [t.strip() for t in content.split(',')]

    # すでに存在する場合はスキップ
    if tag in tags:
        return False

    # バックアップ作成
    if backup:
        backup_path = txt_path.with_suffix('.txt.bak')
        backup_path.write_text(content, encoding='utf-8')

    # タグを追加
    if position == "start":
        tags.insert(0, tag)
    else:  # end
        tags.append(tag)

    # 保存
    new_content = ', '.join(tags)
    txt_path.write_text(new_content, encoding='utf-8')

    return True


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='全タグファイルに共通タグを一括追加',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 全画像の先頭に nasumiso_style を追加
  python scripts/add_common_tag.py \\
    --input projects/nasumiso_v1/3_tagged \\
    --tag "nasumiso_style"

  # 全画像の末尾に masterpiece を追加（バックアップ付き）
  python scripts/add_common_tag.py \\
    --input projects/nasumiso_v1/3_tagged \\
    --tag "masterpiece" \\
    --position end \\
    --backup
        """
    )

    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='タグファイルがあるディレクトリのパス'
    )

    parser.add_argument(
        '--tag',
        type=str,
        required=True,
        help='追加するタグ'
    )

    parser.add_argument(
        '--position',
        type=str,
        choices=['start', 'end'],
        default='start',
        help='タグの追加位置（デフォルト: start）'
    )

    parser.add_argument(
        '--backup',
        action='store_true',
        help='バックアップファイル（.txt.bak）を作成する'
    )

    parser.add_argument(
        '--exclude-jp',
        action='store_true',
        help='日本語タグファイル（_jp.txt）を除外する'
    )

    args = parser.parse_args()

    # パスをPathオブジェクトに変換
    input_dir = Path(args.input)

    # ディレクトリの存在確認
    if not input_dir.exists():
        print(f"エラー: ディレクトリが存在しません: {input_dir}", file=sys.stderr)
        sys.exit(1)

    if not input_dir.is_dir():
        print(f"エラー: パスがディレクトリではありません: {input_dir}", file=sys.stderr)
        sys.exit(1)

    # タグファイルを取得
    txt_files = sorted(input_dir.glob('*.txt'))

    # _jp.txtを除外
    if args.exclude_jp:
        txt_files = [f for f in txt_files if not f.name.endswith('_jp.txt')]

    if not txt_files:
        print(f"エラー: {input_dir} にタグファイルが見つかりません", file=sys.stderr)
        sys.exit(1)

    print(f"処理対象: {len(txt_files)}個のタグファイル")
    print(f"追加するタグ: '{args.tag}'")
    print(f"追加位置: {args.position}")
    if args.backup:
        print("バックアップ: 有効")
    print("-" * 50)

    added_count = 0
    skipped_count = 0

    for txt_file in txt_files:
        added = add_tag_to_file(
            txt_file,
            args.tag,
            args.position,
            args.backup
        )

        if added:
            print(f"✓ {txt_file.name}: タグを追加しました")
            added_count += 1
        else:
            print(f"- {txt_file.name}: すでに存在するためスキップ")
            skipped_count += 1

    print("-" * 50)
    print(f"完了: {added_count}個に追加, {skipped_count}個スキップ")

    if added_count > 0:
        print(f"\n次のステップ: git diff で変更を確認し、コミットしてください")


if __name__ == '__main__':
    main()
