# なすみそクリエイター - 開発ガイド

## プロジェクト概要

**なすみそクリエイター**は、イラストレーター「なすみそ」の画風を学習し、LoRAモデルとして再現・応用するアシスタントツールです。

- **ステータス**: フェーズ1（MVP）完了 - エンドツーエンドのLoRA学習・画像生成フロー確立済み
- **技術スタック**: Python, Google Colab, kohya_ss, Stable Diffusion (Anything V5), AUTOMATIC1111 WebUI
- **開発環境**: MacBook Air M1

---

## 開発ワークフロー（6ステップ）

1. **作業指示** - 開発者が作業指示を出す（`requirements.md`に記述）
2. **作業計画** - Claude Codeが`work-plan.md`に作業計画を記述
3. **計画確認** - 開発者が計画を確認し、実装指示を出す
4. **実装** - Claude Codeが実装（進捗は`work-plan.md`で管理）
5. **テスト** - テスト実行、問題があれば`notes.md`に記録
6. **仕様反映と完了処理** - `spec/`に仕様反映後、`completed/REQ-XXX/`に移動

詳細: [workflow.md](workflow.md)

---

## クイックリンク

### ドキュメント
- **[workflow.md](workflow.md)** - ワークフロー詳細とドキュメント管理ルール
- **[spec/overview.md](spec/overview.md)** - プロジェクト概要
- **[spec/spec.md](spec/spec.md)** - 実装済み機能の使い方（ユーザー向け）
- **[spec/reference.md](spec/reference.md)** - 技術詳細・API仕様（開発者向け）
- **[KNOWLEDGE.md](KNOWLEDGE.md)** - プロジェクト全体の知見・ノウハウ

### 管理
- **[requirements.md](requirements.md)** - 現在の作業指示
- **[work-plan.md](work-plan.md)** - 現在の作業計画
- **[notes.md](notes.md)** - 現在の作業メモ
- **[completed/](completed/)** - 完了した要件

---

## 簡略コマンド

開発者は以下の簡略表現で指示できます：

| コマンド | 説明 |
|---------|------|
| `plan REQ-XXX` | work-plan.mdに作業計画を作成 |
| `implement REQ-XXX` | work-plan.mdの計画に基づいて実装開始 |
| `test REQ-XXX` | テストを実行、work-plan.mdを更新 |
| `complete REQ-XXX` | completed/REQ-XXX/に移動、仕様反映 |

---

## プロジェクト構造

```
NasumisoCreator/
├── .claude/              # Claude Code管理ファイル
│   ├── README.md        # このファイル
│   ├── workflow.md      # ワークフロー詳細
│   ├── spec/            # 仕様書
│   └── completed/       # 完了した要件
├── projects/            # プロジェクトデータ
│   └── nasumiso_v1/     # なすみそLoRAプロジェクト
├── scripts/             # 前処理スクリプト
├── notebooks/           # Google Colab学習ノートブック
└── CLAUDE.md            # Claude Code用クイックリファレンス
```

詳細: [CLAUDE.md](../CLAUDE.md)
