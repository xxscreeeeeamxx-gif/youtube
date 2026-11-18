#!/usr/bin/env python3
"""第13弾4本（2026-12-14〜17。方向転換の実験の27〜30本目）の背景を生成する。

接頭辞: fj_（不二家の期限切れ原料）/ mm_（三菱自動車のリコール隠し）/ pu_（ぷよぷよとコンパイルの破綻）/ ah_（耐震偽装）
方針は gen_now12_bgs.py と同じ。実在の会社のロゴ・社名の文字・店の意匠・商品のパッケージは描かない。
実在のゲームの画面・キャラクター・ぷよ（色の玉）は描かない（画面は色の四角だけ）。ペコちゃんの絵も描かない。
実在の人の写真や肖像は描かない。差し替え用は元の絵に要素を足すか減らす。

実行: PYTHONPATH=. python scripts/gen_now13_bgs.py [名前...]
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.gen_drama_bgs import H, OUT, W, base, vgrad, wood_floor  # noqa: E402
from scripts.gen_famicom_bgs import _crt, _phone, _shacho_base, _text_c, _window, kaihatsu as _fc_kaihatsu, year_card  # noqa: E402
from scripts.gen_anpan_bgs import kobo_manju, mise as _anpan_mise  # noqa: E402
from scripts.gen_tamagotchi_bgs import _office_base, pc as _tama_pc  # noqa: E402
from scripts.gen_now2_bgs import heya2  # noqa: E402
from scripts.gen_now3_bgs import jimusho90, tenjikai  # noqa: E402
from scripts.gen_now8_bgs import ld_tower, tj_kaiken, tj_shinbun  # noqa: E402
from scripts.gen_now_bgs import kaigi as _now_kaigi  # noqa: E402
from scripts.gen_now9_bgs import _light, _press  # noqa: E402
from scripts.gen_now_bgs import FLOOR, _d, _rgb  # noqa: E402
from scripts.gen_sega_bgs import _person_line, kaiken as _sega_kaiken  # noqa: E402
from scripts.gen_sogo_bgs import uriba as _sogo_uriba, uriba_kara as _sogo_uriba_kara  # noqa: E402
from scripts.gen_sogo_bgs import saibansho as _sogo_saibansho  # noqa: E402
from scripts.gen_now2_bgs import shingikai  # noqa: E402
from scripts.gen_tb_bgs import yakusho as _tb_yakusho  # noqa: E402

SQ = [(230, 70, 70), (60, 140, 230), (250, 200, 50), (70, 180, 100), (170, 90, 210)]   # 色の四角（ゲームの画面の代わり）


def _lines(d, x0, y0, x1, n, gap=34, col=(110, 110, 110), w=5):
    """文字の代わりの線。"""
    for j in range(n):
        d.line([(x0, y0 + j * gap), (x1 - (j % 3) * 40, y0 + j * gap)], fill=col, width=w)


def _dark(img, alpha=120, col=(10, 14, 30)):
    """全体を暗くする（夜・消灯）。"""
    from PIL import Image
    layer = Image.new("RGBA", img.size, (*col, alpha))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def _squares(d, x0, y0, x1, y1, n=6, seed=1):
    """画面の中の色の四角（ゲームの画面の代わり）。"""
    rnd = random.Random(seed)
    cw = (x1 - x0) / n
    for c in range(n):
        h = rnd.randint(1, 4)
        for r in range(h):
            s = cw * 0.8
            x = x0 + c * cw + cw * 0.1
            y = y1 - (r + 1) * s - 6
            if y < y0:
                break
            d.rectangle([x, y, x + s, y + s], fill=SQ[rnd.randint(0, len(SQ) - 1)])


# ---------------------------------------------------------------- ぷよぷよとコンパイルの破綻
def pu_heya():
    """今の部屋。机に豚の貯金箱とカードのケース（茶番）。"""
    img = heya2("none")
    d = _d(img)
    d.ellipse([240, 560, 380, 640], fill=(240, 170, 180), outline=(180, 110, 120), width=3)        # 貯金箱
    d.ellipse([350, 580, 390, 610], fill=(230, 150, 160))
    d.rectangle([290, 556, 330, 562], fill=(120, 80, 80))
    for k in range(2):
        d.rectangle([270 + k * 70, 630, 290 + k * 70, 648], fill=(220, 150, 160))
    d.rounded_rectangle([430, 590, 540, 642], radius=6, fill=(60, 90, 160), outline=(30, 50, 100), width=3)  # カードのケース
    d.rectangle([446, 600, 524, 632], fill=(200, 220, 250))
    return img


def pu_shachoshitsu(mode=""):
    """広島の社長室。大きな机と本棚。
    yoru は夜（机に電話と封筒の束）、e は壁に丸い屋根の建物の大きな絵（架空）、
    shorui は机に書類が山になって崩れる、kara は壁の絵が外され、日に焼けていない四角い跡だけ。"""
    img = _shacho_base()
    d = _d(img)
    if mode == "e":
        d.rectangle([110, 130, 700, 520], fill=(250, 248, 240), outline=(120, 96, 70), width=12)
        d.rectangle([130, 150, 680, 380], fill=(170, 210, 236))
        d.pieslice([230, 210, 580, 520], 180, 360, fill=(250, 250, 250), outline=(150, 150, 160), width=4)  # 丸い屋根
        for k in range(5):
            d.arc([250 + k * 20, 230 + k * 18, 560 - k * 20, 520 - k * 18], 180, 360, fill=(200, 206, 220), width=3)
        d.rectangle([130, 365, 680, 500], fill=(130, 180, 120))
        for x in (170, 610):                                                                    # 両脇の塔
            d.rectangle([x, 250, x + 40, 365], fill=(240, 236, 226), outline=(150, 150, 160), width=3)
            d.polygon([(x - 6, 250), (x + 20, 210), (x + 46, 250)], fill=(220, 90, 80))
        d.rectangle([330, 365, 480, 395], fill=(230, 230, 236))
    elif mode == "kara":
        d.rectangle([110, 130, 700, 520], fill=(228, 222, 208), outline=(206, 198, 182), width=4)
        d.ellipse([398, 112, 412, 126], fill=(90, 80, 70))
    if mode == "yoru":
        img = _dark(img, 130)
        d = _d(img)
        img = _light(img, [[(1180, 560), (1420, 560), (1500, 700), (1100, 700)]], (255, 220, 150), alpha=60)
        d = _d(img)
        d.rectangle([1250, 520, 1270, 600], fill=(60, 60, 60))                                 # 卓上の灯り
        d.polygon([(1220, 520), (1300, 520), (1280, 490), (1240, 490)], fill=(200, 170, 90))
    if mode == "shorui":
        rnd = random.Random(7)
        for k in range(26):
            x = 640 + rnd.randint(0, 640)
            y = 640 - rnd.randint(0, 160)
            d.rectangle([x, y - 70, x + 120, y], fill=(246, 242, 230), outline=(170, 160, 140), width=2)
        for k in range(7):
            x = 560 + k * 130
            d.polygon([(x, 930), (x + 110, 912), (x + 120, 960), (x + 10, 980)], fill=(246, 242, 230), outline=(170, 160, 140))
    elif mode in ("", "e", "kara"):
        for k in range(3):
            x, y = 960 + k * 22, 640 - k * 8
            d.rectangle([x, y - 60, x + 120, y + 20], fill=(244, 240, 228), outline=(170, 160, 140), width=2)
    if mode == "yoru":
        for k in range(6):                                                                      # 封筒の束
            d.rectangle([760 + k * 10, 600 - k * 6, 900 + k * 10, 660 - k * 6], fill=(236, 226, 196), outline=(150, 130, 100), width=2)
    _phone(d, 1220, 590, 0.6)
    return img


def pu_inshokuten():
    """1990年の東京の飲食店。テーブル席、吊り下げの灯り、壁の品書き（文字は線だけ）。"""
    img = _rgb(base((200, 170, 130), (176, 146, 110)))
    wood_floor(img, FLOOR, col=(110, 80, 56), line=(92, 66, 46))
    d = _d(img)
    d.rectangle([0, 560, W, 600], fill=(120, 84, 56))
    for k in range(6):
        x = 120 + k * 300
        d.rectangle([x, 120, x + 70, 420], fill=(250, 244, 226), outline=(120, 90, 60), width=3)
        d.line([(x + 35, 150), (x + 35, 390)], fill=(60, 50, 40), width=6)
    for x in (480, 1440):
        d.line([(x, 0), (x, 200)], fill=(60, 50, 40), width=3)
        d.pieslice([x - 70, 170, x + 70, 290], 180, 360, fill=(230, 170, 90))
    img = _light(img, [[(410, 230), (550, 230), (640, 700), (320, 700)], [(1370, 230), (1510, 230), (1600, 700), (1280, 700)]], (255, 230, 170), alpha=40)
    d = _d(img)
    for cx in (480, 1440):
        d.rectangle([cx - 230, 680, cx + 230, 710], fill=(90, 60, 40))
        d.rectangle([cx - 20, 710, cx + 20, 900], fill=(70, 46, 30))
        d.ellipse([cx - 60, 660, cx - 10, 684], fill=(250, 250, 250))
        d.ellipse([cx + 20, 660, cx + 70, 684], fill=(250, 250, 250))
    return img


def pu_kissaten():
    """喫茶店。窓のブラインド、4人がけのテーブルにコーヒーカップ。"""
    img = _rgb(base((150, 110, 80), (128, 92, 66)))
    wood_floor(img, FLOOR, col=(90, 62, 44), line=(74, 50, 36))
    d = _d(img)
    d.rectangle([520, 110, 1400, 470], fill=(220, 214, 196), outline=(70, 50, 36), width=10)
    for k in range(12):
        d.line([(530, 130 + k * 28), (1390, 130 + k * 28)], fill=(190, 180, 160), width=8)
    for x in (200, 1720):
        d.ellipse([x - 60, 200, x + 60, 320], fill=(90, 130, 80))
        d.rectangle([x - 30, 320, x + 30, 420], fill=(130, 90, 60))
    d.rectangle([700, 690, 1220, 720], fill=(70, 46, 30))
    d.rectangle([940, 720, 980, 900], fill=(54, 36, 24))
    for x in (780, 900, 1020, 1120):
        d.ellipse([x, 668, x + 50, 692], fill=(250, 250, 246), outline=(150, 140, 130), width=2)
        d.ellipse([x + 10, 672, x + 40, 684], fill=(100, 60, 40))
    return img


def pu_kaihatsu():
    """開発室。机にパソコンが並び、画面は色の四角だけ。"""
    img = _office_base()
    d = _d(img)
    d.rectangle([0, 700, W, 730], fill=(170, 160, 146))
    for k in range(6):
        x = 120 + k * 290
        d.rectangle([x, 520, x + 220, 690], fill=(200, 196, 186), outline=(120, 116, 110), width=4)
        d.rectangle([x + 16, 534, x + 204, 670], fill=(20, 24, 40))
        _squares(d, x + 24, 540, x + 196, 664, n=6, seed=k + 3)
        d.rectangle([x + 90, 690, x + 130, 700], fill=(150, 146, 140))
    return img


def pu_booth():
    """おもちゃショーの狭いブース。壁に手書きの張り紙（文字は線だけ）、人があふれる。"""
    img = tenjikai()
    d = _d(img)
    d.rectangle([780, 250, 1140, 560], fill=(252, 250, 240), outline=(160, 150, 130), width=4)
    _lines(d, 810, 300, 1110, 7, gap=36, col=(40, 40, 40), w=7)
    _person_line(d, 600, 1060, 12, 1.0)
    return img


def pu_kaijo():
    """1996年の大会の会場。大きな舞台と、客席を埋める人の頭。"""
    img = vgrad((W, H), (30, 30, 50), (50, 44, 70))
    d = _d(img)
    d.rectangle([260, 120, 1660, 560], fill=(60, 50, 90), outline=(200, 180, 90), width=8)
    for k in range(5):
        d.rectangle([300 + k * 270, 160, 520 + k * 270, 300], fill=SQ[k])
    d.rectangle([200, 560, 1720, 640], fill=(120, 90, 60))
    img = _light(img, [[(500, 0), (620, 0), (900, 560), (300, 560)], [(1300, 0), (1420, 0), (1620, 560), (1020, 560)]], (255, 240, 200), alpha=50)
    d = _d(img)
    rnd = random.Random(5)
    for r in range(6):
        for c in range(30):
            x = c * 66 + (r % 2) * 33 + rnd.randint(-6, 6)
            y = 700 + r * 64
            d.ellipse([x, y, x + 46, y + 46], fill=(20 + r * 6, 18 + r * 6, 28 + r * 6))
    return img


def pu_mensetsu():
    """面接室。机と椅子、横にカラオケの機械とマイク、小さな画面に歌詞の線。"""
    img = _office_base()
    d = _d(img)
    d.rectangle([700, 660, 1220, 690], fill=(150, 120, 90))
    d.rectangle([720, 690, 740, 900], fill=(120, 96, 70))
    d.rectangle([1180, 690, 1200, 900], fill=(120, 96, 70))
    d.rectangle([1400, 520, 1640, 900], fill=(50, 50, 60), outline=(20, 20, 24), width=4)       # カラオケの機械
    for k in range(3):
        d.ellipse([1460, 600 + k * 90, 1580, 680 + k * 90], fill=(30, 30, 36), outline=(90, 90, 100), width=3)
    d.rectangle([1380, 300, 1660, 500], fill=(30, 34, 50), outline=(80, 80, 90), width=6)
    _lines(d, 1410, 360, 1630, 3, gap=40, col=(240, 240, 140), w=8)
    d.line([(1330, 520), (1330, 900)], fill=(60, 60, 60), width=6)                              # マイクスタンド
    d.ellipse([1316, 490, 1344, 530], fill=(40, 40, 40))
    return img


def pu_keibi(asa=False):
    """夜の工事現場。足場と柵、赤い誘導の光。asa は同じ構図で朝。"""
    img = vgrad((W, H), (16, 20, 40), (40, 40, 60)) if not asa else vgrad((W, H), (190, 210, 236), (240, 220, 200))
    d = _d(img)
    for k in range(6):                                                                        # 足場
        x = 300 + k * 230
        d.line([(x, 120), (x, 760)], fill=(130, 130, 140) if not asa else (110, 110, 120), width=8)
    for r in range(5):
        d.line([(300, 160 + r * 140), (1450, 160 + r * 140)], fill=(130, 130, 140) if not asa else (110, 110, 120), width=8)
    d.rectangle([0, 760, W, H], fill=(60, 60, 64) if not asa else (150, 146, 140))
    for k in range(8):                                                                        # 柵
        x = 60 + k * 240
        d.rectangle([x, 700, x + 200, 740], fill=(240, 200, 40))
        for j in range(4):
            d.polygon([(x + j * 50, 700), (x + j * 50 + 25, 700), (x + j * 50 + 5, 740), (x + j * 50 - 20, 740)], fill=(30, 30, 30))
        d.rectangle([x + 10, 740, x + 22, 820], fill=(200, 200, 200))
    if not asa:
        img = _light(img, [[(1600, 600), (1700, 600), (1760, 760), (1540, 760)]], (255, 60, 40), alpha=60, blur=8)
        d = _d(img)
        for x in (180, 980, 1650):
            d.ellipse([x, 650, x + 30, 680], fill=(255, 80, 60))
    return img


def pu_kyoshitsu():
    """専門学校の教室。並んだ机にパソコン、前に白板。"""
    img = _office_base()
    d = _d(img)
    d.rectangle([560, 120, 1360, 420], fill=(250, 250, 248), outline=(140, 140, 140), width=6)
    _lines(d, 600, 170, 1300, 5, gap=48, col=(60, 80, 140), w=6)
    for r in range(2):
        y = 620 + r * 150
        d.rectangle([60, y + 60, W - 60, y + 80], fill=(180, 170, 156))
        for k in range(7):
            x = 110 + k * 260
            d.rectangle([x, y - 40, x + 130, y + 56], fill=(40, 44, 56), outline=(140, 140, 140), width=3)
    return img


def pu_shisaku():
    """小さな部屋の机。ノートパソコンの画面に色の四角、横にノートと鉛筆（2016年）。"""
    img = heya2("none")
    d = _d(img)
    d.rectangle([700, 640, 1220, 670], fill=(150, 120, 90))
    d.polygon([(820, 640), (1100, 640), (1140, 660), (780, 660)], fill=(170, 170, 176))
    d.rectangle([840, 440, 1080, 640], fill=(40, 44, 56), outline=(150, 150, 156), width=6)
    _squares(d, 860, 460, 1060, 625, n=5, seed=9)
    d.rectangle([1130, 600, 1210, 650], fill=(250, 248, 236), outline=(150, 150, 150), width=2)
    _lines(d, 1140, 612, 1200, 3, gap=12, col=(100, 100, 160), w=2)
    return img


def pu_gendai():
    """今の大会の会場。暗い舞台に大きな画面（色の四角）、青い照明、客席の頭。"""
    img = vgrad((W, H), (10, 14, 30), (30, 30, 60))
    d = _d(img)
    d.rectangle([360, 90, 1560, 600], fill=(14, 18, 34), outline=(80, 160, 255), width=8)
    # 画面はトーナメント表（ゲームの盤面に見えないように、線と名前の枠だけ）
    ys = [150 + k * 52 for k in range(8)]
    for k, y in enumerate(ys):
        d.rectangle([420, y, 620, y + 34], fill=(40, 60, 110), outline=(120, 170, 255), width=2)
        d.rectangle([1300, y, 1500, y + 34], fill=(40, 60, 110), outline=(120, 170, 255), width=2)
    for side, (xa, xb) in enumerate(((620, 760), (1300, 1160))):
        for k in range(0, 8, 2):
            y1, y2 = ys[k] + 17, ys[k + 1] + 17
            d.line([(xa, y1), ((xa + xb) // 2, y1), ((xa + xb) // 2, y2), (xa, y2)], fill=(120, 170, 255), width=3)
            d.line([((xa + xb) // 2, (y1 + y2) // 2), (xb, (y1 + y2) // 2)], fill=(120, 170, 255), width=3)
    for xb, xc in ((760, 900), (1160, 1020)):
        mids = [(ys[k] + ys[k + 1]) // 2 + 17 for k in range(0, 8, 2)]
        for j in range(0, 4, 2):
            d.line([(xb, mids[j]), ((xb + xc) // 2, mids[j]), ((xb + xc) // 2, mids[j + 1]), (xb, mids[j + 1])], fill=(120, 170, 255), width=3)
            d.line([((xb + xc) // 2, (mids[j] + mids[j + 1]) // 2), (xc, (mids[j] + mids[j + 1]) // 2)], fill=(120, 170, 255), width=3)
    d.line([(900, 360), (1020, 360)], fill=(255, 210, 80), width=6)
    d.rectangle([900, 470, 1020, 540], fill=(255, 210, 80), outline=(200, 150, 40), width=3)     # 優勝の台（盃は描かない）
    img = _light(img, [[(100, 0), (200, 0), (500, 700), (0, 700)], [(1720, 0), (1820, 0), (1920, 700), (1420, 700)]], (80, 160, 255), alpha=50)
    d = _d(img)
    for c in range(30):
        x = c * 66
        d.ellipse([x, 880, x + 50, 930], fill=(16, 18, 30))
        d.rounded_rectangle([x - 6, 920, x + 56, H], radius=16, fill=(20, 22, 36))
    return img


# ---------------------------------------------------------------- 不二家の期限切れ原料
def fj_heya():
    """今の部屋。ソファにクッション、その下に小さなしみ（茶番）。"""
    img = heya2("none")
    d = _d(img)
    d.rounded_rectangle([1240, 600, 1820, 760], radius=30, fill=(150, 110, 90))
    d.rounded_rectangle([1240, 520, 1820, 640], radius=30, fill=(170, 126, 104))
    d.ellipse([1500, 650, 1640, 700], fill=(120, 70, 60))
    d.rounded_rectangle([1470, 600, 1640, 690], radius=24, fill=(240, 210, 120), outline=(190, 160, 80), width=3)
    return img


def fj_shokudo():
    """本社の社員食堂の会見。前に長机とマイク、手前の長机の列、通路まで記者とカメラ。"""
    img = _rgb(base((236, 232, 222), (220, 216, 206)))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(176, 170, 160))
    for k in range(5):
        d.rectangle([90 + k * 380, 110, 340 + k * 380, 330], fill=(200, 220, 236), outline=(140, 140, 140), width=6)
    d.rectangle([0, 380, W, 400], fill=(200, 196, 186))
    d.rectangle([620, 560, 1300, 600], fill=(240, 240, 240), outline=(150, 150, 150), width=3)  # 前の長机
    d.rectangle([620, 600, 1300, 700], fill=(250, 250, 250))
    for x in (720, 960, 1200):
        d.line([(x, 560), (x - 14, 500)], fill=(40, 40, 40), width=5)
        d.ellipse([x - 26, 486, x - 4, 508], fill=(30, 30, 30))
    _press(d, 20, 1060, 7, 1.05)
    _press(d, 1420, 1060, 7, 1.05)
    return img


def fj_honsha():
    """銀座の本社ビル（2007年。社名の文字は描かない）。"""
    return ld_tower()


def fj_kaigi(mode=""):
    """本社の会議室。長い机、壁のスクリーン、壁に札（「推進委員会」）。
    gaihi はスクリーンに赤い枠の頁と「外秘」の文字、kara は紙が回収されて机が空、スクリーンは消えている。"""
    img = _rgb(base((214, 212, 206), (198, 196, 190)))
    wood_floor(img, FLOOR, col=(106, 96, 86), line=(88, 80, 72))
    d = _d(img)
    d.rectangle([600, 90, 1320, 470], fill=(250, 250, 250) if mode != "kara" else (150, 150, 150), outline=(80, 80, 80), width=6)
    if mode == "gaihi":
        d.rectangle([660, 130, 1260, 440], fill=(255, 250, 248), outline=(210, 30, 30), width=14)
        _text_c(d, 960, 150, "外秘", 64, (210, 30, 30))
        _lines(d, 700, 260, 1220, 5, gap=38, col=(200, 40, 40), w=8)
    elif mode == "":
        for k in range(5):
            h = 60 + k * 40
            d.rectangle([700 + k * 110, 420 - h, 770 + k * 110, 420], fill=(80, 120, 180))
    d.rectangle([100, 150, 420, 230], fill=(250, 248, 240), outline=(140, 120, 90), width=5)
    _text_c(d, 260, 164, "推進委員会", 40, (40, 40, 40))
    d.rectangle([240, 680, 1680, 720], fill=(110, 80, 56))
    for x in (300, 1600):
        d.rectangle([x, 720, x + 30, 900], fill=(90, 64, 44))
    if mode != "kara":
        for k in range(8):
            x = 320 + k * 170
            d.rectangle([x, 660, x + 90, 684], fill=(246, 242, 230), outline=(160, 150, 130), width=2)
            if mode == "gaihi":
                d.rectangle([x + 4, 664, x + 86, 668], fill=(210, 40, 40))
    return img


def _kan(d, x, y, s=1.0):
    """牛乳の集乳缶（左下が x, y）。"""
    w, h = 90 * s, 150 * s
    d.rounded_rectangle([x, y - h, x + w, y], radius=int(14 * s), fill=(200, 204, 210), outline=(120, 124, 130), width=3)
    d.rectangle([x + 20 * s, y - h - 20 * s, x + w - 20 * s, y - h + 4], fill=(180, 184, 190), outline=(120, 124, 130), width=3)
    d.line([(x, y - h * 0.6), (x + w, y - h * 0.6)], fill=(150, 154, 160), width=3)


def fj_kojo(kan=False):
    """埼玉工場の仕込み場。白い壁、ステンレスの台、ミキサー。kan は台の前に牛乳の缶が積まれる。"""
    img = _rgb(base((240, 242, 244), (228, 230, 232)))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(190, 196, 200))
    for k in range(4):
        d.rectangle([80 + k * 470, 100, 380 + k * 470, 140], fill=(250, 250, 240))
    d.rectangle([140, 600, 1780, 630], fill=(200, 206, 212), outline=(140, 146, 150), width=3)  # ステンレスの台
    for x in (180, 960, 1700):
        d.rectangle([x, 630, x + 24, 900], fill=(170, 176, 180))
    d.ellipse([1300, 380, 1560, 470], fill=(210, 214, 220), outline=(130, 134, 140), width=4)   # ミキサー
    d.rectangle([1320, 420, 1540, 600], fill=(200, 204, 210), outline=(130, 134, 140), width=4)
    d.rectangle([1400, 300, 1460, 400], fill=(150, 154, 160))
    for k in range(5):                                                                        # 天板（シューの皮の列）
        for j in range(4):
            d.ellipse([320 + k * 140 + j * 30, 570, 350 + k * 140 + j * 30, 596], fill=(220, 180, 110))
    if kan:
        for i, (x, y) in enumerate(((200, 900), (300, 900), (400, 900), (250, 750), (350, 750))):
            _kan(d, x, y)
    return img


def fj_keiji():
    """工場の廊下の掲示板。「遵法絶対」の貼り紙と、ほかの紙（文字は線だけ）。"""
    img = _rgb(base((232, 234, 236), (220, 222, 224)))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(186, 190, 194))
    d.rectangle([500, 140, 1420, 700], fill=(190, 150, 100), outline=(120, 90, 60), width=10)
    d.rectangle([760, 190, 1160, 660], fill=(252, 252, 250), outline=(150, 150, 150), width=3)
    _text_c(d, 960, 230, "遵法", 110, (200, 30, 30))
    _text_c(d, 960, 380, "絶対", 110, (200, 30, 30))
    _lines(d, 800, 560, 1120, 2, gap=40, col=(60, 60, 60), w=6)
    for x0, y0 in ((540, 200), (540, 430), (1200, 220), (1200, 450)):
        d.rectangle([x0, y0, x0 + 180, y0 + 190], fill=(250, 250, 244), outline=(160, 160, 160), width=2)
        _lines(d, x0 + 18, y0 + 30, x0 + 160, 4, gap=34, col=(90, 90, 90), w=5)
    return img


def fj_fax():
    """正月の本社の事務所。机のファックス機から紙が1枚出てくる。人はいない。"""
    img = _office_base()
    d = _d(img)
    d.rectangle([560, 640, 1360, 670], fill=(170, 160, 146))
    d.rectangle([880, 540, 1100, 640], fill=(226, 226, 222), outline=(110, 110, 110), width=4)
    d.rectangle([900, 556, 960, 580], fill=(60, 120, 80))
    for k in range(3):
        d.rectangle([980 + k * 30, 556, 1000 + k * 30, 572], fill=(150, 150, 150))
    d.polygon([(910, 540), (1070, 540), (1090, 430), (930, 440)], fill=(252, 252, 250), outline=(160, 160, 160))
    _lines(d, 945, 460, 1070, 3, gap=22, col=(60, 60, 60), w=4)
    d.rectangle([950, 455, 1060, 470], fill=(210, 50, 50))
    return img


def fj_koho(denwa=False):
    """人事総務部の机が1つだけの広報。電話が1台。denwa は同じ机に電話が4台。"""
    img = _office_base()
    d = _d(img)
    d.rectangle([660, 640, 1260, 670], fill=(170, 160, 146))
    for x in (680, 1220):
        d.rectangle([x, 670, x + 20, 900], fill=(140, 130, 116))
    d.rectangle([1000, 560, 1200, 640], fill=(244, 240, 228), outline=(170, 160, 140), width=2)
    xs = (760,) if not denwa else (700, 800, 900, 1000)
    for x in xs:
        _phone(d, x, 590, 0.6)
    if denwa:
        for x in xs:
            for k in range(3):
                d.arc([x - 20 - k * 16, 520 - k * 16, x + 80 + k * 16, 600 + k * 16], 200, 340, fill=(220, 60, 60), width=4)
    return img


def fj_mise(mode=""):
    """架空の洋菓子店。ショーケースにケーキ（丸と四角）、壁にクリスマスの予約の貼り紙（文字は線だけ）。
    shutter は店の正面のシャッターと「おわび」の貼り紙、akari は明かりのついたショーケース（再開の日）。"""
    if mode == "shutter":
        img = vgrad((W, H), (170, 196, 226), (220, 228, 236))
        d = _d(img)
        d.rectangle([300, 140, 1620, 880], fill=(210, 196, 180), outline=(150, 140, 130), width=6)
        d.polygon([(280, 140), (1640, 140), (1620, 230), (300, 230)], fill=(150, 60, 70))
        d.rectangle([420, 300, 1500, 880], fill=(190, 194, 200), outline=(130, 134, 140), width=6)
        for k in range(26):
            d.line([(420, 320 + k * 22), (1500, 320 + k * 22)], fill=(160, 164, 170), width=3)
        d.rectangle([820, 400, 1100, 740], fill=(252, 252, 250), outline=(160, 160, 160), width=3)
        _text_c(d, 960, 420, "おわび", 54, (30, 30, 30))
        _lines(d, 850, 520, 1070, 5, gap=40, col=(60, 60, 60), w=5)
        d.rectangle([0, 880, W, H], fill=(186, 184, 178))
        return img
    img = _rgb(base((246, 236, 226), (232, 220, 208)))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(190, 170, 150))
    d.rectangle([0, 60, W, 140], fill=(150, 60, 70))
    d.rectangle([560, 470, 1360, 800], fill=(236, 240, 244), outline=(120, 110, 100), width=8)
    d.line([(560, 640), (1360, 640)], fill=(160, 150, 140), width=6)
    rnd = random.Random(4)
    for r, y in enumerate((600, 770)):
        for k in range(7):
            x = 610 + k * 105
            if rnd.random() < 0.5:
                d.ellipse([x, y - 50, x + 70, y], fill=(250, 236, 200), outline=(200, 170, 120), width=2)
                d.ellipse([x + 26, y - 62, x + 44, y - 46], fill=(220, 40, 60))
            else:
                d.rectangle([x, y - 50, x + 70, y], fill=(240, 220, 190), outline=(190, 150, 110), width=2)
                d.rectangle([x, y - 50, x + 70, y - 38], fill=(250, 250, 250))
    if mode == "akari":
        img = _light(img, [[(560, 470), (1360, 470), (1500, 900), (420, 900)]], (255, 240, 190), alpha=60)
        d = _d(img)
        d.rectangle([570, 480, 1350, 492], fill=(255, 250, 220))
    else:
        d.rectangle([140, 220, 420, 560], fill=(252, 250, 240), outline=(160, 150, 130), width=3)  # 予約の貼り紙
        d.polygon([(280, 250), (220, 380), (340, 380)], fill=(60, 140, 80))
        d.rectangle([270, 380, 290, 400], fill=(120, 80, 50))
        _lines(d, 170, 430, 390, 3, gap=36, col=(200, 40, 40), w=6)
    return img


def fj_roka():
    """役所の廊下。長い廊下と、右にエレベーターの扉。"""
    img = _rgb(base((226, 226, 220), (212, 212, 206)))
    d = _d(img)
    d.polygon([(0, FLOOR), (760, 560), (1160, 560), (W, FLOOR)], fill=(170, 170, 164))
    d.rectangle([0, FLOOR, W, H], fill=(170, 170, 164))
    d.rectangle([760, 300, 1160, 560], fill=(200, 200, 196), outline=(170, 170, 166), width=3)
    for k in range(4):
        d.rectangle([60 + k * 160, 200 - k * 20, 140 + k * 160, 760 - k * 40], fill=(190, 176, 150), outline=(150, 140, 120), width=3)
    d.rectangle([1380, 260, 1760, 900], fill=(180, 184, 190), outline=(120, 124, 130), width=8)
    d.line([(1570, 270), (1570, 890)], fill=(120, 124, 130), width=6)
    d.rectangle([1500, 200, 1640, 240], fill=(40, 40, 40))
    d.ellipse([1555, 208, 1585, 232], fill=(240, 180, 60))
    d.rectangle([1790, 520, 1820, 580], fill=(200, 200, 196), outline=(120, 120, 120), width=2)
    return img


def fj_studio():
    """朝の情報番組のスタジオ（架空）。明るい背景のパネルとテーブル、人の影だけ。"""
    img = vgrad((W, H), (120, 170, 220), (200, 220, 240))
    d = _d(img)
    for k in range(5):
        d.rectangle([100 + k * 360, 120, 400 + k * 360, 520], fill=(240, 246, 252), outline=(160, 190, 220), width=6)
        d.rectangle([140 + k * 360, 160, 360 + k * 360, 300], fill=[(250, 200, 80), (120, 200, 140), (240, 140, 120), (130, 170, 240), (250, 200, 80)][k])
    d.rectangle([520, 640, 1400, 700], fill=(250, 250, 250), outline=(170, 180, 190), width=4)
    d.rectangle([560, 700, 1360, 900], fill=(220, 230, 240))
    d.rectangle([0, 900, W, H], fill=(150, 160, 176))
    _person_line(d, 760, 640, 4, 0.9, cols=[(60, 70, 90)] * 4)
    return img


def fj_gendai():
    """今の夜の街角。ビルの壁の大きな看板の明かり（絵は描かない）。"""
    img = vgrad((W, H), (20, 26, 50), (60, 60, 90))
    d = _d(img)
    for x, h, w in ((0, 700, 420), (420, 820, 560), (980, 760, 420), (1400, 860, 520)):
        d.rectangle([x, H - h, x + w, H], fill=(40, 44, 60))
        for r in range(int(h / 90)):
            for c in range(int(w / 80)):
                if (r + c) % 3:
                    d.rectangle([x + 20 + c * 80, H - h + 30 + r * 90, x + 60 + c * 80, H - h + 70 + r * 90], fill=(230, 210, 140))
    img = _light(img, [[(560, 260), (1000, 260), (1080, 620), (480, 620)]], (255, 220, 230), alpha=50, blur=20)
    d = _d(img)
    d.rectangle([600, 300, 960, 580], fill=(250, 236, 240), outline=(240, 120, 150), width=10)
    d.rectangle([0, 960, W, H], fill=(50, 50, 60))
    return img


# ---------------------------------------------------------------- 耐震偽装
def ah_heya():
    """今の部屋。床に段ボール箱と伝票、机にスマホ（茶番）。"""
    img = heya2("none")
    d = _d(img)
    d.rectangle([1260, 700, 1560, 900], fill=(200, 160, 110), outline=(150, 116, 76), width=4)
    d.line([(1260, 740), (1560, 740)], fill=(170, 130, 90), width=6)
    d.rectangle([1320, 770, 1460, 840], fill=(252, 252, 246), outline=(150, 150, 150), width=2)
    _lines(d, 1334, 788, 1446, 3, gap=16, col=(80, 80, 80), w=3)
    d.rounded_rectangle([300, 600, 350, 640], radius=6, fill=(30, 30, 36))
    return img


def ah_iinkai():
    """国会の委員会室。正面の高い委員長席、中央の証言席、左右に議員の長机、木の壁。"""
    img = _rgb(base((150, 120, 90), (128, 100, 74)))
    d = _d(img)
    for k in range(9):
        d.rectangle([40 + k * 215, 60, 220 + k * 215, 360], fill=(170, 140, 106), outline=(120, 92, 66), width=4)
    d.rectangle([660, 300, 1260, 470], fill=(110, 76, 50), outline=(80, 54, 36), width=6)   # 委員長席
    d.rectangle([680, 280, 1240, 300], fill=(130, 92, 62))
    d.line([(960, 300), (946, 250)], fill=(30, 30, 30), width=5)
    d.ellipse([934, 238, 956, 260], fill=(30, 30, 30))
    d.rectangle([0, 470, W, H], fill=(70, 100, 80))                                         # じゅうたん
    for side in (0, 1):                                                                     # 議員の長机
        x0 = 0 if side == 0 else 1420
        d.polygon([(x0, 560), (x0 + 500, 600), (x0 + 500, 660), (x0, 620)] if side == 0 else
                  [(x0, 600), (x0 + 500, 560), (x0 + 500, 620), (x0, 660)], fill=(120, 84, 56))
    d.rectangle([840, 640, 1080, 700], fill=(120, 84, 56), outline=(80, 54, 36), width=4)  # 証言席
    d.rectangle([860, 700, 1060, 760], fill=(100, 70, 46))
    d.line([(960, 640), (972, 590)], fill=(30, 30, 30), width=5)
    d.ellipse([962, 578, 984, 600], fill=(30, 30, 30))
    return img


def ah_kaigi(yoru=False, yotei=False):
    """本社の会議室。机いっぱいに構造計算書の分厚い束。yoru は夜、同じ机に予定表（「藤沢 10/28」）。
    yotei は昼のまま、ボードに予定表（「藤沢 10/28」）だけを足す（時刻を決めて見せないため）。"""
    img = _rgb(base((214, 212, 206), (198, 196, 190)))
    wood_floor(img, FLOOR, col=(106, 96, 86), line=(88, 80, 72))
    d = _d(img)
    d.rectangle([700, 120, 1220, 400], fill=(250, 250, 248), outline=(120, 120, 116), width=6)
    if yoru or yotei:
        _text_c(d, 960, 160, "藤沢 10/28", 70, (40, 40, 40))
        _lines(d, 760, 280, 1160, 3, gap=36, col=(90, 90, 90), w=5)
    d.rectangle([240, 680, 1680, 720], fill=(110, 80, 56))
    for x in (300, 1600):
        d.rectangle([x, 720, x + 30, 900], fill=(90, 64, 44))
    rnd = random.Random(12)
    for k in range(9):
        x = 330 + k * 150
        h = rnd.randint(3, 7)
        for j in range(h):
            d.rectangle([x, 676 - (j + 1) * 16, x + 110, 676 - j * 16], fill=(236, 232, 220) if j % 2 else (210, 220, 236), outline=(150, 146, 140), width=1)
    if yoru:
        img = _dark(img, 120)
        img = _light(img, [[(500, 0), (1420, 0), (1500, 760), (420, 760)]], (255, 230, 170), alpha=40, blur=10)
    return img


def ah_madoguchi():
    """民間の審査機関の窓口。カウンターに分厚い計算書の束、後ろに書類の棚。"""
    img = _rgb(base((230, 232, 234), (216, 218, 220)))
    d = _d(img)
    for k in range(4):
        x = 160 + k * 420
        d.rectangle([x, 140, x + 300, 520], fill=(200, 196, 186), outline=(150, 146, 140), width=4)
        for r in range(4):
            for c in range(6):
                d.rectangle([x + 16 + c * 46, 160 + r * 90, x + 50 + c * 46, 236 + r * 90], fill=[(80, 110, 160), (160, 80, 70), (90, 140, 100)][(r + c) % 3])
    d.rectangle([0, 620, W, 700], fill=(170, 160, 146), outline=(130, 120, 106), width=4)
    d.rectangle([0, 700, W, H], fill=(196, 196, 190))
    for k in range(4):
        x = 720 + k * 130
        for j in range(6):
            d.rectangle([x, 616 - (j + 1) * 22, x + 110, 616 - j * 22], fill=(246, 242, 230), outline=(150, 146, 140), width=2)
    return img


def ah_sekkei():
    """構造設計事務所の机。パソコンと広げた図面（線だけ）。"""
    img = _office_base()
    d = _d(img)
    d.rectangle([560, 640, 1360, 670], fill=(170, 160, 146))
    d.rectangle([600, 450, 900, 640], fill=(40, 44, 56), outline=(150, 150, 156), width=6)
    _lines(d, 630, 480, 870, 5, gap=28, col=(140, 220, 160), w=4)
    d.rectangle([960, 560, 1320, 640], fill=(220, 236, 250), outline=(120, 140, 170), width=3)
    for k in range(6):
        d.line([(980 + k * 56, 570), (980 + k * 56, 630)], fill=(80, 110, 170), width=2)
    for k in range(3):
        d.line([(970, 580 + k * 20), (1310, 580 + k * 20)], fill=(80, 110, 170), width=2)
    return img


def ah_soft():
    """構造計算のソフトの画面（架空）。表の中の「地震力係数 1.00 → 0.50」の欄。"""
    img = vgrad((W, H), (30, 34, 44), (40, 44, 56))
    d = _d(img)
    d.rectangle([260, 100, 1660, 900], fill=(236, 238, 242), outline=(120, 124, 130), width=10)
    d.rectangle([270, 110, 1650, 170], fill=(60, 90, 150))
    for r in range(7):
        y = 230 + r * 90
        d.rectangle([320, y, 1600, y + 70], fill=(250, 250, 252) if r % 2 else (230, 234, 240), outline=(190, 194, 200), width=2)
        if r != 3:
            _lines(d, 350, y + 34, 900, 1, col=(110, 110, 120), w=6)
            _lines(d, 1100, y + 34, 1500, 1, col=(110, 110, 120), w=6)
    y = 230 + 3 * 90
    d.rectangle([320, y, 1600, y + 70], fill=(255, 236, 236), outline=(210, 40, 40), width=6)
    _text_c(d, 640, y + 10, "地震力係数", 44, (30, 30, 30))
    _text_c(d, 1300, y + 10, "1.00 → 0.50", 44, (210, 30, 30))
    return img


def ah_genba():
    """工事現場。打つ前の柱の鉄筋が並び、足場と型枠。"""
    img = vgrad((W, H), (176, 200, 226), (226, 230, 232))
    d = _d(img)
    d.rectangle([0, 760, W, H], fill=(150, 146, 140))
    for k in range(4):                                                                       # 柱の鉄筋のかご
        x = 260 + k * 420
        for j in range(6):
            d.line([(x + j * 24, 260), (x + j * 24, 760)], fill=(120, 80, 60), width=7)
        for r in range(10):
            d.rectangle([x - 6, 300 + r * 46, x + 126, 306 + r * 46], fill=(140, 96, 70))
    for k in range(3):                                                                       # 型枠の板
        d.rectangle([60 + k * 640, 700, 380 + k * 640, 760], fill=(200, 170, 110), outline=(150, 120, 70), width=3)
    d.line([(0, 200), (W, 200)], fill=(110, 110, 120), width=8)
    for k in range(9):
        d.line([(k * 240, 200), (k * 240, 760)], fill=(110, 110, 120), width=6)
    return img


def ah_kagi():
    """引き渡しの机。鍵の束と、書類と判子。"""
    img = _rgb(base((236, 232, 222), (222, 218, 208)))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(180, 170, 156))
    d.rectangle([520, 600, 1400, 640], fill=(150, 116, 80))
    d.rectangle([560, 640, 1360, 900], fill=(130, 100, 70))
    for k in range(4):
        x = 600 + k * 90
        d.ellipse([x, 560, x + 40, 600], outline=(200, 170, 60), width=6)
        d.rectangle([x + 16, 540, x + 26, 568], fill=(200, 170, 60))
    d.rectangle([1000, 548, 1240, 600], fill=(250, 250, 246), outline=(150, 150, 150), width=2)
    _lines(d, 1016, 560, 1220, 3, gap=12, col=(80, 80, 80), w=3)
    d.rectangle([1280, 560, 1310, 600], fill=(180, 40, 40))
    return img


def ah_model(kinshi=False):
    """モデルルームの広いリビング（架空）。大きな窓とソファ。kinshi は同じ部屋に「使用禁止」の貼り紙。"""
    img = _rgb(base((244, 240, 232), (232, 228, 220)))
    wood_floor(img, FLOOR, col=(190, 160, 120), line=(170, 140, 100))
    d = _d(img)
    d.rectangle([300, 120, 1620, 600], fill=(190, 216, 236), outline=(220, 220, 220), width=14)
    for x in (740, 1180):
        d.line([(x, 120), (x, 600)], fill=(220, 220, 220), width=10)
    d.rounded_rectangle([140, 700, 760, 860], radius=26, fill=(200, 196, 186))
    d.rounded_rectangle([1160, 700, 1780, 860], radius=26, fill=(200, 196, 186))
    d.ellipse([820, 800, 1100, 880], fill=(160, 120, 80))
    if kinshi:
        d.rectangle([780, 220, 1140, 520], fill=(252, 252, 250), outline=(200, 40, 40), width=8)
        _text_c(d, 960, 260, "使用禁止", 72, (200, 30, 30))
        _lines(d, 820, 380, 1100, 3, gap=36, col=(60, 60, 60), w=5)
    return img


def ah_manshon(kie=False):
    """夕方のマンションの外観（架空）。窓の明かり。kie は明かりがほとんど消えている。"""
    img = vgrad((W, H), (90, 100, 150), (240, 170, 120))
    d = _d(img)
    d.rectangle([520, 100, 1400, 900], fill=(200, 196, 190), outline=(150, 146, 140), width=6)
    rnd = random.Random(31)
    for r in range(10):
        for c in range(8):
            x, y = 560 + c * 105, 130 + r * 76
            on = rnd.random() < (0.7 if not kie else 0.06)
            d.rectangle([x, y, x + 70, y + 46], fill=(250, 220, 140) if on else (90, 96, 110))
            d.rectangle([x - 6, y + 52, x + 76, y + 60], fill=(170, 166, 160))
    d.rectangle([0, 900, W, H], fill=(110, 110, 110))
    return img


def ah_uketsuke(kara=False):
    """本社の受付。カウンターと、壁の社名の板（文字は描かない）。kara は板が外れて、ねじ穴と跡だけ。"""
    img = _rgb(base((230, 228, 222), (216, 214, 208)))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(170, 166, 160))
    if kara:
        d.rectangle([680, 180, 1240, 320], fill=(222, 220, 214), outline=(206, 204, 198), width=3)
        for x, y in ((700, 200), (1220, 200), (700, 300), (1220, 300)):
            d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(120, 120, 120))
    else:
        d.rectangle([680, 180, 1240, 320], fill=(60, 80, 120), outline=(40, 50, 80), width=4)
        d.rectangle([720, 230, 1200, 270], fill=(200, 210, 230))
    d.rectangle([560, 560, 1360, 760], fill=(200, 190, 170), outline=(150, 140, 120), width=4)
    d.rectangle([540, 540, 1380, 570], fill=(150, 130, 100))
    return img


def ah_gendai():
    """今の建築の審査の窓口。2つ並んだ窓口（二重の審査）と、明るいロビー。"""
    img = vgrad((W, H), (236, 240, 244), (220, 226, 232))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(190, 194, 198))
    for k in range(2):
        x = 420 + k * 640
        d.rectangle([x, 220, x + 440, 560], fill=(250, 250, 252), outline=(150, 160, 176), width=6)
        d.rectangle([x, 220, x + 440, 270], fill=[(60, 120, 200), (60, 160, 120)][k])
        d.rectangle([x - 20, 560, x + 460, 640], fill=(200, 204, 210), outline=(150, 156, 166), width=4)
        for j in range(3):
            d.rectangle([x + 60 + j * 120, 520 - j * 10, x + 160 + j * 120, 556], fill=(246, 242, 230), outline=(150, 146, 140), width=2)
    return img


# ---------------------------------------------------------------- 三菱自動車のリコール隠し
def mm_heya():
    """今の部屋。机に自転車のヘルメット、壁に駅までの地図（茶番）。"""
    img = heya2("none")
    d = _d(img)
    d.pieslice([250, 560, 380, 660], 180, 360, fill=(60, 130, 210), outline=(30, 70, 130), width=3)
    d.rectangle([250, 606, 380, 616], fill=(30, 70, 130))
    d.rectangle([520, 160, 820, 380], fill=(246, 244, 232), outline=(150, 140, 120), width=4)
    d.line([(560, 340), (640, 280), (720, 300), (780, 200)], fill=(220, 70, 60), width=6)
    d.ellipse([550, 330, 570, 350], fill=(40, 120, 60))
    d.ellipse([770, 190, 790, 210], fill=(40, 120, 60))
    return img


def mm_tana(kara=False):
    """品質保証部の書類棚に2つの箱（「P」「H」の札）。kara は立入検査の日、空っぽの棚と、扉が開いた更衣室のロッカー。"""
    img = _rgb(base((226, 226, 220), (212, 212, 206)))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(170, 170, 164))
    d.rectangle([200, 140, 1000, 860], fill=(150, 150, 156), outline=(110, 110, 116), width=6)
    for r in range(4):
        d.rectangle([210, 300 + r * 170, 990, 316 + r * 170], fill=(120, 120, 126))
    if not kara:
        for i, (x, lab, col) in enumerate(((260, "P", (60, 110, 180)), (620, "H", (200, 60, 60)))):
            d.rectangle([x, 160, x + 320, 296], fill=(200, 170, 120), outline=(140, 110, 70), width=4)
            d.rectangle([x + 110, 180, x + 210, 270], fill=(252, 252, 250), outline=col, width=5)
            _text_c(d, x + 160, 186, lab, 60, col)
            for k in range(3):
                d.rectangle([x + 20 + k * 100, 330, x + 90 + k * 100, 470], fill=(246, 242, 230), outline=(160, 150, 130), width=2)
    for k in range(4):                                                                      # 更衣室のロッカー
        x = 1180 + k * 170
        d.rectangle([x, 220, x + 150, 860], fill=(160, 170, 180), outline=(110, 116, 124), width=4)
        for j in range(3):
            d.line([(x + 40, 260 + j * 14), (x + 110, 260 + j * 14)], fill=(110, 116, 124), width=3)
    if kara:
        x = 1180 + 2 * 170
        d.rectangle([x, 220, x + 150, 860], fill=(60, 60, 66))
        d.polygon([(x + 150, 220), (x + 260, 250), (x + 260, 830), (x + 150, 860)], fill=(170, 180, 190), outline=(110, 116, 124))
        for j in range(4):
            d.rectangle([x + 14, 500 + j * 80, x + 136, 570 + j * 80], fill=(200, 170, 120), outline=(140, 110, 70), width=3)
    return img


def mm_doro():
    """事故のあとの、人のいない県道の遠景（2002年。昼の静かな道。人も車も描かない）。"""
    img = vgrad((W, H), (200, 210, 220), (226, 228, 230))
    d = _d(img)
    d.polygon([(0, 560), (W, 520), (W, H), (0, H)], fill=(150, 160, 130))
    d.polygon([(820, 540), (1100, 536), (1700, H), (200, H)], fill=(110, 110, 114))
    d.line([(960, 540), (950, H)], fill=(240, 240, 240), width=10)
    for k in range(8):
        x = 120 + k * 220
        d.rectangle([x, 380, x + 160, 560], fill=(200, 196, 186), outline=(150, 146, 140), width=3)
        d.polygon([(x - 10, 380), (x + 80, 330), (x + 170, 380)], fill=(130, 100, 90))
    for x in (700, 1260):
        d.line([(x, 300), (x, 560)], fill=(90, 90, 90), width=8)
    return img


def mm_seimei(kara=False):
    """4社の署名の欄が並ぶ共同声明の紙（文字は線だけ）。kara は1社の欄だけ空白。"""
    img = vgrad((W, H), (120, 100, 80), (140, 118, 96))
    d = _d(img)
    d.rectangle([360, 60, 1560, 1020], fill=(250, 248, 240), outline=(180, 170, 150), width=4)
    _lines(d, 440, 130, 1480, 6, gap=46, col=(70, 70, 70), w=6)
    for k in range(4):
        y = 460 + k * 130
        blank = kara and k == 0
        d.line([(480, y + 80), (1440, y + 80)], fill=(150, 150, 150), width=3)
        if not blank:
            _lines(d, 500, y + 20, 900, 1, col=(40, 40, 40), w=8)
            d.line([(1000, y + 60), (1100, y + 20), (1200, y + 70), (1300, y + 30)], fill=(30, 40, 120), width=5)
    return img


def mm_hanbaiten():
    """客のいない販売店（架空の車が2台、カウンターに電話）。"""
    img = _rgb(base((236, 238, 240), (222, 224, 226)))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(200, 200, 204))
    d.rectangle([80, 100, 1840, 460], fill=(200, 222, 236), outline=(160, 170, 180), width=8)
    from scripts.gen_now_bgs import _car
    _car(d, 200, 820, 1.4, col=(200, 60, 60))
    _car(d, 1240, 820, 1.4, col=(230, 230, 236))
    d.rectangle([760, 640, 1160, 700], fill=(170, 160, 146))
    _phone(d, 900, 590, 0.6)
    return img


def mm_shoji():
    """商社の自動車事業本部の机。壁に世界地図。"""
    img = _office_base()
    d = _d(img)
    d.rectangle([520, 110, 1400, 460], fill=(180, 210, 230), outline=(120, 120, 120), width=6)
    for (x, y, w, h) in ((620, 190, 160, 110), (820, 170, 140, 160), (1000, 180, 200, 120), (1220, 300, 120, 90), (700, 330, 90, 80)):
        d.ellipse([x, y, x + w, y + h], fill=(150, 190, 130))
    d.rectangle([600, 640, 1320, 670], fill=(170, 160, 146))
    _phone(d, 700, 590, 0.6)
    return img


def mm_yakuinshitsu():
    """役員室。段ボールの上に再建計画の束。"""
    img = _shacho_base()
    d = _d(img)
    for k in range(3):
        d.rectangle([180 + k * 30, 720 - k * 110, 440 + k * 30, 830 - k * 110], fill=(200, 160, 110), outline=(150, 116, 76), width=4)
    for j in range(5):
        d.rectangle([250, 500 - j * 14, 470, 514 - j * 14], fill=(246, 242, 230), outline=(150, 146, 140), width=2)
    return img


def mm_isu():
    """役員室の机と、誰も座っていない椅子（益子の死去の場面）。"""
    img = _shacho_base()
    d = _d(img)
    d.rounded_rectangle([880, 420, 1040, 600], radius=24, fill=(60, 50, 46))                # 背もたれ
    d.rectangle([870, 590, 1050, 640], fill=(70, 58, 52))                                    # 座面
    d.rectangle([950, 640, 970, 820], fill=(50, 50, 54))
    for dx in (-80, 0, 80):
        d.line([(960, 820), (960 + dx, 860)], fill=(50, 50, 54), width=8)
    return img


def mm_kaigishitsu():
    """2017年の本社の会議室（取材）。白い壁、明るい机に録音機とコップ。"""
    img = vgrad((W, H), (240, 242, 244), (226, 230, 234))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(180, 186, 194))
    for k in range(3):
        d.rectangle([200 + k * 540, 110, 640 + k * 540, 460], fill=(200, 222, 238), outline=(180, 190, 200), width=6)
    d.rectangle([420, 660, 1500, 700], fill=(236, 236, 232), outline=(170, 170, 170), width=3)
    for x in (480, 1420):
        d.rectangle([x, 700, x + 20, 900], fill=(150, 150, 156))
    d.rounded_rectangle([900, 620, 1000, 660], radius=8, fill=(40, 40, 46))                # 録音機
    d.ellipse([918, 630, 940, 652], fill=(200, 60, 60))
    for x in (700, 1180):
        d.rectangle([x, 610, x + 36, 660], fill=(230, 240, 250), outline=(150, 160, 170), width=2)
    return img


def mm_board(saisei=False):
    """役員会議室のホワイトボード。「損害賠償請求」／saisei は同じボードに「再生計画」と右上がりの線。"""
    img = _rgb(base((214, 212, 206), (198, 196, 190)))
    wood_floor(img, FLOOR, col=(106, 96, 86), line=(88, 80, 72))
    d = _d(img)
    d.rectangle([520, 110, 1400, 520], fill=(252, 252, 250), outline=(140, 140, 140), width=8)
    if saisei:
        _text_c(d, 960, 140, "再生計画", 80, (30, 60, 140))
        d.line([(640, 470), (820, 420), (1000, 380), (1260, 280)], fill=(40, 140, 80), width=10)
    else:
        _text_c(d, 960, 140, "損害賠償請求", 80, (40, 40, 40))
        _lines(d, 640, 300, 1280, 4, gap=46, col=(80, 80, 80), w=6)
    d.rectangle([240, 680, 1680, 720], fill=(110, 80, 56))
    for x in (300, 1600):
        d.rectangle([x, 720, x + 30, 900], fill=(90, 64, 44))
    return img


def mm_jikken(kara=False):
    """岡崎の実験の部屋。計測器の台と架空の軽、壁に目標「29.2」の紙。kara は紙が外された同じ部屋。"""
    img = _rgb(base((226, 228, 230), (212, 214, 216)))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(150, 154, 160))
    d.rectangle([600, 820, 1320, 860], fill=(90, 90, 96))                                 # 計測の台（ローラー）
    for x in (700, 1160):
        d.ellipse([x, 800, x + 70, 870], fill=(60, 60, 66))
    from scripts.gen_now_bgs import _car
    _car(d, 640, 820, 2.5, col=(240, 240, 236))
    d.rectangle([140, 380, 420, 760], fill=(80, 84, 96), outline=(50, 50, 56), width=4)      # 計測器
    d.rectangle([170, 410, 390, 520], fill=(20, 30, 40))
    _lines(d, 190, 440, 370, 3, gap=26, col=(120, 220, 160), w=4)
    if kara:
        d.rectangle([760, 150, 1160, 400], fill=(232, 232, 228), outline=(220, 220, 216), width=3)
    else:
        d.rectangle([760, 150, 1160, 400], fill=(252, 250, 240), outline=(200, 60, 60), width=6)
        _text_c(d, 960, 170, "目標", 50, (40, 40, 40))
        _text_c(d, 960, 250, "29.2", 110, (200, 40, 40))
    return img


def mm_yokohama():
    """横浜の会見場。2社の会見の舞台（無地の幕）と、手前の報道陣のフラッシュ。顔は描かない。"""
    img = vgrad((W, H), (40, 50, 80), (60, 70, 100))
    d = _d(img)
    d.rectangle([300, 100, 1620, 560], fill=(230, 232, 236), outline=(180, 184, 190), width=6)
    d.rectangle([520, 520, 1400, 600], fill=(250, 250, 250), outline=(170, 170, 170), width=3)
    for x in (700, 960, 1220):
        d.line([(x, 520), (x - 14, 470)], fill=(40, 40, 40), width=5)
        d.ellipse([x - 26, 456, x - 4, 478], fill=(30, 30, 30))
    _press(d, 20, 1060, 8, 1.05)
    _press(d, 1350, 1060, 8, 1.05)
    img = _light(img, [[(600, 300), (700, 300), (760, 600), (540, 600)], [(1200, 260), (1300, 260), (1360, 600), (1140, 600)]], (255, 255, 255), alpha=50, blur=6)
    return img


def mm_garage():
    """タイヤ交換のガレージ。ジャッキの上の架空の車、外したタイヤ、工具の棚。"""
    img = _rgb(base((200, 200, 196), (184, 184, 180)))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(140, 140, 138))
    for k in range(3):
        d.rectangle([80, 200 + k * 160, 420, 214 + k * 160], fill=(120, 100, 80))
        for j in range(6):
            d.rectangle([100 + j * 52, 150 + k * 160, 130 + j * 52, 200 + k * 160], fill=[(200, 60, 60), (60, 90, 160), (80, 80, 86)][j % 3])
    from scripts.gen_now_bgs import _car
    _car(d, 720, 760, 2.6, col=(120, 150, 190))
    d.rectangle([900, 760, 960, 840], fill=(200, 60, 40))
    for x in (1500, 1640):
        d.ellipse([x, 760, x + 130, 900], fill=(40, 40, 44), outline=(24, 24, 28), width=6)
        d.ellipse([x + 40, 805, x + 90, 855], fill=(170, 170, 176))
    return img


def mm_gendai():
    """今のショールーム（架空の車。大きな窓、明るい床）。"""
    img = vgrad((W, H), (236, 240, 244), (222, 226, 232))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(210, 212, 216))
    for k in range(4):
        d.rectangle([60 + k * 470, 80, 480 + k * 470, 520], fill=(200, 222, 238), outline=(170, 180, 190), width=6)
    from scripts.gen_now_bgs import _car
    _car(d, 260, 860, 1.8, col=(70, 70, 80))
    _car(d, 1180, 860, 1.8, col=(230, 230, 236))
    return img


LOCATIONS = {
    # 三菱自動車のリコール隠し
    "mm_heya": mm_heya, "mm_kaiken": _sega_kaiken, "mm_tana": mm_tana, "mm_tana_kara": lambda: mm_tana(kara=True),
    "mm_honsha_kaiken": tj_kaiken, "mm_rouka": fj_roka, "mm_doro": mm_doro, "mm_kaigi": _now_kaigi,
    "mm_seimei": mm_seimei, "mm_seimei_kara": lambda: mm_seimei(kara=True), "mm_hanbaiten": mm_hanbaiten,
    "mm_shoji": mm_shoji, "mm_yakuinshitsu": mm_yakuinshitsu, "mm_isu": mm_isu, "mm_kaigishitsu": mm_kaigishitsu,
    "mm_board": mm_board, "mm_board_saisei": lambda: mm_board(saisei=True), "mm_houtei": _sogo_saibansho,
    "mm_jikken": mm_jikken, "mm_jikken_kara": lambda: mm_jikken(kara=True), "mm_yokohama": mm_yokohama,
    "mm_garage": mm_garage, "mm_shinbun": tj_shinbun, "mm_gendai": mm_gendai,
    # 耐震偽装
    "ah_heya": ah_heya, "ah_iinkai": ah_iinkai, "ah_honsha": jimusho90,
    "ah_kaigi": ah_kaigi, "ah_kaigi_yoru": lambda: ah_kaigi(yoru=True), "ah_kaigi_yotei": lambda: ah_kaigi(yotei=True), "ah_madoguchi": ah_madoguchi,
    "ah_sekkei": ah_sekkei, "ah_soft": ah_soft, "ah_genba": ah_genba, "ah_kagi": ah_kagi,
    "ah_kokkosho": shingikai, "ah_yakusho": _tb_yakusho,
    "ah_model": ah_model, "ah_model_kinshi": lambda: ah_model(kinshi=True),
    "ah_manshon": ah_manshon, "ah_manshon_kie": lambda: ah_manshon(kie=True),
    "ah_uketsuke": ah_uketsuke, "ah_uketsuke_kara": lambda: ah_uketsuke(kara=True),
    "ah_houtei": _sogo_saibansho, "ah_shinbun": tj_shinbun, "ah_gendai": ah_gendai,
    # ぷよぷよとコンパイルの破綻
    "pu_heya": pu_heya, "pu_shachoshitsu": pu_shachoshitsu,
    "pu_shachoshitsu_yoru": lambda: pu_shachoshitsu("yoru"), "pu_shachoshitsu_e": lambda: pu_shachoshitsu("e"),
    "pu_shachoshitsu_shorui": lambda: pu_shachoshitsu("shorui"), "pu_shachoshitsu_kara": lambda: pu_shachoshitsu("kara"),
    "pu_jimusho": _tama_pc, "pu_kaihatsu": pu_kaihatsu, "pu_inshokuten": pu_inshokuten, "pu_kissaten": pu_kissaten,
    "pu_manjuya": _anpan_mise, "pu_manju_kojo": kobo_manju, "pu_booth": pu_booth, "pu_kaijo": pu_kaijo,
    "pu_mensetsu": pu_mensetsu, "pu_kaiken": _sega_kaiken, "pu_jimusho_kara": lambda: _dark(jimusho90(yoru=True), 140),
    "pu_keibi": pu_keibi, "pu_keibi_asa": lambda: pu_keibi(asa=True), "pu_kyoshitsu": pu_kyoshitsu,
    "pu_shisaku": pu_shisaku, "pu_shinbun": tj_shinbun, "pu_gendai": pu_gendai, "pu_esports": pu_gendai,
    # 不二家の期限切れ原料
    "fj_heya": fj_heya, "fj_shokudo": fj_shokudo, "fj_honsha": fj_honsha,
    "fj_kaigi": fj_kaigi, "fj_kaigi_gaihi": lambda: fj_kaigi("gaihi"), "fj_kaigi_kara": lambda: fj_kaigi("kara"),
    "fj_kojo": fj_kojo, "fj_kojo_kan": lambda: fj_kojo(kan=True), "fj_keiji": fj_keiji, "fj_fax": fj_fax,
    "fj_koho": fj_koho, "fj_koho_denwa": lambda: fj_koho(denwa=True),
    "fj_mise": fj_mise, "fj_mise_shutter": lambda: fj_mise("shutter"), "fj_mise_akari": lambda: fj_mise("akari"),
    "fj_uriba": _sogo_uriba, "fj_uriba_kara": _sogo_uriba_kara, "fj_roka": fj_roka, "fj_studio": fj_studio,
    "fj_kaiken": _sega_kaiken, "fj_shinbun": tj_shinbun, "fj_gendai": fj_gendai,
}

# 年号カード。接頭辞ごとに "fj_card_2007" のように作る（台帳を見て足す）
CARDS = {"pu": ["1982", "1990", "1991", "1992", "1994", "1996", "1997", "1998", "2002", "2016", "2025", "2026"],
         "fj": ["2006", "2007", "2008", "2026"],
         "mm": ["2000", "2002", "2004", "2005", "2008", "2012", "2016", "2020", "2026"],
         "ah": ["1982", "1998", "2004", "2005", "2006", "2007", "2008", "2011", "2015", "2026"]}


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1:])
    for name, fn in LOCATIONS.items():
        if only and name not in only:
            continue
        _rgb(fn()).save(OUT / f"{name}.png")
        print(f"生成完了: {name}.png")
    for pre, years in CARDS.items():
        for y in years:
            nm = f"{pre}_card_{y}"
            if only and nm not in only:
                continue
            year_card(f"{y}年").save(OUT / f"{nm}.png")
            print(f"生成完了: {nm}.png")
