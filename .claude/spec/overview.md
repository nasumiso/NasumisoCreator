# なすみそクリエイター - プロジェクト概要

## プロジェクト情報

- **プロジェクト名**: なすみそクリエイター（NasumisoCreator）
- **バージョン**: 1.0 (MVP)
- **開始日**: 2025-10
- **ステータス**: フェーズ1完了 - エンドツーエンドのLoRA学習・画像生成フロー確立済み

---

## 目的

イラストレーター「なすみそ」氏の絵柄を学習し、LoRAモデルとして再現・応用できるアシスタントツールを提供する。画像の収集・タグ付け・LoRA学習・生成・再利用までを一貫して支援し、AIとの共創を実現する。

---

## 主な機能

### 1. データ前処理
- 画像のリネーム・リサイズ（LoRA学習用の前処理）
- WD14 Taggerによる自動タグ付け
- タグの一括編集・管理

### 2. LoRA学習
- Google Colabでのクラウド学習（kohya_ssベース）
- Anything V5ベースモデルを使用
- TensorBoardによる学習進捗の可視化

### 3. 画像生成
- AUTOMATIC1111 WebUIでのLoRA使用（Mac環境）
- プロンプトによる画像制御

**詳細**: [spec.md](./spec.md) - 機能の使い方 | [reference.md](./reference.md) - 技術詳細

---

## 対象ユーザー

- **こすうけ（開発者）**: 元ゲームプログラマ、生成AIと画像処理に精通（MacBook Air M1使用）
  - 学習環境の構築・スクリプト実装・運用を担当
- **なすみそ**: 男性イラストレーター、非エンジニア
  - 画像提供とフィードバックを担当
  - 簡単に使えるUIを想定（フェーズ2以降）

---

## 技術スタック

### 開発環境
- **開発・生成環境**: MacBook Air M1
- **学習環境**: Google Colab（GPU利用、無料版/Colab Pro）

### 主要ツール
- **Python**: 画像処理・自動タグ付けスクリプト
- **kohya_ss**: LoRA学習ツール（Google Colab環境）
- **Stable Diffusion**: Anything V5（SD 1.5ベース）
- **WD14 Tagger v2**: 自動キャプション生成（ONNX Runtime）
- **AUTOMATIC1111 WebUI**: 画像生成インターフェース（Mac環境: `~/stable-diffusion-webui/`）

---

## ワークフロー（8ステップ）

1. **画像収集**: なすみそから画像を受領 → `projects/nasumiso_v1/1_raw_images/`
2. **画像処理**: リネーム＋512x512リサイズ → `projects/nasumiso_v1/2_processed/`
3. **自動タグ付け**: WD14 Taggerで`.txt`生成 → `projects/nasumiso_v1/3_tagged/`
4. **Google Driveアップロード**: タグ付き画像をGoogle Driveにアップロード（Colab学習用）
5. **学習実行**: Google Colabで`train_lora_nasutomo.ipynb`を使用してLoRA学習 → Google Drive `/MyDrive/NasuTomo/output/` に学習済みモデル（.safetensors）を保存
6. **モデルダウンロードと配置**:
   - Google Driveから学習済みLoRAモデルをダウンロード
   - ローカルの`projects/nasumiso_v1/lora_models/`に保存
   - `~/stable-diffusion-webui/models/Lora/`にコピー（画像生成用）
7. **画像生成**: Mac環境のStableDiffusion WebUI (`~/stable-diffusion-webui/`) でテスト生成 → `~/stable-diffusion-webui/outputs/`
8. **品質チェックと再学習**: フィードバックに基づき改善

---

## プロジェクトディレクトリ構造

```
NasumisoCreator/
├── .claude/              # Claude Code管理ファイル
├── projects/             # プロジェクトごとのデータ管理
│   └── nasumiso_v1/
│       ├── 1_raw_images/     # ステップ1: 元画像
│       ├── 2_processed/      # ステップ2: リサイズ・リネーム済み
│       ├── 3_tagged/         # ステップ3: タグ付き画像 → Google Driveへ
│       └── lora_models/      # ステップ5: 学習済みLoRAモデル
├── scripts/              # Python前処理スクリプト
├── notebooks/            # Google Colab学習ノートブック
│   └── train_lora_nasutomo.ipynb
└── docs/                 # ドキュメント
```

**注**: 画像生成環境は別ディレクトリ `~/stable-diffusion-webui/` に配置

---

## 開発ロードマップ

### フェーズ1: MVP開発（✓ 完了）
- ✓ 画像前処理スクリプト（リネーム・リサイズ・自動タグ付け・共通タグ追加・日本語タグ生成）
- ✓ Google Colab学習ノートブック（`train_lora_nasutomo.ipynb`）
- ✓ Mac環境でのStableDiffusion WebUI設置
- ✓ エンドツーエンドでのLoRA学習・画像生成フローの確立

### フェーズ2: 機能拡張
- GUIツール化（ローカルで完結・なすみそ氏でも操作可能）
- 複数人のスタイル切替・混合LoRA対応
- パラメータチューニング支援機能

### フェーズ3: 高度化・実用化
- SDXL対応・画像品質向上機能
- なすみそ本人向け簡易出力UI（表情差分量産など）
- スタンプ/グッズ用の自動レイアウト機能

---

## 参考資料

### プロジェクト内ドキュメント
- [spec.md](./spec.md) - 実装済み機能の使い方（ユーザー向け）
- [reference.md](./reference.md) - 技術詳細・API仕様（開発者向け）
- [KNOWLEDGE.md](../KNOWLEDGE.md) - プロジェクト全体の技術的知見

### 外部リソース
- [kohya_ss公式リポジトリ](https://github.com/bmaltais/kohya_ss) - LoRA学習ツール
- [AUTOMATIC1111 WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) - 画像生成UI
- [WD14 Tagger](https://github.com/toriato/stable-diffusion-webui-wd14-tagger) - 自動キャプション生成
