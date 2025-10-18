# scripts/ - 前処理スクリプト

## 概要

LoRA学習前の画像処理を自動化するPythonスクリプト群

## スクリプト一覧（予定）

### 1. `prepare_images.py`
- **機能**: 画像のリネーム・リサイズ
- **入力**: `projects/*/1_raw_images/`
- **出力**: `projects/*/2_processed/`

### 2. `auto_caption.py`
- **機能**: WD14 Taggerによる自動タグ付け
- **入力**: `projects/*/2_processed/`
- **出力**: `projects/*/3_tagged/`

### 3. `organize_dataset.py`
- **機能**: Colab学習用データセット整形
- **入力**: `projects/*/3_tagged/`
- **出力**: `projects/*/4_dataset/`

## 使用方法

各スクリプトの詳細は実装後に追記します。
