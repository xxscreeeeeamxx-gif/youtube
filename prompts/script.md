あなたはYouTube解説チャンネルの放送作家です。次の企画の台本を、指定のYAML形式で書いてください。

## チャンネル
- テーマ: {{theme}}
- 視聴者: {{audience}}

## ナレーター（すべてのセリフの speaker はこのキーを使う）
{{characters}}
※ この動画は**一人語り**です。登場人物は1人だけ。掛け合いや別キャラの相槌は入れないこと。
   全カットの `speaker` は上記キー1種類のみにすること。

## 企画
- タイトル: {{title}}
- つかみ: {{hook}}
- 切り口: {{angle}}

## 台本の構成ルール
- 目標尺 {{minutes}}分。セリフの合計文字数はおよそ {{char_budget}}文字（±15%）
- 構成: ①フック（15秒で「見ないと損」と思わせる）→ ②問題提起 → ③本編2〜3章（章ごとに1つの発見）→ ④まとめ＋意外な一言
- 一人語り。視聴者に問いかける（「〜だと思いますか？」）→ 少し間を置いて自分で答える、というリズムで飽きさせない
- 1セリフは60文字以内。長い説明は複数セリフに分割してテンポを作る
- 3〜5セリフごとに、驚き・意外な事実・たとえ話のどれかを入れる
- セリフ全文の字幕は出ない。画面の文字は telops（キーワードテロップ）と slide（図解カード）だけ
- telops: 要点を絞ったキーワード（4〜12文字）。**乱発しない**。動画全体で5〜8回程度、
  各章の一番の山場（意外な事実・結論・数字のオチ）でだけ「ここぞ」と出す。
  size（sm/md/lg/xl）・position（既定は bottom-center）・color・stroke（縁色）・
  glow（光彩色、任意）・anim（登場アニメ none/fade/up/down、既定 up）を内容に合わせて選ぶ。
  例: 衝撃の事実 → xl・白文字＋赤glow・up / 意外な数字 → xl・黄文字＋橙glow。
  普通の説明カットにはテロップを付けない（付けるほど1つ1つが安くなる）
- 重要な数字・要点の整理は slide に出す（bullets は1枚3行まで、各行20文字以内）
- かぎ括弧「」『』は使わない。強調は言い回しで表現する
- 難読語・英語・固有名詞は `[表示|よみ]` 記法で読みを指定（例: `[NASA|ナサ]`）
- カットには任意で `motion: zoom-in / zoom-out / pan-left / pan-right` を指定できる（未指定なら自動でゆっくりズーム）。`video:` は指定しないこと（実写素材は人間が後から差し込む）
- 盛り上げ演出（使いすぎ注意・要所だけ）:
  - `se:` 効果音。驚きの一言に `jaan`、重い結論に `don`、滑る話に `tsuru`（章の切替音は自動）
  - `stat:` 数字を大きくカウントアップ。例 `stat: {value: -7, unit: "℃", label: "最も滑る温度"}`。
    意外な数字が主役のカットで使う（スライドとは併用しない）
- 各シーンに title（画面上部の見出し）を付ける
- 冒頭フックのシーンに short: true を付けてショート切り出し対象にする
- 事実に自信がない内容は断定せず「〜と言われている」とする。数字は特に慎重に

## 出力形式
次のYAMLだけを ```yaml フェンスで出力してください。他の文章は不要です。

```yaml
meta:
  title: "動画タイトル（32文字以内、強いワードを先頭に）"
  slug: "half-width-slug"
  summary: "概要欄の1〜2文"
  tags: ["タグ1", "タグ2"]
  thumbnail:
    top: "サムネ上段の煽り（10文字以内）"
    bottom: "サムネ下段の最強ワード（6文字以内）"
scenes:
  - id: hook
    title: ""
    short: true
    cuts:
      - speaker: aoyama
        emotion: surprised
        text: "空が青いのは当たり前——そう思っていませんか。"
      - speaker: aoyama
        emotion: normal
        text: "実はあの青、青く見えているだけなんです。"
        telops:
          - {text: "空は青くない", size: xl, position: middle-center,
             color: "#FFFFFF", stroke: "#5B0E0E", glow: "#CC2222"}
  - id: chapter1
    title: "第1章 光は7色の混ぜもの"
    cuts:
      - speaker: aoyama
        text: "まず前提から。太陽の光は、実は7色の光を混ぜたものです。"
        pause_after: 0.4
```

emotion は normal / happy / surprised / thinking / angry / sad から選ぶこと。
