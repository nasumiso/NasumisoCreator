# projects/ - プロジェクトデータ管理

## 概要

各イラストレーター・キャラクターごとにプロジェクトフォルダを作成します。

## フォルダ構成

```
projects/
└── nasumiso_v1/                    # プロジェクト名
    ├── 1_raw_images/               # ステップ1: なすみそから受領した元画像
    ├── 2_processed/                # ステップ2: リサイズ・リネーム済み画像
    ├── 3_tagged/                   # ステップ3: タグ付き画像（.txtペア）
    ├── 4_dataset/                  # ステップ4: Colab学習用データセット
    └── lora_models/                # ステップ5: 学習済みLoRAモデル
```

## ワークフロー

1. **1_raw_images/** - なすみそから画像を受領して配置
2. **2_processed/** - `scripts/prepare_images.py` で処理
3. **3_tagged/** - `scripts/auto_caption.py` でタグ生成
4. **4_dataset/** - `scripts/organize_dataset.py` で整形
5. **lora_models/** - Colabでの学習結果を保存

## 新規プロジェクト作成

同じ構造でフォルダを作成してください：
```bash
mkdir -p projects/新プロジェクト名/{1_raw_images,2_processed,3_tagged,4_dataset,lora_models}
```
