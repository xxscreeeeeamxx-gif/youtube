# 効果音の出典

**音源ファイルは git 管理しない**（`assets/se/` は .gitignore 対象）。
2026-09-18 まで、このフォルダには出典の記録が無かった。失うと取り直せないので記録する。

## 効果音ラボ

- 入手元: https://soundeffect-lab.info/
- 利用規約: https://soundeffect-lab.info/agreement/
- 商用利用可・クレジット表記不要
- **再配布は禁止**。規約の禁止事項に「再配布禁止」、該当例として
  「効果音を販売もしくは配布」と明記されている

| ファイル | 用途 |
|---|---|
| `don.mp3` | 登場・宣告。衝撃演出（画面シェイク＋押しズーム＋集中線）が自動で付く |
| `oti.mp3` | ボケのオチ |
| `jaan.mp3` | 発表・お披露目 |
| `pinpon.mp3` | 正解 |
| `bubu.mp3` | 不正解。**ドラマ回では使わない**（SKILL.md の方針） |
| `levelup.mp3` | 達成・進歩 |
| `pop.mp3` | 小さな出現 |
| `trans.mp3` | 場面転換（channel.yaml の video.transition.se が参照） |
| `xylo.mp3` | 章切り替えのピアノ |
| `tsukkomi.mp3` | ビシッ（鋭いツッコミ）anime/mp3/tsukkomi-1.mp3 |
| `hammer.mp3` | ピコッハンマー（軽いツッコミ）anime/mp3/pico-pico-hammer1.mp3 |
| `zukko.mp3` | ずっこけ ドテーン anime/mp3/fall-down1.mp3 |
| `chin.mp3` | チーン（失敗・がっかり）anime/mp3/tin1.mp3 |
| `manuke.mp3` | 間抜け・気の抜ける音 anime/mp3/stupid5.mp3 |
| `gaan.mp3` | ピアノでガーン（ショック）anime/mp3/shock2.mp3 |
| `bikkuri.mp3` | 頭の上に「！」（驚き）anime/mp3/surprise1.mp3 |
| `hirameki.mp3` | ひらめく anime/mp3/flash1.mp3 |
| `tenten.mp3` | 目が点 カーン、カァカァ（しらけ）anime/mp3/stunned1.mp3 |
| `shobon.mp3` | しょげる anime/mp3/cute-sad1.mp3 |
| `namida.mp3` | 涙のしずく（しんみり）anime/mp3/teardrop1.mp3 |

2026-09-29 に上の11個を追加（ユーザー承認のうえ取得）。ここから下の個別パスは
`https://soundeffect-lab.info/sound/` からの相対。ytf/assets_gen.py の SE_SOURCES にも登録してあるので、
別のPCでは `_gen_se_library` を流せば同じ物が揃う。

個々の音源ページのURLは当時記録されていない。取り直すときは上記サイトで
用途の近い音を選び直すことになる（尺が変わると台本側の間の取り方に影響する）。

## この素材をコミットしてはいけない

再配布禁止のため、**公開・非公開を問わず GitHub に上げない**。
PC間の移動はUSBメモリか自分のクラウドドライブで行う（自分の別のPCに
自分のコピーを移すのは配布ではない）。
