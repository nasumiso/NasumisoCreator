# なすみそクリエイター - プロジェクト概要

## プロジェクト情報

- **プロジェクト名**: なすみそクリエイター（NasumisoCreator）
- **バージョン**: 1.0 (MVP)
- **開始日**: 2025-10
- **ステータス**: 開発中（画像前処理・自動タグ付け実装済み）

---

## 目的

イラストレーター「なすみそ」氏の絵柄を学習し、LoRAモデルとして再現・応用できるアシスタントツールを提供する。画像の収集・タグ付け・LoRA学習・生成・再利用までを一貫して支援し、AIとの共創を実現する。

---

## 主な機能

### 1. データ前処理
- 画像のリネーム・リサイズ（LoRA学習用の前処理）
- WD14 Taggerによる自動タグ付け
- タグの一括編集・管理
- データセット整形（kohya_ss標準フォーマット対応）

### 2. LoRA学習
- Google Colabでのクラウド学習
- kohya_ssベースの学習フロー
- 推奨パラメータ設定の提供
- 学習済みモデル（.safetensors）の出力

### 3. 画像生成
- AUTOMATIC1111 WebUIでのLoRA使用（Windows環境）
- プロンプトテンプレートの提供
- 生成結果の管理

**詳細情報**:
- 実装済み機能の使い方: [spec.md](./spec.md) - ユーザー向け機能説明
- 技術詳細・API仕様: [reference.md](./reference.md) - 開発者向け技術情報

---

## 対象ユーザー

- **こすうけ（開発者）**: 元ゲームプログラマ、生成AIと画像処理に精通（MacBook Air M1使用）
  - 学習環境の構築・スクリプト実装・運用を担当
- **なすみそ**: 男性イラストレーター、非エンジニア
  - 画像提供とフィードバックを担当
  - 簡単に使えるUIを想定（フェーズ2以降）
- **想定利用シーン**: スタンプ、グッズ、構図提案、ラフ生成、プロトタイピング

---

## 技術スタック

### 開発環境
- **開発マシン**: MacBook Air M1
- **学習環境**: Google Colab（GPU利用、無料版/Colab Pro）
- **生成環境**: MacBook Air M1（`~/stable-diffusion-webui/`）

### 主要ツール・技術
- **Python**: 画像処理・自動タグ付けスクリプト
- **kohya_ss**: LoRA学習ツール（Google Colab環境）
- **Stable Diffusion**: ベースモデル（Anything V5 - SD 1.5ベース）
- **WD14 Tagger v2**: 自動キャプション生成（ONNX Runtime）
- **AUTOMATIC1111 WebUI**: 画像生成インターフェース（Mac環境: `~/stable-diffusion-webui/`）

### 学習・生成プラットフォーム
- **Google Colab**: クラウドGPU学習（CUDAツールチェーン自動利用、`train_lora_nasutomo.ipynb`使用）
- **Mac環境（M1）**: データ前処理、画像生成（`~/stable-diffusion-webui/`）
  - 学習は非対応（CUDA非対応のため、Google Colab推奨）

---

## アーキテクチャ概要

### プロジェクトディレクトリ構造

```
NasumisoCreator/
├── .claude/                        # Claude Code管理ファイル
│   ├── claude.md
│   ├── requirements.md
│   ├── work-plan.md
│   ├── notes.md
│   ├── spec/                       # 仕様書
│   └── completed/                  # 完了した要件
│
├── projects/                       # プロジェクトごとのデータ管理
│   └── nasumiso_v1/
│       ├── 1_raw_images/          # ステップ1: なすみそから受領した元画像
│       ├── 2_processed/           # ステップ2: リサイズ・リネーム済み画像
│       ├── 3_tagged/              # ステップ3: タグ付き画像（.txtペア）→Google Driveにアップロード
│       ├── 4_dataset/             # （未使用: 当初計画のデータセット整形用）
│       └── lora_models/           # ステップ5: 学習済みLoRAモデル（Google Driveからダウンロード）
│
├── scripts/                        # Python前処理スクリプト
│   ├── prepare_images.py          # リネーム・リサイズ
│   ├── auto_caption.py            # 自動タグ付け
│   ├── add_common_tag.py          # 共通タグ一括追加
│   ├── generate_jp_tags.py        # 日本語タグ生成
│   └── organize_dataset.py        # （未実装: データセット整形）
│
├── notebooks/                      # Colab学習ノートブック
│   └── train_lora_nasutomo.ipynb  # Google Colab用LoRA学習ノートブック
│
├── docs/                           # ドキュメント
├── .gitignore                      # Git除外設定
├── CLAUDE.md                       # プロジェクト概要（Claude Code用）
└── requirements.txt                # Python依存パッケージ
```

**注**: 画像生成環境は別ディレクトリ `~/stable-diffusion-webui/` に配置されており、このプロジェクトディレクトリには含まれません。

### ワークフロー（7ステップ）

1. **画像収集**: なすみそから画像を受領 → `projects/nasumiso_v1/1_raw_images/`
2. **画像処理**: リネーム＋512x512リサイズ → `projects/nasumiso_v1/2_processed/`
3. **自動タグ付け**: WD14 Taggerで`.txt`生成 → `projects/nasumiso_v1/3_tagged/`
4. **Google Driveアップロード**: タグ付き画像をGoogle Driveにアップロード（Colab学習用）
5. **学習実行**: Google Colabで`train_lora_nasutomo.ipynb`を使用してLoRA学習 → Google Drive内の`NasuTomo/output/`に保存、学習後ローカルの`projects/nasumiso_v1/lora_models/`にダウンロード
6. **画像生成**: Mac環境のStableDiffusion WebUI (`~/stable-diffusion-webui/`) でテスト生成 → `~/stable-diffusion-webui/outputs/`
7. **品質チェックと再学習**: フィードバックに基づき改善

---

## 開発ロードマップ

### フェーズ1: MVP開発（✓ 完了）
- ✓ 画像管理スクリプトの実装（リネーム・リサイズ）
- ✓ 自動タグ付けツールの統合（WD14 Tagger v2）
- ✓ 共通タグ一括追加スクリプトの実装
- ✓ 日本語タグ生成スクリプトの実装
- ✓ Colab学習ノートブックの作成（`train_lora_nasutomo.ipynb`）
- ✓ Mac環境でのStableDiffusion WebUI設置
- ✓ 基本的なディレクトリ構造の確立
- ✓ ドキュメント整備（開発手順書・仕様書）
- ✓ エンドツーエンドでのLoRA学習・画像生成フローの確立

### フェーズ2: 機能拡張
- GUIツール化（ローカルで完結・なすみそ氏でも操作可能）
- 複数人のスタイル切替・混合LoRA対応
- パラメータチューニング支援機能
- 学習進捗の可視化
- バッチ処理・自動化の強化

### フェーズ3: 高度化・実用化
- SDXL対応・画像品質向上機能
- なすみそ本人向け簡易出力UI（表情差分量産など）
- スタンプ/グッズ用の自動レイアウト機能
- プロンプトライブラリの構築
- 生成画像の品質評価システム

---

## 制約事項

### 技術的制約
- **Mac環境での学習制限**: CUDA/cuDNN非対応のため、ローカル学習は実用的でない
- **GPU要件**: Google Colab依存（無料版は利用時間制限あり）
- **生成環境**: Mac環境（`~/stable-diffusion-webui/`、M1チップ対応）
- **画像枚数**: 10〜100枚程度が推奨（少なすぎると学習不足、多すぎると過学習）
- **学習時間**: 15枚・10エポックで約20〜30分（Google Colab基準）
- **データ転送**: Google Driveを介して学習データと学習済みモデルを転送

### ビジネス的制約
- **個人開発**: リソースは開発者1名（こすうけ）
- **非エンジニアユーザー対応**: なすみそが簡単に使えるよう、複雑な手作業を排除する必要あり
- **コスト**: Colab無料版の制限内で運用（必要に応じてColab Pro検討）

---

## 成功基準

### MVP（フェーズ1）の成功基準
- ✓ LoRA学習用の画像データ準備が簡単に行える（手動作業10分以内）
- ✓ kohya_ssベースでLoRAモデルを学習可能（エラーなく完走）
- ✓ 学習済みLoRAモデル（.safetensors）が正常に出力される
- ✓ Mac環境で学習済みLoRAを使って画像生成できる
- ✓ 複数プロジェクト管理（例：「なすみそLoRA v1」「別キャラLoRA」）ができる

### 品質基準
- なすみそのスタイルが再現できている（本人の確認が必要）
- 過学習していない（同じ構図ばかりにならない）
- プロンプトへの反応が適切（指示した要素が反映される）
- 生成画像が実用レベル（スタンプ・グッズに使える品質）

### ユーザビリティ基準
- なすみそが非エンジニアでも基本操作を実行できる（フェーズ2以降）
- スクリプト実行でエラーが出ない（適切なエラーハンドリング）
- ドキュメントを見ればこすうけ・なすみそ共に手順が理解できる

---

## 参考資料

### プロジェクト内ドキュメント
- [spec.md](./spec.md) - 実装済み機能の使い方（ユーザー向け）
- [reference.md](./reference.md) - 技術詳細・API仕様（開発者向け）
- [要件定義書](./original/要件定義書.md) - 詳細な要件仕様とMVP定義
- [開発手順書](./original/開発手順書.md) - Mac環境向けLoRA学習の完全版手順
- [KNOWLEDGE.md](../KNOWLEDGE.md) - プロジェクト全体の技術的知見

### 外部リソース
- [kohya_ss公式リポジトリ](https://github.com/bmaltais/kohya_ss) - LoRA学習ツール
- [AUTOMATIC1111 WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) - 画像生成UI
- [WD14 Tagger](https://github.com/toriato/stable-diffusion-webui-wd14-tagger) - 自動キャプション生成
- [Stable Diffusion](https://huggingface.co/runwayml/stable-diffusion-v1-5) - ベースモデル

### 学習・参考記事
- Google Colab でのLoRA学習に関するチュートリアル
- LoRAパラメータチューニングのベストプラクティス
- Danbooru タグの使い方
