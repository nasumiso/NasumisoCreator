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

## 実装済み機能（続き）

### 5. LoRA学習（train_lora_nasutomo.ipynb）

**目的**: Google ColabでLoRA学習を実行し、なすみその画風を学習したモデルを作成する

**できること**:
- Google Colab上でkohya_ssを使用したLoRA学習
- Anything V5ベースモデルを使用した学習
- Google Drive経由でのデータセット読み込みと学習済みモデルの保存
- TensorBoardによる学習進捗の可視化
- カスタマイズ可能な学習パラメータ（エポック数、学習率、LoRA次元など）

**基本的な使い方**:
1. `projects/nasumiso_v1/3_tagged/` のタグ付き画像をGoogle Driveの `/MyDrive/NasuTomo/datasets/` にアップロード
2. Google Colabで `notebooks/train_lora_nasutomo.ipynb` を開く
3. セルを上から順に実行
   - Google Driveマウント
   - kohya_ssセットアップ
   - Anything V5モデルのダウンロード（初回のみ）
   - LoRA学習実行
4. **学習完了後のモデル配置**:
   - Google Drive `/MyDrive/NasuTomo/output/` から学習済みモデル（.safetensors）をダウンロード
   - ローカルの `projects/nasumiso_v1/lora_models/` に保存（バックアップ用）
   - `~/stable-diffusion-webui/models/Lora/` にコピー（画像生成用）

**いつ使う？**:
- タグ付けと共通タグ追加が完了した後
- 画像生成用のLoRAモデルを作成したい時
- 学習パラメータを調整して品質を改善したい時

**ポイント**:
- **ベースモデル**: Anything V5（SD 1.5ベース）を使用
- **学習時間**: 15枚・10エポックで約20〜30分（Google Colab無料版基準）
- **推奨パラメータ**:
  - `network_dim=64`, `network_alpha=32`: LoRAの次元設定
  - `max_train_epochs=10`: エポック数
  - `learning_rate=1e-4`: 学習率
  - `batch_size=1`, `gradient_accumulation_steps=2`: バッチサイズ
- **TensorBoard**: 学習進捗をリアルタイムで確認可能
- **データ転送**: Google Driveを介してデータセットと学習済みモデルを転送

**実装日**: 2025-11-02

---

### 6. 画像生成（StableDiffusion WebUI）

**目的**: 学習済みLoRAモデルを使用して、なすみその画風で画像を生成する

**できること**:
- AUTOMATIC1111 WebUIを使用した画像生成
- 学習済みLoRAモデルの適用
- プロンプトによる詳細な画像制御
- 生成パラメータの調整（サンプリング方法、ステップ数、CFG Scaleなど）
- 生成画像の保存と管理

**基本的な使い方**:
1. 学習済みLoRAモデルを `~/stable-diffusion-webui/models/Lora/` に配置
2. WebUIを起動:
   ```bash
   cd ~/stable-diffusion-webui
   ./webui.sh
   ```
3. ブラウザで `http://127.0.0.1:7860/` にアクセス
4. プロンプト入力エリアにプロンプトを記述
   - LoRA適用: `<lora:nasumiso_v1:1.0>` を追加
   - スタイルタグ: `nasumiso_style` を追加
5. 「Generate」ボタンで画像生成
6. 生成画像は `~/stable-diffusion-webui/outputs/` に保存される

**いつ使う？**:
- LoRA学習が完了した後
- なすみその画風で新しいイラストを生成したい時
- プロンプトやパラメータを調整して品質を確認したい時

**ポイント**:
- **実行環境**: Mac（M1チップ）対応
- **LoRA適用方法**: プロンプトに `<lora:モデル名:強度>` を記述（強度は0.0〜1.0）
- **推奨設定**:
  - Sampling method: DPM++ 2M Karras
  - Sampling steps: 20〜30
  - CFG Scale: 7〜9
  - 解像度: 512x512（学習時と同じサイズ推奨）
- **スタイル再現**: `nasumiso_style` タグを含めることで画風の再現性が向上
- **起動時間**: 初回起動は数分かかる場合あり（モデル読み込み）

**実装日**: 2025-11-02（WebUI設置）

---

## 未実装機能

### 7. データセット整形（organize_dataset.py）

**目的**: kohya_ss形式でデータセットを整形する

**ステータス**: 未実装（現在は手動でGoogle Driveにアップロード）

---

## 機能一覧チェックリスト

### データ前処理
- [x] 画像リネーム・リサイズ（prepare_images.py）
- [x] 自動タグ付け（auto_caption.py）
- [x] 共通タグ一括追加（add_common_tag.py）
- [x] 日本語タグ生成（generate_jp_tags.py）
- [ ] データセット整形（organize_dataset.py）※現在は手動でGoogle Driveアップロード

### LoRA学習
- [x] Google Colab学習ノートブック（train_lora_nasutomo.ipynb）
- [x] 学習パラメータ設定（ノートブック内に実装）

### 画像生成
- [x] StableDiffusion WebUI設置（`~/stable-diffusion-webui/`）
- [x] LoRA適用による画像生成
- [ ] プロンプトテンプレート
- [ ] 生成ログ管理

---

## 典型的な使い方の流れ

### ステップ1〜3: 画像準備からタグ付けまで（Mac環境）

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
```

### ステップ4: Google Driveアップロード

```bash
# 3_taggedフォルダの画像と.txtファイルを
# Google Driveの /MyDrive/NasuTomo/datasets/ にアップロード
# （手動またはGoogle Drive デスクトップアプリ使用）
```

### ステップ5: LoRA学習（Google Colab）

1. Google Colabで `notebooks/train_lora_nasutomo.ipynb` を開く
2. セルを上から順に実行
3. 学習完了（約20〜30分）

### ステップ6: モデルダウンロードと配置

```bash
# 1. Google Driveから学習済みモデルをダウンロード
# /MyDrive/NasuTomo/output/nasumiso_v1.safetensors を
# ローカルの projects/nasumiso_v1/lora_models/ に保存

# 2. 画像生成用にコピー
cp projects/nasumiso_v1/lora_models/nasumiso_v1.safetensors \
   ~/stable-diffusion-webui/models/Lora/
```

### ステップ7: 画像生成（Mac環境）

```bash
# 1. WebUIを起動
cd ~/stable-diffusion-webui
./webui.sh

# 2. ブラウザで http://127.0.0.1:7860/ にアクセス

# 3. プロンプトに以下を含める:
#    <lora:nasumiso_v1:1.0>, nasumiso_style, [その他のプロンプト]

# 4. 生成画像は ~/stable-diffusion-webui/outputs/ に保存される
```

### ステップ8: 品質チェックと再学習

生成画像を確認し、必要に応じてパラメータ調整や追加学習を実施
```

---

## 更新履歴

| 日付 | 機能 | 説明 |
|------|------|------|
| 2025-10-18 | prepare_images.py | 画像前処理機能を実装 |
| 2025-10-19 | auto_caption.py | 自動タグ付け機能を実装 |
| 2025-10-19 | add_common_tag.py | 共通タグ一括追加機能を実装 |
| 2025-10-19 | generate_jp_tags.py | 日本語タグ生成機能を実装 |
| 2025-11-02 | train_lora_nasutomo.ipynb | Google Colab用LoRA学習ノートブック作成 |
| 2025-11-02 | StableDiffusion WebUI | Mac環境にWebUI設置、画像生成環境構築 |
| 2025-11-03 | Windows環境セットアップ | Windows向けセットアップスクリプトとドキュメント追加 |

---

## Windows環境向けセットアップ

### 7. Windows環境向けセットアップ（setup_windows.bat / ドキュメント）

**目的**: なすみそさんがWindows環境でStable Diffusion WebUIをセットアップし、画像生成を実行できるようにする

**できること**:
- Python/Gitのインストール確認とエラーメッセージ表示
- Stable Diffusion WebUIの自動クローン
- デスクトップショートカットの自動作成
- 詳細なセットアップ手順とトラブルシューティング
- プロンプトの書き方ガイド（初心者向け）

**セットアップスクリプト**:
- `setup/setup_windows.bat`: WebUIの自動セットアップ
- `setup/create_shortcut.bat`: デスクトップショートカット作成

**ドキュメント**:
- `docs/setup_windows.md`: セットアップ手順（前提条件、インストール、トラブルシューティング）
- `docs/quickstart_nasumiso.md`: なすみそさん向けクイックスタート（WebUIの使い方、プロンプトの書き方、FAQ）
- `docs/model_download.md`: モデルファイルのダウンロードと配置方法

**基本的な使い方**:

1. **セットアップスクリプト実行** (Windows):
   - `setup/setup_windows.bat` をダブルクリック
   - Python/Gitがインストールされているか自動チェック
   - Stable Diffusion WebUIを `%USERPROFILE%\Documents\stable-diffusion-webui\` に自動クローン

2. **モデルファイル配置**:
   - Google Driveから `anything-v5.safetensors` と `nasumiso_v1.safetensors` をダウンロード
   - それぞれ指定フォルダに配置（ドキュメント参照）

3. **WebUI起動**:
   - `webui-user.bat` をダブルクリック（またはデスクトップショートカット使用）
   - ブラウザで `http://127.0.0.1:7860/` にアクセス

4. **画像生成**:
   - プロンプト例: `<lora:nasumiso_v1:1.0>, nasumiso_style, 1girl, solo, smile`
   - 詳細は `docs/quickstart_nasumiso.md` 参照

**いつ使う？**:
- なすみそさんがWindows環境で初めてセットアップする時
- 環境を再構築する時
- トラブル時の参照ドキュメントとして

**ポイント**:
- **LoRAとベースモデルの関係**: LoRAモデルは単体では動作せず、必ずベースモデル（anything-v5.safetensors）が必要
- **学習時と推論時のベースモデル統一**: 学習時に使用したベースモデルと同じものを推論時も使用することで、画風の再現度が向上
- **Git管理方針**: スクリプトとドキュメントのみGit管理、Python本体やWebUI本体は管理対象外
- **モデルファイル共有**: 大容量のためGit管理せず、Google Drive等で別途共有
- **イラストレーター向け設計**: 技術用語を避け、わかりやすい表現と豊富なFAQを提供

**実装日**: 2025-11-03

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
