# 作業計画: [REQ-001] 画像管理

## 概要
画像の前処理スクリプト（`scripts/prepare_images.py`）を実装し、1_raw_images/配下の画像を512x512にリサイズ、連番リネームして2_processed/に出力する。

## 準備
- [x] 1_raw_images/の画像枚数と形式を確認（15枚のPNG画像を確認済み）
- [x] Pillowライブラリがrequirements.txtに含まれているか確認
- [x] 2_processed/ディレクトリが存在するか確認、なければ作成
- [x] 開発手順書.mdのステップ②の仕様を確認

## 実装
- [x] `scripts/prepare_images.py`を作成
- [x] コマンドライン引数の設計（--input, --output, --size）
- [x] 画像読み込み機能の実装（PIL/Pillow使用）
- [x] リサイズ機能の実装（アスペクト比維持 + 中央クロップ）
- [x] 連番リネーム機能の実装（img001.png, img002.png, ...形式）
- [x] エラーハンドリングの実装（非画像ファイルのスキップ、破損ファイル対応）
- [x] 処理状況の表示機能（進捗表示）

## テスト
- [x] 15枚の画像が正常に処理されるか確認
- [x] 出力画像が512x512にリサイズされているか確認
- [x] 連番リネーム（img001.png～img015.png）が正しく行われているか確認
- [x] アスペクト比が異なる画像の処理結果を目視確認
- [x] .DS_Storeなど非画像ファイルが含まれる場合の挙動確認
- [x] 実行コマンド確認:
  ```bash
  python scripts/prepare_images.py \
    --input projects/nasumiso_v1/1_raw_images \
    --output projects/nasumiso_v1/2_processed \
    --size 512
  ```

## テスト結果

**実行コマンド**:
```bash
python3 scripts/prepare_images.py \
  --input projects/nasumiso_v1/1_raw_images \
  --output projects/nasumiso_v1/2_processed \
  --size 512
```

**結果**: ✅ 成功
- 処理対象: 15枚の画像
- 成功: 15枚（100%）
- スキップ: 0枚
- 処理時間: 約1秒

**出力確認**:
- すべての画像が512x512のPNG形式
- ファイル名: img001.png～img015.png（連番形式）
- 画質: 許容範囲内（目視確認済み）

**エラーハンドリング確認**:
- .DS_Storeなど非画像ファイルは自動スキップ
- エラー時も処理継続、最後に結果報告

## ドキュメント更新
- [x] `scripts/README.md`に`prepare_images.py`の使い方を追記
- [x] `.claude/spec/implementation.md`に実装内容を記録
- [x] `.claude/notes.md`に作業ログと技術的知見を記録

## 技術的な方針
- **リサイズ方法**: 短辺を512pxに合わせて拡大/縮小し、長辺を中央クロップ
- **品質保持**: PNG形式で保存（ロスレス）
- **リサンプリング**: Pillow.Image.LANCZOS（高品質）使用
- **コメント規則**: 関数のdocstringは日本語、型ヒント活用

## 完了条件
✅ 以下がすべて満たされた時点で完了
1. `scripts/prepare_images.py`が正常に動作する
2. `projects/nasumiso_v1/2_processed/`に15枚の512x512画像が連番で配置されている
3. 画質が許容範囲内で保たれている
4. エラーハンドリングが適切に実装されている
5. ドキュメントが更新されている
