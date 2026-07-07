# yt-factory — 顔出しなし解説チャンネル 動画量産システム

VOICEVOX + FFmpeg + Pillow + Claude で、
**ネタ出し → 台本 → 音声 → 素材 → 組み立て → 書き出し** を自動化するパイプライン。
静止画＋カット割り＋表情差分の「紙芝居」スタイル専用（動画生成AI不使用）。

```
ytf ideas                  # ネタ出し（LLM）→ ideas/backlog.yaml
ytf script --idea <id>     # 台本生成（LLM）→ projects/<slug>/script.yaml
ytf make <slug>            # 音声合成→映像→サムネ→概要欄→ショート 一括
```

`projects/<slug>/out/` に 本編mp4 / ショートmp4 / サムネPNG / 概要欄テキスト（VOICEVOXクレジット自動挿入）が揃う。

## クイックスタート

```bash
pip install -e '.[llm]'
ytf assets --init      # プレースホルダー素材を生成
ytf doctor             # 環境チェック
# VOICEVOXアプリを起動してから:
ytf make sample        # サンプル台本で1本ビルド
# VOICEVOXが無い環境での動作確認は: ytf make sample --tts dummy
```

## ドキュメント

- [docs/DESIGN.md](docs/DESIGN.md) — 全体設計・アーキテクチャ・ロードマップ
- [docs/WORKFLOW.md](docs/WORKFLOW.md) — 日々の運用手順・チューニング箇所

## 構成

```
channel.yaml        チャンネル設定（テーマ・キャラ・声・見た目）← ほぼ全ての調整はここ
prompts/            LLMプロンプトテンプレート（ネタ出し・台本）
ytf/                パイプライン本体（Python）
assets/             立ち絵・背景・BGM（gitignore対象、ytf assets --init で初期化）
ideas/backlog.yaml  ネタのストック
projects/<slug>/    動画1本ごとの作業ディレクトリ（台本・音声・出力）
```

## 音声クレジット

VOICEVOX 各キャラクターの利用規約に従い、生成される概要欄に
`VOICEVOX:ずんだもん` 等のクレジットが自動で挿入されます。
