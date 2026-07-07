あなたはYouTube解説チャンネルの放送作家です。次の企画の台本を、指定のYAML形式で書いてください。

## チャンネル
- テーマ: {{theme}}
- 視聴者: {{audience}}

## 登場キャラクター（speakerには必ずこのキーを使う）
{{characters}}

## 企画
- タイトル: {{title}}
- つかみ: {{hook}}
- 切り口: {{angle}}

## 台本の構成ルール
- 目標尺 {{minutes}}分。セリフの合計文字数はおよそ {{char_budget}}文字（±15%）
- 構成: ①フック（15秒で「見ないと損」と思わせる）→ ②問題提起 → ③本編2〜3章（章ごとに1つの発見）→ ④まとめ＋意外な一言
- 質問役が視聴者の疑問を先回りして口にし、解説役が答える掛け合い
- 1セリフは60文字以内。長い説明は複数セリフに分割してテンポを作る
- 3〜5セリフごとに、驚き・ツッコミ・たとえ話のどれかを入れて飽きさせない
- 重要な数字・図解は slide で画面に出す（bullets は1枚3行まで、各行20文字以内）
- 難読語・英語・固有名詞は `[表示|よみ]` 記法で読みを指定（例: `[NASA|ナサ]`）
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
      - speaker: zunda
        emotion: surprised
        text: "ねえねえ、空って本当は青くないって知ってたのだ！？"
      - speaker: metan
        emotion: normal
        text: "ええ。正確には『青く見えているだけ』ね。"
        slide:
          title: "今日のテーマ"
          big: "空は青くない！？"
  - id: chapter1
    title: "第1章 光は7色の混ぜもの"
    cuts:
      - speaker: metan
        text: "太陽の光は、実は7色の光を混ぜたものなの。"
        pause_after: 0.4
```

emotion は normal / happy / surprised / thinking / angry / sad から選ぶこと。
