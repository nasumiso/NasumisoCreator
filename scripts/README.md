# scripts/ - 前処理スクリプト

## 概要

LoRA学習前の画像処理を自動化するPythonスクリプト群

## スクリプト一覧

### 1. `prepare_images.py` ✅ 実装済み
- **機能**: 画像のリネーム・リサイズ
- **入力**: `projects/*/1_raw_images/`
- **出力**: `projects/*/2_processed/`
- **処理内容**:
  - 画像を512x512（またはカスタムサイズ）にリサイズ
  - アスペクト比を維持し、中央クロップで正方形化
  - 連番リネーム（img001.png, img002.png, ...）
  - PNG形式で高品質保存（LANCZOS リサンプリング）

**使用方法**:
```bash
python3 scripts/prepare_images.py \
  --input projects/nasumiso_v1/1_raw_images \
  --output projects/nasumiso_v1/2_processed \
  --size 512
```

**オプション**:
- `--input`: 入力ディレクトリのパス（必須）
- `--output`: 出力ディレクトリのパス（必須）
- `--size`: 出力画像サイズ（デフォルト: 512）

**動作確認済み**: 15枚の画像を正常に処理

---

### 2. `auto_caption.py` ✅ 実装済み
- **機能**: WD14 Taggerによる自動タグ付け
- **入力**: `projects/*/2_processed/`
- **出力**: `projects/*/3_tagged/`
- **処理内容**:
  - WD14 Tagger v2（SmilingWolf/wd-v1-4-moat-tagger-v2）を使用
  - ONNX Runtimeで推論を実行
  - 画像を448x448にリサイズ（アスペクト比維持+パディング）
  - 信頼度しきい値（デフォルト: 0.35）でタグをフィルタリング
  - Danbooru形式のタグをカンマ区切りで.txtファイルに出力
  - 画像も3_tagged/にコピー

**使用方法**:
```bash
python3 scripts/auto_caption.py \
  --input projects/nasumiso_v1/2_processed \
  --output projects/nasumiso_v1/3_tagged \
  --threshold 0.35
```

**オプション**:
- `--input`: 入力ディレクトリのパス（必須）
- `--output`: 出力ディレクトリのパス（必須）
- `--threshold`: タグの信頼度しきい値（デフォルト: 0.35）

**動作確認済み**: 15枚の画像に対し、各8-9個のタグを生成

**技術的な詳細**:
- モデル: SmilingWolf/wd-v1-4-moat-tagger-v2（Hugging Faceからダウンロード）
- 画像サイズ: 448x448（モデルの入力仕様）
- タグ数: 全9,083種類のDanbooruタグから選択
- 出力形式: `img001.txt` (画像名と同じベース名)

### 3. `organize_dataset.py` （未実装）
- **機能**: Colab学習用データセット整形
- **入力**: `projects/*/3_tagged/`
- **出力**: `projects/*/4_dataset/`

## 必要な依存関係

```bash
pip3 install -r requirements.txt
```

現在必要なパッケージ:
- Pillow >= 10.0.0 (画像処理)
- onnxruntime >= 1.15.0 (WD14 Tagger推論)
- numpy >= 1.24.0 (数値計算)
- pandas >= 2.0.0 (CSVタグリスト読み込み)
- huggingface-hub >= 0.16.0 (モデルダウンロード)
