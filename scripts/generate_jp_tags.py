#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日本語タグファイル生成スクリプト

機能:
- 英語タグファイルを日本語に翻訳して確認用ファイルを生成
- _jp.txt というサフィックスで保存
- タグレビュー時に使用
"""

import argparse
import sys
from pathlib import Path
from typing import Dict


# タグの日本語翻訳辞書
TAG_TRANSLATIONS: Dict[str, str] = {
    # キャラクター数
    "1boy": "男の子1人",
    "1girl": "女の子1人",
    "2boys": "男の子2人",
    "2girls": "女の子2人",
    "multiple_boys": "複数の男の子",
    "multiple_girls": "複数の女の子",
    "solo": "単独",
    "no_humans": "人物なし",

    # 焦点
    "male_focus": "男性中心",
    "female_focus": "女性中心",

    # 外見
    "black_hair": "黒髪",
    "short_hair": "短髪",
    "long_hair": "長髪",
    "blue_skin": "青い肌色",
    "colored_skin": "色付きの肌",
    "chibi": "ちびキャラ",

    # 服装
    "shirt": "シャツ",
    "short_sleeves": "半袖",
    "serafuku": "セーラー服",
    "school_uniform": "制服",
    "sailor_collar": "セーラーカラー",
    "japanese_clothes": "和服",
    "glasses": "眼鏡",

    # 動作
    "eating": "食べている",
    "holding": "持っている",
    "holding_food": "食べ物を持っている",
    "chewing": "噛んでいる",
    "open_mouth": "口を開けている",
    "closed_eyes": "目を閉じている",
    "looking_at_viewer": "こちらを見ている",
    "smile": "笑顔",
    "smiling": "微笑んでいる",

    # アイテム
    "food": "食べ物",
    "bread": "パン",
    "food_on_face": "顔に食べ物",
    "monitor": "モニター",

    # 背景
    "green_background": "緑背景",
    "white_background": "白背景",
    "simple_background": "シンプルな背景",
    "black_background": "黒背景",
    "negative_space": "余白",

    # 構図
    "upper_body": "上半身",
    "full_body": "全身",
    "cropped_torso": "胴体クロップ",

    # カラー
    "green_sailor_collar": "緑のセーラーカラー",

    # スタイル・品質
    "nasumiso_style": "なすみそ風",
    "simple_lineart": "シンプルな線画",
    "masterpiece": "傑作",
    "best_quality": "最高品質",
    "high_quality": "高品質",

    # その他
    "general": "一般",
    "sensitive": "センシティブ",
    "comic": "コミック",
    "monochrome": "モノクロ",
    "greyscale": "グレースケール",
}


def translate_tags(tags: list[str]) -> list[str]:
    """
    タグのリストを日本語に翻訳

    Args:
        tags: 英語タグのリスト

    Returns:
        日本語タグのリスト（翻訳がない場合は元のタグ + "(原文)"）
    """
    translated = []
    for tag in tags:
        tag = tag.strip()
        if tag in TAG_TRANSLATIONS:
            translated.append(TAG_TRANSLATIONS[tag])
        else:
            translated.append(f"{tag}(原文)")
    return translated


def generate_jp_file(txt_path: Path) -> None:
    """
    英語タグファイルから日本語版を生成

    Args:
        txt_path: 英語タグファイルのパス
    """
    # タグを読み込み
    content = txt_path.read_text(encoding='utf-8')
    tags = content.split(', ')

    # 日本語に翻訳
    tags_jp = translate_tags(tags)

    # 日本語ファイルを作成
    jp_filename = txt_path.stem + '_jp.txt'
    jp_filepath = txt_path.parent / jp_filename

    # カンマ区切りで保存
    jp_content = ', '.join(tags_jp)
    jp_filepath.write_text(jp_content, encoding='utf-8')


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='タグファイルから日本語確認用ファイルを生成',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 3_tagged/内の全タグファイルを日本語化
  python scripts/generate_jp_tags.py \\
    --input projects/nasumiso_v1/3_tagged

  # 特定のファイルのみ
  python scripts/generate_jp_tags.py \\
    --input projects/nasumiso_v1/3_tagged \\
    --file img001.txt
        """
    )

    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='タグファイルがあるディレクトリのパス'
    )

    parser.add_argument(
        '--file',
        type=str,
        help='特定のファイル名（指定しない場合は全ファイル）'
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
    if args.file:
        txt_files = [input_dir / args.file]
        if not txt_files[0].exists():
            print(f"エラー: ファイルが見つかりません: {txt_files[0]}", file=sys.stderr)
            sys.exit(1)
    else:
        txt_files = sorted(input_dir.glob('*.txt'))
        # _jp.txtを除外
        txt_files = [f for f in txt_files if not f.name.endswith('_jp.txt')]

    if not txt_files:
        print(f"エラー: {input_dir} にタグファイルが見つかりません", file=sys.stderr)
        sys.exit(1)

    print(f"処理対象: {len(txt_files)}個のタグファイル\n")

    for txt_file in txt_files:
        generate_jp_file(txt_file)

        jp_filename = txt_file.stem + '_jp.txt'
        print(f"✓ {txt_file.name} → {jp_filename}")

    print(f"\n完了: {len(txt_files)}個の日本語タグファイルを生成しました")
    print(f"確認用ファイル: *_jp.txt")


if __name__ == '__main__':
    main()
