#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CoreML高速化のベンチマークスクリプト

機能:
- CoreML無効版とCoreML有効版の処理時間を測定
- 同じ画像セットで比較
"""

import argparse
import sys
import time
from pathlib import Path
from typing import List

import numpy as np
import onnxruntime as ort
from huggingface_hub import hf_hub_download
from PIL import Image

# WD14 Tagger v2のモデルID
MODEL_ID = "SmilingWolf/wd-v1-4-moat-tagger-v2"
MODEL_FILENAME = "model.onnx"


class SimpleTagger:
    """ベンチマーク用の簡易Taggerクラス"""

    def __init__(self, use_coreml: bool = True):
        """
        初期化

        Args:
            use_coreml: CoreMLを使用するか（デフォルト: True）
        """
        self.image_size = 448
        self.use_coreml = use_coreml

        print(f"モード: {'CoreML有効' if use_coreml else 'CPU専用'}")
        print("モデルをロード中...")

        # ONNXモデルのダウンロード
        model_path = hf_hub_download(
            repo_id=MODEL_ID,
            filename=MODEL_FILENAME
        )

        # ONNXランタイムセッションの作成
        if use_coreml:
            providers = ['CoreMLExecutionProvider', 'CPUExecutionProvider']
        else:
            providers = ['CPUExecutionProvider']

        self.session = ort.InferenceSession(model_path, providers=providers)

        # 使用中のプロバイダーを確認
        available_providers = self.session.get_providers()
        print(f"使用プロバイダー: {available_providers}")

    def _preprocess_image(self, image: Image.Image) -> np.ndarray:
        """画像を前処理"""
        # リサイズとパディング
        image.thumbnail((self.image_size, self.image_size), Image.Resampling.LANCZOS)

        # 正方形にパディング
        canvas = Image.new('RGB', (self.image_size, self.image_size), (255, 255, 255))
        offset = ((self.image_size - image.width) // 2, (self.image_size - image.height) // 2)
        canvas.paste(image, offset)

        # NumPy配列に変換
        img_array = np.array(canvas, dtype=np.float32)
        img_array = np.expand_dims(img_array, axis=0)

        return img_array

    def predict(self, image_path: Path):
        """画像からタグを予測（結果は使わない）"""
        # 画像を読み込み
        image = Image.open(image_path).convert("RGB")

        # 前処理
        input_array = self._preprocess_image(image)

        # 推論
        input_name = self.session.get_inputs()[0].name
        output_name = self.session.get_outputs()[0].name

        _ = self.session.run([output_name], {input_name: input_array})[0]


def get_image_files(input_dir: Path) -> List[Path]:
    """指定ディレクトリから画像ファイルを取得"""
    image_extensions = {'.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'}
    image_files = [
        f for f in input_dir.iterdir()
        if f.is_file() and f.suffix in image_extensions
    ]
    return sorted(image_files)


def benchmark(input_dir: Path, use_coreml: bool) -> float:
    """
    ベンチマークを実行

    Args:
        input_dir: 入力ディレクトリ
        use_coreml: CoreMLを使用するか

    Returns:
        総処理時間（秒）
    """
    # 画像ファイルを取得
    image_files = get_image_files(input_dir)

    if not image_files:
        print(f"エラー: {input_dir} に画像ファイルが見つかりません")
        return 0.0

    print(f"画像数: {len(image_files)}枚")
    print("-" * 50)

    # Taggerを初期化
    tagger = SimpleTagger(use_coreml=use_coreml)

    # ベンチマーク実行
    print("\nベンチマーク開始...")
    start_time = time.time()

    for idx, image_path in enumerate(image_files, start=1):
        tagger.predict(image_path)
        if idx % 5 == 0 or idx == len(image_files):
            print(f"処理中... {idx}/{len(image_files)}")

    end_time = time.time()
    elapsed = end_time - start_time

    print(f"\n総処理時間: {elapsed:.2f}秒")
    print(f"平均処理時間: {elapsed/len(image_files):.3f}秒/枚")

    return elapsed


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='CoreML高速化のベンチマーク',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # CoreML無効版
  python scripts/benchmark_coreml.py \\
    --input projects/nasumiso_v1/2_processed \\
    --no-coreml

  # CoreML有効版
  python scripts/benchmark_coreml.py \\
    --input projects/nasumiso_v1/2_processed
        """
    )

    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='入力ディレクトリのパス'
    )

    parser.add_argument(
        '--no-coreml',
        action='store_true',
        help='CoreMLを無効化（CPU専用）'
    )

    args = parser.parse_args()

    # パスをPathオブジェクトに変換
    input_dir = Path(args.input)

    # 入力ディレクトリの存在確認
    if not input_dir.exists():
        print(f"エラー: 入力ディレクトリが存在しません: {input_dir}", file=sys.stderr)
        sys.exit(1)

    if not input_dir.is_dir():
        print(f"エラー: 入力パスがディレクトリではありません: {input_dir}", file=sys.stderr)
        sys.exit(1)

    # ベンチマーク実行
    use_coreml = not args.no_coreml
    elapsed = benchmark(input_dir, use_coreml)

    if elapsed > 0:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
