# 開発ワークフロー詳細

このドキュメントは、なすみそクリエイタープロジェクトの開発ワークフローとドキュメント管理ルールを定義します。

---

## 6ステップの開発サイクル

このプロジェクトは以下の6ステップで進行します：

### Step 1: 作業指示
開発者が作業指示を出します。大きな作業は`requirements.md`に記述します。

### Step 2: 作業計画
Claude Codeが`work-plan.md`に作業計画をチェックリスト形式で記述します。

### Step 3: 計画確認
開発者が計画を確認し、実装指示を出します。

### Step 4: 実装
Claude Codeが実装を行います。進捗は`work-plan.md`のチェックリストで管理します。
**注**: この段階では`spec.md`や`reference.md`の更新は不要です。

### Step 5: テスト
Claude Codeがテストを実行し、`work-plan.md`のチェックリストを完了させます。問題があれば`notes.md`に記録します。

### Step 6: 仕様反映と完了処理
開発者が成果物を確認後、以下を実行：
- `spec/spec.md`に機能仕様を追記（ユーザー向け）
- `spec/reference.md`に技術詳細を追記（開発者向け）
- `completed/REQ-XXX/`フォルダに移動

---

## ドキュメント構成

```
.claude/
├── README.md              # クイックリファレンス
├── workflow.md            # このファイル（ワークフロー詳細）
├── requirements.md        # 現在の作業指示（進行中・未着手のみ）
├── work-plan.md           # 現在の作業計画・チェックリスト
├── notes.md               # 現在のREQ作業中の気づき・メモ
├── KNOWLEDGE.md           # プロジェクト全体の知見・ノウハウ
├── spec/                  # 仕様書ディレクトリ
│   ├── overview.md       # プロジェクト概要・アーキテクチャ
│   ├── spec.md           # 実装済み機能の使い方（ユーザー向け）
│   └── reference.md      # 技術詳細・API仕様（開発者向け）
└── completed/             # 完了した要件ごとのフォルダ
    └── REQ-XXX/
        ├── requirement.md  # 要件詳細
        ├── work-plan.md    # 作業計画・チェックリスト
        └── notes.md        # 気づき・メモのログとふりかえり
```

---

## 各ドキュメントの役割

### requirements.md
- **目的**: 大きな作業の指示を記述する
- **記述者**: 主に開発者
- **形式**: `[REQ-XXX]` 形式で管理
- **ステータス**: 🔄作業中 / 📋未着手
- **保持ルール**: 現在進行中と未着手のみ。完了したら`completed/REQ-XXX/`へ移動

### spec/ ディレクトリ
- **目的**: プロジェクトの仕様を構造化して記録
- **記述者**:
  - 初期作成: 開発者またはClaude Code
  - 実装完了後の追記: Claude Code（spec.mdとreference.mdに記録）
  - 随時編集: 開発者（必要に応じて修正・更新）
- **ファイル構成**:
  - **overview.md**: プロジェクト概要・アーキテクチャ
  - **spec.md**: 実装済み機能の使い方（ユーザー向け・「何ができるか」に焦点）
  - **reference.md**: 技術詳細・API仕様（開発者向け・パラメータ、処理フロー、技術制約）
- **保持ルール**: 常に最新の仕様を保持

### work-plan.md
- **目的**: 作業計画と進捗をチェックリストで管理、テスト結果も記録
- **記述者**: Claude Code（Step 2で作成、Step 5でテスト結果を反映）
- **形式**: `- [ ]` チェックリスト形式で記述
- **内容**: 準備/実装/テスト の各チェックリスト、テスト実行結果
- **保持ルール**: 現在の作業のみ。完了したら`completed/REQ-XXX/`へ移動

### notes.md
- **目的**: 現在のREQ作業中の気づき・メモを記録
- **記述者**: 主にClaude Code、開発者も追記可
- **内容**: 作業中の気づき、解決した問題、テストで発見した問題点など
- **保持ルール**: REQ作業中のみ使用。完了時に`completed/REQ-XXX/notes.md`に移動し、テンプレに戻る

### KNOWLEDGE.md
- **目的**: プロジェクト全体を通して得られた気づき・ノウハウを蓄積
- **記述者**: 主にClaude Code（完了処理時）、開発者も追記可
- **内容**: REQ固有ではなく、プロジェクト横断で役立つ知見、技術Tips、設計パターンなど
- **保持ルール**: 常に保持。完了処理時に、notes.mdから汎用的な知見を抽出して追記

### completed/REQ-XXX/
- **目的**: 完了した要件に関する全情報を保管
- **構造**:
  - `requirement.md`: その要件の詳細（requirements.mdから抽出）
  - `work-plan.md`: 作業計画と実行結果
  - `notes.md`: その作業で得られた気づき・メモのログとふりかえり・感想
- **作成タイミング**: Step 6完了後、開発者の指示で移動

---

## 完了処理の詳細

要件が完了したら（Step 6完了後）：

### 1. 開発者が指示
```
「REQ-XXXを完了フォルダに移動してください」
```

### 2. Claude Codeが実行する処理
1. `completed/REQ-XXX/`フォルダを作成
2. requirements.mdから該当要件を抽出して`completed/REQ-XXX/requirement.md`として保存
3. work-plan.mdの内容を`completed/REQ-XXX/work-plan.md`として保存
4. notes.mdの内容を適宜要約して、`completed/REQ-XXX/notes.md`として保存、ふりかえりとして感想を記述
5. 実装した機能の使い方を`spec/spec.md`に追記（ユーザー向け・「何ができるか」）
6. 実装した機能の技術詳細を`spec/reference.md`に追記（開発者向け・パラメータ、処理フロー、技術制約）
7. notes.mdから汎用的な知見を抽出して`KNOWLEDGE.md`に追記
8. requirements.mdとwork-plan.mdから該当部分を削除
9. notes.mdをテンプレに戻す

### 3. 完了後の状態
- requirements.mdは次の作業のみ
- work-plan.mdは空（または次の作業待ち）
- notes.mdはテンプレに戻る
- 完了した要件の実装履歴は`completed/REQ-XXX/notes.md`に保存
- 実装した機能の使い方は`spec/spec.md`に追記（ユーザー向け）
- 実装した機能の技術詳細は`spec/reference.md`に追記（開発者向け）
- 汎用的な知見は`KNOWLEDGE.md`に蓄積

---

## 簡略コマンド

開発者は以下の簡略表現で指示できます。Claude Codeはこれを理解し、適切に実行してください。

### 作業計画
```
plan REQ-XXX
計画 REQ-XXX
```
→ requirements.mdのREQ-XXXについて、work-plan.mdに作業計画をチェックリスト形式で記述

### 実装開始
```
implement REQ-XXX
実装 REQ-XXX
```
→ work-plan.mdの計画に基づいて実装を開始

### テスト実行
```
test REQ-XXX
テスト REQ-XXX
```
→ テストを実行し、work-plan.mdのチェックリストを完了。問題があればnotes.mdに記録

### 完了処理
```
complete REQ-XXX
完了 REQ-XXX
archive REQ-XXX
```
→ completed/REQ-XXX/フォルダを作成し、関連ファイルを移動

### 複合指示
```
implement and test REQ-XXX
```
→ 実装とテストを連続実行

---

## 開発開始時の確認事項

Claude Codeでの作業開始時は：
1. この`workflow.md`を読む
2. `spec/`ディレクトリでプロジェクトの仕様を確認
3. `requirements.md`で現在の作業指示を確認
4. `work-plan.md`で進行中のタスクがあるか確認
5. 新規作業の場合は`work-plan.md`に計画を記述してから実装開始
6. 要件完了時は開発者の指示で`completed/REQ-XXX/`に移動
