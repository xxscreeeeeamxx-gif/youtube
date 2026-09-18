# Windows PC への移行手順

このリポジトリを Windows で動かすための手順。
**コードは両OS対応済み**（2026-09-18）。あとは外部ツールとフォントを入れるだけ。

移行で引っかかるのは、コードではなく**リポジトリに入っていないもの**。
ライセンス上コミットできない素材が多く、`git clone` しただけでは動かない。

## まず容量の話（ここを間違えると丸一日溶ける）

| | 容量 | どうするか |
|---|---|---|
| リポジトリ全体 | **87 GB** | 全部コピーしてはいけない |
| └ うち生成物（`out/` `frames/` `audio/`） | **85 GB** | **運ばない**。ビルドし直せば再生成される |
| └ Git管理分 | 50 MB | `git clone` で入る |
| └ **Git管理外だが必要な素材** | **1.1 GB** | **手で運ぶ**（下表） |

**運ぶのは 1.1 GB だけ。** 外付けSSDやUSBメモリで足りる。

### 手で運ぶもの（USBメモリ等でコピー）

| フォルダ | 容量 | 中身 | 無いとどうなる |
|---|---|---|---|
| `assets/clips/` | 934 MB | 実写クリップ・自作アニメ | 解説回のビルドが落ちる |
| `tools/` | 138 MB | ffmpeg / AquesTalkPlayer | **何も動かない**（※Windows版に差し替え） |
| `assets/bgm/` | 75 MB | BGM | **全動画が無音の章だらけになる** |
| `assets/fonts/` | 26 MB | 源界明朝・851チカラヅヨク | サムネが作れない |
| `assets/characters/` | 4.6 MB | 立ち絵PSD | **キャラが出ない** |
| `assets/se/` | 380 KB | 効果音 | 「ドン」などが鳴らない |
| `client_secret.json` | 数KB | YouTube APIの認証情報 | 投稿できない |

**`tools/` だけは中身を入れ替える**（Mac用バイナリが入っているため。②③参照）。
ほかはそのままコピーでよい。`.ttf` も `.psd` も `.mp3` もOS非依存。

### 運ばないもの

- `projects/**/out/` `frames/` `audio/` — **85GBの正体**。ビルドで再生成される
- `.venv/` — OSが違うので作り直す（①）
- `.youtube_token.json` — 2台で共有すると片方が弾かれる。各PCで取り直す（⑥）

### 手順

```
REM 1. Gitで台本・設定・背景を持ってくる
git clone <リポジトリのURL> C:\yt
cd C:\yt

REM 2. Macから素材をコピー（USBメモリ経由）
REM    assets\clips assets\bgm assets\fonts assets\characters assets\se
REM    tools（中身は後で入れ替える）
REM    client_secret.json
```

**Mac側でUSBに入れるときは、生成物を除いて固めること**（そのまま `assets` を
コピーすれば済むが、`projects` は絶対に含めない）:

```bash
tar czf /Volumes/USB/ytf-assets.tgz assets/clips assets/bgm assets/fonts \
    assets/characters assets/se client_secret.json
```

---

## ① Python と仮想環境

**Python 3.10 以上を推奨**（Mac側は 3.9 で動いているが、3.9 は `X | None` 記法のために
`eval_type_backport` に依存している。3.10+ ならその依存が不要になる）。

```
winget install Python.Python.3.12
cd <リポジトリ>
python -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements.txt
```

以降、コマンドは `.venv\Scripts\python` で実行する。

**PowerShell の場合、環境変数の指定方法が Mac と違う**:

```
$env:PYTHONPATH="."
$env:YTF_FFMPEG="$PWD\tools\ffmpeg.exe"
$env:YTF_FFPROBE="$PWD\tools\ffprobe.exe"
```

---

## ② ffmpeg / ffprobe

https://www.gyan.dev/ffmpeg/builds/ の `ffmpeg-release-essentials.zip` を落とし、
中の `bin\ffmpeg.exe` と `bin\ffprobe.exe` を `tools\` に置く。

置いたら確認:

```
.\tools\ffmpeg.exe -version
```

---

## ③ AquesTalkPlayer（ゆっくり音声）

**人物物語のナレーションは全部これ**。無いとドラマ回が作れない。

https://www.a-quest.com/products/aquestalkplayer.html から **Windows版**を入手し、
`tools\AquesTalkPlayer\AquesTalkPlayer.exe` に置く（通常インストールでも可）。

**注意: Windows版とMac版でコマンドラインの書式が違う。**

| | 書式 |
|---|---|
| macOS | `-T テキスト -P プリセット -W 出力` |
| Windows | `/T テキスト /P プリセット /W 出力` |

`ytf/voice.py` が OS を見て自動で切り替えるので、**触る必要はない**。
ただし場所を変えた場合は `channel.yaml` に書く:

```yaml
aquestalk:
  player_path: "C:/Program Files/AquesTalkPlayer/AquesTalkPlayer.exe"
```

**プリセット名を Mac と揃えること。** `channel.yaml` のキャラ定義が参照している
プリセット名が Windows 側の AquesTalkPlayer に無いと、合成が失敗する。
GUI を一度起動して、同じ名前のプリセットがあるか確認する。

**商用利用には別途ライセンスが必要**（¥6,380/年）。収益化を始める前に購入すること。
遡って購入はできない。

---

## ④ フォント ★ここが一番の落とし穴

**ヒラギノ角ゴシック W9 は macOS 専用**で、Windows には入っていない。
サムネの見出しと本編のテロップが全部これを使っている。

### 推奨: Noto Sans JP を入れて両OSで見た目を揃える

https://fonts.google.com/noto/specimen/Noto+Sans+JP から
**Black (900)** と **Bold (700)** を落とし、`assets\fonts\` に置く。

```
assets\fonts\NotoSansJP-Black.otf
assets\fonts\NotoSansJP-Bold.otf
```

**同梱フォントは探索順の先頭**なので、これを置けば Mac でもこちらが使われ、
**両OSで完全に同じ絵が出る**。ライセンスは SIL Open Font License（商用可）。

置かない場合は OS 標準にフォールバックする（BIZ UDPGothic Bold →
游ゴシック Bold → メイリオ Bold の順）。ただし**ヒラギノ W9 より細いので、
サムネの印象が変わる**。既存32本と並べたときに浮く。

### サムネ用の飾りフォント

`assets\fonts\SOURCES.md` の入手元から落とし直す（どちらも .ttf なのでOS非依存）。

- `genkai-mincho.ttf` — 源界明朝
- `851CHIKARA-DZUYOKU_kanaA_004.ttf` — 851チカラヅヨク

---

## ⑤ VOICEVOX

https://voicevox.hiroshiba.jp/ から Windows版を入れる。

`ytf/voice.py` が既定で
`%LOCALAPPDATA%\Programs\VOICEVOX\vv-engine\run.exe` を探し、
**落ちていればヘッドレスで自動起動する**（GUIを開いておく必要はない）。

インストール先を変えた場合は `channel.yaml`:

```yaml
voicevox:
  engine_path: "D:/VOICEVOX/vv-engine/run.exe"
```

**キャラのスタイルIDが Mac と同じか確認すること**（ずんだもん=3、春日部つむぎ=8 など）。
VOICEVOX のバージョンが違うとIDがずれることがある。`ytf voices` で一覧が出る。

---

## ⑥ YouTube の認証

1. Mac の `client_secret.json` を Windows のリポジトリ直下にコピー
   （**これはGit管理外。USBメモリ等で手で運ぶ。メールやチャットに貼らない**）
2. Windows 側で再認証:

```
.venv\Scripts\python scripts\upload_youtube.py auth
```

ブラウザが開くので「日常研究所」のアカウントで承認する。
`.youtube_token.json` が作られる。

**`.youtube_token.json` はコピーしないこと。** 7日で失効するうえ、
2台で同じトークンを使うと片方が弾かれる。各PCで取り直す。

なお Google Cloud のプロジェクトが「テスト中」の間は**7日ごとに再認証が要る**。
「本番」に切り替えれば不要になる。

---

## ⑦ 動作確認

この順で通れば移行完了。

```
REM 1. 設定が読めるか
.venv\Scripts\python -c "import sys;sys.path.insert(0,'.');from ytf.config import Config,resolve_font;Config.load();print('font:',resolve_font('w9'))"

REM 2. サムネが描けるか（フォントの確認になる）
.venv\Scripts\python scripts\gen_thumbnails.py toyoda-kiichiro

REM 3. 音声が作れるか（VOICEVOXとAquesTalkの確認）
.venv\Scripts\python -m ytf.cli voice toyoda-kiichiro

REM 4. 動画が焼けるか（ffmpegの確認）
.venv\Scripts\python -m ytf.cli make toyoda-kiichiro --skip-reading-check

REM 5. YouTubeに繋がるか（送信はしない）
.venv\Scripts\python scripts\upload_youtube.py thumbnail-all --dry-run
```

**2 でサムネを出したら、Macで作った既存のサムネと並べて見比べること。**
フォントが違うと字の太さが変わる。同じに見えなければ ④ をやり直す。

---

## 既知の違い・注意

- **日本語のフォルダ名**（`projects/アップロード済み/人物物語/...`）を使っている。
  Windows でも動くが、**パスが長くなりやすい**。リポジトリを
  `C:\Users\<name>\Documents\...` のような深い場所に置くと 260 文字制限に当たる。
  **`C:\yt` のような浅い場所に置く**か、長いパスを有効にする:
  ```
  reg add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1 /f
  ```
- **改行コード**。`.gitattributes` が無いので、Git の設定次第で LF/CRLF が混ざる。
  混ぜたくなければ `git config core.autocrlf false` にしておく。
- **`frames/` が巨大**（1本で1〜2GB）。ビルドのキャッシュなので消してよい。
  ディスクが小さいPCでは、こまめに消す。
- **faster-whisper が初回だけモデルを落とす**（数百MB）。読み検査の3種目で使う。
  オフラインのPCでは事前にモデルを取得しておくこと。
- **立ち絵の PSD（`assets/characters/`）は `.gitignore` 対象**。二次配布禁止のため
  コミットしていない。手で運ぶか、`assets/characters/SOURCES.md` の入手元から
  落とし直す。無いと `make` がキャラを描けない。

---

## Mac側をどうするか

**両方で作業しないほうがいい。** `projects/` の `out/` は Git 管理外なので、
2台で別々にビルドすると、どちらが最新か分からなくなる。

移行するなら、Windows に移した時点で **Mac 側では新規ビルドをしない**と決めて、
Git だけで台本と設定を同期するのが安全。
