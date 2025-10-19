#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動タグ付けスクリプト (WD14 Tagger)

機能:
- WD14 Tagger v2を使用してDanbooruタグを自動生成
- 信頼度しきい値によるフィルタリング
- 画像とタグファイル(.txt)を出力ディレクトリに配置
"""

import argparse
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import onnxruntime as ort
import pandas as pd
from huggingface_hub import hf_hub_download
from PIL import Image


# WD14 Tagger v2のモデルID
MODEL_ID = "SmilingWolf/wd-v1-4-moat-tagger-v2"
MODEL_FILENAME = "model.onnx"
TAGS_FILENAME = "selected_tags.csv"


class WD14Tagger:
    """WD14 Tagger v2を使った自動タグ付けクラス"""

    def __init__(self, threshold: float = 0.35, use_coreml: bool = False):
        """
        初期化

        Args:
            threshold: タグの信頼度しきい値（デフォルト: 0.35）
            use_coreml: CoreML高速化を使用するか（デフォルト: False）
        """
        self.threshold = threshold
        self.image_size = 448
        self.use_coreml = use_coreml

        print(f"信頼度しきい値: {self.threshold}")
        print(f"実行モード: {'CoreML有効' if use_coreml else 'CPU専用'}")
        print("モデルをロード中...")

        # ONNXモデルのダウンロード
        model_path = hf_hub_download(
            repo_id=MODEL_ID,
            filename=MODEL_FILENAME
        )

        # ONNXランタイムセッションの作成
        if use_coreml:
            # CoreMLExecutionProviderが利用可能か事前にチェック
            available = ort.get_available_providers()
            if 'CoreMLExecutionProvider' in available:
                # CoreMLExecutionProviderを優先的に使用（Mac用高速化）
                # 注意: 小規模バッチ処理ではオーバーヘッドによりCPUより遅くなる可能性あり
                providers = ['CoreMLExecutionProvider', 'CPUExecutionProvider']
            else:
                # CoreML未サポート環境ではCPUで実行
                print("警告: CoreMLExecutionProviderが利用できません。CPUで実行します。")
                print("（CoreMLはApple Silicon Mac専用です）")
                providers = ['CPUExecutionProvider']
        else:
            # CPU専用（デフォルト）
            providers = ['CPUExecutionProvider']

        self.session = ort.InferenceSession(model_path, providers=providers)

        # 使用中のプロバイダーを確認
        available_providers = self.session.get_providers()
        print(f"使用プロバイダー: {available_providers}")
        if 'CoreMLExecutionProvider' in available_providers:
            print("✓ CoreML高速化が有効です（Apple Neural Engine使用）")
            print("  注意: 小規模バッチではCPU専用より遅くなる可能性があります")
        else:
            print("ℹ CPU実行モード")

        # タグリストの取得
        self.tags = self._load_tags()

        print(f"モデルロード完了（タグ数: {len(self.tags)}）\n")

    def _load_tags(self) -> List[str]:
        """
        WD14 Taggerのタグリストを取得

        Returns:
            タグのリスト
        """
        # selected_tags.csvをダウンロード
        tags_path = hf_hub_download(
            repo_id=MODEL_ID,
            filename=TAGS_FILENAME
        )

        # CSVを読み込んでタグリストを作成
        df = pd.read_csv(tags_path)
        tags = df["name"].tolist()

        return tags

    def _preprocess_image(self, image: Image.Image) -> np.ndarray:
        """
        画像を前処理

        Args:
            image: PIL画像

        Returns:
            前処理済みNumPy配列
        """
        # リサイズとパディング
        # アスペクト比を保持して最大サイズに収める
        image.thumbnail((self.image_size, self.image_size), Image.Resampling.LANCZOS)

        # 正方形にパディング
        canvas = Image.new('RGB', (self.image_size, self.image_size), (255, 255, 255))
        offset = ((self.image_size - image.width) // 2, (self.image_size - image.height) // 2)
        canvas.paste(image, offset)

        # NumPy配列に変換（0-255の範囲をそのまま使用）
        img_array = np.array(canvas, dtype=np.float32)

        # (H, W, C) -> (1, H, W, C) 形式に変換（バッチ次元を追加）
        img_array = np.expand_dims(img_array, axis=0)

        return img_array

    def predict(self, image_path: Path) -> Dict[str, float]:
        """
        画像からタグを予測

        Args:
            image_path: 画像ファイルのパス

        Returns:
            {タグ名: 信頼度}の辞書
        """
        # 画像を読み込み
        image = Image.open(image_path).convert("RGB")

        # 前処理
        input_array = self._preprocess_image(image)

        # 推論
        input_name = self.session.get_inputs()[0].name
        output_name = self.session.get_outputs()[0].name

        outputs = self.session.run([output_name], {input_name: input_array})[0]

        # モデル出力はすでに確率値（0-1）なので、そのまま使用
        probabilities = outputs[0]

        # タグと信頼度を辞書化
        tag_scores = {
            tag: float(prob)
            for tag, prob in zip(self.tags, probabilities)
            if prob >= self.threshold
        }

        # 信頼度でソート（降順）
        tag_scores = dict(sorted(tag_scores.items(), key=lambda x: x[1], reverse=True))

        return tag_scores

    def predict_tags_only(self, image_path: Path) -> List[str]:
        """
        画像からタグのみを予測（信頼度は含まない）

        Args:
            image_path: 画像ファイルのパス

        Returns:
            タグのリスト
        """
        tag_scores = self.predict(image_path)
        return list(tag_scores.keys())


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


def process_images(
    input_dir: Path,
    output_dir: Path,
    threshold: float = 0.35,
    use_coreml: bool = False
) -> Tuple[int, int]:
    """
    画像を一括処理してタグ付け

    Args:
        input_dir: 入力ディレクトリ
        output_dir: 出力ディレクトリ
        threshold: タグの信頼度しきい値（デフォルト: 0.35）
        use_coreml: CoreML高速化を使用するか（デフォルト: False）

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
    print(f"信頼度しきい値: {threshold}")
    print("-" * 50)

    # WD14 Taggerを初期化
    tagger = WD14Tagger(threshold=threshold, use_coreml=use_coreml)

    success_count = 0
    skip_count = 0

    for idx, image_path in enumerate(image_files, start=1):
        try:
            # タグを予測
            tags = tagger.predict_tags_only(image_path)

            # タグをカンマ区切りで結合
            tag_string = ", ".join(tags)

            # 出力ファイル名（元の画像名を維持）
            output_image = output_dir / image_path.name
            output_txt = output_dir / f"{image_path.stem}.txt"

            # 画像をコピー
            shutil.copy2(image_path, output_image)

            # タグを.txtファイルに保存
            output_txt.write_text(tag_string, encoding="utf-8")

            print(f"✓ [{idx:02d}/{len(image_files)}] {image_path.name}")
            print(f"  タグ数: {len(tags)}")
            if tags:
                # 最初の5タグを表示
                preview_tags = ", ".join(tags[:5])
                if len(tags) > 5:
                    preview_tags += ", ..."
                print(f"  プレビュー: {preview_tags}")

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
        description='WD14 Taggerを使って画像に自動タグ付け',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python scripts/auto_caption.py \\
    --input projects/nasumiso_v1/2_processed \\
    --output projects/nasumiso_v1/3_tagged \\
    --threshold 0.35
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
        '--threshold',
        type=float,
        default=0.35,
        help='タグの信頼度しきい値（デフォルト: 0.35）'
    )

    parser.add_argument(
        '--use-coreml',
        action='store_true',
        help='CoreML高速化を有効にする（Mac Apple Silicon用、デフォルト: 無効）'
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
    success, skip = process_images(input_dir, output_dir, args.threshold, args.use_coreml)

    # 結果に応じて終了コードを設定
    if success == 0:
        sys.exit(1)
    elif skip > 0:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
