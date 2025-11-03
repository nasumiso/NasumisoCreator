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

### prepare_images.py

**コマンド**:
```bash
python scripts/prepare_images.py --input <入力> --output <出力> [--size 512]
```

**主要パラメータ**:
- `--input`: 入力画像ディレクトリ（必須）
- `--output`: 出力ディレクトリ（必須）
- `--size`: 出力サイズ（デフォルト: 512）

**処理内容**:
- 画像を連番リネーム（img001.png, img002.png, ...）
- 指定サイズに中央クロップでリサイズ（LANCZOS）
- PNG形式で出力

**技術仕様**: Pillow, RGB 8bit, EXIF削除

---

### auto_caption.py

**コマンド**:
```bash
python scripts/auto_caption.py --input <入力> --output <出力> [--threshold 0.35] [--use-coreml]
```

**主要パラメータ**:
- `--input`: 入力画像ディレクトリ（必須）
- `--output`: 出力ディレクトリ（必須）
- `--threshold`: タグ信頼度しきい値（デフォルト: 0.35）
- `--use-coreml`: CoreML高速化（Mac Apple Silicon用、デフォルト無効）

**処理内容**:
- WD14 Tagger v2で画像を自動タグ付け（9,083種類のDanbooruタグ）
- 画像を448x448にリサイズ（アスペクト比維持＋パディング）
- しきい値以上のタグを.txtファイルに保存

**技術仕様**:
- **モデル**: WD14 Tagger v2 (wd-v1-4-moat-tagger-v2)
- **ランタイム**: ONNX Runtime
- **入力サイズ**: 448x448 (RGB, 0-255範囲)
- **推奨しきい値**: 0.35

**重要な実装ノート**:
- 画像正規化は不要（0-255範囲をそのまま使用）
- sigmoid適用は不要（モデル出力が既に確率値）
- transformersライブラリは非対応（ONNX Runtime必須）

**CoreML高速化**:
- Mac Apple Silicon環境でNeural Engine使用可能
- `--use-coreml`で有効化（デフォルト無効）
- 注意: 小規模バッチ処理ではCPUより約2.7倍遅い（オーバーヘッドのため）
- CPU推奨: 約1.07秒/画像（Mac M1基準）

---

### add_common_tag.py

**コマンド**:
```bash
python scripts/add_common_tag.py --input <入力> --tag <タグ> [--exclude-jp]
```

**主要パラメータ**:
- `--input`: タグ付き画像ディレクトリ（必須）
- `--tag`: 追加するタグ（必須、Danbooru形式推奨）
- `--exclude-jp`: 日本語タグファイル（_jp.txt）を除外

**処理内容**:
- 各.txtファイルの先頭に指定タグを追加
- UTF-8エンコーディング、上書き保存

**使用例**:
```bash
python scripts/add_common_tag.py --input projects/nasumiso_v1/3_tagged --tag "nasumiso_style" --exclude-jp
```

**Git管理**: タグファイルはGit管理対象（自動タグ付け後・共通タグ追加後・手動修正後にコミット推奨）

---

### generate_jp_tags.py

**コマンド**:
```bash
python scripts/generate_jp_tags.py --input <入力>
```

**主要パラメータ**:
- `--input`: タグ付き画像ディレクトリ（必須）

**処理内容**:
- 英語タグを日本語に変換（静的辞書マッピング）
- 未登録タグは英語のまま出力
- `<画像名>_jp.txt` として保存

**技術仕様**: スクリプト内辞書による簡易的な翻訳（主要タグのみ対応）

**Git管理**: 日本語タグファイル（`*_jp.txt`）は`.gitignore`で除外（再生成可能）

---

## データセット整形

### organize_dataset.py

**ステータス**: 未実装（現在は手動でGoogle Driveにアップロード）

**想定仕様**:
- kohya_ss標準フォーマットでデータセットを整形
- 入力: `projects/nasumiso_v1/3_tagged/`
- 出力: Google Drive `/MyDrive/NasuTomo/datasets/`

---

## LoRA学習

### train_lora_nasutomo.ipynb

**機能**: Google ColabでLoRA学習を実行

**技術スタック**:
- **プラットフォーム**: Google Colab（GPU: T4/V100等）
- **学習ツール**: kohya_ss (bmaltais/kohya_ss)
- **ベースモデル**: Anything V5 (SD 1.5ベース)
- **出力形式**: `.safetensors`（fp16精度）

**処理フロー**:
1. Google Driveマウント
2. kohya_ssセットアップ
3. Anything V5ダウンロード（初回のみ、Civitaiから）
4. 学習実行（`accelerate launch train_network.py`）

**主要パラメータ**:
| パラメータ | 値 | 説明 |
|-----------|-----|------|
| `--network_dim` | 64 | LoRAのrank（次元数） |
| `--network_alpha` | 32 | LoRAのアルファ値 |
| `--max_train_epochs` | 10 | 最大エポック数 |
| `--learning_rate` | 1e-4 | 学習率 |
| `--train_batch_size` | 1 | バッチサイズ |
| `--gradient_accumulation_steps` | 2 | 勾配蓄積（実質バッチサイズ2） |
| `--resolution` | 512,512 | 学習解像度 |
| `--mixed_precision` | fp16 | 混合精度学習 |
| `--optimizer_type` | AdamW8bit | オプティマイザ |
| `--lr_scheduler` | cosine_with_restarts | 学習率スケジューラ |
| `--clip_skip` | 2 | CLIPレイヤースキップ |

**TensorBoard**: `%tensorboard --logdir="/content/drive/MyDrive/NasuTomo/logs"`

**出力先**: `/MyDrive/NasuTomo/output/nasumiso_v1.safetensors`

**パフォーマンス**: 15枚・10エポックで約20〜30分（Colab無料版、T4 GPU基準）

**注意事項**: Colab無料版は利用時間制限あり（連続12時間）、学習データは手動でGoogle Driveにアップロード

---

## 画像生成

### StableDiffusion WebUI

**機能**: AUTOMATIC1111 WebUIを使用した画像生成

**技術スタック**:
- **WebUI**: AUTOMATIC1111/stable-diffusion-webui
- **実行環境**: Mac（M1チップ、MPS backend）
- **設置場所**: `~/stable-diffusion-webui/`
- **アクセスURL**: `http://127.0.0.1:7860/`

**起動方法**:
```bash
cd ~/stable-diffusion-webui
./webui.sh
```

**LoRA適用**:
- LoRA配置先: `~/stable-diffusion-webui/models/Lora/`
- プロンプト指定: `<lora:nasumiso_v1:1.0>, nasumiso_style, 1girl, ...`
- 強度: 0.0〜1.0（推奨: 0.7〜1.0）

**推奨生成パラメータ**:
| パラメータ | 推奨値 |
|-----------|--------|
| Sampling method | DPM++ 2M Karras |
| Sampling steps | 20〜30 |
| CFG Scale | 7〜9 |
| Resolution | 512 x 512 |

**パフォーマンス**: 512x512で約10〜20秒/枚（Mac M1基準）

**注意事項**: LoRAファイル名に日本語は使用不可

---

## Windows環境向けセットアップ

### setup_windows.bat

**機能**: Windows環境でのStable Diffusion WebUI自動セットアップ

**技術仕様**:
- **ファイル形式**: Windows Batch Script (.bat)
- **文字エンコーディング**: UTF-8 (chcp 65001)
- **実行権限**: 管理者権限不要（通常ユーザー権限で実行可能）

**処理フロー**:
1. Python/Gitのインストール確認（`python --version`, `git --version`）
2. インストール先の確認と既存フォルダの削除確認
3. Stable Diffusion WebUIのクローン（`git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git`）
4. 次のステップの案内表示

**インストール先**:
```
%USERPROFILE%\Documents\stable-diffusion-webui\
```

**前提条件**:
- Python 3.10.11以上（PATH設定必須）
- Git for Windows（PATH設定必須）

**終了コード**:
- 0: 正常終了
- 1: Python/Git未インストール、ダウンロード失敗

---

### create_shortcut.bat

**機能**: デスクトップにWebUI起動ショートカットを作成

**技術仕様**:
- **ショートカット作成**: PowerShell経由でWScript.Shellを使用
- **ショートカット名**: `Stable Diffusion WebUI.lnk`
- **配置先**: `%USERPROFILE%\Desktop\`
- **ターゲット**: `%USERPROFILE%\Documents\stable-diffusion-webui\webui-user.bat`

**PowerShellコマンド**:
```powershell
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut('%SHORTCUT%')
$s.TargetPath = '%INSTALL_DIR%\webui-user.bat'
$s.WorkingDirectory = '%INSTALL_DIR%'
$s.Save()
```

---

### ドキュメント構成

**setup_windows.md** (5.8KB):
- 前提条件（Python 3.10.11、Git for Windows）
- インストール手順（スクリーンショット記載箇所明示）
- トラブルシューティング（よくあるエラーと対処法）

**quickstart_nasumiso.md** (10.3KB):
- WebUIの起動方法と画面説明
- プロンプトの書き方（基本〜応用、例文豊富）
- 推奨パラメータ設定
- よくある質問（FAQ）

**model_download.md** (4.7KB):
- ベースモデル（anything-v5.safetensors, 約4.27GB）の入手方法
- LoRAモデル（nasumiso_v1.safetensors, 約150MB）の入手方法
- ファイル配置場所の詳細説明

**設計思想**:
- イラストレーター向けに技術用語を極力避ける
- スクリーンショット記載箇所を明示（後で画像追加可能）
- トラブルシューティングを充実

---

### .gitignore更新内容

**追加された除外パターン**:
```gitignore
# Python仮想環境
*.pyo
env/
dist/
build/

# システムファイル（OS固有）
desktop.ini
*.swp
*.swo
*~

# 外部ツール（stable-diffusion-webui は別管理）
stable-diffusion-webui/
```

**設計方針**:
- セットアップスクリプト、ドキュメントのみGit管理
- Python本体、WebUI本体、モデルファイルは管理対象外
- OS固有ファイル（Windows/Mac両対応）を除外

---

### 重要な技術的気づき

**LoRAとベースモデルの関係**:
- LoRAモデルは差分データのため、単体では動作不可
- 学習時のベースモデル（anything-v5.safetensors）と推論時のベースモデルを統一する必要あり
- 異なるベースモデルを使用すると画風の再現度が低下

**ベースモデルの確認方法**:
```bash
# Mac環境
ls ~/stable-diffusion-webui/models/Stable-diffusion/

# Windows環境
dir %USERPROFILE%\Documents\stable-diffusion-webui\models\Stable-diffusion\
```

**モデルファイル配置**:
- ベースモデル: `models/Stable-diffusion/anything-v5.safetensors`
- LoRAモデル: `models/Lora/nasumiso_v1.safetensors`

---

## ドキュメント管理

このファイルはREQ完了時にClaude Codeが更新します。技術仕様を簡潔に記録してください。
