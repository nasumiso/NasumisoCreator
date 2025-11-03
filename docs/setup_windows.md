# Windows環境セットアップガイド

Stable Diffusion WebUIをWindows環境にセットアップして、LoRAモデルを使った画像生成を行うための手順書です。

## 前提条件

### 動作環境

- **OS**: Windows 10 / 11（64bit）
- **GPU**: NVIDIA製GPU（RTX 3060以上推奨）
- **メモリ**: 16GB以上推奨
- **ストレージ**: 空き容量 20GB以上

### 必要なソフトウェア

セットアップ前に以下のソフトウェアをインストールしてください。

#### 1. Python 3.10.11

**ダウンロード**: https://www.python.org/downloads/release/python-31011/

- ページ下部の "Windows installer (64-bit)" をクリックしてダウンロード
- インストーラーを実行
- **重要**: 「Add Python to PATH」に必ずチェックを入れる
- "Install Now" をクリック
- インストール完了後、PCを再起動

**確認方法**:
```cmd
python --version
```
`Python 3.10.11` と表示されればOK

#### 2. Git for Windows

**ダウンロード**: https://git-scm.com/download/win

- "64-bit Git for Windows Setup" をクリックしてダウンロード
- インストーラーを実行
- 基本的にデフォルト設定のまま "Next" で進める
- インストール完了後、PCを再起動

**確認方法**:
```cmd
git --version
```
`git version 2.x.x` のように表示されればOK

---

## セットアップ手順

### Step 1: このリポジトリをダウンロード

以下のいずれかの方法でこのリポジトリを入手します。

#### 方法A: ZIPでダウンロード（推奨）

1. こすうけさんから共有されたZIPファイルをダウンロード
2. 適当な場所（例: `C:\Users\なすみそ\Documents\`）に解凍
3. 解凍したフォルダ内の `setup` フォルダを開く

#### 方法B: Git cloneでダウンロード

```cmd
cd %USERPROFILE%\Documents
git clone [リポジトリURL]
cd NasumisoCreator\setup
```

### Step 2: 自動セットアップスクリプトを実行

1. `setup` フォルダ内の **`setup_windows.bat`** を右クリック
2. 「管理者として実行」を選択
3. スクリプトが以下を自動的に実行します：
   - Python/Gitのインストール確認
   - Stable Diffusion WebUIのダウンロード
   - インストール先: `C:\Users\[ユーザー名]\Documents\stable-diffusion-webui\`

**所要時間**: 5〜10分（インターネット速度による）

### Step 3: モデルファイルを配置

#### 3-1. モデルファイルをダウンロード

こすうけさんから共有されたGoogle Driveリンクから以下をダウンロード：

- `anything-v5.safetensors` (ベースモデル)
- `nasumiso_v1.safetensors` (LoRAモデル)

#### 3-2. モデルファイルを配置

ダウンロードしたファイルを以下の場所に移動：

**ベースモデル**:
```
C:\Users\[ユーザー名]\Documents\stable-diffusion-webui\models\Stable-diffusion\
```
→ `anything-v5.safetensors` を配置

**LoRAモデル**:
```
C:\Users\[ユーザー名]\Documents\stable-diffusion-webui\models\Lora\
```
→ `nasumiso_v1.safetensors` を配置

詳細は [model_download.md](model_download.md) を参照してください。

### Step 4: Stable Diffusion WebUIを起動

1. 以下のファイルをダブルクリック：
   ```
   C:\Users\[ユーザー名]\Documents\stable-diffusion-webui\webui-user.bat
   ```

2. 初回起動時は依存関係のインストールが自動実行されます
   - **所要時間**: 10〜20分
   - 黒い画面（コマンドプロンプト）にたくさんのログが流れますが、正常です
   - 「Running on local URL: http://127.0.0.1:7860」と表示されたら完了

3. ブラウザで以下のURLにアクセス：
   ```
   http://127.0.0.1:7860/
   ```

4. Stable Diffusion WebUIの画面が表示されれば成功！

### Step 5（オプション）: デスクトップショートカットを作成

毎回ファイルを探すのが面倒な場合、デスクトップにショートカットを作成できます。

1. `setup` フォルダ内の **`create_shortcut.bat`** をダブルクリック
2. デスクトップに「Stable Diffusion WebUI」というショートカットが作成されます
3. 次回からはこのショートカットをダブルクリックするだけで起動できます

---

## トラブルシューティング

### Python/Gitが見つからないエラー

**症状**: `'python' は、内部コマンドまたは外部コマンド...` というエラー

**対処法**:
1. Python/Gitを再インストール
2. インストール時に「Add to PATH」にチェックを入れたか確認
3. PCを再起動

### ダウンロードが失敗する

**症状**: `git clone` でエラーが発生

**対処法**:
1. インターネット接続を確認
2. ファイアウォール/セキュリティソフトがブロックしていないか確認
3. 別のネットワーク（テザリングなど）で試す

### WebUIが起動しない

**症状**: `webui-user.bat` を実行してもすぐに画面が閉じる

**対処法**:
1. コマンドプロンプトから実行してエラーメッセージを確認：
   ```cmd
   cd %USERPROFILE%\Documents\stable-diffusion-webui
   webui-user.bat
   ```
2. エラーメッセージをこすうけさんに共有

### モデルが選択できない

**症状**: WebUIでモデルが表示されない

**対処法**:
1. モデルファイルが正しい場所に配置されているか確認
2. ファイル名が正しいか確認（拡張子 `.safetensors` まで含む）
3. WebUIを再起動

---

## 次のステップ

セットアップが完了したら、[quickstart_nasumiso.md](quickstart_nasumiso.md) を参照して、実際に画像を生成してみましょう！
