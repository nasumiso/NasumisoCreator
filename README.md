# なすみそクリエイター (NasumisoCreator)

イラストレーター「なすみそ」の画風を学習し、LoRAモデルとして再現・応用するアシスタントツール

## プロジェクト概要

- **開発者**: こすうけ
- **イラストレーター**: なすみそ
- **目的**: LoRA学習による画風の再現とAI共創
- **技術**: Python, Google Colab, kohya_ss, Stable Diffusion

## ディレクトリ構造

- `projects/` - プロジェクトごとのデータ管理
- `scripts/` - Python前処理スクリプト
- `notebooks/` - Colab学習ノートブック
- `outputs/` - 生成結果・プロンプト
- `docs/` - ドキュメント
- `config/` - 設定ファイル
- `.claude/` - Claude Code管理ファイル

## 詳細ドキュメント

- [プロジェクト概要](./.claude/spec/overview.md) - 背景、目的、アーキテクチャ
- [機能仕様](./.claude/spec/spec.md) - 実装済み機能の使い方（ユーザー向け）
- [技術リファレンス](./.claude/spec/reference.md) - 技術詳細・API仕様（開発者向け）
- [要件定義書](./.claude/spec/original/要件定義書.md) - MVP要件定義
- [開発手順書](./.claude/spec/original/開発手順書.md) - Mac環境向け学習手順

## セットアップ

### 1. Python仮想環境の作成

```bash
python3 -m venv .venv
source .venv/bin/activate  # Mac/Linux
# または
.venv\Scripts\activate  # Windows
```

### 2. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 3. スクリプトの実行

```bash
# 画像前処理（リサイズ・リネーム）
python scripts/prepare_images.py \
  --input projects/nasumiso_v1/1_raw_images \
  --output projects/nasumiso_v1/2_processed \
  --size 512
```

## ステータス

現在: 初期開発段階（画像前処理スクリプト実装済み）
