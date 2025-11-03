# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

**NasumisoCreator**は、イラストレーター「なすみそ」の画風を学習し、LoRAモデルとして再現・応用するアシスタントツールです。

- **ステータス**: フェーズ1（MVP）完了
- **技術スタック**: Python, Google Colab, kohya_ss, Stable Diffusion (Anything V5), AUTOMATIC1111 WebUI
- **開発環境**: MacBook Air M1

## 8ステップのワークフロー

1. **画像収集**: なすみそから画像を受領 → `projects/nasumiso_v1/1_raw_images/`
2. **画像処理**: リネーム＋512x512リサイズ → `projects/nasumiso_v1/2_processed/`
3. **自動タグ付け**: WD14 Taggerで`.txt`生成 → `projects/nasumiso_v1/3_tagged/`
4. **Google Driveアップロード**: タグ付き画像をGoogle Driveにアップロード（Colab学習用）
5. **学習実行**: Google Colabで`train_lora_nasutomo.ipynb`を使用してLoRA学習
6. **モデルダウンロードと配置**: Google Driveから.safetensorsをDL → `projects/nasumiso_v1/lora_models/` と `~/stable-diffusion-webui/models/Lora/` に配置
7. **画像生成**: Mac環境のStableDiffusion WebUI (`~/stable-diffusion-webui/`) でテスト生成
8. **品質チェックと再学習**: フィードバックに基づき改善

## 開発ワークフロー（6ステップ）

1. **作業指示** → 2. **作業計画** → 3. **計画確認** → 4. **実装** → 5. **テスト** → 6. **仕様反映と完了処理**

詳細: [.claude/workflow.md](.claude/workflow.md)

## 作業開始前に必ず実行すること

1. [.claude/README.md](.claude/README.md) でプロジェクトガイドを確認
2. [.claude/workflow.md](.claude/workflow.md) でワークフロー詳細を理解
3. [.claude/requirements.md](.claude/requirements.md) で現在の作業指示を確認
4. [.claude/work-plan.md](.claude/work-plan.md) で進行中のタスクがあるか確認
5. 新規作業の場合：実装前に必ず`work-plan.md`に計画を記述する
6. 実装完了後：`spec/spec.md`と`spec/reference.md`に仕様を記録する

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

### 仮想環境のセットアップ

```bash
# 仮想環境の作成
python3 -m venv .venv

# 仮想環境の有効化
source .venv/bin/activate  # Mac/Linux

# 依存関係のインストール
pip install -r requirements.txt
```

## コマンド

### 画像前処理ワークフロー（Mac環境）

```bash
# 仮想環境を有効化
source .venv/bin/activate

# 1. 画像前処理（リネーム・リサイズ）
python scripts/prepare_images.py \
  --input projects/nasumiso_v1/1_raw_images \
  --output projects/nasumiso_v1/2_processed \
  --size 512

# 2. 自動タグ付け（WD14 Tagger v2）
python scripts/auto_caption.py \
  --input projects/nasumiso_v1/2_processed \
  --output projects/nasumiso_v1/3_tagged \
  --threshold 0.35

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

1. Google Colabで `notebooks/train_lora_nasutomo.ipynb` を開く
2. セルを上から順に実行
3. 学習完了後、`/MyDrive/NasuTomo/output/` から.safetensorsファイルをダウンロード
4. `projects/nasumiso_v1/lora_models/` に保存

### 画像生成（Mac環境）

```bash
# WebUIを起動
cd ~/stable-diffusion-webui
./webui.sh

# ブラウザで http://127.0.0.1:7860/ にアクセス
# プロンプト: <lora:nasumiso_v1:1.0>, nasumiso_style, [その他のプロンプト]
```

## 参照ドキュメント

- [.claude/README.md](.claude/README.md) - 開発ガイド
- [.claude/workflow.md](.claude/workflow.md) - ワークフロー詳細
- [.claude/spec/overview.md](.claude/spec/overview.md) - プロジェクト概要
- [.claude/spec/spec.md](.claude/spec/spec.md) - 実装済み機能の使い方（ユーザー向け）
- [.claude/spec/reference.md](.claude/spec/reference.md) - 技術詳細・API仕様（開発者向け）
- [.claude/KNOWLEDGE.md](.claude/KNOWLEDGE.md) - プロジェクト全体の知見・ノウハウ
