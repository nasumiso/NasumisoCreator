# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

**NasumisoCreator**は、イラストレーター「なすみそ」の画風を学習し、LoRAモデルとして再現・応用するアシスタントツールです。

- **ステータス**: フェーズ1（MVP）完了
- **技術スタック**: Python, Google Colab, kohya_ss, Stable Diffusion (Anything V5), AUTOMATIC1111 WebUI
- **開発環境**: MacBook Air M1

## アーキテクチャ概要

本プロジェクトは3つの実行環境に分散したパイプライン構成です：

1. **Mac環境（ローカル）**: 画像前処理スクリプト（`scripts/`）で画像のリサイズ・リネーム・タグ付けを実行
2. **Google Colab（クラウド）**: GPU環境でLoRA学習（`notebooks/train_lora_nasutomo.ipynb`）を実行
3. **Mac環境（AUTOMATIC1111 WebUI）**: 学習済みLoRAモデルを使った画像生成（`~/stable-diffusion-webui/`、このリポジトリ外）

データフローは `1_raw_images/` → `2_processed/` → `3_tagged/` → Google Drive → Colab学習 → `lora_models/` → WebUI という単方向パイプラインです。

## 開発ワークフロー

本プロジェクトは6ステップの開発サイクルで進行します：

1. **作業指示** → 2. **作業計画** → 3. **計画確認** → 4. **実装** → 5. **テスト** → 6. **仕様反映と完了処理**

### 作業開始前の必須確認事項

1. [.claude/workflow.md](.claude/workflow.md) でワークフロー詳細を理解
2. [.claude/requirements.md](.claude/requirements.md) で現在の作業指示を確認
3. [.claude/work-plan.md](.claude/work-plan.md) で進行中のタスクがあるか確認
4. 新規作業時：実装前に必ず`work-plan.md`に計画を記述
5. 実装完了後：`spec/spec.md`と`spec/reference.md`に仕様を記録

## プロジェクト構造

```
NasumisoCreator/
├── .claude/              # 開発管理ドキュメント
│   ├── README.md        # クイックリファレンス
│   ├── workflow.md      # ワークフロー詳細
│   ├── spec/            # 仕様書
│   └── completed/       # 完了した要件
├── projects/            # プロジェクトデータ
│   └── nasumiso_v1/     # なすみそLoRAプロジェクト
├── scripts/             # Python前処理スクリプト
├── notebooks/           # Colab学習ノートブック
└── docs/                # ドキュメント
```

**注**: 画像生成環境は別ディレクトリ `~/stable-diffusion-webui/` に配置（Mac環境）

## セットアップ

```bash
# 仮想環境の作成と有効化
python3 -m venv .venv
source .venv/bin/activate

# 依存関係のインストール
pip install -r requirements.txt
```

## コマンドリファレンス

### 画像前処理パイプライン（Mac環境）

```bash
# 仮想環境を有効化
source .venv/bin/activate

# 1. リネーム・リサイズ（512x512）
python scripts/prepare_images.py \
  --input projects/nasumiso_v1/1_raw_images \
  --output projects/nasumiso_v1/2_processed \
  --size 512

# 2. WD14 Tagger v2で自動タグ付け
python scripts/auto_caption.py \
  --input projects/nasumiso_v1/2_processed \
  --output projects/nasumiso_v1/3_tagged \
  --threshold 0.35

# オプション: CoreML高速化（Apple Silicon専用、小規模バッチでは逆に遅い場合あり）
python scripts/auto_caption.py \
  --input projects/nasumiso_v1/2_processed \
  --output projects/nasumiso_v1/3_tagged \
  --threshold 0.35 \
  --use-coreml

# 3. 共通タグ追加（画風学習用）
python scripts/add_common_tag.py \
  --input projects/nasumiso_v1/3_tagged \
  --tag "nasumiso_style" \
  --exclude-jp

# 4. 日本語タグ生成（確認用）
python scripts/generate_jp_tags.py \
  --input projects/nasumiso_v1/3_tagged
```

### LoRA学習（Google Colab）

1. `notebooks/train_lora_nasutomo.ipynb` をColabで開く
2. Google Driveに `3_tagged/` の内容をアップロード
3. セルを順に実行（GPU環境で学習）
4. `/MyDrive/NasuTomo/output/` から.safetensorsをダウンロード
5. `projects/nasumiso_v1/lora_models/` と `~/stable-diffusion-webui/models/Lora/` に配置

### 画像生成（AUTOMATIC1111 WebUI）

```bash
cd ~/stable-diffusion-webui
./webui.sh
# http://127.0.0.1:7860/ でアクセス
# プロンプト例: <lora:nasumiso_v1:1.0>, nasumiso_style, 1girl, solo
```

## 参照ドキュメント

- [.claude/README.md](.claude/README.md) - 開発ガイド
- [.claude/workflow.md](.claude/workflow.md) - ワークフロー詳細
- [.claude/spec/overview.md](.claude/spec/overview.md) - プロジェクト概要
- [.claude/spec/spec.md](.claude/spec/spec.md) - 実装済み機能の使い方（ユーザー向け）
- [.claude/spec/reference.md](.claude/spec/reference.md) - 技術詳細・API仕様（開発者向け）
- [.claude/KNOWLEDGE.md](.claude/KNOWLEDGE.md) - プロジェクト全体の知見・ノウハウ
