#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
画像前処理スクリプト

機能:
- 指定フォルダ内の画像を連番リネーム（img001.png など）
- 指定サイズにリサイズ（デフォルト: 512x512）
- アスペクト比を維持し、中央クロップで調整
"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple

from PIL import Image


def get_image_files(input_dir: Path) -> List[Path]:
    """
    指定ディレクトリから画像ファイルを取得

    Args:
        input_dir: 入力ディレクトリのパス

    Returns:
        画像ファイルのパスリスト（ソート済み）
    """
    # サポートする画像形式
    image_extensions = {'.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'}

    image_files = [
        f for f in input_dir.iterdir()
        if f.is_file() and f.suffix in image_extensions
    ]

    # ファイル名でソート
    return sorted(image_files)


def resize_and_crop(image: Image.Image, target_size: int) -> Image.Image:
    """
    画像を指定サイズにリサイズし、中央クロップ

    アスペクト比を維持しながら、短辺を target_size に合わせてリサイズし、
    長辺を中央でクロップして正方形にする。

    Args:
        image: 入力画像
        target_size: 目標サイズ（正方形の一辺の長さ）

    Returns:
        リサイズ・クロップ済みの画像
    """
    width, height = image.size

    # アスペクト比を維持しながら、短辺を target_size に合わせる
    if width < height:
        # 幅が短い場合
        new_width = target_size
        new_height = int(height * (target_size / width))
    else:
        # 高さが短い場合
        new_height = target_size
        new_width = int(width * (target_size / height))

    # 高品質リサンプリングでリサイズ
    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # 中央クロップで正方形にする
    left = (new_width - target_size) // 2
    top = (new_height - target_size) // 2
    right = left + target_size
    bottom = top + target_size

    cropped = resized.crop((left, top, right, bottom))

    return cropped


def process_images(
    input_dir: Path,
    output_dir: Path,
    target_size: int = 512
) -> Tuple[int, int]:
    """
    画像を一括処理

    Args:
        input_dir: 入力ディレクトリ
        output_dir: 出力ディレクトリ
        target_size: 目標サイズ（デフォルト: 512）

    Returns:
        (成功数, スキップ数) のタプル
    """
    # 出力ディレクトリが存在しない場合は作成
    output_dir.mkdir(parents=True, exist_ok=True)

    # 画像ファイルを取得
    image_files = get_image_files(input_dir)

    if not image_files:
        print(f"エラー: {input_dir} に画像ファイルが見つかりません")
        return 0, 0

    print(f"処理対象: {len(image_files)}枚の画像")
    print(f"出力サイズ: {target_size}x{target_size}")
    print("-" * 50)

    success_count = 0
    skip_count = 0

    for idx, image_path in enumerate(image_files, start=1):
        try:
            # 画像を開く
            with Image.open(image_path) as img:
                # RGBAまたはRGBに変換（モード統一）
                if img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGB')

                # リサイズ・クロップ
                processed = resize_and_crop(img, target_size)

                # 出力ファイル名（連番: img001.png, img002.png, ...）
                output_filename = f"img{idx:03d}.png"
                output_path = output_dir / output_filename

                # PNG形式で保存（ロスレス）
                processed.save(output_path, 'PNG', optimize=True)

                print(f"✓ [{idx:02d}/{len(image_files)}] {image_path.name} → {output_filename}")
                success_count += 1

        except Exception as e:
            print(f"✗ [{idx:02d}/{len(image_files)}] {image_path.name}: エラー - {e}")
            skip_count += 1
            continue

    print("-" * 50)
    print(f"完了: {success_count}枚成功, {skip_count}枚スキップ")

    return success_count, skip_count


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='画像を連番リネーム・リサイズして出力',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python scripts/prepare_images.py \\
    --input projects/nasumiso_v1/1_raw_images \\
    --output projects/nasumiso_v1/2_processed \\
    --size 512
        """
    )

    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='入力ディレクトリのパス'
    )

    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='出力ディレクトリのパス'
    )

    parser.add_argument(
        '--size',
        type=int,
        default=512,
        help='出力画像のサイズ（正方形の一辺、デフォルト: 512）'
    )

    args = parser.parse_args()

    # パスをPathオブジェクトに変換
    input_dir = Path(args.input)
    output_dir = Path(args.output)

    # 入力ディレクトリの存在確認
    if not input_dir.exists():
        print(f"エラー: 入力ディレクトリが存在しません: {input_dir}", file=sys.stderr)
        sys.exit(1)

    if not input_dir.is_dir():
        print(f"エラー: 入力パスがディレクトリではありません: {input_dir}", file=sys.stderr)
        sys.exit(1)

    # 処理実行
    success, skip = process_images(input_dir, output_dir, args.size)

    # 結果に応じて終了コードを設定
    if success == 0:
        sys.exit(1)
    elif skip > 0:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
