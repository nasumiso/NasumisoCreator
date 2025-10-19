# なすみそクリエイター - 機能仕様

このファイルは、実装済み機能の仕様を記録します。

## このファイルについて

**目的**: 実装済み機能の「何ができるか」をユーザー視点で説明
**対象読者**: こすうけ（開発者）、なすみそ（イラストレーター）
**更新タイミング**: REQ完了時に、Claude Codeが該当機能の仕様を追記
**内容**: 機能の目的、使い方、使用例

**技術詳細は記録しません**。それらは以下を参照：
- 技術詳細・API仕様: [reference.md](./reference.md) - 開発者向け技術情報
- プロジェクト概要: [overview.md](./overview.md) - 背景、目的、アーキテクチャ
- 実装履歴: [completed/REQ-XXX/notes.md](../completed/) - 各要件の実装詳細
- プロジェクト知見: [KNOWLEDGE.md](../KNOWLEDGE.md) - 技術Tips、設計パターン

---

## 実装済み機能

### 1. 画像前処理（prepare_images.py）

**目的**: LoRA学習用に画像を整形する

**できること**:
- 画像を連番にリネーム（img001.png, img002.png, ...）
- 画像を512x512にリサイズ（アスペクト比を維持して中央切り抜き）
- 高品質な変換（LANCZOS方式）

**基本的な使い方**:
```bash
python scripts/prepare_images.py \
  --input projects/nasumiso_v1/1_raw_images \
  --output projects/nasumiso_v1/2_processed \
  --size 512
```

**いつ使う？**:
- なすみそから画像を受け取った直後
- LoRA学習の準備として最初に実行

**実装日**: 2025-10-18

---

### 2. 自動タグ付け（auto_caption.py）

**目的**: AIが画像の内容を自動でタグ付けする

**できること**:
- WD14 Tagger v2を使って画像の内容を分析
- Danbooruタグ形式で自動タグ生成（例: `1girl, long_hair, blue_eyes, ...`）
- タグファイル（.txt）を画像と同じ名前で生成
- **Mac（Apple Silicon）でCoreML高速化オプション対応**（デフォルト無効）

**基本的な使い方**:
```bash
python scripts/auto_caption.py \
  --input projects/nasumiso_v1/2_processed \
  --output projects/nasumiso_v1/3_tagged \
  --threshold 0.35
```

**いつ使う？**:
- 画像前処理の後
- 手動でタグを付ける前の下準備として

**ポイント**:
- しきい値（threshold）を下げるとタグが増える
- 推奨は0.35（精度と網羅性のバランスが良い）
- デフォルトはCPU実行（高速・安定）
- `--use-coreml`オプションでCoreML高速化を有効化可能（実験的機能）
  - 注意: 小規模バッチ処理ではCPUより遅くなる可能性あり

**実装日**: 2025-10-19
**CoreML対応**: 2025-10-19

---

### 3. 共通タグ一括追加（add_common_tag.py）

**目的**: 全画像に同じタグを一括で追加する

**できること**:
- 全てのタグファイルの先頭に指定したタグを追加
- 画風学習用の共通タグ（例: `nasumiso_style`）を簡単に設定

**基本的な使い方**:
```bash
python scripts/add_common_tag.py \
  --input projects/nasumiso_v1/3_tagged \
  --tag "nasumiso_style" \
  --exclude-jp
```

**いつ使う？**:
- 自動タグ付けの後
- 特定の画風・キャラクター・スタイルを学習させたい時

**ポイント**:
- `--exclude-jp` をつけると日本語タグファイル（_jp.txt）は除外される
- 学習用の重要なタグなので、忘れずに実行する

**実装日**: 2025-10-19

---

### 4. 日本語タグ生成（generate_jp_tags.py）

**目的**: イラストレーター確認用に日本語タグを生成する

**できること**:
- 英語タグを日本語に翻訳（例: `1girl` → `女性1人`）
- なすみそが内容を確認しやすくする

**基本的な使い方**:
```bash
python scripts/generate_jp_tags.py \
  --input projects/nasumiso_v1/3_tagged
```

**いつ使う？**:
- タグ付けが完了した後
- なすみそにタグ内容を確認してもらう時

**ポイント**:
- 日本語タグファイル（_jp.txt）はGit管理対象外
- 必要に応じて何度でも再生成可能
- 完全な翻訳ではなく、主要タグのみ対応

**実装日**: 2025-10-19

---

## 未実装機能

### 5. データセット整形（organize_dataset.py）

**目的**: kohya_ss形式でデータセットを整形する

**ステータス**: 未実装

---

### 6. LoRA学習（train_lora_sd15.ipynb）

**目的**: Google ColabでLoRA学習を実行する

**ステータス**: 未実装

---

## 機能一覧チェックリスト

### データ前処理
- [x] 画像リネーム・リサイズ（prepare_images.py）
- [x] 自動タグ付け（auto_caption.py）
- [x] 共通タグ一括追加（add_common_tag.py）
- [x] 日本語タグ生成（generate_jp_tags.py）
- [ ] データセット整形（organize_dataset.py）

### LoRA学習
- [ ] Google Colab学習ノートブック
- [ ] 学習パラメータ設定テンプレート

### 画像生成
- [ ] プロンプトテンプレート
- [ ] 生成ログ管理

---

## 典型的な使い方の流れ

### ステップ1〜4: 画像準備からデータセット作成まで

```bash
# 仮想環境を有効化
source .venv/bin/activate

# 1. 画像前処理（リネーム・リサイズ）
python scripts/prepare_images.py \
  --input projects/nasumiso_v1/1_raw_images \
  --output projects/nasumiso_v1/2_processed \
  --size 512

# 2. 自動タグ付け
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

# 5. データセット整形（未実装）
# python scripts/organize_dataset.py --project nasumiso_v1
```

### ステップ5: LoRA学習（Google Colab）

→ 未実装（将来的に`notebooks/train_lora_sd15.ipynb`で実行予定）

### ステップ6: 画像生成（Windows環境）

→ AUTOMATIC1111 WebUIで手動実行

---

## 更新履歴

| 日付 | 機能 | 説明 |
|------|------|------|
| 2025-10-18 | prepare_images.py | 画像前処理機能を実装 |
| 2025-10-19 | auto_caption.py | 自動タグ付け機能を実装 |
| 2025-10-19 | add_common_tag.py | 共通タグ一括追加機能を実装 |
| 2025-10-19 | generate_jp_tags.py | 日本語タグ生成機能を実装 |

---

## 使い方

### 仕様の追記（REQ完了時）

REQ完了時に、以下の情報を追記してください：

1. **目的**: この機能が何のためにあるか
2. **できること**: 機能の概要を箇条書き
3. **基本的な使い方**: 最も一般的なコマンド例
4. **いつ使う？**: 使用タイミング・シーン
5. **ポイント**: 注意点や便利な使い方
6. **実装日**: 実装完了日

### 新規機能カテゴリの追加

新しい機能カテゴリが必要な場合は、セクションを追加してください。
