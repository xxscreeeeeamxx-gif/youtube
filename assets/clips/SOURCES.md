# 動画クリップの出典

動画ファイル自体はサイズが大きいため git 管理せず（`assets/clips/` は .gitignore 対象）、
ここに出典を記録して再取得できるようにする。すべて Pexels License（クレジット不要・商用可）。

| ファイル | 内容 | 作者 | 出典 |
|---|---|---|---|
| skate_spiral.mp4 | フィギュアスケートのスパイラル | Pavel Danilyuk | https://www.pexels.com/ で "figure skating ice" |
| melting_ice.mp4 | つらら・溶ける氷 | Geun Goh | https://www.pexels.com/ で "melting ice water" |
| demo.mp4 | 動作確認用テストパターン（`ytf assets --init` で生成・再生成可能） | — | — |
| battery_anim.mp4 | 電池仕組みアニメ2フェーズ（自作。`scripts/gen_battery_anim.py`・battery-80用） | — | — |
| battery_anim_duo.mp4 | 電池仕組みアニメ4フェーズ（自作。`scripts/gen_battery_anim_duo.py`・battery-80-duo用） | — | — |
| hook_gauge.mp4 | 充電ゲージ→寿命バーアニメ（自作。`scripts/gen_infographics.py`） | — | — |
| graph_decay.mp4 | 容量劣化グラフアニメ（自作。同上） | — | — |
| toggle_80.mp4 | 設定トグル→80%停止アニメ（自作。同上） | — | — |
| care_checklist.mp4 | 電池ケア3項目チェックリストアニメ（自作。同上） | — | — |
| heat_flame.mp4 | 燃える薪の炎クローズアップ | Paul Antonescu | https://www.pexels.com/video/close-up-of-burning-wood-6755351/ |
| settings_tap.mp4 | スマホ操作のクローズアップ | Coverr | https://www.pexels.com/video/blurred-video-of-man-scrolling-on-his-phone-853985/ |
| ev_charge.mp4 | EV充電ステーション | Kindel Media | https://www.pexels.com/video/close-up-shot-of-a-car-at-a-charging-station-9790134/ |
| sleep_phone.mp4 | 就寝中の人 | cottonbro studio | https://www.pexels.com/video/a-woman-sleeping-in-a-white-bed-6753381/ |
| hot_car.mp4 | フロントガラス越しの強い日差し | Ton Souza | https://www.pexels.com/video/the-glare-of-the-sun-causing-diminished-visibility-in-driving-4377434/ |
| wireless_charge.mp4 | ワイヤレス充電器に置く手元 | Pixabay | https://www.pexels.com/video/samsung-charging-855932/ |
| old_phone.mp4 | スマホの設定画面を操作する手元 | Foysal Ahmed | https://www.pexels.com/video/a-person-checking-the-battery-rate-of-his-mobile-phone-4201544/ |

再取得は `ytf media "<検索語>" --video` か、`ytf edit` の素材ブラウザ「動画」から。
