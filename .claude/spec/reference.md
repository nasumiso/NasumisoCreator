# なすみそクリエイター - 技術リファレンス

このファイルは、実装済み機能の技術詳細を記録します。

## このファイルについて

**目的**: 開発者向けの技術仕様・API・パラメータ詳細を記録
**更新タイミング**: REQ完了時に、Claude Codeが該当機能の技術詳細を追記
**対象読者**: Claude Code、開発者（こすうけ）
**内容**: コマンド詳細、パラメータ仕様、処理フロー、技術制約

**ユーザー向け機能説明は記録しません**。それらは以下を参照：
- ユーザー向け機能仕様: [spec.md](./spec.md) - 「何ができるか」を説明
- プロジェクト概要: [overview.md](./overview.md) - 背景、目的、アーキテクチャ

---

## データ前処理スクリプト

### prepare_images.py - 画像前処理

**コマンド**:
```bash
python scripts/prepare_images.py \
  --input <入力ディレクトリ> \
  --output <出力ディレクトリ> \
  --size <サイズ>
```

**パラメータ詳細**:
| パラメータ | 型 | 必須 | デフォルト | 説明 |
|-----------|-----|------|-----------|------|
| `--input` | str | ✓ | - | 入力画像ディレクトリのパス |
| `--output` | str | ✓ | - | 出力ディレクトリのパス |
| `--size` | int | - | 512 | 出力画像サイズ（正方形の一辺のピクセル数） |

**処理フロー**:
1. **画像ファイル収集**
   - 対応形式: `.png`, `.jpg`, `.jpeg`（大文字小文字不問）
   - 再帰的なサブディレクトリ探索は行わない

2. **リネーム処理**
   - 連番形式: `img001.png`, `img002.png`, ...
   - ゼロパディング: 3桁（001-999）

3. **リサイズ処理**
   - アスペクト比維持: 短辺を目標サイズに合わせる
   - 中央クロップ: 長辺を中央から切り取り正方形化
   - リサンプリング: LANCZOS（高品質）

4. **出力処理**
   - 形式: PNG（ロスレス）
   - 最適化: `optimize=True`で圧縮効率向上
   - 出力ディレクトリが存在しない場合は自動作成

**技術仕様**:
- **ライブラリ**: Pillow (PIL)
- **色空間**: RGB
- **ビット深度**: 8bit
- **メタデータ**: 保持されない（EXIF情報は削除される）

**エラーハンドリング**:
- 入力ディレクトリが存在しない → エラー終了
- 画像が読み込めない → スキップして次へ
- 出力ディレクトリ作成失敗 → エラー終了

**実装済み**: 2025-10-18

---

### auto_caption.py - 自動タグ付け

**コマンド**:
```bash
python scripts/auto_caption.py \
  --input <入力ディレクトリ> \
  --output <出力ディレクトリ> \
  --threshold <しきい値>
```

**パラメータ詳細**:
| パラメータ | 型 | 必須 | デフォルト | 説明 |
|-----------|-----|------|-----------|------|
| `--input` | str | ✓ | - | 入力画像ディレクトリのパス |
| `--output` | str | ✓ | - | 出力ディレクトリのパス |
| `--threshold` | float | - | 0.35 | タグの信頼度しきい値（0.0-1.0） |
| `--use-coreml` | flag | - | False | CoreML高速化を有効にする（Mac Apple Silicon用） |

**処理フロー**:
1. **モデル読み込み**
   - モデル: `SmilingWolf/wd-v1-4-moat-tagger-v2`
   - 形式: ONNX Runtime
   - 自動ダウンロード: Hugging Face Hub経由

2. **画像前処理**
   - リサイズ: 448x448（アスペクト比維持）
   - パディング: 白色で正方形化
   - 正規化: **不要**（0-255の範囲をそのまま使用）
   - 色空間: RGB

3. **推論処理**
   - 入力形状: `[1, 3, 448, 448]` (NCHW形式)
   - 出力: 9,083個のタグに対する確率値
   - sigmoid適用: **不要**（モデル出力が既に確率値）

4. **タグ選択**
   - しきい値以上のタグのみ選択
   - Danbooru形式（アンダースコア区切り）
   - カンマ区切りで.txtファイルに保存

5. **ファイル出力**
   - 画像と.txtファイルを出力ディレクトリにコピー
   - ファイル名の対応関係を維持

**技術仕様**:
- **モデル**: WD14 Tagger v2 (wd-v1-4-moat-tagger-v2)
- **ランタイム**: ONNX Runtime (CoreMLExecutionProvider対応)
- **入力サイズ**: 448x448 (RGB)
- **タグ数**: 9,083種類のDanbooruタグ
- **推奨しきい値**: 0.35 (P=Rポイント: 0.3771)
- **ライブラリ**: `huggingface_hub`, `onnxruntime`, `Pillow`, `numpy`
- **高速化**: CoreMLExecutionProvider（Mac Apple Silicon対応）

**重要な技術的注意事項**:

1. **画像正規化は不要**
   - WD14 Tagger v2は0-255の範囲を期待
   - 0-1正規化すると誤ったタグが生成される

2. **sigmoid適用は不要**
   - モデル出力が既に確率値（0-1範囲）
   - 追加のsigmoid適用は不要

3. **transformersライブラリは非対応**
   - ONNX Runtimeでの推論が必須
   - `AutoModel.from_pretrained()`は使用不可

**CoreML高速化（2025-10-19追加、デフォルト無効）**:

`--use-coreml`オプションでCoreMLExecutionProviderを使用可能：
```python
# デフォルト（CPU専用）
providers = ['CPUExecutionProvider']

# --use-coreml 指定時（プロバイダー可用性チェック付き）
if use_coreml:
    available = ort.get_available_providers()
    if 'CoreMLExecutionProvider' in available:
        providers = ['CoreMLExecutionProvider', 'CPUExecutionProvider']
    else:
        # CoreML未サポート環境では警告してCPUにフォールバック
        print("警告: CoreMLExecutionProviderが利用できません。CPUで実行します。")
        providers = ['CPUExecutionProvider']

session = ort.InferenceSession(model_path, providers=providers)
```

- **対応環境**: Mac（Apple Silicon）
- **高速化デバイス**: Neural Engine
- **デフォルト**: 無効（CPU実行）
- **有効化方法**: `--use-coreml`フラグを指定
- **フォールバック**: CoreML利用不可時は警告表示してCPUで実行（事前チェック実装）
- **クロスプラットフォーム対応**: Linux/Windows環境でも安全に動作
- **ハイブリッド実行**: CoreML対応ノード（約74%）+ CPU非対応ノード（約26%）
- **プロバイダー確認**: `session.get_providers()` で実行時確認可能

**重要な実装ノート**:
ONNX Runtimeは利用できないプロバイダーを指定すると`ValueError`を発生させる。
自動フォールバックは行われないため、`ort.get_available_providers()`による事前チェックが必須。
これにより、CoreML非対応環境（Linux/Windows等）でも`--use-coreml`指定時にクラッシュせずCPUで実行できる。

**注意事項**:
- ベンチマークの結果、小規模バッチ処理（1枚ずつ）ではCPU専用より約2.7倍遅い
- 理由: ハイブリッド実行のオーバーヘッド、初期化コスト
- 大規模モデルや大量バッチ処理では効果がある可能性あり
- 現在のユースケースでは**CPU専用（デフォルト）を推奨**

**パフォーマンス**:
- **CPU推論**: 約1.07秒/画像（Mac M1基準、15枚テスト）
- **CoreML推論**: 約2.92秒/画像（Mac M1基準、15枚テスト、--use-coreml有効時）
- メモリ使用量: 約500MB（モデル読み込み時）

**ベンチマーク結果**（MacBook Air M1、15枚の画像）:
| モード | 総処理時間 | 平均処理時間/枚 |
|--------|-----------|----------------|
| CPU専用（デフォルト） | 16.05秒 | 1.070秒/枚 |
| CoreML有効 | 43.80秒 | 2.920秒/枚 |

**実装済み**: 2025-10-19
**CoreML対応**: 2025-10-19（オプション機能、デフォルト無効）

---

### add_common_tag.py - 共通タグ一括追加

**コマンド**:
```bash
python scripts/add_common_tag.py \
  --input <入力ディレクトリ> \
  --tag <追加するタグ> \
  [--exclude-jp]
```

**パラメータ詳細**:
| パラメータ | 型 | 必須 | デフォルト | 説明 |
|-----------|-----|------|-----------|------|
| `--input` | str | ✓ | - | タグ付き画像ディレクトリのパス |
| `--tag` | str | ✓ | - | 追加するタグ（Danbooru形式推奨） |
| `--exclude-jp` | bool | - | False | 日本語タグファイル（_jp.txt）を除外 |

**処理フロー**:
1. **ファイル収集**
   - 対象: `.txt`ファイル
   - 除外条件: `--exclude-jp`が指定された場合、`*_jp.txt`を除外

2. **タグ追加処理**
   - 各.txtファイルの**先頭**に指定タグを追加
   - 既存タグとの区切り: カンマ+スペース (`, `)
   - 元ファイルを上書き

3. **エンコーディング**
   - 読み書き: UTF-8
   - 改行コード: 保持

**技術仕様**:
- **ライブラリ**: 標準ライブラリのみ（`pathlib`, `argparse`）
- **エンコーディング**: UTF-8
- **バックアップ**: なし（上書き保存）

**使用例**:
```bash
# 全画像にnasumiso_styleタグを追加（日本語ファイルは除外）
python scripts/add_common_tag.py \
  --input projects/nasumiso_v1/3_tagged \
  --tag "nasumiso_style" \
  --exclude-jp
```

**Git管理との連携**:
- タグファイルはGit管理対象
- コミット推奨タイミング:
  1. 自動タグ付け実行後
  2. 共通タグ追加後
  3. 手動修正後

**実装済み**: 2025-10-19

---

### generate_jp_tags.py - 日本語タグ生成

**コマンド**:
```bash
python scripts/generate_jp_tags.py \
  --input <入力ディレクトリ>
```

**パラメータ詳細**:
| パラメータ | 型 | 必須 | デフォルト | 説明 |
|-----------|-----|------|-----------|------|
| `--input` | str | ✓ | - | タグ付き画像ディレクトリのパス |

**処理フロー**:
1. **ファイル収集**
   - 対象: `.txt`ファイル（`*_jp.txt`を除く）

2. **タグ変換処理**
   - 英語タグを日本語に変換（辞書マッピング）
   - 未登録タグ: そのまま残す（英語のまま）
   - 区切り文字: カンマ+スペース (`, `)

3. **ファイル出力**
   - 出力形式: `<画像名>_jp.txt`
   - エンコーディング: UTF-8

**技術仕様**:
- **翻訳方式**: 静的辞書マッピング（簡易的）
- **辞書**: スクリプト内に定義（主要タグのみ）
- **未対応タグ**: 英語のまま出力

**翻訳辞書の例**:
```python
TAG_TRANSLATION = {
    "1girl": "女性1人",
    "solo": "単独",
    "long_hair": "長い髪",
    "blue_eyes": "青い目",
    # ... 省略
}
```

**制限事項**:
- 完全な翻訳ではない（主要タグのみ対応）
- 機械翻訳は使用していない
- 翻訳精度は辞書の網羅性に依存

**Git管理**:
- 日本語タグファイル（`*_jp.txt`）は`.gitignore`で除外
- 必要に応じて再生成可能

**実装済み**: 2025-10-19

---

## データセット整形

### organize_dataset.py - データセット整形

**機能**: kohya_ss標準フォーマットでデータセットを整形する

**ステータス**: 未実装（現在は手動でGoogle Driveにアップロード）

**想定仕様**:
- 入力: `projects/nasumiso_v1/3_tagged/`
- 出力: Google Drive `/MyDrive/NasuTomo/datasets/`
- kohya_ss標準フォーマット:
  - `<繰り返し回数>_<プロジェクト名>/` ディレクトリ構造
  - 画像と.txtファイルを同じディレクトリに配置

---

## LoRA学習

### train_lora_nasutomo.ipynb - Google Colab用LoRA学習ノートブック

**機能**: Google ColabでLoRA学習を実行する

**ステータス**: 実装済み

**技術スタック**:
- **プラットフォーム**: Google Colab（GPU: T4/V100等、無料版/Colab Pro）
- **学習ツール**: kohya_ss (bmaltais/kohya_ss)
- **ベースモデル**: Anything V5 (anything-v5.safetensors, SD 1.5ベース)
- **出力形式**: `.safetensors`（fp16精度）

**処理フロー**:

1. **環境セットアップ**
   ```python
   # Google Driveマウント
   from google.colab import drive
   drive.mount('/content/drive')

   # kohya_ssクローン
   !git clone https://github.com/bmaltais/kohya_ss.git

   # セットアップ実行
   !./setup.sh
   !pip install voluptuous

   # Accelerate設定
   !accelerate config default
   ```

2. **ベースモデルダウンロード**
   ```bash
   # Anything V5をCivitaiからダウンロード
   wget -O anything-v5.safetensors "https://civitai.com/api/download/models/30163"
   # 保存先: /content/drive/MyDrive/NasuTomo/models/
   ```

3. **データセット配置**
   - 学習データ: `/content/drive/MyDrive/NasuTomo/datasets/`
   - 画像と.txtファイルをペアで配置

4. **LoRA学習実行**
   ```bash
   accelerate launch --num_cpu_threads_per_process=1 ./sd-scripts/train_network.py \
     --enable_bucket \
     --min_bucket_reso=256 \
     --max_bucket_reso=1024 \
     --pretrained_model_name_or_path="/content/drive/MyDrive/NasuTomo/models/anything-v5.safetensors" \
     --train_data_dir="/content/drive/MyDrive/NasuTomo/datasets" \
     --output_dir="/content/drive/MyDrive/NasuTomo/output" \
     --output_name="nasumiso_v1" \
     --resolution="512,512" \
     --network_module=networks.lora \
     --network_dim=64 \
     --network_alpha=32 \
     --train_batch_size=1 \
     --gradient_accumulation_steps=2 \
     --max_train_epochs=10 \
     --learning_rate=1e-4 \
     --lr_scheduler="cosine_with_restarts" \
     --lr_warmup_steps=100 \
     --optimizer_type="AdamW8bit" \
     --mixed_precision="fp16" \
     --save_precision="fp16" \
     --save_every_n_epochs=1 \
     --cache_latents \
     --cache_latents_to_disk \
     --gradient_checkpointing \
     --clip_skip=2 \
     --xformers \
     --save_model_as=safetensors \
     --logging_dir="/content/drive/MyDrive/NasuTomo/logs" \
     --log_with=tensorboard
   ```

**主要パラメータ詳細**:

| パラメータ | 値 | 説明 |
|-----------|-----|------|
| `--pretrained_model_name_or_path` | anything-v5.safetensors | ベースモデルのパス |
| `--train_data_dir` | /MyDrive/NasuTomo/datasets | 学習データディレクトリ |
| `--output_dir` | /MyDrive/NasuTomo/output | 出力ディレクトリ |
| `--output_name` | nasumiso_v1 | 出力ファイル名 |
| `--resolution` | 512,512 | 学習解像度 |
| `--network_dim` | 64 | LoRAのrank（次元数） |
| `--network_alpha` | 32 | LoRAのアルファ値（スケール調整） |
| `--train_batch_size` | 1 | バッチサイズ |
| `--gradient_accumulation_steps` | 2 | 勾配蓄積ステップ（実質バッチサイズ2） |
| `--max_train_epochs` | 10 | 最大エポック数 |
| `--learning_rate` | 1e-4 | 学習率 |
| `--lr_scheduler` | cosine_with_restarts | 学習率スケジューラ |
| `--optimizer_type` | AdamW8bit | オプティマイザ（8bit量子化） |
| `--mixed_precision` | fp16 | 混合精度学習 |
| `--save_precision` | fp16 | 保存精度 |
| `--save_every_n_epochs` | 1 | エポックごとに保存 |
| `--cache_latents` | flag | VAE潜在表現をキャッシュ（高速化） |
| `--cache_latents_to_disk` | flag | 潜在表現をディスクにキャッシュ |
| `--gradient_checkpointing` | flag | 勾配チェックポイント（メモリ節約） |
| `--clip_skip` | 2 | CLIPレイヤースキップ |
| `--xformers` | flag | xFormers（Attention高速化） |
| `--enable_bucket` | flag | バケット機能（アスペクト比維持） |
| `--min_bucket_reso` | 256 | 最小バケット解像度 |
| `--max_bucket_reso` | 1024 | 最大バケット解像度 |

**TensorBoard可視化**:
```python
%load_ext tensorboard
%tensorboard --logdir="/content/drive/MyDrive/NasuTomo/logs"
```

**出力ファイル**:
- 学習済みLoRAモデル: `/MyDrive/NasuTomo/output/nasumiso_v1.safetensors`
- エポックごとのチェックポイント: `nasumiso_v1-000001.safetensors`, `nasumiso_v1-000002.safetensors`, ...
- ログ: `/MyDrive/NasuTomo/logs/`

**パフォーマンス**:
- **学習時間**: 15枚・10エポックで約20〜30分（Google Colab無料版、T4 GPU基準）
- **メモリ使用量**: 約8〜10GB（GPU VRAM）
- **ディスク使用量**: 約50〜100MB/モデル（fp16精度）

**技術的注意事項**:
- Google Colab無料版は利用時間制限あり（連続12時間、1日最大使用量制限）
- セッション切断時の対策: Google Driveにデータを保存しているため、再実行可能
- ベースモデルは初回ダウンロード後、Google Driveに保存され再利用可能
- 学習データは `3_tagged` から手動でGoogle Driveにアップロード

**実装済み**: 2025-11-02

---

## 画像生成

### StableDiffusion WebUI - Mac環境での画像生成

**機能**: AUTOMATIC1111 WebUIを使用した画像生成

**ステータス**: 実装済み

**技術スタック**:
- **WebUI**: AUTOMATIC1111/stable-diffusion-webui
- **実行環境**: Mac（M1チップ）
- **設置場所**: `~/stable-diffusion-webui/`
- **アクセスURL**: `http://127.0.0.1:7860/`

**起動方法**:
```bash
cd ~/stable-diffusion-webui
./webui.sh
```

**技術仕様**:
- **バックエンド**: PyTorch（MPS backend for Mac）
- **対応モデル**: Stable Diffusion 1.5, SDXL
- **LoRA配置先**: `~/stable-diffusion-webui/models/Lora/`
- **出力ディレクトリ**: `~/stable-diffusion-webui/outputs/txt2img-images/`

**LoRA適用方法**:
```
プロンプト: <lora:nasumiso_v1:1.0>, nasumiso_style, 1girl, ...
```
- `<lora:モデル名:強度>` 形式で指定
- 強度は0.0〜1.0（推奨: 0.7〜1.0）
- モデル名は拡張子なし

**推奨生成パラメータ**:
| パラメータ | 推奨値 | 説明 |
|-----------|--------|------|
| Sampling method | DPM++ 2M Karras | サンプリング方法 |
| Sampling steps | 20〜30 | サンプリングステップ数 |
| CFG Scale | 7〜9 | プロンプト遵守度 |
| Width x Height | 512 x 512 | 解像度（学習時と同じ） |
| Batch count | 1〜4 | 生成枚数 |
| Seed | -1（ランダム） | シード値 |

**処理フロー**:
1. WebUI起動（初回はモデルダウンロード・セットアップ）
2. LoRAモデルを `models/Lora/` に配置
3. プロンプト入力（LoRA指定含む）
4. パラメータ調整
5. Generate実行
6. 生成画像は自動保存（`outputs/txt2img-images/日付/`）

**パフォーマンス**:
- **生成時間**: 512x512で約10〜20秒/枚（Mac M1基準）
- **起動時間**: 初回起動は3〜5分（モデル読み込み）
- **メモリ使用量**: 約4〜6GB（システムメモリ）

**技術的注意事項**:
- Mac M1環境ではMPS（Metal Performance Shaders）を使用
- CUDA非対応のため、GPU学習はGoogle Colab推奨
- 生成のみならMac環境で十分実用的
- LoRAファイル名に日本語は使用不可（認識されない）

**実装済み**: 2025-11-02

---

## 使い方

### 仕様の追記（REQ完了時）

REQ完了時に、以下の情報を追記してください：

1. **コマンド構文**: 引数と使用例
2. **パラメータ詳細**: 型、必須/任意、デフォルト値、説明
3. **処理フロー**: ステップバイステップの処理内容
4. **技術仕様**: 使用ライブラリ、アルゴリズム、制約
5. **エラーハンドリング**: 想定されるエラーと対処方法
6. **パフォーマンス**: 処理時間、メモリ使用量（可能であれば）

### 新規機能カテゴリの追加

新しい機能カテゴリが必要な場合は、セクションを追加してください。
