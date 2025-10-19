# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

**NasumisoCreator** は、イラストレーター「なすみそ」の画風を学習し、LoRAモデルとして再現・応用するアシスタントツールです。

- **開発者**: こすうけ（MacBook Air M1使用）
- **技術スタック**: Python, Google Colab, kohya_ss, Stable Diffusion, AUTOMATIC1111 WebUI
- **現在のステータス**: 画像前処理・自動タグ付けスクリプト実装済み

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
6. 実装完了後：`spec/spec.md`（ユーザー向け）と`spec/reference.md`（開発者向け）に機能仕様を記録する
7. 要件完了時：開発者の指示で`completed/REQ-XXX/`に移動、spec.mdとreference.mdに仕様を反映

## プロジェクト構造

```
NasumisoCreator/
├── .claude/                        # 開発管理ドキュメント
│   ├── claude.md                   # ワークフロールール詳細
│   ├── requirements.md             # 現在の作業指示
│   ├── work-plan.md                # 作業計画・チェックリスト
│   ├── notes.md                    # 現在のREQ作業中の気づき・メモ
│   ├── KNOWLEDGE.md                # プロジェクト全体の知見・ノウハウ
│   ├── spec/                       # 仕様書
│   │   ├── overview.md            # プロジェクト概要・アーキテクチャ
│   │   ├── spec.md                # 実装済み機能の使い方（ユーザー向け）
│   │   ├── reference.md           # 技術詳細・API仕様（開発者向け）
│   │   └── original/              # 初期要件定義
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
│   ├── prepare_images.py          # リネーム・リサイズ（実装済み）
│   ├── auto_caption.py            # 自動タグ付け（実装済み）
│   ├── add_common_tag.py          # 共通タグ一括追加（実装済み）
│   ├── generate_jp_tags.py        # 日本語タグ生成（実装済み）
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

### 画像前処理ワークフロー

```bash
# 仮想環境を有効化してから実行
source .venv/bin/activate

# 1. 画像のリネーム・リサイズ（512x512）
python scripts/prepare_images.py \
  --input projects/nasumiso_v1/1_raw_images \
  --output projects/nasumiso_v1/2_processed \
  --size 512

# 2. 自動タグ付け（WD14 Tagger v2）
python scripts/auto_caption.py \
  --input projects/nasumiso_v1/2_processed \
  --output projects/nasumiso_v1/3_tagged \
  --threshold 0.35

# 3. 共通タグの一括追加（画風学習用）
python scripts/add_common_tag.py \
  --input projects/nasumiso_v1/3_tagged \
  --tag "nasumiso_style" \
  --exclude-jp

# 4. 日本語タグファイル生成（確認用）
python scripts/generate_jp_tags.py \
  --input projects/nasumiso_v1/3_tagged

# 5. データセット整形（未実装）
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
  - 型ヒント推奨（Python 3.9.6対応）
  - ファイル先頭に `#!/usr/bin/env python3` と `# -*- coding: utf-8 -*-` を記述
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

## 技術的な重要事項

### WD14 Tagger v2の使用上の注意
- **画像正規化は不要**: モデルは0-255の範囲を期待（0-1正規化すると誤ったタグが生成される）
- **モデル出力**: 既に確率値のため、sigmoid適用は不要
- **推奨しきい値**: 0.35（P=Rポイント: 0.3771）
- **実装方式**: ONNX Runtime（transformersは非対応）

### タグ管理のベストプラクティス
1. 自動タグ付け実行 → Gitコミット（自動生成版）
2. 共通タグ追加（nasumiso_styleなど） → Gitコミット
3. 手動でタグレビュー・修正 → Gitコミット（修正版）
4. Git差分で変更履歴を追跡可能

### Git管理
- **画像ファイル**: `.gitignore`で除外（プライバシー保護）
- **タグファイル (.txt)**: Git管理対象（手動修正履歴を追跡）

## 参照ドキュメント

- `.claude/claude.md` - ワークフロー詳細ルール
- `.claude/spec/overview.md` - プロジェクト概要・アーキテクチャ
- `.claude/spec/spec.md` - 実装済み機能の使い方（ユーザー向け）
- `.claude/spec/reference.md` - 技術詳細・API仕様（開発者向け）
- `.claude/KNOWLEDGE.md` - プロジェクト全体の知見・ノウハウ
- `.claude/spec/original/要件定義書.md` - MVP要件定義
- `.claude/spec/original/開発手順書.md` - Mac環境向け学習手順
