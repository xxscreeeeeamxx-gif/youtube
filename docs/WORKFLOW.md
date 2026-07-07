# 日々の運用フロー

## 初回セットアップ（Mac）

```bash
# 1. 依存インストール
pip install -e '.[llm]'        # APIモードを使うなら [llm] 付き
# ffmpeg が無ければ: brew install ffmpeg

# 2. 素材の初期化（まずはプレースホルダーで動作確認）
ytf assets --init

# 3. 環境チェック
ytf doctor

# 4. VOICEVOXアプリを起動しておく（エンジンが :50021 で立つ）

# 5. APIモードにする場合
export ANTHROPIC_API_KEY=sk-ant-...
```

本番用の立ち絵は `assets/characters/zunda/` `assets/characters/metan/` に
`normal.png / happy.png / surprised.png / thinking.png / angry.png / sad.png`
という名前で置くだけで差し替わります（公認立ち絵素材の利用規約を確認のこと）。

## 1本作る（APIモード・最短ルート）

```bash
ytf ideas                    # ネタ15本をストックに追加（週1回で十分）
ytf ideas --list             # ストック確認、IDを選ぶ
ytf script --idea sky-blue   # 台本生成 → projects/<slug>/script.yaml

# ★ここで台本を必ず目視レビュー（事実確認・表現調整）。編集はYAMLを直接いじる

ytf make <slug>              # 音声→映像→サムネ→概要欄→ショート 一括生成
ytf qc <slug> --whisper      # 誤読チェック（初回や新語が多いときだけでOK）
```

`projects/<slug>/out/` に以下が揃うので、YouTube Studio にアップロード:

- `video.mp4` … 本編
- `short_*.mp4` … ショート（縦）
- `thumbnail.png` … サムネイル
- `metadata.txt` … タイトル・概要欄（クレジット入り）・タグ（コピペ用）

## コピペ半自動モード（APIキーなし）

```bash
ytf ideas                          # → ideas/prompt.md が生成される
# claude.ai にプロンプトを貼り、返答を r.txt に保存
ytf ideas --response r.txt

ytf script --idea sky-blue         # → プロンプトが書き出される
# 同様に返答を保存して
ytf script --response r2.txt
ytf make <slug>
```

## 品質を上げるチューニング場所

| 直したいこと | 場所 |
|---|---|
| 誤読 | 台本の `[表示|よみ]` 記法 / `channel.yaml` の `voicevox.dictionary` |
| 話速・声のトーン | `channel.yaml` の `speed_scale` / `style_overrides` |
| 台本の芸風 | `prompts/script.md`（構成ルール・キャラの口調） |
| ネタの方向性 | `prompts/ideas.md` と `channel.yaml` の `channel.theme` |
| 見た目 | `assets/` の差し替え / `compose.py` のレイアウト定数 |
| BGM | `assets/bgm/` に置いて `channel.yaml` の `video.bgm.file` を設定 |

## 量産時の目安

1本あたりの人間の作業は **台本レビュー（5〜10分）+ アップロード（2分）** に収束する想定。
音声合成〜書き出しはM5なら10分動画で数分。台本レビューを溜めてバッチ処理すれば1日3本は現実的。
