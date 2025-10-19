# なすみそクリエイター

## プロジェクト概要
- **プロジェクト名**: なすみそクリエイター (NasumisoCreator)
- **バージョン**: 1.0 (MVP)
- **開発者**: こすうけ（元ゲームプログラマ、MacBook Air M1使用）
- **イラストレーター**: なすみそ（画像提供・フィードバック担当）
- **技術スタック**: Python, Google Colab, kohya_ss, Stable Diffusion, AUTOMATIC1111 WebUI
- **概要**: イラストレーター「なすみそ」の画風を学習し、LoRAモデルとして再現・応用するアシスタントツール

## 開発ワークフロー

このプロジェクトは以下の6ステップで進行します：

1. **作業指示** - 開発者が作業指示を出す（大きな作業はrequirements.mdに記述）
2. **作業計画** - Claude Codeがwork-plan.mdに作業計画をチェックリスト形式で記述
3. **計画確認** - 開発者が計画を確認し、実装指示を出す
4. **実装** - Claude Codeが実装を行う（進捗はwork-plan.mdのチェックリストで管理、spec.mdやreference.mdの更新は不要）
5. **テスト** - Claude Codeがテストを実行し、work-plan.mdのチェックリストを完了させる。問題があればnotes.mdに記録
6. **仕様反映と完了処理** - 開発者が成果物を確認後、spec/spec.md、reference.mdへの仕様反映を指示。完了後、completed/REQ-XXX/フォルダに移動

## ドキュメント構成
```
.claude/
├── claude.md              # このファイル（プロジェクト概要・開発ルール）
├── requirements.md        # 現在の作業指示（進行中・未着手のみ）
├── spec/                  # 仕様書ディレクトリ
│   ├── overview.md       # プロジェクト概要・アーキテクチャ
│   ├── spec.md           # 実装済み機能の使い方（ユーザー向け）
│   ├── reference.md      # 技術詳細・API仕様（開発者向け）
│   └── original/         # 初期要件定義
├── work-plan.md           # 現在の作業計画・チェックリスト
├── notes.md               # 現在のREQ作業中の気づき・メモ（完了時にテンプレに戻る）
├── KNOWLEDGE.md           # プロジェクト全体を通して得られた気づき・ノウハウ
└── completed/             # 完了した要件ごとのフォルダ
    └── REQ-XXX/
        ├── requirement.md  # 要件詳細
        ├── work-plan.md    # 作業計画・チェックリスト
        └── notes.md        # その作業で得られた気づき・メモのログとふりかえり・感想
```

### 各ドキュメントの役割

#### requirements.md
- **目的**: 大きな作業の指示を記述する
- **記述者**: 主に開発者
- **形式**: [REQ-XXX] 形式で管理
- **ステータス**: 🔄作業中 / 📋未着手
- **保持ルール**: 現在進行中と未着手のみ。完了したらcompleted/REQ-XXX/へ移動

#### spec/ ディレクトリ
- **目的**: プロジェクトの仕様を構造化して記録
- **記述者**:
  - 初期作成: 開発者またはClaude Code
  - 実装完了後の追記: Claude Code（spec.mdとreference.mdに記録）
  - 随時編集: 開発者（必要に応じて修正・更新）
- **ファイル構成**:
  - **overview.md**: プロジェクト概要・アーキテクチャ（背景、目的、7ステップワークフロー）
  - **spec.md**: 実装済み機能の使い方（ユーザー向け・「何ができるか」に焦点）
  - **reference.md**: 技術詳細・API仕様（開発者向け・パラメータ、処理フロー、技術制約）
  - **original/**: 初期要件定義書
- **保持ルール**: 常に最新の仕様を保持

#### work-plan.md
- **目的**: 作業計画と進捗をチェックリストで管理、テスト結果も記録
- **記述者**: Claude Code（Step 2で作成、Step 5でテスト結果を反映）
- **形式**: `- [ ]` チェックリスト形式で記述
- **内容**: 準備/実装/テスト の各チェックリスト、テスト実行結果
- **保持ルール**: 現在の作業のみ。完了したらcompleted/REQ-XXX/へ移動

#### notes.md
- **目的**: 現在のREQ作業中の気づき・メモを記録
- **記述者**: 主にClaude Code、開発者も追記可
- **内容**: 作業中の気づき、解決した問題、テストで発見した問題点など
- **保持ルール**: REQ作業中のみ使用。完了時にcompleted/REQ-XXX/notes.mdに移動し、テンプレに戻る

#### KNOWLEDGE.md
- **目的**: プロジェクト全体を通して得られた気づき・ノウハウを蓄積
- **記述者**: 主にClaude Code（完了処理時）、開発者も追記可
- **内容**: REQ固有ではなく、プロジェクト横断で役立つ知見、技術Tips、設計パターンなど
- **保持ルール**: 常に保持。完了処理時に、notes.mdから汎用的な知見を抽出して追記

#### completed/REQ-XXX/
- **目的**: 完了した要件に関する全情報を保管
- **構造**:
  - `requirement.md`: その要件の詳細（requirements.mdから抽出）
  - `work-plan.md`: 作業計画と実行結果
  - `notes.md`: その作業で得られた気づき・メモのログ（.claude/notes.mdから移動）とふりかえり・感想
- **作成タイミング**: Step 6完了後、開発者の指示で移動

## 完了時の移動ルール

要件が完了したら（Step 6完了後）：

### 1. 開発者が指示
```
「REQ-XXXを完了フォルダに移動してください」
```

### 2. Claude Codeが実行
- `completed/REQ-XXX/` フォルダを作成
- requirements.mdから該当要件を抽出して `completed/REQ-XXX/requirement.md` として保存
- work-plan.mdの内容を `completed/REQ-XXX/work-plan.md` として保存
- notes.mdの内容を適宜要約して、 `completed/REQ-XXX/notes.md` として保存、ふりかえりとして感想を記述
- 実装した機能の使い方を `spec/spec.md` に追記（ユーザー向け・「何ができるか」）
- 実装した機能の技術詳細を `spec/reference.md` に追記（開発者向け・パラメータ、処理フロー、技術制約）
- notes.mdから汎用的な知見を抽出して `KNOWLEDGE.md` に追記
- requirements.mdとwork-plan.mdから該当部分を削除
- notes.mdをテンプレに戻す

### 3. 結果
- requirements.mdは次の作業のみ
- work-plan.mdは空（または次の作業待ち）
- notes.mdはテンプレに戻る
- 完了した要件の実装履歴はcompleted/REQ-XXX/notes.mdに保存
- 実装した機能の使い方はspec/spec.mdに追記（ユーザー向け）
- 実装した機能の技術詳細はspec/reference.mdに追記（開発者向け）
- 汎用的な知見はKNOWLEDGE.mdに蓄積

## 簡略指示の定義

開発者は以下の簡略表現で指示することがあります。Claude Codeはこれを理解し、適切に実行してください。

### 作業計画
- 「plan REQ-XXX」
- 「計画 REQ-XXX」
→ requirements.mdのREQ-XXXについて、work-plan.mdに作業計画をチェックリスト形式で記述

### 実装開始
- 「implement REQ-XXX」
- 「実装 REQ-XXX」
→ work-plan.mdの計画に基づいて実装を開始

### テスト実行
- 「test REQ-XXX」
- 「テスト REQ-XXX」
→ テストを実行し、work-plan.mdのチェックリストを完了。問題があればnotes.mdに記録

### 完了処理
- 「complete REQ-XXX」
- 「完了 REQ-XXX」
- 「archive REQ-XXX」
→ completed/REQ-XXX/フォルダを作成し、関連ファイルを移動


### 複合指示
- 「implement and test REQ-XXX」
→ 実装とテストを連続実行

## 技術スタック

[プロジェクトで使用している技術を列挙]

例：
- **言語**: Python 3.11
- **フレームワーク**: Django 4.2
- **データベース**: PostgreSQL 15
- **その他**: Redis, Celery, etc.

## プロジェクト構造
```
[プロジェクトのディレクトリ構造を記述]

例：
project/
├── src/
│   ├── main.py
│   └── ...
├── tests/
│   └── ...
├── docs/
│   └── ...
└── .claude/
    ├── claude.md
    ├── requirements.md
    └── ...
```

## コーディング規則

### 基本ルール
- [命名規則]
- [インデント規則]
- [コメント規則]
- [その他プロジェクト固有のルール]

例：
- 変数名、関数名は `snake_case` を使用
- クラス名は `PascalCase` を使用
- インデントは4スペース
- コメントは日本語で記述

## 重要な注意事項

### [プロジェクト固有の注意事項]

例：
- 環境変数は `.env` ファイルで管理
- APIキーは絶対にコミットしない
- など

### テスト要件

#### 実装後（毎回）
[基本的なテストの実行方法]

例：
```bash
pytest tests/
```

#### PR前（重要時）
[統合テストや包括的なテストの実行方法]

例：
```bash
pytest tests/ --cov
```

### バージョン管理
- [Gitワークフローの説明]
- [ブランチ戦略]
- [コミットメッセージの規則]

例：
- メインブランチ: `main`
- 開発ブランチ: `develop`
- フィーチャーブランチ: `feature/xxx`
- コミットメッセージ: 日本語OK、説明的な内容にする

## 参照ドキュメント

- [作業指示書](./requirements.md) - 現在の作業指示
- [仕様書ディレクトリ](./spec/) - プロジェクトの設計書と実装記録
- [現在の作業計画](./work-plan.md) - 進行中の作業チェックリスト
- [作業メモ](./notes.md) - 現在のREQ作業中の気づき・メモ
- [ナレッジベース](./KNOWLEDGE.md) - プロジェクト全体を通して得られた知見・ノウハウ
- [完了した要件](./completed/) - 過去に完了した全要件

## 開発開始時の確認事項

Claude Codeでの作業開始時は：
1. このclaude.mdを読む
2. spec/ディレクトリでプロジェクトの仕様を確認
3. requirements.mdで現在の作業指示を確認
4. work-plan.mdで進行中のタスクがあるか確認
5. 新規作業の場合はwork-plan.mdに計画を記述してから実装開始
6. 要件完了時は開発者の指示でcompleted/REQ-XXX/に移動

## プロジェクト固有の情報

[その他、プロジェクト特有の重要な情報をここに記述]

例：
- デプロイ手順
- 開発環境のセットアップ方法
- 外部サービスとの連携方法
- など
