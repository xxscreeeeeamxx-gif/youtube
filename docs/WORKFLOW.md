# 日々の運用フロー

方針: **LLMのAPIは使わない**（ネタ出し・台本はあなたが claude.ai にコピペ）。
機械的な工程（ビルド・通知・アップロード）は n8n が自動で回す。
→ n8n の導入は [automation/README.md](../automation/README.md)

## 初回セットアップ（Mac）

```bash
./scripts/setup_mac.sh   # ffmpeg・パッケージ・素材・環境チェックまで一括
# VOICEVOXアプリを起動しておく（エンジンが :50021 で立つ）
ytf make sample          # 動作確認
```

本番用の立ち絵は、公認立ち絵素材（利用規約を確認）から表情PNGを書き出し、

```bash
python3 scripts/import_sprites.py zunda ~/Downloads/zunda_pngs
python3 scripts/import_sprites.py metan ~/Downloads/metan_pngs
```

で取り込めます（余白トリミング・サイズ統一まで自動。normal.png だけでも可）。

## 1本作る流れ（あなたの作業は3点だけ）

```bash
# ① ネタ出し（週1回まとめてでOK）
ytf ideas                       # → ideas/prompt.md が生成される
#    claude.ai にプロンプトを貼り、返答をファイル保存して:
ytf ideas --response r.txt
ytf ideas --list                # ストック確認

# ② 台本
ytf script --idea sky-blue      # → プロンプトが書き出される
#    claude.ai に貼り、返答を保存して:
ytf script --response r2.txt    # → projects/<slug>/script.yaml

#    ★台本を目視レビュー（事実確認・表現調整。YAMLを直接編集してよい）
ytf approve <slug>              # 承認マーク → n8nが自動ビルド＆完成通知

# ③ 完成動画を確認したら
ytf release <slug>              # → n8nがYouTubeへ非公開アップロード
#    YouTube Studio でサムネ設定＆公開
```

進行状況の確認: `ytf status`

n8nを使わない場合は `ytf make <slug>` で手動ビルド、
アップロードは YouTube Studio に `out/video.mp4` をドラッグして
`out/metadata.txt` をコピペ。

## 品質を上げるチューニング場所

| 直したいこと | 場所 |
|---|---|
| 誤読 | 台本の `[表示|よみ]` 記法 / `channel.yaml` の `voicevox.dictionary` |
| 話速・声のトーン | `channel.yaml` の `speed_scale` / `style_overrides` |
| 台本の芸風 | `prompts/script.md`（構成ルール・キャラの口調） |
| ネタの方向性 | `prompts/ideas.md` と `channel.yaml` の `channel.theme` |
| 見た目 | `assets/` の差し替え / `compose.py` のレイアウト定数 |
| BGM | `assets/bgm/` に置いて `channel.yaml` の `video.bgm.file` を設定 |

誤読が心配な回は `ytf qc <slug> --whisper` で書き起こし突合ができます。

## 量産時の目安

1本あたりの人間の作業は
**コピペ2往復（5分）＋台本レビュー（5〜10分）＋動画確認・公開（5分）** に収束する想定。
ビルドとアップロードはn8nが勝手にやるので、レビューを溜めてまとめて捌けば1日3本は現実的。
