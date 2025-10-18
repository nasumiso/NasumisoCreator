# 開発ノート

このファイルは月次セクションで管理されます。月末に当月セクションを折りたたみ、重要な情報のみ残します。

---

## 2025-10 (当月)

### 2025-10-18: REQ-001 画像管理 完了
- `scripts/prepare_images.py`を実装し、画像前処理機能を完了
- 詳細は`completed/REQ-001/notes.md`を参照

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
