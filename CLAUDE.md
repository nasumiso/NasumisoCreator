# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

**NasumisoCreator** は、ドキュメント駆動型の構造化開発ワークフローを採用したプロジェクトです。現在は初期セットアップ段階で、ソースコードはまだ実装されていません。

## 開発ワークフロー

このプロジェクトは`.claude/`ディレクトリで管理される6ステップのワークフローに従います：

1. **作業指示** - 開発者が作業指示を出す（requirements.mdに記述）
2. **作業計画** - Claude Codeがwork-plan.mdに作業計画をチェックリスト形式で記述
3. **計画確認** - 開発者が計画を確認し、実装指示を出す
4. **実装** - Claude Codeが実装（進捗はwork-plan.mdで管理）
5. **テスト** - Claude Codeがテストを実行、work-plan.mdのチェックリストを完了させる
6. **仕様反映と完了処理** - 開発者確認後、spec/implementation.mdに反映、completed/REQ-XXX/に移動

### 作業開始前に必ず実行すること

1. `.claude/claude.md`を読んで詳細なワークフロー指示を理解する
2. `spec/`ディレクトリでプロジェクト仕様を確認する
3. `requirements.md`で現在の作業指示を確認する
4. `work-plan.md`で進行中のタスクがあるか確認する
5. 新規作業の場合：実装前に必ず`work-plan.md`に計画を記述する
6. 実装完了後：`spec/implementation.md`に実装内容を記録する
7. 要件完了時：開発者の指示で`completed/REQ-XXX/`に移動する

## ドキュメント構造

```
.claude/
├── claude.md              # プロジェクト概要・ワークフロールール（詳細ガイド）
├── requirements.md        # 現在の作業指示（進行中・未着手のみ）
├── spec/                  # 仕様書ディレクトリ
│   ├── overview.md       # プロジェクト概要（任意）
│   ├── implementation.md # 実装済み機能（Claude Codeが記録）
│   └── README.md         # spec/ディレクトリのガイド
├── work-plan.md           # 現在の作業計画・チェックリスト
├── notes.md               # 月次作業ログ
└── completed/             # 完了した要件ごとのフォルダ
    └── REQ-XXX/
        ├── requirement.md  # 要件詳細
        ├── work-plan.md    # 作業計画・チェックリスト
        └── notes.md        # 作業固有のメモ
```

### 主要ドキュメント

**requirements.md**
- 形式：`[REQ-XXX]` 形式、ステータス 🔄（作業中）/ 📋（未着手）
- 現在進行中と未着手のみを保持
- 完了したら`completed/REQ-XXX/`へ移動

**spec/implementation.md**
- Claude Codeが実装完了後にここに記録
- 開発者も必要に応じて更新
- 常に最新状態を保持

**work-plan.md**
- Step 2でClaude Codeが作成
- チェックリスト形式：`- [ ]` で準備/実装/テストのタスクを記述
- テスト実行結果も記録
- 現在の作業のみ保持、完了したら`completed/REQ-XXX/`へ移動

**notes.md**
- 作業履歴と技術的知見を蓄積
- 月次セクション管理：`## YYYY-MM (当月)` → `## YYYY-MM`（アーカイブ）
- テスト時の問題点も記録
- `## Tips`セクションは常時参照用
- 完了した要件の詳細ログは`completed/REQ-XXX/notes.md`に保存

## 完了処理

要件が完了したら（Step 6完了後）、開発者が指示：
```
「REQ-XXXを完了フォルダに移動してください」
```

Claude Codeが実行する処理：
1. `completed/REQ-XXX/`フォルダを作成
2. `requirements.md`から該当要件を抽出 → `completed/REQ-XXX/requirement.md`として保存
3. `work-plan.md`の内容を`completed/REQ-XXX/work-plan.md`として保存
4. `notes.md`から関連する重要な情報を`completed/REQ-XXX/notes.md`として抽出
5. `requirements.md`と`work-plan.md`から該当部分を削除

## 重要な注意事項

### ワークフロールール
- **必ず作業計画を作成**：実装前に`work-plan.md`に計画を記述（Step 2）
- **計画のスキップ禁止**：開発者が計画を確認してから実装を開始
- **実装内容を必ず記録**：実装完了後は`spec/implementation.md`を更新
- **移動は開発者指示後**：開発者の指示なしに`completed/`への移動は行わない
- **コミットは明示的指示時のみ**：開発者が明示的に要求した時のみコミットする

### ドキュメント言語
- すべてのドキュメントは**日本語**で記述
- コードコメントの規則は最初の実装時に確立

### 現在のプロジェクト状態
- **ステータス**：初期セットアップ段階
- **ソースコード**：未作成
- **技術スタック**：最初の要件に基づいて決定予定
- **テスト方法**：最初の実装時に確立予定

## このプロジェクトでの作業方法

プロジェクトにまだコードが存在しないため、以下に注力してください：

1. `requirements.md`の要件を理解する
2. `work-plan.md`に詳細な作業計画を作成する
3. 技術選択について開発者に確認する
4. すべての実装詳細を`spec/implementation.md`に記録する
5. 6ステップのワークフローを厳密に守る

## 参照

詳細なワークフロー指示とルールについては、常に`.claude/claude.md`を参照してください。
