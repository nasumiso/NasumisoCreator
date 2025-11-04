# なすみそクリエイター - クイックスタートガイド

Stable Diffusion WebUIを使って、なすみそさんの画風で画像を生成する方法を説明します。

## 準備

以下が完了していることを確認してください：

- ✅ Stable Diffusion WebUIがインストール済み
- ✅ ベースモデル（anything-v5.safetensors）が配置済み
- ✅ LoRAモデル（nasumiso_v1.safetensors）が配置済み

まだの方は [setup_windows.md](setup_windows.md) を参照してセットアップを完了してください。

---

## WebUIの起動

1. デスクトップの「Stable Diffusion WebUI」ショートカットをダブルクリック
   - または `C:\Users\[ユーザー名]\Documents\stable-diffusion-webui\webui-user.bat` を実行

2. 黒い画面が開き、たくさんのログが流れます（正常です）

3. 「Running on local URL: http://127.0.0.1:7860」と表示されたら、ブラウザで以下にアクセス：
   ```
   http://127.0.0.1:7860/
   ```

---

## 画像生成の基本

### 1. モデルの選択

画面左上の「Stable Diffusion checkpoint」から `anything-v5.safetensors` を選択します。

### 2. プロンプトの入力

**プロンプト（Prompt）** = 生成したい画像の説明を英語で入力します。

#### 基本的なプロンプト例

```
<lora:nasumiso_v1:1.0>, nasumiso_style, 1girl, solo, smile, long hair, blue eyes, school uniform
```

**プロンプトの構成要素**:

- `<lora:nasumiso_v1:1.0>`: なすみそLoRAを強度1.0で適用
- `nasumiso_style`: なすみそさんの画風を指定
- `1girl`: 女の子1人
- `solo`: 単独
- `smile`: 笑顔
- `long hair`: 長髪
- `blue eyes`: 青い瞳
- `school uniform`: 制服

#### その他の例

**女の子・カジュアル**:
```
<lora:nasumiso_v1:1.0>, nasumiso_style, 1girl, solo, casual clothes, sitting, indoor, window
```

**男の子**:
```
<lora:nasumiso_v1:1.0>, nasumiso_style, 1boy, solo, cool, jacket, outdoor
```

**2人**:
```
<lora:nasumiso_v1:1.0>, nasumiso_style, 2girls, friends, talking, cafe
```

### 3. ネガティブプロンプトの入力

**ネガティブプロンプト（Negative Prompt）** = 生成したくない要素を指定します。

#### 推奨のネガティブプロンプト

```
lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry
```

これにより、低品質な画像や解剖学的におかしい画像を避けられます。

### 4. パラメータの設定

#### 推奨設定（初心者向け）

| パラメータ | 推奨値 | 説明 |
|----------|-------|------|
| **Sampling method** | DPM++ 2M Karras | 高品質で安定 |
| **Sampling steps** | 20〜30 | 品質と速度のバランス |
| **Width / Height** | 512 x 512 | 標準サイズ |
| **CFG Scale** | 7〜9 | プロンプトへの忠実度 |
| **Seed** | -1（ランダム） | 毎回異なる画像 |

### 5. 生成実行

「Generate」ボタンをクリックすると、画像生成が開始されます。

**所要時間**: 数秒〜数十秒（GPUの性能による）

---

## WebUI画面の見方

```
┌─────────────────────────────────────────────────────────┐
│ [Stable Diffusion checkpoint] anything-v5.safetensors   │  ← モデル選択
├─────────────────────────────────────────────────────────┤
│ Prompt:                                                 │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ <lora:nasumiso_v1:1.0>, nasumiso_style, 1girl, ... │ │  ← プロンプト入力
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ Negative Prompt:                                        │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ lowres, bad anatomy, bad hands, ...                 │ │  ← ネガティブプロンプト
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ [Sampling method] [Steps] [Width] [Height] [CFG Scale] │  ← パラメータ設定
│                                                         │
│ [🎴 LoRA] [Generate]                                    │  ← ボタン類
├─────────────────────────────────────────────────────────┤
│                                                         │
│          【生成された画像がここに表示】                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 応用テクニック

### LoRAの強度を調整する

`<lora:nasumiso_v1:1.0>` の最後の数値を変更することで、画風の強さを調整できます。

- `<lora:nasumiso_v1:0.5>`: 弱め（元のモデルの特徴が強く出る）
- `<lora:nasumiso_v1:0.8>`: やや弱め
- `<lora:nasumiso_v1:1.0>`: 標準（推奨）
- `<lora:nasumiso_v1:1.2>`: やや強め

### 同じ画像を再生成する

気に入った画像のSeed値をメモしておき、次回同じSeed値を入力することで、似た構図の画像を生成できます。

生成された画像の下に表示される「Seed: 1234567890」のような数値をコピーして、次回のSeedパラメータに入力します。

### 高解像度化（Hires. fix）

より高解像度な画像を生成したい場合：

1. 「Hires. fix」にチェックを入れる
2. 「Upscaler」は "Latent" または "R-ESRGAN 4x+" を選択
3. 「Upscale by」を 2.0 に設定（512x512 → 1024x1024）

**注意**: 生成時間が長くなります

### バッチ生成

一度に複数の画像を生成したい場合：

- **Batch count**: 何回生成するか（例: 4）
- **Batch size**: 1回あたり何枚生成するか（例: 1）

例: Batch count=4, Batch size=1 → 合計4枚の画像を順番に生成

---

## プロンプトの書き方のコツ

### 基本ルール

1. **英語で記述**: 日本語は使えません
2. **カンマ区切り**: 要素をカンマで区切る
3. **具体的に**: 曖昧な表現より具体的な単語
4. **順番が重要**: 前に書いた要素ほど強く反映される

### よく使う単語

#### キャラクター
- `1girl` / `1boy`: 女の子1人 / 男の子1人
- `2girls`: 女の子2人
- `solo`: 単独

#### 表情
- `smile`: 笑顔
- `happy`: 嬉しそう
- `sad`: 悲しそう
- `surprised`: 驚いた
- `crying`: 泣いている

#### 髪型・髪色
- `long hair` / `short hair`: 長髪 / 短髪
- `ponytail`: ポニーテール
- `black hair` / `brown hair` / `blonde hair`: 黒髪 / 茶髪 / 金髪

#### 服装
- `school uniform`: 制服
- `casual clothes`: カジュアルな服
- `dress`: ドレス
- `hoodie`: パーカー

#### 場所・背景
- `outdoor`: 屋外
- `indoor`: 屋内
- `school`: 学校
- `park`: 公園
- `cafe`: カフェ
- `bedroom`: 寝室

#### ポーズ・構図
- `standing`: 立っている
- `sitting`: 座っている
- `looking at viewer`: こちらを見ている
- `from side`: 横から
- `upper body`: 上半身
- `full body`: 全身

---

## よくある質問（FAQ）

### Q1: 生成された画像が期待と違う

**A**: 以下を試してください：
- プロンプトをより具体的にする
- CFG Scaleを調整（7〜9の間で）
- 何度か生成し直す（Seedが-1の場合、毎回異なる結果）
- LoRAの強度を調整（0.8〜1.2の間で）

### Q2: 画像が崩れている

**A**:
- Sampling stepsを増やす（20→30）
- ネガティブプロンプトを追加
- CFG Scaleを下げる（9→7）
- 別のSampling methodを試す（Euler a など）

### Q3: 生成が遅い

**A**:
- Sampling stepsを減らす（30→20）
- 画像サイズを小さくする（512x512推奨）
- Hires. fixをオフにする
- Batch sizeを1にする

### Q4: LoRAが効いていない気がする

**A**:
- プロンプトの最初に `<lora:nasumiso_v1:1.0>` があるか確認
- `nasumiso_style` も忘れずに入れる
- LoRAの強度を上げる（1.0→1.2）
- WebUIを再起動してモデルを再読み込み

### Q5: WebUIが起動しない

**A**:
- PCを再起動
- ファイアウォールやセキュリティソフトを一時的に無効化
- エラーメッセージをこすうけさんに共有

---

## 画像の保存

生成された画像は自動的に以下のフォルダに保存されます：

```
C:\Users\[ユーザー名]\Documents\stable-diffusion-webui\outputs\txt2img-images\[日付]
```

画像を右クリック→「名前を付けて保存」でも保存できます。

---

## 次のステップ

慣れてきたら以下を試してみましょう：

1. **img2img**: 元の画像をベースに新しい画像を生成
2. **Inpainting**: 画像の一部を修正
3. **ControlNet**: ポーズや構図をより細かく制御

詳しくはこすうけさんに相談してください！

---

## トラブル時の連絡先

わからないことや問題が発生した場合は、こすうけさんに以下の情報と共に連絡してください：

- エラーメッセージのスクリーンショット
- 実行した手順
- 使用したプロンプト

楽しい創作ライフを！
