# 作業計画

## 現在の作業

### [REQ-006] Gradioベースのなすみそ学習ツールUI開発

#### 準備
- [ ] 既存スクリプトの動作確認（prepare_images.py, auto_caption.py, add_common_tag.py）
- [ ] requirements.txtの依存関係確認と必要なパッケージの追加
- [ ] Google Drive API認証情報のセットアップ方法を調査
- [ ] プロジェクト構造の決定（app.py配置場所、モジュール分割）

#### 実装フェーズ1: 基本構造とタブ1（画像準備） ✅ 完了
- [x] app.pyの基本構造作成（Gradio 3タブレイアウト）
- [x] タブ1: 画像準備タブのUI構築
  - [x] フォルダ選択UI（デフォルト: projects/nasumiso_v1/1_raw_images）
  - [x] 「変換開始」ボタン
  - [x] リアルタイム進捗表示エリア
- [x] タブ1: 既存スクリプト統合ロジック
  - [x] prepare_images.pyの実行処理
  - [x] auto_caption.pyの実行処理（しきい値0.35固定）
  - [x] add_common_tag.pyの実行処理（nasumiso_style固定）
  - [x] 進捗表示の実装（ファイル名、進捗%）
  - [x] エラーハンドリング（ファイル不存在、処理失敗）

**実装完了日**: 2025-11-08
**コミット**: 9e07902 (feat: Gradio WebUIに画像前処理パイプライン機能を実装)
**実装内容**:
- Gradio 4.44.1 + huggingface-hub < 1.0 で環境構築
- タブ1「画像準備」に3ステップパイプライン実装（リサイズ→タグ付け→共通タグ追加）
- リアルタイムプログレスバー対応（gr.Progress API）
- フォルダを開くボタン、画像情報表示機能も実装

#### 実装フェーズ2: タブ2（タグ編集）
- [ ] タブ2: タグ編集タブのUI構築
  - [ ] 画像一覧表示（サムネイル、projects/nasumiso_v1/3_tagged/）
  - [ ] 画像選択UI
  - [ ] タグテキストエリア（編集可能）
  - [ ] 保存ボタン
  - [ ] 固有タグ一括追加UI
- [ ] タブ2: タグ編集ロジック
  - [ ] 画像一覧の読み込み処理
  - [ ] タグファイル（.txt）の読み込み処理
  - [ ] タグ編集・保存処理（.txtファイル更新）
  - [ ] 固有タグ一括追加処理（複数画像選択対応）
  - [ ] エラーハンドリング

#### 実装フェーズ3: タブ3（学習・モデル管理）基本機能
- [ ] タブ3: 学習・モデル管理タブのUI構築
  - [ ] Google Drive連携セクション
    - [ ] 「Google Driveにアップロード」ボタン
    - [ ] 進捗表示エリア
  - [ ] Google Colab連携セクション
    - [ ] 「Google Colabで学習」リンク
  - [ ] モデル管理セクション
    - [ ] 「モデルダウンロード」ボタン
    - [ ] 「Stable Diffusionに配置」ボタン
    - [ ] モデル一覧表示
- [ ] Google Drive API統合
  - [ ] OAuth 2.0認証フロー実装
  - [ ] credentials.json, token.jsonの管理ロジック
  - [ ] ファイルアップロード処理（3_tagged/ → /MyDrive/NasuTomo/datasets/）
  - [ ] 進捗表示（アップロード中のファイル名、進捗%）
  - [ ] エラーハンドリング（認証失敗、ネットワークエラー）
- [ ] Google Colab連携
  - [ ] notebooks/train_lora_nasutomo.ipynbを開くリンク実装
- [ ] モデル管理機能
  - [ ] Google Driveからモデルダウンロード処理
  - [ ] ダウンロード先設定（projects/nasumiso_v1/lora_models/）
  - [ ] Stable Diffusion WebUIへの自動配置処理
    - [ ] Mac: ~/stable-diffusion-webui/models/Lora/
    - [ ] Windows: %USERPROFILE%\Documents\stable-diffusion-webui\models\Lora\
  - [ ] エラーハンドリング

#### 実装フェーズ4: クロスプラットフォーム対応
- [ ] パス操作をPathlibに統一
- [ ] 環境依存処理の分岐実装（Mac/Windows）
- [ ] 設定ファイル（config.json）の実装
  - [ ] Stable Diffusion WebUIパス設定
  - [ ] 学習モード設定（training_mode: colab/local）
  - [ ] デフォルト設定の提供
- [ ] 起動スクリプト作成
  - [ ] start_nasumiso_trainer.sh（Mac用）
  - [ ] start_nasumiso_trainer.bat（Windows用）
  - [ ] 実行権限設定

#### 実装フェーズ5: ログとエラーハンドリング
- [ ] ログ出力機能の実装
  - [ ] logs/ディレクトリの自動作成
  - [ ] 処理履歴のログファイル出力
  - [ ] タイムスタンプ付きログ
- [ ] エラーメッセージの統一
  - [ ] わかりやすいエラーメッセージ表示
  - [ ] エラー時の推奨アクション提示
- [ ] .gitignore更新
  - [ ] credentials.json, token.jsonを除外
  - [ ] logs/を除外

#### テスト（Mac環境）
- [ ] タブ1: 画像準備機能のテスト
  - [ ] フォルダ選択 → 変換実行 → 正常完了
  - [ ] 進捗表示の確認
  - [ ] エラー時の挙動確認（空フォルダ、無効パスなど）
- [ ] タブ2: タグ編集機能のテスト
  - [ ] 画像一覧表示確認
  - [ ] タグ編集・保存確認
  - [ ] 固有タグ一括追加確認
- [ ] タブ3: Google Drive連携のテスト
  - [ ] OAuth 2.0認証フロー確認
  - [ ] ファイルアップロード確認
  - [ ] 進捗表示確認
  - [ ] エラーハンドリング確認
- [ ] タブ3: モデル管理のテスト
  - [ ] モデルダウンロード確認
  - [ ] Stable Diffusionへの配置確認（Mac）
- [ ] 起動スクリプトのテスト（Mac）
  - [ ] ./start_nasumiso_trainer.sh で起動確認
  - [ ] ポート7861で起動確認
- [ ] エンドツーエンドテスト（Mac環境）
  - [ ] 全工程を通した動作確認（画像準備 → タグ編集 → アップロード → モデル配置）
- [ ] ログ出力の確認

#### ドキュメント作成
- [ ] README.md更新
  - [ ] セットアップ手順（依存パッケージインストール）
  - [ ] Google Drive API認証情報の取得・設定方法
  - [ ] 起動方法（Mac/Windows）
  - [ ] 各タブの使い方
  - [ ] トラブルシューティング
- [ ] config.json.exampleの作成（サンプル設定ファイル）

#### テスト結果
（テスト実行後、ここに結果を記録）

---

## 完了した要件の作業計画について

完了した要件の作業計画は `completed/REQ-XXX/work-plan.md` に移動されています。

---

## 作業計画テンプレート

新しい作業計画を作成する際は、以下の形式を使用してください：

### [REQ-XXX] タイトル

#### 準備
- [ ] [準備タスク1]
- [ ] [準備タスク2]

#### 実装
- [ ] [実装タスク1]
- [ ] [実装タスク2]
- [ ] [実装タスク3]

#### テスト
- [ ] [テストタスク1]
- [ ] [テストタスク2]

#### テスト結果
（テスト実行後、ここに結果を記録）

---

## 使い方

### Step 2: 作業計画の作成
- Claude Code が requirements.md の要件を元に、このファイルにチェックリストを作成

### Step 4: 実装中
- Claude Code が各タスクを `- [x]` に変更しながら進捗を管理

### Step 5: テスト実行
- Claude Code がテストを実行し、結果を「テスト結果」セクションに記録
- 問題が発見された場合は notes.md に詳細を記録

### Step 6: 完了処理
- 開発者の指示で completed/REQ-XXX/work-plan.md に移動
