# [REQ-004] フェーズ1完了に伴うドキュメント整理

ステータス: ✓ 完了

## 要求内容
一旦overview.mdのフェーズ1が完了しました。
サンプル画像の用意からタグ付け、Colab上での学習、WebUIでの推論(生成)ができました。それに伴う、現状の実装ベースでドキュメントに反映、整理したい。

私が思いつくのを以降上げるので考慮しながら、各種ドキュメントを整理して。

## overview.md について
- 4_datasetフォルダ は使っていません。 3_tagged で処理しています。
- `train_lora_nasutomo.ipynb` が、学習用のColabノートブックになります。
- outputsフォルダは使っていません。代わりに、
  `/Users/k_sohara/stable-diffusion-webui/` にStableDiffusionのWebUIをインストールしています。そこから画像生成を行い、そこのoutputs フォルダに生成物があります。

## spec.mdについて
- ステップ5，ステップ6について現状の実装を反映させて。

## train_lora_nasutomo.ipynb について
- 学習のベースモデルは、anything-v5.safetensorsを使用しています。

## StableDiffusionWebUIについて
- このコマンドで、StableDiffusion WebUIが起動できます。
```
cd ~/stable-diffusion-webui
./webui.sh
```
'http://127.0.0.1:7860/' にアクセス

## 必要な要素
- （実装に必要な要素）
- （考慮すべき点）

## ゴール
- 各種ドキュメントが現状実装に即したものになっている
- できるだけ各ドキュメントに重複がない
