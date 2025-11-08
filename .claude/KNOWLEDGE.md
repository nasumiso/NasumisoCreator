# ナレッジベース

このファイルは、プロジェクト全体を通して得られた気づき・ノウハウを蓄積します。
REQ固有ではなく、プロジェクト横断で役立つ知見を記録してください。

---

## Python環境

### 仮想環境管理
- **仮想環境**: `.venv`ディレクトリで管理
- **有効化**: `source .venv/bin/activate` (Mac/Linux)
- **無効化**: `deactivate`
- **依存関係インストール**: `pip install -r requirements.txt` (venv有効化後)
- **Python バージョン**: Python 3.9.6

---

## 画像処理

### Pillow推奨設定
- **リサンプリング**: `Image.LANCZOS`（高品質）
- **保存形式**: PNG（ロスレス）
- **最適化オプション**: `optimize=True`で圧縮率向上

### アスペクト比調整
- **中央クロップ**: キャラクター中心を保持
- **パディング**: 背景が重要な場合（今回は未使用）

---

## WD14 Tagger

### 画像正規化の注意点
- **重要**: WD14 Tagger v2は0-255の範囲を期待
- **誤り**: 0-1正規化（`/ 255.0`）を適用すると誤ったタグが生成される
- **正解**: 正規化処理は不要（`Image.open()` → `resize()` → そのまま使用）

### 実装方式
- **ONNX Runtime方式**: transformers非対応のため、onnxruntimeを使用
- **sigmoid適用**: モデル出力が既に確率値の場合は不要（確認が必要）

---

## タグ管理

### タグ管理のベストプラクティス
1. **自動タグ付け実行** → Gitコミット（自動生成版）
2. **共通タグ追加**（nasumiso_styleなど） → Gitコミット
3. **手動でタグレビュー・修正** → Gitコミット（修正版）
4. 差分で何を変更したか確認可能

### 重要なタグ
- **nasumiso_style**: 全画像に追加することで画風を学習させる
- **日本語タグ**: イラストレーター確認用、Git管理不要（_jp.txtは自動生成可能）

---

## Git管理

### ブランチ戦略
- **メインブランチ**: `main`
- **フィーチャーブランチ**: `feature/xxx`
- **コミットメッセージ**: 日本語OK、説明的な内容にする

### プライバシー保護
- **画像ファイル**: `.gitignore`で除外（プライバシー保護）
- **タグファイル**: Git管理対象（手動修正履歴を追跡）

---

## デバッグ方法

### 画像処理エラー
- **ファイル破損チェック**: `PIL.Image.open()`でエラーが出るか確認
- **画像サイズ確認**: `file <image_path>` コマンドで確認

### パス問題
- **Pathlib使用**: 絶対パス・相対パスを統一
- **存在確認**: `Path.exists()` で事前チェック

### エンコーディング
- **Python3ファイル**: `# -*- coding: utf-8 -*-`を追加（特に日本語コメントが多い場合）

---

## コマンドリファレンス

### 画像前処理
```bash
# 仮想環境の有効化
source .venv/bin/activate

# 画像のリネーム・リサイズ
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

# 仮想環境の無効化
deactivate
```

### Git操作
```bash
# ステータス確認
git status

# 差分確認
git diff <file>
git diff

# 履歴確認
git log --oneline -5

# ブランチ作成
git checkout -b feature/xxx
```

---

## 設計パターン

### スクリプト構造
- **argparse**: コマンドライン引数の標準的な処理
- **Pathlib**: ファイルパス操作の推奨方法
- **型ヒント**: Python 3.9+で推奨（可読性向上）

### エラーハンドリング
- **ファイル操作**: try-exceptで例外をキャッチ
- **ログ出力**: print()で進捗を表示（ユーザーフレンドリー）
- **検証**: 処理前に入力ファイルの存在を確認

---

## ハードウェアアクセラレーション

### CoreML（Mac Apple Silicon）

**適用条件**:
- 大規模モデル（パラメータ数が多い）
- バッチ処理（複数データを一度に処理）
- CoreML完全対応モデル（100%のノードがCoreML実行可能）

**不向きな条件**:
- 小規模バッチ処理（1枚ずつ処理など）
- 軽量モデル（CPU実行でも十分高速）
- ハイブリッド実行（CoreMLとCPUの切り替えが頻発）

**実測例（WD14 Tagger、15枚処理）**:
- CPU専用: 16.05秒（1.070秒/枚）
- CoreML有効: 43.80秒（2.920秒/枚）
- 結果: CoreMLの方が2.7倍遅い

**理由**:
1. プロバイダー間の切り替えオーバーヘッド
2. 初期化コスト（小規模処理では毎回発生）
3. メモリコピー・データ変換コスト

**教訓**:
- **高速化技術は万能ではない**
- **実測なしの最適化は危険**
- ベンチマークを取ってから実装判断をすべき

### 実装方針

```python
# デフォルトは実用的な設定（CPU）
# オプションで高速化機能を提供（--use-coreml）
if use_coreml:
    # CoreMLが利用可能か事前チェック（クロスプラットフォーム対応）
    available = ort.get_available_providers()
    if 'CoreMLExecutionProvider' in available:
        providers = ['CoreMLExecutionProvider', 'CPUExecutionProvider']
    else:
        # CoreML未サポート環境では警告を表示してCPUにフォールバック
        print("警告: CoreMLExecutionProviderが利用できません。CPUで実行します。")
        providers = ['CPUExecutionProvider']
else:
    providers = ['CPUExecutionProvider']
```

**重要**: ONNX Runtimeは利用できないプロバイダーを指定すると`ValueError`を発生させる。
自動フォールバックは行われないため、`ort.get_available_providers()`で事前チェックが必須。

---

## Gradio WebUI

### 環境構築の重要な注意点
- **Gradio 4.44.1** は `huggingface-hub < 1.0` を要求
- `huggingface-hub >= 1.0` をインストールすると ImportError が発生
- requirements.txt に明記が必要

### 進捗表示のパターン
- `gr.Progress()` はリアルタイム更新される（プログレスバー）
- `Textbox` などの outputs は関数終了時に一度だけ更新される
- 複数ステップの場合は進捗率を分割して管理（例: ステップ1=0〜30%、ステップ2=30〜80%）

### クロスプラットフォーム対応
- フォルダを開く処理: `platform.system()` で分岐（Darwin/Windows/Linux）
- ファイルパス処理: Pathlib を使用してクロスプラットフォーム対応

---

## 今後の追加予定

- LoRA学習のパラメータチューニング知見
- 画像生成のプロンプトテンプレート
- データセット整形のベストプラクティス
- Google Drive API 統合の知見（フェーズ3実装後）
