# 開発ノート

このファイルは月次セクションで管理されます。月末に当月セクションを折りたたみ、重要な情報のみ残します。

---

## 2025-10 (当月)

### 2025-10-18: REQ-001 画像管理 完了
- `scripts/prepare_images.py`を実装し、画像前処理機能を完了
- 詳細は`completed/REQ-001/notes.md`を参照

### 2025-10-19: REQ-002 自動タグ付け 完了

#### 実装完了
- `scripts/auto_caption.py`を実装し、WD14 Taggerによる自動タグ付けを完了
- ONNX Runtime方式で実装（transformers非対応のため）
- sigmoid関数の誤適用問題を発見・修正（モデル出力が既に確率値だった）

#### 画像正規化問題の発見と修正
**問題**: 自動生成されたタグが画像内容と一致しない（例: カラー画像に`monochrome`, `no_humans`など）

**原因**: 画像の正規化方法が間違っていた
- 実装: 0-1正規化（`/ 255.0`）を適用していた
- 正解: WD14 Tagger v2は0-255の範囲を期待

**修正**: `_preprocess_image`メソッドから正規化処理を削除

**結果**: 正しいタグが生成されるようになった
- 修正前: `black_background, monochrome, no_humans` など（誤り）
- 修正後: `1boy, male_focus, eating, food` など（正しい）

#### タグ管理ワークフローの構築
**追加スクリプト**:
1. `scripts/add_common_tag.py` - 共通タグ（nasumiso_styleなど）の一括追加
2. `scripts/generate_jp_tags.py` - 日本語確認用タグファイル生成

**Git管理体制の確立**:
- `.gitignore`を更新してタグファイル（.txt）のみGit管理対象に
- 画像ファイル（.png）はプライバシー保護のため除外
- タグの手動修正履歴をコミットで追跡可能に

**実施した初期設定**:
- 全15枚に`nasumiso_style`タグを追加（画風学習のため）
- 日本語タグファイル（_jp.txt）を生成（イラストレーター報告用）

**今後の流れ**: 手動でタグレビュー → 誤タグ削除 → Gitコミット

技術的な詳細は`.claude/spec/implementation.md`を参照

---

## 完了した要件の作業ログについて

完了した要件の作業ログは `completed/REQ-XXX/notes.md` に移動されています。

---

## Tips (常時参照)

### Python環境
- **仮想環境**: `.venv`ディレクトリで管理
- **有効化**: `source .venv/bin/activate` (Mac/Linux)
- **無効化**: `deactivate`
- **依存関係インストール**: `pip install -r requirements.txt` (venv有効化後)
- **Python バージョン**: Python 3.9.6

### 画像処理
- **Pillow推奨設定**:
  - リサンプリング: `Image.LANCZOS`（高品質）
  - 保存形式: PNG（ロスレス）
  - 最適化オプション: `optimize=True`で圧縮率向上
- **アスペクト比調整**:
  - 中央クロップ: キャラクター中心を保持
  - パディング: 背景が重要な場合（今回は未使用）

### コマンド一覧
```bash
# 仮想環境の有効化
source .venv/bin/activate

# 画像前処理（リサイズ・リネーム）
python scripts/prepare_images.py \
  --input projects/nasumiso_v1/1_raw_images \
  --output projects/nasumiso_v1/2_processed \
  --size 512

# 自動タグ付け（WD14 Tagger）
python scripts/auto_caption.py \
  --input projects/nasumiso_v1/2_processed \
  --output projects/nasumiso_v1/3_tagged \
  --threshold 0.35

# 共通タグの一括追加
python scripts/add_common_tag.py \
  --input projects/nasumiso_v1/3_tagged \
  --tag "nasumiso_style" \
  --exclude-jp

# 日本語タグファイル生成（確認用）
python scripts/generate_jp_tags.py \
  --input projects/nasumiso_v1/3_tagged

# 依存関係インストール（venv有効化後）
pip install -r requirements.txt

# 画像サイズ確認
file projects/nasumiso_v1/2_processed/img001.png

# 仮想環境の無効化
deactivate
```

### Git操作
- **ブランチ作成**: `git checkout -b feature/xxx`
- **ステータス確認**: `git status`
- **コミット**: 開発者の明示的指示後のみ
- **差分確認**: `git diff <file>` または `git diff`
- **履歴確認**: `git log --oneline -5`

### タグ管理のベストプラクティス
- **自動タグ付け後の流れ**:
  1. 自動タグ付け実行 → Gitコミット（自動生成版）
  2. 共通タグ追加（nasumiso_styleなど） → Gitコミット
  3. 手動でタグレビュー・修正 → Gitコミット（修正版）
  4. 差分で何を変更したか確認可能
- **画像正規化**: WD14 Tagger v2は0-255の範囲を期待（0-1正規化は不要）
- **日本語タグ**: イラストレーター確認用、Git管理不要（_jp.txtは自動生成可能）
- **nasumiso_style**: 全画像に追加することで画風を学習させる

### デバッグ方法
- **画像処理エラー**: PIL.Image.open()でファイル破損をチェック
- **パス問題**: Pathlibを使用して絶対パス・相対パスを統一
- **エンコーディング**: Python3ファイルは`# -*- coding: utf-8 -*-`を追加

---

## 使い方

### 月次管理
月末に以下を実施：
1. 当月セクション（`## YYYY-MM (当月)`）を前月セクション（`## YYYY-MM`）に改名
2. 重要な情報のみ残し、詳細は折りたたむ
3. 新しい当月セクション（`## YYYY-MM (当月)`）を作成

### 作業ログの記録
- 実装中に気づいた点、解決した問題などを随時記録
- 日付とタイトルを付けて整理

### Tips セクション
- プロジェクト全体で役立つ技術メモを蓄積
- カテゴリ別に整理して検索しやすくする
