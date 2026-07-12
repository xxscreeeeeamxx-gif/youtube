# BGMの出典

音源ファイルは git 管理しない（assets/bgm/ は .gitignore 対象）。ここに出典を記録して再取得できるようにする。

## DOVA-SYNDROME（フリーBGM・商用利用可・クレジット表記不要）

利用規約: https://dova-s.jp/_contents/license/ に従う。加工可・YouTube収益化可。
再取得: 各詳細ページの「ダウンロード」から（ループ版があるものはループ版を採用）。

| ファイル | 曲名 | 作曲者 | 出典 |
|---|---|---|---|
| haru_kitchen.mp3 | 春のキッチン | もっぴーさうんど | https://dova-s.jp/bgm/detail/2881 |
| shuffle_shuffle.mp3 | shuffle shuffle | KK | https://dova-s.jp/bgm/detail/5598 |
| natsuyasumi.mp3 | 少年達の夏休み的なBGM | 鷹尾まさき(タカオマサキ) | https://dova-s.jp/bgm/detail/2190 |
| jitaku_nite.mp3 | 自宅にて | KK | https://dova-s.jp/bgm/detail/4041 |
| honwaka_puppu.mp3 | ほんわかぷっぷー | もっぴーさうんど | https://dova-s.jp/bgm/detail/1854 |
| hirusagari.mp3 | 昼下がり気分 | KK | https://dova-s.jp/bgm/detail/4695 |
| pastel_house.mp3 | パステルハウス | かずち | https://dova-s.jp/bgm/detail/1021 |
| 10do.mp3 | 10℃ | しゃろう | https://dova-s.jp/bgm/detail/12420 |
| 223am.mp3 | 2:23 AM | しゃろう | https://dova-s.jp/bgm/detail/13494 |
| you_and_me.mp3 | You and Me | しゃろう | https://dova-s.jp/bgm/detail/13787 |
| kinakusai.mp3 | むむ・・・きな臭いぞ！！ | こばっと | https://dova-s.jp/bgm/detail/11618 |
| serious.mp3 | シリアス | japaneo | https://dova-s.jp/bgm/detail/8526 |

### 状況別の使い分けガイド

- ほのぼの・日常・ゆる解説: 10do(10℃) / haru_kitchen(春のキッチン) / pastel_house / honwaka_puppu / jitaku_nite
- 軽快・楽しい・テンポよく: shuffle_shuffle / natsuyasumi / hirusagari / you_and_me
- しんみり・感動・開発秘話: 223am(2:23 AM)
- 怪しい・注意喚起・詐欺の話: kinakusai(むむ・・・きな臭いぞ！！)
- シリアス・緊張感: serious(シリアス)

## 自作（コミット不要・再生成可能）

- ambient / mystery / warm / beat: `ytf assets --init` のシンセ生成
- pop: MusicGen生成（`ytf bgm`）

切り替えは channel.yaml の video.bgm.file か、`ytf edit` の 🎵BGM ピッカーから。
