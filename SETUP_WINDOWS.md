# Windows PC への移行手順

このリポジトリを Windows で動かすための手順。
**コードもフォントも両OS対応済み**（2026-09-18）。あとは外部ツール3つ
（ffmpeg / AquesTalkPlayer / VOICEVOX）と素材1.0GBを入れるだけ。

移行で引っかかるのは、コードではなく**リポジトリに入っていないもの**。
ライセンス上コミットできない素材が多く、`git clone` しただけでは動かない。

## まず容量の話（ここを間違えると丸一日溶ける）

| | 容量 | どうするか |
|---|---|---|
| リポジトリ全体 | **87 GB** | 全部コピーしてはいけない |
| └ うち生成物（`out/` `frames/` `audio/`） | **85 GB** | **運ばない**。ビルドし直せば再生成される |
| └ Git管理分 | 50 MB | `git clone` で入る |
| └ **Git管理外だが必要な素材** | **80 MB** | **手で運ぶ**（下表） |

**運ぶのは 80 MB だけ。** どんなUSBメモリでも入る。

### 手で運ぶもの（USBメモリ等でコピー）

| フォルダ | 容量 | 中身 | 無いとどうなる |
|---|---|---|---|
| `assets/bgm/` | 75 MB | BGM | **全動画が無音の章だらけになる** |
| `assets/characters/` | 4.6 MB | 立ち絵PNG（4キャラ×表情6） | **キャラが出ない** |
| `assets/se/` | 380 KB | 効果音 | 「ドン」などが鳴らない |
| `client_secret.json` | 数KB | YouTube APIの認証情報 | 投稿できない |

**`assets/clips/`（934MB）は運ばない**（2026-09-18 に調査して除外）。
実写クリップと自作アニメが入っているが、参照しているのは**公開済みの動画だけ**で、
それらは方針上ビルドし直さない。新作の人物物語4本（トヨタ・ブリヂストン・
サントリー・オムロン）を調べたところ `video:` の参照は**0件**だった。
新作のアニメは `gen_*_extras.py` がその場で作って `assets/clips/` に書き出すので、
空のフォルダから始めて問題ない。背景389枚は Git 管理下なので clone で入る。

**`tools/` は運ばない。** 中身は ffmpeg / ffprobe / AquesTalkPlayer の
**Mac用バイナリだけ**なので、Windows では②③で入れ直す。
ほかはそのままコピーでよい。`.psd` も `.mp3` も `.mp4` もOS非依存。

**フォントも運ばなくてよい**（2026-09-18 変更）。Noto Sans JP を
リポジトリに同梱したので `git clone` で入る。④参照。

### 運ばないもの

- `projects/**/out/` `frames/` `audio/` — **85GBの正体**。ビルドで再生成される
- `tools/` — Mac用バイナリ。Windows版を入れ直す（②③）
- `.venv/` — OSが違うので作り直す（①）
- `.youtube_token.json` — 2台で共有すると片方が弾かれる。各PCで取り直す（⑥）

### 手順

```
REM 1. Gitで台本・設定・背景を持ってくる
git clone <リポジトリのURL> C:\yt
cd C:\yt

REM 2. Macから素材をコピー（USBメモリ経由）
REM    assets\clips assets\bgm assets\characters assets\se
REM    client_secret.json
REM    ※ tools と assets\fonts は運ばない
```

**Mac側でUSBに入れるときは、生成物を除いて固めること**（そのまま `assets` を
コピーすれば済むが、`projects` は絶対に含めない）:

```bash
zip -r -q ~/Desktop/ytf-assets.zip \
    assets/bgm assets/characters assets/se
```

---

## 手を動かす人が最小で済むやり方（推奨）

Windows 側に Claude Code が入っているなら、**人がやるのは3つだけ**:

1. USBメモリを Windows PC に挿す
2. Claude Code を開いて、下の1文を貼る
3. ⑥ でブラウザが開いたら YouTube の承認を押す

```
https://github.com/xxscreeeeeamxx-gif/youtube.git を C:\yt にcloneして、
SETUP_WINDOWS.md のとおりに移行を完了して。素材とclient_secret.jsonは
USBメモリの「Windows移行用」フォルダにある。⑦の動作確認まで通して。
```

### エージェント向け: 実行順と検証

人の確認を待たずに通してよい。各手順は必ず検証まで行うこと。

| | やること | 通ったと言える条件 |
|---|---|---|
| 0 | `winget` で Python 3.12 / Git / VOICEVOX を入れる | **パッケージIDは推測せず `winget search` で実物を確認してから入れる**。`python --version` が 3.12 を返す |
| 1 | `git clone ... C:\yt` | `C:\yt\ytf\cli.py` が存在する。**置き場所は C:\yt 固定**（日本語フォルダ名があり260文字制限に当たるため） |
| 2 | USBの `ytf-assets.zip` を `C:\yt` に展開、`client_secret.json` を `C:\yt` 直下へ | `C:\yt\assets\characters\zunda\normal.png` が存在する |
| 3 | ① venv と `pip install -r requirements.txt` | `.venv\Scripts\python -c "import PIL,yaml,pydantic"` が通る |
| 4 | ② ffmpeg / ffprobe を `tools\` へ | `.\tools\ffmpeg.exe -version` が出る |
| 5 | ③ AquesTalkPlayer（Windows版） | **配布ページからの入手は人の操作が要る場合がある。要るなら止めて頼むこと**。置き場所は `tools\AquesTalkPlayer\AquesTalkPlayer.exe` |
| 6 | ⑥ `upload_youtube.py auth` | **承認は人が押す。代わりに押さない。**ブラウザを開くところまでやって待つ |
| 7 | ⑦ の動作確認5本 | 5本とも通る |

**触らなくていいもの**: ④フォント（同梱済み）、`channel.yaml` の
`engine_path`/`player_path`（書くとOS判定を壊す。②③で既定の場所に置けば足りる）。

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

## ④ フォント（作業不要）

**2026-09-18 に解決済み。何もしなくていい。**

以前はここが最大の落とし穴だった（ヒラギノ角ゴシック W9 は macOS 専用で、
サムネの見出しも本編のテロップも全部これを使っていたため）。
**Noto Sans JP をリポジトリに同梱した**ので、`git clone` した時点で入っている。

```
assets/fonts/NotoSansJP-Black.otf   4.6 MB   w9（見出し・テロップ）
assets/fonts/NotoSansJP-Bold.otf    4.4 MB   w6（本文・スライド）
```

`resolve_font()` の**探索順の先頭**なので、Mac でもこちらが使われる。
つまり**どちらのPCで作っても字形が完全に一致する**。
ライセンスは SIL Open Font License 1.1（再配布可・商用可）。

ヒラギノ W9 との差は実測で見出し幅924px一致・縦線がわずかに細い程度で、
サムネの実寸168pxでは見分けがつかない。既存32本と並べても浮かない。

### 飾りフォント（源界明朝・851チカラヅヨク）は要らない

サムネを2分割に作り直した時点（2026-09-12）で**全SPECから外れている**。
現在はすべて `layout="panels"` ＋ `font("w9")` のみ。
`gen_thumbnails.py` の `FONTS` 辞書に定義だけ残っているが、どこからも呼ばれない。
**Windows に持っていく必要はない**（どちらも再配布不可なので Git にも入っていない）。

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
同梱フォントを使うので一致するはずだが、ここがズレていれば
`assets/fonts/NotoSansJP-Black.otf` が clone されていない
（＝OS標準フォントに落ちている）。1 の出力で実際のパスが確認できる。

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
- **立ち絵（`assets/characters/`）は `.gitignore` 対象**。二次配布禁止のため
  コミットしていない。中身は PSD ではなく**書き出し済みの PNG**で、
  `zunda/ tsumugi/ zundamon/ metan/` の下に `normal happy sad surprised thinking angry`
  の6枚ずつ（計24枚）。手で運ぶか、`assets/characters/SOURCES.md` の入手元から
  落とし直す。無いと `make` がキャラを描けない。

---

## Mac側をどうするか

**両方で作業しないほうがいい。** `projects/` の `out/` は Git 管理外なので、
2台で別々にビルドすると、どちらが最新か分からなくなる。

移行するなら、Windows に移した時点で **Mac 側では新規ビルドをしない**と決めて、
Git だけで台本と設定を同期するのが安全。
