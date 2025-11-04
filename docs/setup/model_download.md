# モデルファイルのダウンロードと配置

Stable Diffusion WebUIで画像生成を行うには、2種類のモデルファイルが必要です。

## 必要なモデルファイル

| モデル | ファイル名 | サイズ | 用途 |
|--------|-----------|--------|------|
| ベースモデル | `anything-v5.safetensors` | 約 4.27 GB | 画像生成の基礎 |
| LoRAモデル | `nasumiso_v1.safetensors` | 約 150 MB | なすみそ画風 |

---

## ダウンロード

こすうけさんから共有された[Google Driveリンク](https://drive.google.com/drive/folders/1YAcEx0EJ4yVIPVVD46W5IqcNOzfsKQNu?usp=drive_link)から上記2ファイルをダウンロードしてください。

**注意**: ファイルサイズが大きいため、安定したインターネット接続環境で行ってください。

---

## 配置

ダウンロードしたファイルを以下の場所に移動します。

### ベースモデル

```
C:\Users\[ユーザー名]\Documents\stable-diffusion-webui\models\Stable-diffusion\
```
→ `anything-v5.safetensors` を配置

### LoRAモデル

```
C:\Users\[ユーザー名]\Documents\stable-diffusion-webui\models\Lora\
```
→ `nasumiso_v1.safetensors` を配置

**フォルダの開き方**: エクスプローラーのアドレスバーに `%USERPROFILE%\Documents\stable-diffusion-webui\models\Stable-diffusion` をコピペして Enter

---

## 配置確認

1. `webui-user.bat` を起動
2. ブラウザで http://127.0.0.1:7860/ にアクセス
3. 左上の「Stable Diffusion checkpoint」で `anything-v5.safetensors` が表示されていればOK
4. 「🎴」ボタンで `nasumiso_v1` が表示されていればOK

---

## トラブルシューティング

### モデルが表示されない
- 配置場所とファイル名を再確認
- WebUIを再起動
- ファイルサイズを確認（ダウンロードが不完全な場合は再DL）

### 新しいLoRAモデルを追加する場合
1. Google Driveから `.safetensors` ファイルをダウンロード
2. `models\Lora\` に配置
3. WebUIを再起動

---

次は [quickstart_nasumiso.md](quickstart_nasumiso.md) を参照して、実際に画像を生成してみましょう！
