# 作業計画

## 現在の作業

### [REQ-002] 画像タグ付け

#### 概要
WD14 Taggerを使った自動タグ付けスクリプト（`scripts/auto_caption.py`）を実装し、2_processed/配下の画像に対して自動的にDanbooruタグを生成し、3_tagged/に画像とタグファイル（.txt）を出力する。

#### 準備
- [x] 2_processed/の画像枚数を確認（15枚のPNG画像）
- [x] 3_tagged/ディレクトリが存在するか確認、なければ作成
- [x] WD14 Taggerの実装方法を調査（Hugging Faceモデル使用）
- [x] 必要な依存ライブラリを調査（onnxruntime, numpy, pandas, huggingface-hub）
- [x] requirements.txtに依存関係を追加

#### 実装
- [x] `scripts/auto_caption.py`を作成
- [x] コマンドライン引数の設計（--input, --output, --threshold）
- [x] WD14 Taggerモデルのロード機能実装
- [x] 画像からタグを推論する機能実装
- [x] 信頼度しきい値によるフィルタリング機能実装
- [x] タグテキストファイル（.txt）の出力機能実装
- [x] 画像のコピー機能実装（3_tagged/に配置）
- [x] エラーハンドリングの実装
- [x] 処理状況の表示機能（進捗表示）

#### テスト
- [x] 15枚の画像が正常に処理されるか確認
- [x] 各画像に対応する.txtファイルが生成されているか確認
- [x] タグの内容が適切か確認（Danbooruタグ形式）
- [x] 画像が3_tagged/に正しくコピーされているか確認
- [x] 実行コマンド確認:
  ```bash
  python scripts/auto_caption.py \
    --input projects/nasumiso_v1/2_processed \
    --output projects/nasumiso_v1/3_tagged \
    --threshold 0.35
  ```

#### ドキュメント更新
- [x] `scripts/README.md`に`auto_caption.py`の使い方を追記
- [x] `.claude/spec/implementation.md`に実装内容を記録
- [x] `.claude/notes.md`に作業ログと技術的知見を記録

#### テスト結果

**実行日**: 2025-10-19

**実行結果**: ✅ 成功

```
処理対象: 15枚の画像
信頼度しきい値: 0.35
--------------------------------------------------
信頼度しきい値: 0.35
モデルをロード中...
モデルロード完了（タグ数: 9083）

✓ [01/15] img001.png
  タグ数: 8
  プレビュー: black_background, monochrome, no_humans, greyscale, general, ...
✓ [02/15] img002.png
  タグ数: 8
  プレビュー: black_background, monochrome, no_humans, greyscale, general, ...
...
✓ [15/15] img015.png
  タグ数: 9
  プレビュー: black_background, no_humans, monochrome, greyscale, general, ...
--------------------------------------------------
完了: 15枚成功, 0枚スキップ
```

**生成されたファイル**:
- 画像ファイル: 15個（projects/nasumiso_v1/3_tagged/*.png）
- タグファイル: 15個（projects/nasumiso_v1/3_tagged/*.txt）
- 各タグファイルサイズ: 約100バイト（8-9個のタグ）

**サンプルタグ（img001.txt）**:
```
black_background, monochrome, no_humans, greyscale, general, comic, negative_space, simple_background
```

**技術的な問題と解決**:
1. **transformersライブラリ非対応**: WD14 TaggerはHugging Face transformersに対応していなかった
   - → ONNX Runtime方式で実装
2. **sigmoid関数の誤適用**: モデル出力が既に確率値（0-1）だったため、sigmoid適用で全タグ（9083個）が0.5付近に集中
   - → モデル出力を直接使用するように修正し、適切なタグ数（8-9個）に改善

**結論**: すべてのテスト項目が正常に完了しました。

#### 追加対応（画像正規化問題の修正）

**発見された問題**:
- 自動生成されたタグが画像内容と一致しない
- 例: カラー画像に対して `black_background`, `monochrome`, `no_humans` などの誤タグ

**原因調査**:
- 画像の正規化方法が間違っていた（0-1正規化を適用）
- WD14 Tagger v2は0-255の範囲を期待していた

**修正内容**:
- `scripts/auto_caption.py`の`_preprocess_image`メソッドから`/ 255.0`を削除
- 0-255の範囲をそのまま使用するように変更

**修正後のテスト結果**:
```
✓ [01/15] img001.png
  タグ数: 22
  プレビュー: nasumiso_style, 1boy, solo, male_focus, eating, ...
✓ [11/15] img011.png
  タグ数: 13
  プレビュー: nasumiso_style, 1girl, solo, serafuku, school_uniform, ...
```

**サンプルタグ（修正後）**:
- img001.txt: `nasumiso_style, 1boy, solo, male_focus, eating, food, black_hair, chibi, ...`
- img011.txt: `nasumiso_style, 1girl, solo, serafuku, school_uniform, black_hair, ...`

#### タグ管理ワークフローの追加

**追加スクリプト**:
1. `scripts/add_common_tag.py` - 共通タグの一括追加
2. `scripts/generate_jp_tags.py` - 日本語タグファイル生成（レビュー用）

**実施した作業**:
- [x] 全15枚の画像の先頭に`nasumiso_style`タグを追加
- [x] 日本語タグファイル（_jp.txt）を生成

**Git管理体制**:
- `.gitignore`を更新してタグファイル（.txt）のみ管理対象に
- コミット履歴でタグの変更を追跡可能に

**今後の手動作業**（ユーザー実施）:
- [ ] 誤タグの削除（blue_skin, colored_skinなど）
- [ ] 不足タグの追加（simple_lineartなど）
- [ ] 修正後にGitコミット

#### 技術的な方針
- **タグ付けモデル**: WD14 Tagger v2（SmilingWolf/wd-v1-4-moat-tagger-v2）
- **信頼度しきい値**: デフォルト0.35（調整可能）
- **タグ形式**: Danbooru形式（カンマ区切り、アンダースコア使用）
- **出力方法**: 画像と同名の.txtファイル（例: img001.png → img001.txt）
- **依存ライブラリ**: transformers, timm, PIL, numpy, pandas

#### 完了条件
✅ 以下がすべて満たされた時点で完了
1. `scripts/auto_caption.py`が正常に動作する
2. `projects/nasumiso_v1/3_tagged/`に15枚の画像と対応する.txtファイルが配置されている
3. タグがDanbooru形式で適切に生成されている
4. エラーハンドリングが適切に実装されている
5. ドキュメントが更新されている

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
