# サムネイル用フォントの入手元とライセンス

- genkai-mincho.ttf — 源界明朝（フロップデザイン）
  入手: https://www.flopdesign.com/freefont/genkai.html
  ライセンス: SIL Open Font License 1.1（商用可・再配布可）
- 851CHIKARA-DZUYOKU_kanaA_004.ttf — 851チカラヅヨク かなA Ver0.04
  入手: https://pm85122.onamae.jp/851ch-dz.html
  ライセンス: フリーフォント（商用可・改造再配布自由・著作権は放棄せず）
- (任意) ラノベPOP v2 — BOOTHログインが必要なため未取得。
  https://booth.pm/ja/items/2328262 から入手して本ディレクトリに置くと
  scripts/gen_thumbnails.py が自動で使う

## Noto Sans JP（同梱・Git管理下）

- `NotoSansJP-Black.otf` / `NotoSansJP-Bold.otf`
- 出典: https://github.com/notofonts/noto-cjk `Sans/SubsetOTF/JP/`
- ライセンス: SIL Open Font License 1.1（**再配布可・商用可**）
- 用途: `resolve_font()` の w9 / w6。**探索順の先頭**なので、Mac でも Windows でも
  これが使われる＝どちらで作っても同じ絵が出る
- 日本語サブセット版を選んだ理由: フルCJK版は1本17MBでリポジトリが太る。
  日本語サブセットなら4.6MBで、このチャンネルの用途には十分

### 使っていないフォント（Git管理外・手で運ぶ必要なし）

`genkai-mincho.ttf` と `851CHIKARA-DZUYOKU` は、サムネを2分割に作り直した
（2026-09-12）時点で**全SPECから外れた**。gen_thumbnails.py の FONTS 辞書に
定義だけ残っているが、どのレイアウトからも呼ばれない。Windows に持っていく必要はない。
