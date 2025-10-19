# REQ-003: CoreMLでの高速化

## ステータス
✅ 完了

## 要求内容
auto_caption.pyについて、CoreMLで高速化したい。MacでCUDAは使えないので。

## 必要な要素
CoreMLを使えるようにして、使って。
もしそれが使えず、他の代替手段があるなら検討して。

## ゴール
CoreMLもしくは代替手段で、auto_caption.py の推論が高速化されていること。

## 実装結果
- CoreMLExecutionProviderを実装（ONNX Runtime使用）
- ベンチマークを実施した結果、小規模バッチ処理ではCPU専用より遅いことが判明
- デフォルトをCPU実行に変更、`--use-coreml`オプションで有効化可能にした
- CoreML実装は将来的な活用のために残置

## 完了日
2025-10-19
