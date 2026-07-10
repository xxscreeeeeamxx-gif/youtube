---
name: video-production
description: このリポジトリ（yt-factory）で解説動画を1本作る・修正するときの標準ワークフロー。台本執筆の芸風、素材収集、演出、ビルド、検証、コミットまでの全手順。動画を「作って」「直して」「ビルドして」と言われたら必ずこれに従う。
---

# yt-factory 動画制作スキル

顔出しなし解説チャンネル（青山龍星の一人語り）の動画を、ネタ→台本→素材→演出→ビルド→検証まで一貫して作る。

## 前提・環境

- 仮想環境: `. .venv/bin/activate` + `export PYTHONPATH=.`
- ffmpeg: brew未導入の環境ではスクラッチパッドの静的バイナリを
  `YTF_FFMPEG`/`YTF_FFPROBE` で指定（過去セッション参照）
- VOICEVOX: **手動起動は不要**。`ensure_engine` がアプリ内蔵エンジン
  （`/Applications/VOICEVOX.app/Contents/Resources/vv-engine/run`）を
  ヘッドレス自動起動する
- 話者: 青山龍星（style 13）・話速1.15・デフォルトトーン（ピッチ/抑揚はいじらない）

## 1本作る手順

1. **ネタ**: `ideas/backlog.yaml` から選ぶ（新案は同形式で追記、使ったら `status: used`）
2. **台本**: `projects/<slug>/script.yaml` を直接書く（スキーマは `ytf/schema.py`）
   - 芸風は下記「語り口」を厳守。書いたら `Project.load_script()` で検証
3. **背景素材**: Pexels等から各章・小トピックに合う画像を収集
   - `ytf/media.py` の `search_pexels`+`insert_media(kind="background")` を使う
   - **必ずコンタクトシートを作って目視確認**し、合わないものは差し替える
   - シーンに `background:`、カット途中の切替は cut の `background:`
   - 数カットごとに背景を切り替える（1画像が短時間だけ動く＝滑らか＆飽きない）
4. **演出**（乱発しない）:
   - `telops:` 章の山場だけ（動画全体で5〜8個）。size/position/色/glow/anim
   - `stat:` 意外な数字はカウントアップ（unitの半角%は自動で全角％化される）
   - `se:` は付けない（章切替の音は自動）
   - 全画面動画: `video:` + `video_span:` + `video_full: true` + `video_speed: 0.6` など
5. **ビルド**: `python -m ytf.cli make <slug>`（音声・セグメントはキャッシュされる）
6. **検証**（必須）:
   - 尺: video.mp4 と narration.wav の duration がほぼ一致
   - フレーム抽出で目視: hookテロップ / stat数字 / 章トランジション / 新背景
   - `ytf qc <slug> --whisper` で誤読チェック（faster-whisperで高速）
7. **コミット&プッシュ**: 背景画像(assets/backgrounds/)はコミットする。
   動画/音声/クリップは gitignore 済み
8. `open projects/<slug>/out/video.mp4` でユーザーに見せる

## 語り口（チャンネルの芸風・最重要）

**饒舌に畳みかける一人語り＋視聴者への軽い煽り**:
- 短文をリズムよく重ねる。「で、満充電。これはもう、朝8時の通勤電車です」
- 視聴者に直接踏み込む: 「〜していませんか」「心当たり、ありますよね」
  「ええ、たった今充電器に挿したあなたの話です」— 各章に1回以上
- 上から目線にせずユーモアで中和。かぎ括弧「」は使わない
- 事実に自信がない数字・研究は「〜と言われています」「〜という報告があります」
- 難読語は `[表示|よみ]` 記法。恒久的な誤読は `ytf dict add <表記> <よみ>`
- 章構成: フック（煽り＋テーマ提示・short: true）→ 本編2〜3章 → 実用 → まとめ＋逆説の一言

## 便利コマンド

| コマンド | 用途 |
|---|---|
| `ytf edit <slug>` | ブラウザ編集画面（テロップ/読み/素材/BGM/書き出しがGUIで完結） |
| `ytf media "<query>"` / `--video` | Pexels/Wikimedia素材のDL（ライセンスはmedia/credits.txtに記録） |
| `ytf bgm "<雰囲気>" --name <名前>` | MusicGenでBGM生成（要 torch+transformers） |
| `ytf dict add <表記> <よみ>` | VOICEVOX誤読の恒久修正 |
| `ytf qc <slug> --whisper` | 誤読チェック（faster-whisper優先） |
| `ytf status` / `approve` / `release` | 進行管理（n8n連携のマーカー） |

## 実装上の注意（ハマりどころ）

- 台本テキスト変更→音声から再生成（キャッシュで差分のみ）。演出変更→セグメントのみ再生成
- drawtext に半角 `%` を渡すと Stray% で文字ごと消える（buildが全角％に変換済み）
- Wikimedia画像の挿入はオリジナルURLを使う（サムネ生成APIは不安定）
- 章トランジション中はナレーションに `lead` 秒の無音が入る（video.transition.lead）
- モーラ単位の発話タイミングが timing.json の `moras` に入っている
  （「この単語の瞬間にテロップ」等の演出を作るときはこれを使う。whisper不要）
- 検証で作った一時プロジェクトや背景はコミット前に必ず掃除する

## 素材・音源のライセンス

- 画像/動画: Pexels License（クレジット不要）を優先。Wikimediaは credits.txt を確認し
  CC BY系なら概要欄にクレジット追記
- 効果音: 効果音ラボ（商用可・クレジットは概要欄に自動挿入される）
- BGM: 自作シンセ4曲 + MusicGen生成（`ytf bgm`）。外部曲は assets/bgm/ に置けば選べる
