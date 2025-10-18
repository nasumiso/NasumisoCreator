# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

**NasumisoCreator** は、イラストレーター「なすみそ」の画風を学習し、LoRAモデルとして再現・応用するアシスタントツールです。

- **開発者**: こすうけ（MacBook Air M1使用）
- **技術スタック**: Python, Google Colab, kohya_ss, Stable Diffusion, AUTOMATIC1111 WebUI
- **現在のステータス**: 初期セットアップ段階（ソースコード未実装）

### 7ステップのワークフロー

1. **画像収集**: なすみそから画像を受領 → `projects/nasumiso_v1/1_raw_images/`
2. **画像処理**: リネーム＋512x512リサイズ → `projects/nasumiso_v1/2_processed/`
3. **自動タグ付け**: WD14 Taggerで`.txt`生成 → `projects/nasumiso_v1/3_tagged/`
4. **データセット整形**: 画像+タグをペアで配置 → `projects/nasumiso_v1/4_dataset/`
5. **学習実行**: Google ColabでLoRA学習 → `projects/nasumiso_v1/lora_models/`
6. **画像生成**: Windows環境のWebUIでテスト生成 → `outputs/test_generations/`
7. **品質チェックと再学習**: フィードバックに基づき改善

## 開発ワークフロー（6ステップの実装サイクル）

このプロジェクトは`.claude/`ディレクトリで管理される6ステップのワークフローに従います：

1. **作業指示** - 開発者が作業指示を出す（requirements.mdに記述）
2. **作業計画** - Claude Codeがwork-plan.mdに作業計画をチェックリスト形式で記述
3. **計画確認** - 開発者が計画を確認し、実装指示を出す
4. **実装** - Claude Codeが実装（進捗はwork-plan.mdで管理）
5. **テスト** - Claude Codeがテストを実行、work-plan.mdのチェックリストを完了させる
6. **仕様反映と完了処理** - 開発者確認後、spec/implementation.mdに反映、completed/REQ-XXX/に移動

### 作業開始前に必ず実行すること

1. `.claude/claude.md`を読んで詳細なワークフロー指示を理解する
2. `.claude/spec/overview.md`でプロジェクト全体像を確認する
3. `.claude/requirements.md`で現在の作業指示を確認する
4. `.claude/work-plan.md`で進行中のタスクがあるか確認する
5. 新規作業の場合：実装前に必ず`work-plan.md`に計画を記述する
6. 実装完了後：`spec/implementation.md`に実装内容を記録する
7. 要件完了時：開発者の指示で`completed/REQ-XXX/`に移動する

## プロジェクト構造

```
NasumisoCreator/
├── .claude/                        # 開発管理ドキュメント
│   ├── claude.md                   # ワークフロールール詳細
│   ├── requirements.md             # 現在の作業指示
│   ├── work-plan.md                # 作業計画・チェックリスト
│   ├── notes.md                    # 月次作業ログ
│   ├── spec/                       # 仕様書
│   │   ├── overview.md            # プロジェクト概要
│   │   └── implementation.md      # 実装済み機能
│   └── completed/                  # 完了した要件
│
├── projects/                       # プロジェクトごとのデータ管理
│   └── nasumiso_v1/
│       ├── 1_raw_images/          # 元画像
│       ├── 2_processed/           # リサイズ・リネーム済み
│       ├── 3_tagged/              # タグ付き画像（.txtペア）
│       ├── 4_dataset/             # Colab学習用データセット
│       └── lora_models/           # 学習済みLoRAモデル
│
├── scripts/                        # Python前処理スクリプト
│   ├── prepare_images.py          # リネーム・リサイズ（未実装）
│   ├── auto_caption.py            # 自動タグ付け（未実装）
│   └── organize_dataset.py        # データセット整形（未実装）
│
├── notebooks/                      # Colab学習ノートブック
│   └── train_lora_sd15.ipynb      # SD 1.5用LoRA学習（未実装）
│
└── outputs/                        # 生成結果（Windows環境）
    ├── test_generations/           # テスト生成画像
    ├── prompts/                    # プロンプトテンプレート
    └── generation_logs/            # 生成パラメータログ
```

## セットアップ

### 仮想環境のセットアップ

```bash
# 仮想環境の作成
python3 -m venv .venv

# 仮想環境の有効化
source .venv/bin/activate  # Mac/Linux
# または
.venv\Scripts\activate  # Windows

# 依存関係のインストール
pip install -r requirements.txt
```

### 仮想環境の無効化

```bash
deactivate
```

## コマンド

### 画像前処理

```bash
# 仮想環境を有効化してから実行
source .venv/bin/activate

# 画像のリネーム・リサイズ
python scripts/prepare_images.py \
  --input projects/nasumiso_v1/1_raw_images \
  --output projects/nasumiso_v1/2_processed \
  --size 512

# 自動タグ付け（未実装）
python scripts/auto_caption.py --project nasumiso_v1

# データセット整形（未実装）
python scripts/organize_dataset.py --project nasumiso_v1
```

## 技術的なアーキテクチャ

### データフロー

1. **前処理（Mac環境）**: `scripts/`のPythonスクリプトで画像処理・タグ付け
2. **学習（Google Colab）**: `notebooks/train_lora_sd15.ipynb`でLoRA学習
3. **生成（Windows環境）**: AUTOMATIC1111 WebUIで画像生成

### 重要な制約

- **Mac環境での学習制限**: CUDA非対応のため、学習はGoogle Colab必須
- **生成環境**: Windows 10/11 + AUTOMATIC1111 WebUI想定
- **画像枚数**: 10〜100枚推奨（過学習・学習不足を避けるため）
- **学習時間**: 50枚・2000ステップで約20〜30分（Colab Pro基準）

## 重要な注意事項

### ワークフロールール
- **必ず作業計画を作成**：実装前に`.claude/work-plan.md`に計画を記述（Step 2）
- **計画のスキップ禁止**：開発者が計画を確認してから実装を開始
- **実装内容を必ず記録**：実装完了後は`.claude/spec/implementation.md`を更新
- **移動は開発者指示後**：開発者の指示なしに`completed/`への移動は行わない
- **コミットは明示的指示時のみ**：開発者が明示的に要求した時のみコミットする

### コーディング規則
- **ドキュメント**: すべて日本語で記述
- **Pythonコード**:
  - コメントは日本語（詳細な説明）と英語（簡潔な説明）を併用
  - 関数・クラス名は英語（snake_case / PascalCase）
  - インデント: 4スペース
  - 型ヒント推奨（Python 3.11対応）
- **新規プロジェクト作成**:
  ```bash
  mkdir -p projects/新プロジェクト名/{1_raw_images,2_processed,3_tagged,4_dataset,lora_models}
  ```

### 環境固有の注意
- **Mac環境（開発）**: スクリプト実装のみ、学習は不可（CUDA非対応）
- **Google Colab（学習）**: kohya_ss使用、GPU必須
- **Windows環境（生成）**: AUTOMATIC1111 WebUI使用

## 完了処理

要件完了時は開発者の指示で`completed/REQ-XXX/`フォルダに移動：

```
「REQ-XXXを完了フォルダに移動してください」
```

## 参照ドキュメント

- `.claude/claude.md` - ワークフロー詳細ルール
- `.claude/spec/overview.md` - プロジェクト全体仕様
- `.claude/spec/original/要件定義書.md` - MVP要件定義
- `.claude/spec/original/開発手順書.md` - Mac環境向け学習手順
