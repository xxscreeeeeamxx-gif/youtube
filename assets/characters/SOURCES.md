# 立ち絵素材の出典

素材本体は二次配布禁止のため git 管理しない（このフォルダは .gitignore 対象）。
再取得できるようここに出典を記録する。

| キャラ | フォルダ | 素材 | 入手元 | 備考 |
|---|---|---|---|---|
| ずんだもん | zundamon/ | 坂本アヒル氏 立ち絵PSD | https://seiga.nicovideo.jp/seiga/im10788496 → https://ux.getuploader.com/s_ahiru/download/37 (PW: zunda) | 東北ずん子プロジェクトのガイドライン範囲で利用可。クレジット: 坂本アヒル |
| 春日部つむぎ | tsumugi/ | 坂本アヒル氏 立ち絵PSD（2021/11/14公開・無料） | 製作: 坂本アヒル https://twitter.com/sakamoto_ahr ／ 公式利用規約 https://tsukushinyoki10.wixsite.com/ktsumugiofficial | 春日部つむぎ公式RULE準拠で商用可・改変可・クレジット任意。PSDToolでレイヤー切替 |

- `<フォルダ>/<emotion>.png`（normal/happy/surprised/thinking/angry/sad）を置く。無い感情は normal にフォールバック
- 未入手の間は `ytf assets --init` のプレースホルダーで代用できる

## 失ったときの復旧手順（2026-09-18 追記）

**PSD本体はこのリポジトリにも手元にも残っていない**（確認済み・0個）。
PNGだけを保持している。復旧は2段階になる。

1. 上表の入手元から PSD を落とす。**ここは手作業**
   （ずんだもんは getuploader のパスワード入力が要る）
2. 書き出しは自動化済み:

   ```bash
   PYTHONPATH=. python3 scripts/export_zundamon_sprites.py <PSDファイル>
   PYTHONPATH=. python3 scripts/export_tsumugi_sprites.py <PSDファイル>
   ```

   PSDTool形式のレイヤー可視状態を切り替えて6感情を書き出し、
   共通bboxで切り抜く。`assets/characters/<キャラ>/<emotion>.png` に出る。

`zunda/` と `metan/` は上の2スクリプトの対象外。失うと復旧手順が無いので、
**PNGのバックアップを別途持っておくこと**（このフォルダ全体で4.6MB）。

## この素材をコミットしてはいけない

二次配布禁止のため、公開・非公開を問わず GitHub に上げない。
PC間の移動はUSBメモリか自分のクラウドドライブで行う。
