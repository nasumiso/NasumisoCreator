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

## 使い方

### Gradio WebUI（推奨）

GUI で簡単に操作できるWebアプリケーションを提供しています。

#### Mac/Linux での起動

```bash
./start_nasumiso_trainer.sh
```

または

```bash
source .venv/bin/activate
python app.py
```

#### アクセス

ブラウザで以下のURLにアクセスしてください:
```
http://127.0.0.1:7861
```

#### 機能

**タブ1: 画像準備**
- 画像のリサイズ（512x512）
- 自動タグ付け（WD14 Tagger）
- 共通タグ追加（nasumiso_style）
- 全処理を一括実行

**タブ2: タグ編集**
- 画像一覧表示
- タグの表示・編集・保存
- 固有タグの一括追加（将来実装予定）

**タブ3: 学習・モデル管理**
- Google Drive連携（将来実装予定）
- Google Colab学習リンク
- モデルダウンロード（将来実装予定）
- Stable Diffusion WebUIへのモデル配置

**タブ4: 設定**
- Stable Diffusion WebUIパスの設定
- 学習モードの設定（colab/local）
- 設定の保存・読み込み

### コマンドラインスクリプト（従来の方法）

```bash
# 画像前処理（リサイズ・リネーム）
python scripts/prepare_images.py \
  --input projects/nasumiso_v1/1_raw_images \
  --output projects/nasumiso_v1/2_processed \
  --size 512

# 自動タグ付け
python scripts/auto_caption.py \
  --input projects/nasumiso_v1/2_processed \
  --output projects/nasumiso_v1/3_tagged \
  --threshold 0.35

# 共通タグ追加
python scripts/add_common_tag.py \
  --input projects/nasumiso_v1/3_tagged \
  --tag "nasumiso_style" \
  --exclude-jp
```

## 設定ファイル

`config.json.example` をコピーして `config.json` を作成し、環境に合わせて編集してください。

```bash
cp config.json.example config.json
```

主な設定項目:
- `sd_webui_path`: Stable Diffusion WebUIのLoRAモデルパス
- `training_mode`: 学習モード（colab または local）
- 各ディレクトリパス

## トラブルシューティング

### Gradioがインストールされていない

```bash
source .venv/bin/activate
pip install gradio
```

### ポート7861が使用中

他のアプリケーションがポート7861を使用している場合、`app.py`の以下の行を編集してポート番号を変更してください:

```python
app.launch(
    server_port=7861,  # ← この番号を変更（例: 7862）
    ...
)
```

### Stable Diffusion WebUIパスが見つからない

WebUIの「設定」タブでパスを確認・設定してください。

## ステータス

**フェーズ1（Mac環境）**: 実装完了
- Gradio WebUI実装
- タブ1: 画像準備機能（リサイズ・自動タグ付け・共通タグ追加）
- タブ2: タグ編集機能（基本実装）
- タブ3: 学習・モデル管理（スタブ実装）
- タブ4: 設定機能

**今後の予定**:
- Google Drive API連携（タブ3）
- タグ編集のチェックボックス形式複数選択
- Windows環境対応
