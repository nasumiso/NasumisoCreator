# モデルファイルのダウンロードと配置

Stable Diffusion WebUIで画像生成を行うには、2種類のモデルファイルが必要です。

## 必要なモデルファイル

### 1. ベースモデル（Stable Diffusion本体）

- **ファイル名**: `anything-v5.safetensors`
- **サイズ**: 約 4.27 GB
- **用途**: 画像生成の基礎となるモデル

### 2. LoRAモデル（なすみそ画風）

- **ファイル名**: `nasumiso_v1.safetensors`
- **サイズ**: 約 150 MB
- **用途**: なすみそさんの画風を学習したモデル

---

## ダウンロード方法

### こすうけさんから共有されたGoogle Driveリンクを使用

1. こすうけさんから送られたGoogle Driveのリンクをブラウザで開く
2. 以下の2つのファイルを探してダウンロード：
   - `anything-v5.safetensors`
   - `nasumiso_v1.safetensors`

**ダウンロード時の注意**:
- ファイルサイズが大きいため、安定したインターネット接続環境で行ってください
- ダウンロード完了まで数分〜数十分かかる場合があります
- ダウンロード中にブラウザを閉じないでください

---

## モデルファイルの配置

ダウンロードしたファイルを以下の場所に移動します。

### ベースモデルの配置

1. ダウンロードした `anything-v5.safetensors` を以下のフォルダに移動：

```
C:\Users\[ユーザー名]\Documents\stable-diffusion-webui\models\Stable-diffusion\
```

**確認方法**:
- フォルダを開いて `anything-v5.safetensors` が表示されていればOK
- ファイルサイズが約 4.27 GB であることを確認

### LoRAモデルの配置

1. ダウンロードした `nasumiso_v1.safetensors` を以下のフォルダに移動：

```
C:\Users\[ユーザー名]\Documents\stable-diffusion-webui\models\Lora\
```

**確認方法**:
- フォルダを開いて `nasumiso_v1.safetensors` が表示されていればOK
- ファイルサイズが約 150 MB であることを確認

---

## フォルダの開き方（Windows）

フォルダへの移動方法がわからない場合：

### 方法1: エクスプローラーのアドレスバーを使用

1. エクスプローラーを開く（Windows + E）
2. 上部のアドレスバーに以下をコピー＆ペースト：
   ```
   %USERPROFILE%\Documents\stable-diffusion-webui\models\Stable-diffusion
   ```
3. Enter キーを押す

### 方法2: 手動で移動

1. エクスプローラーを開く
2. 左側のサイドバーから「ドキュメント」をクリック
3. `stable-diffusion-webui` フォルダを開く
4. `models` フォルダを開く
5. `Stable-diffusion` または `Lora` フォルダを開く

---

## 配置確認

すべてのモデルファイルが正しく配置されているか確認します。

### Stable Diffusion WebUIで確認

1. `webui-user.bat` を起動
2. ブラウザで http://127.0.0.1:7860/ にアクセス
3. 画面左上の「Stable Diffusion checkpoint」ドロップダウンをクリック
4. `anything-v5.safetensors` が表示されていればOK

### LoRAの確認

1. WebUI画面で「Generate」ボタンの下にある「🎴」（LoRAボタン）をクリック
2. `nasumiso_v1` が表示されていればOK

---

## トラブルシューティング

### モデルが表示されない

**原因1**: ファイルの配置場所が間違っている
- 配置先のフォルダパスを再確認してください
- ファイル名のスペルミスがないか確認してください

**原因2**: WebUIがモデルを認識していない
- WebUIを再起動してください（`webui-user.bat` の画面を閉じて再実行）

**原因3**: ファイルのダウンロードが不完全
- ファイルサイズを確認してください
- サイズが明らかに小さい場合は再ダウンロードしてください

### ダウンロードが途中で止まる

- ブラウザのダウンロードマネージャーで「再開」を試してください
- Google Driveの「ダウンロード制限」に達している場合は、時間をおいて再試行してください

---

## 新しいLoRAモデルを追加する場合

学習で新しいLoRAモデルが作成された場合：

1. Google Driveから新しい `.safetensors` ファイルをダウンロード
2. `C:\Users\[ユーザー名]\Documents\stable-diffusion-webui\models\Lora\` に配置
3. WebUIを再起動
4. LoRAリストに表示されることを確認

---

次は [quickstart_nasumiso.md](quickstart_nasumiso.md) を参照して、実際に画像を生成してみましょう！
