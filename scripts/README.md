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

### 2. `auto_caption.py` （未実装）
- **機能**: WD14 Taggerによる自動タグ付け
- **入力**: `projects/*/2_processed/`
- **出力**: `projects/*/3_tagged/`

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
