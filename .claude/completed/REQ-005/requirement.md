# [REQ-005] Windows環境向けセットアップドキュメント・スクリプト作成

## 要求内容
なすみそさん（イラストレーター）がWindows環境でStable Diffusion WebUIを使用した推論（画像生成）を実行できるよう、セットアップ用のスクリプトとドキュメントを作成する。

## 背景
- なすみそさんの環境: Windows 11、NVIDIA RTX 3060搭載
- こすうけさんの環境: MacBook Air M1
- なすみそさんはイラストレーターで、一定のPCリテラシーはあるがソフトウェア技術者ではない
- まずは「1. 推論のみ」を実現し、後に「2. 学習〜推論」へ拡張予定

## 必要な要素
1. **セットアップスクリプト** (`setup/` フォルダに配置)
   - `setup_windows.bat`: Windows環境の自動セットアップスクリプト
     - Python/Gitのインストールチェック
     - Stable Diffusion WebUIのクローン
     - 初回セットアップ手順の案内
   - `create_shortcut.bat`: デスクトップショートカット作成スクリプト

2. **ドキュメント** (`docs/` フォルダに配置)
   - `setup_windows.md`: Windows向け詳細セットアップ手順（スクリーンショット想定）
   - `quickstart_nasumiso.md`: なすみそさん向けクイックスタートガイド
     - WebUIの基本的な使い方
     - プロンプトの書き方
     - パラメータの説明
   - `model_download.md`: モデルファイルのダウンロード・配置方法

3. **.gitignore の更新**
   - Python仮想環境 (`.venv/`, `venv/`)
   - プロジェクトデータ（画像、モデルファイル）
   - OS固有ファイル（`.DS_Store`, `Thumbs.db` 等）
   - 外部ツール（`stable-diffusion-webui/`）

## 設計方針
- **Git管理対象**: セットアップスクリプト、ドキュメントのみ
- **Git管理外**: Python本体、Stable Diffusion WebUI本体、モデルファイル
- **配布方法**:
  - このリポジトリをZIPまたはGit cloneで提供
  - モデルファイルは別途Google Driveで共有
  - Python/Gitは公式サイトから各自ダウンロード

## ゴール
- なすみそさんがセットアップスクリプトとドキュメントに従って、Windows環境でStable Diffusion WebUIを起動できる
- 学習済みモデル（anything-v5.safetensors）とLoRAモデル（nasumiso_v1.safetensors）を使って画像生成できる
- 技術的な知識が少なくても、手順に従えばセットアップできる

## 注意事項
- スクリプトはWindows専用（Mac環境とは分離）
- Stable Diffusion WebUIは外部プロジェクトなのでGit管理に含めない
- モデルファイルは大容量なのでGit管理せず、外部ストレージで共有
