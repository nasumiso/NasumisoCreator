# 作業計画

## 現在の作業

### [REQ-003] CoreMLでの高速化

#### 準備
- [x] 現在のauto_caption.pyの実装を確認
- [x] ONNX RuntimeのCoreMLExecutionProviderについて調査
- [x] 必要な依存パッケージを特定

#### 実装
- [x] requirements.txtにonnxruntime-coremlを追加（またはonnxruntimeを更新）
- [x] auto_caption.pyにCoreMLExecutionProviderを追加
- [x] フォールバック処理を実装（CoreML利用不可時はCPUにフォールバック）
- [x] 実行時のプロバイダー情報をログ出力

#### テスト
- [x] CoreML対応版で画像タグ付けを実行
- [x] 正常に動作することを確認
- [x] 使用されているプロバイダーを確認（CoreML or CPU）
- [x] 処理速度の変化を測定（ベンチマーク実施）

#### ドキュメント更新
- [x] spec.mdを更新（CoreML対応を明記）
- [x] reference.mdを更新（技術詳細を追記）
- [x] notes.mdに実装時の気づきを記録

#### テスト結果

**テスト環境**:
- マシン: MacBook Air M1
- OS: macOS (Darwin 24.6.0)
- Python: 3.9.6
- 仮想環境: .venv

**テスト実行**: 2025-10-19
- コマンド: `python scripts/auto_caption.py --input projects/nasumiso_v1/2_processed --output projects/nasumiso_v1/3_tagged_coreml_test --threshold 0.35`
- 画像数: 15枚

**結果**: ✅ 成功
- 使用プロバイダー: CoreMLExecutionProvider, CPUExecutionProvider
- CoreML高速化: 有効（Apple Neural Engine使用）
- 処理結果: 15枚すべて正常に処理（成功: 15, スキップ: 0）
- CoreMLサポート: 1471ノード中1088ノード（約74%）がCoreMLで実行

**確認事項**:
- ✓ CoreMLExecutionProviderが正常に使用されている
- ✓ すべての画像が正常にタグ付けされた
- ✓ プロバイダー情報が正しくログ出力されている

**ベンチマーク結果**:

| モード | 総処理時間 | 平均処理時間/枚 | 比較 |
|--------|-----------|----------------|------|
| CPU専用 | 16.05秒 | 1.070秒/枚 | ベースライン |
| CoreML有効 | 43.80秒 | 2.920秒/枚 | **2.7倍遅い** |

**結論**:
- CoreMLは正常に動作するが、このユースケースでは高速化効果なし
- 理由: ハイブリッド実行のオーバーヘッド、小規模バッチ処理、軽量モデル
- 実装としては成功（フォールバック機能も確認済み）
- **対応**: デフォルトをCPU実行に変更、`--use-coreml`オプションで有効化可能にした

---

**技術的な検討事項**

CoreMLExecutionProvider:
- ONNX RuntimeのCoreML対応プロバイダー
- Apple Silicon（Neural Engine）を活用
- 実装方針: `providers = ['CoreMLExecutionProvider', 'CPUExecutionProvider']`
- フォールバック戦略: CoreML利用不可時は自動的にCPUにフォールバック

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
