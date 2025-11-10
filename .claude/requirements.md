# 作業指示書

## 📋 未着手

（なし）

## 🔄 作業中

### [REQ-006] Gradioベースのなすみそ学習ツールUI開発
ステータス: 🔄 作業中

---

## 完了した要件について

完了した要件は `completed/REQ-XXX/` フォルダに移動されています。
各フォルダには以下のファイルが含まれます：
- `requirement.md`: 要件の詳細
- `work-plan.md`: 作業計画とチェックリスト
- `notes.md`: 作業固有の重要なメモ

---

## 作業テンプレート

新しい要件を追加する際は、以下の形式を使用してください：

### [REQ-006] Gradioベースのなすみそ学習ツールUI開発
ステータス: 📋 未着手

#### 要求内容
なすみそさんがWindows環境（RTX 3060搭載）で、イラストからLoRAモデルを学習するためのGradio製Webアプリケーションを開発する。既存のPythonスクリプト（画像前処理・自動タグ付け）を統合し、Google DriveおよびGoogle Colab連携機能を実装する。将来的にローカルGPU学習への移行を考慮した設計とする。

**開発フロー:**
1. こすうけがMac環境で開発・動作確認
2. クロスプラットフォーム対応を確認
3. なすみそさんのWindows環境にデプロイ

**主要機能:**
1. **画像準備タブ**: 画像のリネーム・リサイズ・自動タグ付けを一括実行
2. **タグ編集タブ**: 画像ごとのタグ表示・編集、固有タグの追加
3. **学習・モデル管理タブ**: Google Driveへのアップロード、Colab学習連携、モデルダウンロード・配置

**ユーザー:**
- こすうけ（開発者、MacBook Air M1、開発・動作確認）
- なすみそ（非エンジニア、イラストレーター、Windows環境、最終利用者）

#### 必要な要素

**技術スタック:**
- Gradio 4.x（WebUI構築）
- Python 3.9+（既存スクリプトとの互換性）
- Google Drive API v3（OAuth 2.0認証、ファイルアップロード・ダウンロード）
- 既存スクリプト統合（prepare_images.py, auto_caption.py, add_common_tag.py）

**機能要件:**
- タブ1: 画像準備
  - フォルダ選択UI（`projects/nasumiso_v1/1_raw_images`）
  - 「変換開始」ボタンで以下を順次実行:
    1. prepare_images.py（512x512リサイズ・リネーム）
    2. auto_caption.py（WD14 Tagger、しきい値0.35）
    3. add_common_tag.py（`nasumiso_style`自動追加）
  - リアルタイム進捗表示（処理中のファイル名、進捗%）
  
- タブ2: タグ編集
  - `projects/nasumiso_v1/3_tagged/`の画像一覧表示（サムネイル）
  - 画像選択 → タグテキストエリア表示
  - タグ編集・保存機能（.txtファイル更新）
  - 固有タグ一括追加（例: 選択した画像にのみ`chara_alice`を追加）
  
- タブ3: 学習・モデル管理
  - Google Drive連携:
    - 「Google Driveにアップロード」ボタン（OAuth 2.0初回認証、以降は自動ログイン）
    - `3_tagged/`を`/MyDrive/NasuTomo/datasets/`にアップロード
    - 進捗表示（アップロード中のファイル名、進捗%）
  - Google Colab学習:
    - 「Google Colabで学習」リンク（notebooks/train_lora_nasutomo.ipynbを開く）
    - ※学習実行は手動（Colab上でRun All）
  - モデル管理:
    - 「モデルダウンロード」ボタン（`/MyDrive/NasuTomo/output/*.safetensors`を取得）
    - ダウンロード先: `projects/nasumiso_v1/lora_models/`
    - 「Stable Diffusionに配置」ボタン
      - Mac: `~/stable-diffusion-webui/models/Lora/`
      - Windows: `%USERPROFILE%\Documents\stable-diffusion-webui\models\Lora\`

**非機能要件:**
- ポート番号: 7861（Stable Diffusion WebUIの7860と競合回避）
- 起動方法: 
  - Mac: `./start_nasumiso_trainer.sh` または `python app.py`
  - Windows: `start_nasumiso_trainer.bat`
- エラーハンドリング: ファイル不存在、API認証失敗、ネットワークエラー時のわかりやすいメッセージ表示
- ログ出力: 処理履歴を`logs/`に保存（デバッグ用）
- クロスプラットフォーム対応: Mac/Windows両環境で動作確認

**設計上の考慮点:**
- 将来的にローカルGPU学習（RTX 3060）への移行を考慮
  - 設定ファイル（`config.json`）で学習環境を切り替え可能に
  - `training_mode: "colab"` or `"local"`
- Google Drive認証情報の管理
  - `credentials.json`: アプリ認証情報（開発者が提供、Git管理対象外）
  - `token.json`: ユーザー認証トークン（初回認証時に自動生成、Git管理対象外）
- クロスプラットフォーム対応
  - パス操作はPathlibを使用（Windows/Mac両対応）
  - 起動スクリプトは各OS用に用意（.bat, .sh）
  - Stable Diffusionパスは環境変数または設定ファイルで管理

**依存関係:**
- 既存実装: REQ-001（画像前処理）, REQ-002（自動タグ付け）, REQ-003（Windows環境セットアップ）
- 外部サービス: Google Drive, Google Colab
- Python パッケージ: 
  - gradio>=4.0
  - google-auth-oauthlib>=1.0
  - google-auth-httplib2>=0.1
  - google-api-python-client>=2.0

#### ゴール
**フェーズ1: Mac環境での動作確認（こすうけ）**
- [x] Mac環境で`python app.py`またはシェルスクリプトでUIを起動できる（完了: 2025-11-08）
- [x] タブ1で画像を選択し、ボタン一つで前処理（リサイズ・自動タグ付け・共通タグ追加）が完了する（完了: 2025-11-08）
- [x] タブ1で追加タグをカンマ区切りで指定し、フォルダごとに共通タグを追加できる（完了: 2025-11-11）
- [x] テーブル形式のUIで将来的に複数フォルダを追加できる設計になっている（完了: 2025-11-11）
- [x] 画像枚数ボタンをクリックすると、フォルダ内のファイル一覧が表示される（完了: 2025-11-11）
- [ ] タブ2で画像を選択し、タグを編集・保存できる
- [ ] タブ3でGoogle Driveに認証し、学習データをアップロードできる
- [ ] タブ3でGoogle Colabのノートブックを開くリンクが機能する
- [ ] タブ3で学習済みモデルをダウンロードし、Mac環境のStable Diffusion WebUIに自動配置できる
- [ ] エラー発生時にわかりやすいメッセージが表示される
- [ ] Mac環境でエンドツーエンドの動作確認が完了する

**進捗状況**: フェーズ1のタブ1（画像準備）が完了。追加タグ機能、テーブル形式のレイアウト、ファイル一覧表示も実装済み。タブ2、タブ3は未実装。

**フェーズ2: Windows環境への展開（なすみそ）**
- [ ] Windows環境で`nasumiso_trainer.bat`をダブルクリックしてUIを起動できる
- [ ] タブ1〜3の全機能がWindows環境でも動作する
- [ ] Windows環境のStable Diffusion WebUIへのモデル配置が正常に動作する
- [ ] 全体の処理フローが30-40分以内に完了する（学習時間20-30分含む）

**共通ゴール:**
- [ ] 将来的にローカルGPU学習への切り替えが容易な設計になっている
- [ ] README.mdに起動方法・使い方が記載されている

---

## 使い方

### 新規要件の追加
1. 上記のテンプレートを使用して要件を記述
2. ステータスを 📋 未着手 に設定
3. Claude Code に「work-plan.mdに作業計画を記述してください」と依頼

### 作業開始時
1. ステータスを 🔄 作業中 に変更
2. Claude Code が work-plan.md に作業計画を作成

### 作業完了時
1. 開発者が成果物を確認
2. 「REQ-XXXをcompleted/REQ-XXX/に移動してください」と指示
3. Claude Code が自動的に移動処理を実行
