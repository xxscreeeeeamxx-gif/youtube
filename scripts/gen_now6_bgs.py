#!/usr/bin/env python3
"""第6弾4本（2026-11-17〜20。方向転換の実験：会社の転落・破綻・裁判）の背景を生成する。

接頭辞: bf_（武富士の破綻）/ ok_（大塚家具の親子対立）/ nv_（NOVA の破綻）/ sk_（船場吉兆の廃業）
方針は gen_now5_bgs.py と同じ。実在の会社のロゴ・社名の文字・店の意匠は描かない（暖簾にも文字を入れない）。
差し替え用（_kara・_kyugyo など）は元の絵に要素を足すか減らす。

実行: PYTHONPATH=. python scripts/gen_now6_bgs.py [名前...]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.gen_drama_bgs import H, OUT, W, base, tatami_floor, vgrad, wood_floor  # noqa: E402
from scripts.gen_famicom_bgs import year_card  # noqa: E402
from scripts.gen_now_bgs import FLOOR, _d, _rgb, kaigi, yakuin  # noqa: E402
from scripts.gen_now2_bgs import shoken  # noqa: E402
from scripts.gen_now5_bgs import cg_saikosai  # noqa: E402
from scripts.gen_now2_bgs import heya2, kabunushi_kaijo  # noqa: E402
from scripts.gen_now3_bgs import jimusho90  # noqa: E402
from scripts.gen_sega_bgs import _person_line, gendai as _sega_gendai, kaiken as _sega_kaiken  # noqa: E402
from scripts.gen_sogo_bgs import kokkai as _sogo_kokkai, saibansho as _sogo_saibansho  # noqa: E402


# ---------------------------------------------------------------- 船場吉兆・湯木佐知子
def _noren(d, x0, x1, y0, y1, col=(40, 44, 70)):
    """店の入口の暖簾（文字は描かない）。3枚に割る。"""
    w = (x1 - x0) / 3
    for k in range(3):
        d.rectangle([x0 + k * w + 4, y0, x0 + (k + 1) * w - 4, y1], fill=col)
    d.rectangle([x0 - 10, y0 - 14, x1 + 10, y0], fill=(90, 66, 40))


def _pudding(d, x, y, s=1.0):
    """カップのプリン（下の端の中央）。ふたのラベルは線だけ。"""
    d.polygon([(x - 36 * s, y - 70 * s), (x + 36 * s, y - 70 * s), (x + 28 * s, y), (x - 28 * s, y)],
              fill=(236, 230, 210), outline=(150, 140, 120))
    d.rectangle([x - 38 * s, y - 78 * s, x + 38 * s, y - 68 * s], fill=(250, 250, 246), outline=(150, 140, 120))
    d.rectangle([x - 20 * s, y - 50 * s, x + 20 * s, y - 34 * s], fill=(250, 250, 246))
    d.line([(x - 14 * s, y - 42 * s), (x + 14 * s, y - 42 * s)], fill=(200, 40, 40), width=max(int(3 * s), 1))


def sk_heya():
    """今の部屋。机にカップのプリンと、和菓子の箱（文字は線）。"""
    img = heya2("none")
    d = _d(img)
    _pudding(d, 260, 640, 1.0)
    d.rectangle([380, 600, 580, 640], fill=(230, 220, 200), outline=(150, 130, 100), width=3)
    d.line([(400, 620), (560, 620)], fill=(120, 100, 80), width=4)
    return img


def sk_ryotei(kyugyo=False, kara=False):
    """料亭の玄関。格子戸、紺の暖簾、石畳と灯籠。kyugyo は戸に白い貼り紙（休業）、kara は暖簾が無く戸が閉まる。"""
    img = vgrad((W, H), (210, 200, 180), (190, 180, 160))
    d = _d(img)
    d.rectangle([0, 120, W, 820], fill=(120, 96, 66))                                            # 板塀
    for k in range(24):
        d.line([(k * 80, 120), (k * 80, 820)], fill=(100, 78, 52), width=4)
    d.polygon([(0, 120), (W, 120), (W - 120, 40), (120, 40)], fill=(60, 60, 64))                 # 瓦屋根
    d.rectangle([660, 300, 1260, 820], fill=(150, 120, 80), outline=(80, 60, 40), width=6)       # 格子戸
    for k in range(13):
        d.line([(660 + k * 46, 300), (660 + k * 46, 820)], fill=(90, 70, 46), width=4)
    if not kara:
        _noren(d, 680, 1240, 300, 520)
    if kyugyo:
        d.rectangle([900, 560, 1020, 720], fill=(250, 250, 246), outline=(180, 180, 176), width=3)
        for k in range(4):
            d.line([(960 - 30 + k * 20, 580), (960 - 30 + k * 20, 700)], fill=(60, 60, 60), width=3)
    d.rectangle([0, 820, W, H], fill=(150, 146, 136))                                            # 石畳
    for k in range(10):
        d.rectangle([700 + (k % 2) * 60, 840 + k * 24, 1220 - (k % 2) * 60, 856 + k * 24], fill=(170, 166, 156))
    for x in (380, 1540):                                                                        # 灯籠
        d.rectangle([x - 18, 640, x + 18, 820], fill=(130, 126, 120))
        d.rectangle([x - 60, 560, x + 60, 640], fill=(140, 136, 128), outline=(100, 96, 90), width=3)
        d.rectangle([x - 30, 580, x + 30, 620], fill=(250, 220, 150) if not (kyugyo or kara) else (90, 86, 80))
        d.polygon([(x - 80, 560), (x + 80, 560), (x, 500)], fill=(110, 106, 100))
    return img


def sk_zashiki():
    """料亭の座敷。畳、床の間に掛け軸と花、漆の座卓。"""
    img = _rgb(base((226, 214, 186), (210, 198, 170)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    d.rectangle([120, 120, 620, 760], fill=(200, 186, 156), outline=(110, 86, 60), width=8)       # 床の間
    d.rectangle([300, 160, 440, 560], fill=(244, 238, 222), outline=(120, 100, 70), width=4)      # 掛け軸
    d.line([(370, 220), (360, 500)], fill=(40, 40, 40), width=6)
    d.ellipse([340, 640, 400, 700], fill=(150, 90, 70))                                          # 花入れ
    d.line([(370, 640), (350, 580)], fill=(80, 120, 60), width=4)
    for k in range(4):                                                                           # 障子
        x = 800 + k * 270
        d.rectangle([x, 120, x + 250, 760], fill=(246, 242, 230), outline=(140, 116, 80), width=6)
        for r in range(1, 5):
            d.line([(x, 120 + r * 128), (x + 250, 120 + r * 128)], fill=(170, 150, 120), width=2)
        d.line([(x + 125, 120), (x + 125, 760)], fill=(170, 150, 120), width=2)
    d.rectangle([640, 760, 1460, 800], fill=(70, 30, 26))                                        # 座卓
    d.rectangle([680, 800, 720, 880], fill=(60, 26, 22))
    d.rectangle([1380, 800, 1420, 880], fill=(60, 26, 22))
    return img


def sk_itaba():
    """料亭の板場。白木の調理台、まな板と包丁、串に刺したアユ、器の棚。"""
    img = _rgb(base((232, 228, 216), (216, 212, 200)))
    wood_floor(img, FLOOR, col=(180, 170, 150), line=(164, 154, 134))
    d = _d(img)
    d.rectangle([120, 140, 1800, 420], fill=(200, 180, 140), outline=(140, 116, 80), width=6)     # 器の棚
    for r in range(3):
        d.line([(120, 230 + r * 90), (1800, 230 + r * 90)], fill=(140, 116, 80), width=4)
        for k in range(14):
            d.ellipse([150 + k * 118, 196 + r * 90, 230 + k * 118, 226 + r * 90],
                      fill=[(240, 236, 226), (150, 60, 40), (40, 60, 90)][(k + r) % 3])
    d.rectangle([200, 600, 1720, 650], fill=(232, 214, 176), outline=(170, 150, 110), width=4)    # 調理台
    d.rectangle([200, 650, 1720, FLOOR], fill=(206, 190, 156))
    d.rectangle([420, 570, 760, 600], fill=(244, 236, 214))                                       # まな板
    d.line([(480, 584), (700, 584)], fill=(180, 186, 192), width=8)                              # 包丁
    for k in range(4):                                                                           # 串のアユ
        x = 1060 + k * 110
        d.line([(x, 520), (x + 30, 600)], fill=(170, 140, 90), width=4)
        d.ellipse([x - 30, 530, x + 50, 570], fill=(130, 140, 120))
    return img


def sk_urba(kara=False):
    """百貨店の和菓子・総菜の売場。ガラスのショーケースに菓子と小さなラベル。kara は品物が無く白い布。"""
    img = _rgb(base((246, 242, 234), (232, 228, 220)))
    wood_floor(img, FLOOR, col=(214, 206, 192), line=(200, 192, 178))
    d = _d(img)
    for k in range(6):
        d.rectangle([k * 340 + 30, 30, k * 340 + 230, 54], fill=(255, 255, 240))
    d.rectangle([100, 150, 1820, 420], fill=(150, 120, 90))                                      # 背の棚
    d.rectangle([160, 520, 1760, 700], fill=(220, 236, 240), outline=(150, 160, 170), width=6)    # ショーケース
    d.rectangle([160, 700, 1760, FLOOR], fill=(190, 170, 140))
    if kara:
        d.rectangle([200, 560, 1720, 680], fill=(250, 250, 250))
    else:
        for k in range(12):
            x = 230 + k * 128
            _pudding(d, x, 680, 0.8) if k % 3 == 0 else d.rounded_rectangle(
                [x - 40, 620, x + 40, 680], radius=10, fill=[(120, 60, 50), (90, 120, 70), (200, 170, 100)][k % 3])
            d.rectangle([x - 22, 688, x + 22, 698], fill=(250, 250, 250), outline=(160, 40, 40))   # 期限のラベル
    for k in range(8):
        d.rectangle([150 + k * 210, 200, 300 + k * 210, 380], fill=(230, 220, 200), outline=(120, 100, 70), width=3)
    return img


def sk_hotel():
    """ホテルの会見の部屋。金屏風の前に白い布の机とマイク、手前に記者の椅子。"""
    img = _rgb(base((206, 196, 186), (190, 180, 170)))
    wood_floor(img, FLOOR, col=(130, 70, 60), line=(116, 60, 52))
    d = _d(img)
    for k in range(6):                                                                           # 金屏風
        x = 360 + k * 200
        d.rectangle([x, 160, x + 200, 640], fill=(214, 180, 90) if k % 2 == 0 else (200, 166, 80),
                    outline=(150, 120, 60), width=4)
    d.rectangle([520, 600, 1400, 700], fill=(250, 250, 250), outline=(200, 200, 200), width=3)    # 机
    for x in (760, 1160):
        d.line([(x, 600), (x - 20, 540)], fill=(40, 40, 44), width=6)
        d.ellipse([x - 34, 524, x - 6, 552], fill=(30, 30, 34))
    for k in range(12):                                                                          # 記者の椅子
        x = 60 + k * 160
        d.rectangle([x, 900, x + 110, 960], fill=(150, 40, 40))
    return img


def sk_tenant():
    """船場のビル街。料亭のあった場所に建つ灰色のテナントビル（看板の文字なし）。"""
    img = vgrad((W, H), (176, 196, 220), (214, 224, 234))
    d = _d(img)
    for k in range(5):
        x = k * 420 - 60
        h = 300 + (k * 97) % 200
        d.rectangle([x, h, x + 360, 860], fill=(170, 172, 180), outline=(120, 122, 130), width=3)
    d.rectangle([700, 260, 1220, 860], fill=(200, 200, 206), outline=(120, 120, 126), width=4)
    for r in range(8):
        for c in range(5):
            d.rectangle([730 + c * 98, 290 + r * 66, 800 + c * 98, 330 + r * 66], fill=(130, 150, 170))
    d.rectangle([860, 760, 1060, 860], fill=(90, 96, 104))
    d.rectangle([0, 860, W, H], fill=(140, 142, 146))
    return img


# ---------------------------------------------------------------- 大塚家具・大塚久美子
def _sofa(d, x, y, s=1.0, col=(150, 120, 96)):
    """ソファ（下の端の中央）。"""
    d.rounded_rectangle([x - 150 * s, y - 120 * s, x + 150 * s, y - 50 * s], radius=int(20 * s), fill=col)
    d.rounded_rectangle([x - 170 * s, y - 80 * s, x + 170 * s, y - 20 * s], radius=int(18 * s),
                        fill=tuple(min(c + 20, 255) for c in col))
    for xx in (x - 150 * s, x + 140 * s):
        d.rectangle([xx, y - 20 * s, xx + 10 * s, y], fill=(80, 60, 44))


def _table(d, x, y, s=1.0, col=(150, 110, 70)):
    """ダイニングテーブルと椅子2脚（下の端の中央）。"""
    d.rectangle([x - 130 * s, y - 90 * s, x + 130 * s, y - 76 * s], fill=col)
    for xx in (x - 120 * s, x + 110 * s):
        d.rectangle([xx, y - 76 * s, xx + 10 * s, y], fill=tuple(c - 30 for c in col))
    for xx in (x - 190 * s, x + 160 * s):
        d.rectangle([xx, y - 140 * s, xx + 30 * s, y], fill=tuple(c - 20 for c in col))
        d.rectangle([xx - 10 * s, y - 70 * s, xx + 40 * s, y - 60 * s], fill=tuple(c - 20 for c in col))


def ok_heya():
    """今の部屋。家具の無いがらんとした一角と、机に家具のチラシ（文字は線）。"""
    img = heya2("none")
    d = _d(img)
    d.rectangle([200, 600, 380, 640], fill=(250, 246, 236), outline=(170, 160, 140), width=2)
    for k in range(3):
        d.line([(214, 610 + k * 9), (360, 610 + k * 9)], fill=(200, 60, 50) if k == 0 else (120, 110, 100), width=3)
    d.rectangle([980, 640, 1300, 700], fill=(0, 0, 0, 0), outline=(170, 160, 140), width=3)       # ソファを置く場所
    return img


def ok_kobo():
    """1960年代の桐箪笥の工房。木の作業台、かんな、白い桐の箪笥。"""
    img = _rgb(base((214, 200, 176), (196, 182, 158)))
    wood_floor(img, FLOOR, col=(150, 120, 90), line=(132, 104, 76))
    d = _d(img)
    for k in range(3):                                                                           # 桐箪笥
        x = 220 + k * 300
        d.rectangle([x, 300, x + 240, 760], fill=(236, 222, 196), outline=(150, 120, 90), width=4)
        for r in range(4):
            d.line([(x, 300 + (r + 1) * 92), (x + 240, 300 + (r + 1) * 92)], fill=(170, 140, 106), width=3)
            d.rectangle([x + 100, 330 + r * 92, x + 140, 342 + r * 92], fill=(60, 50, 40))
    d.rectangle([1160, 620, 1800, 660], fill=(170, 130, 90))                                     # 作業台
    for xx in (1180, 1760):
        d.rectangle([xx, 660, xx + 20, FLOOR], fill=(130, 100, 70))
    d.rectangle([1300, 596, 1420, 620], fill=(110, 80, 50))                                       # かんな
    for k in range(5):
        d.line([(1480 + k * 30, 618), (1520 + k * 30, 606)], fill=(236, 214, 170), width=6)        # 削りくず
    return img


def ok_showroom(uketsuke=False, sale=False):
    """大きな家具のショールーム。ソファ・テーブル・ベッドが並ぶ。uketsuke は手前に受付の台と記入用紙、
    sale は天井から赤い垂れ幕（文字なし）と客の後ろ姿。"""
    img = _rgb(base((236, 232, 224), (222, 218, 210)))
    wood_floor(img, FLOOR, col=(196, 176, 150), line=(180, 160, 134))
    d = _d(img)
    for k in range(6):
        d.rectangle([k * 340 + 30, 30, k * 340 + 230, 54], fill=(255, 255, 240))
    _sofa(d, 420, 740, 1.0, (150, 120, 96))
    _sofa(d, 1500, 740, 0.9, (90, 100, 120))
    _table(d, 960, 700, 1.0)
    d.rectangle([1200, 560, 1700, 620], fill=(230, 226, 220), outline=(170, 160, 150), width=3)    # ベッド
    d.rectangle([1200, 500, 1240, 620], fill=(150, 120, 90))
    if sale:
        for k in range(4):
            x = 200 + k * 440
            d.rectangle([x, 70, x + 220, 300], fill=(220, 30, 30))
            d.rectangle([x + 30, 120, x + 190, 160], fill=(255, 230, 40))
        _person_line(d, 60, 1060, 12, 1.0)
    if uketsuke:
        d.rectangle([560, 820, 1360, 880], fill=(170, 140, 110), outline=(120, 96, 70), width=4)   # 受付の台
        d.rectangle([560, 880, 1360, H], fill=(150, 120, 92))
        for k in range(4):
            d.rectangle([620 + k * 180, 830, 760 + k * 180, 870], fill=(250, 250, 246), outline=(180, 180, 176))
            d.line([(634 + k * 180, 846), (740 + k * 180, 846)], fill=(150, 150, 156), width=3)
    return img


def ok_kaiken_kanbu():
    """会見場。長机の後ろに、背広の幹部社員がずらりと並ぶ（後ろ姿ではなく影の列）。"""
    img = _sega_kaiken()
    d = _d(img)
    _person_line(d, 260, 470, 20, 0.9, cols=[(40, 44, 56), (50, 54, 66), (36, 40, 50)])
    return img


def ok_depart():
    """駅前の大きな百貨店のビルの跡を使った家具店の外観（看板の文字なし）。"""
    img = vgrad((W, H), (160, 196, 230), (214, 228, 238))
    d = _d(img)
    d.rectangle([260, 180, 1660, 860], fill=(214, 206, 192), outline=(150, 140, 126), width=4)
    for r in range(6):
        d.rectangle([300, 230 + r * 100, 1620, 290 + r * 100], fill=(150, 170, 186))
    d.rectangle([760, 740, 1160, 860], fill=(90, 96, 104))
    d.rectangle([260, 150, 1660, 180], fill=(120, 110, 96))
    d.rectangle([0, 860, W, H], fill=(150, 150, 154))
    d.line([(0, 960), (W, 960)], fill=(240, 240, 240), width=6)
    return img


def ok_tenpo(kara=False):
    """郊外の家具店の外観（看板は色の帯だけ）。kara はシャッターが下り、駐車場が空。"""
    img = vgrad((W, H), (170, 200, 230), (220, 230, 238))
    d = _d(img)
    d.rectangle([300, 300, 1620, 820], fill=(226, 222, 214), outline=(150, 146, 140), width=4)
    d.rectangle([300, 300, 1620, 360], fill=(150, 30, 40))
    if kara:
        for k in range(10):
            d.rectangle([380, 470 + k * 34, 1540, 494 + k * 34], fill=(170, 172, 176))
    else:
        d.rectangle([380, 460, 1540, 820], fill=(170, 200, 216))
        _sofa(d, 700, 800, 0.8)
        _table(d, 1200, 800, 0.8)
    d.rectangle([0, 820, W, H], fill=(120, 122, 126))
    for k in range(12):
        d.line([(k * 170, 840), (k * 170 + 60, H)], fill=(240, 240, 240), width=4)
    if not kara:
        for k in range(4):
            d.rounded_rectangle([200 + k * 420, 900, 360 + k * 420, 980], radius=14,
                                fill=[(200, 60, 50), (60, 90, 150), (220, 220, 226), (60, 60, 66)][k])
    return img


def ok_aoyama():
    """夕方の都心の小さな家具店の入口。ガラス戸、照明、入口の脇に花の鉢。"""
    img = vgrad((W, H), (90, 100, 140), (180, 150, 140))
    d = _d(img)
    d.rectangle([360, 220, 1560, 860], fill=(60, 56, 54))
    d.rectangle([460, 320, 1460, 860], fill=(240, 220, 170))
    _sofa(d, 800, 840, 0.8, (130, 100, 80))
    d.line([(960, 320), (960, 860)], fill=(60, 56, 54), width=10)
    for x in (300, 1620):                                                                        # 花の鉢
        d.rectangle([x - 40, 760, x + 40, 860], fill=(120, 90, 70))
        for k in range(7):
            d.ellipse([x - 70 + k * 18, 680 + (k % 3) * 20, x - 40 + k * 18, 710 + (k % 3) * 20],
                      fill=[(240, 120, 140), (250, 230, 120), (250, 250, 250)][k % 3])
    d.rectangle([0, 860, W, H], fill=(80, 80, 86))
    return img


def ok_kaden():
    """家電量販店の中の家具の売り場。手前にソファとテーブル、奥に家電の棚。"""
    img = _rgb(base((240, 240, 238), (228, 228, 226)))
    wood_floor(img, FLOOR, col=(214, 214, 210), line=(200, 200, 196))
    d = _d(img)
    for k in range(6):
        d.rectangle([k * 340 + 30, 30, k * 340 + 230, 54], fill=(255, 255, 240))
    d.rectangle([60, 160, 1860, 480], fill=(200, 200, 204))
    for k in range(9):
        x = 100 + k * 196
        d.rectangle([x, 200, x + 150, 300], fill=(30, 30, 34))
        d.rectangle([x + 10, 210, x + 140, 290], fill=[(60, 110, 160), (90, 140, 110), (160, 110, 80)][k % 3])
        d.rectangle([x + 10, 340, x + 140, 460], fill=(236, 236, 240), outline=(160, 160, 166), width=3)
    _sofa(d, 560, 820, 1.0, (140, 120, 100))
    _table(d, 1360, 790, 1.0)
    return img


# ---------------------------------------------------------------- 武富士・武井保雄
def bf_heya():
    """今の部屋。テレビに法律事務所の広告のような青い画面（文字は白い線だけ）。"""
    img = heya2("none")
    d = _d(img)
    d.rectangle([1400, 380, 1780, 580], fill=(30, 80, 160))
    for k in range(3):
        d.line([(1430, 420 + k * 40), (1740 - k * 60, 420 + k * 40)], fill=(255, 255, 255), width=10)
    d.rectangle([1620, 520, 1740, 560], fill=(250, 210, 40))
    return img


def bf_4tsubo():
    """1966年の4坪の小さな事務所。机1つと黒電話、そろばん、金庫、窓の外は住宅地。"""
    img = _rgb(base((214, 206, 188), (198, 190, 172)))
    wood_floor(img, FLOOR, col=(140, 112, 84), line=(122, 96, 70))
    d = _d(img)
    d.rectangle([1100, 160, 1500, 440], fill=(120, 96, 70))
    d.rectangle([1116, 176, 1484, 424], fill=(196, 214, 226))
    for k in range(4):
        d.polygon([(1130 + k * 90, 424), (1170 + k * 90, 360), (1210 + k * 90, 424)], fill=(150, 110, 90))
    d.rectangle([520, 600, 980, 640], fill=(150, 116, 84))
    d.rectangle([540, 640, 570, FLOOR], fill=(120, 90, 64))
    d.rectangle([930, 640, 960, FLOOR], fill=(120, 90, 64))
    d.rounded_rectangle([600, 560, 680, 600], radius=10, fill=(30, 30, 34))                     # 黒電話
    d.ellipse([622, 566, 658, 594], fill=(70, 70, 76))
    d.rectangle([720, 584, 900, 600], fill=(90, 60, 40))                                         # そろばん
    for k in range(10):
        d.ellipse([726 + k * 17, 586, 738 + k * 17, 598], fill=(200, 170, 120))
    d.rectangle([180, 520, 400, FLOOR], fill=(90, 96, 100), outline=(60, 64, 68), width=4)       # 金庫
    d.ellipse([270, 600, 310, 640], fill=(200, 200, 200))
    return img


def bf_danchi():
    """1960年代の団地。白い箱型の棟が並び、ベランダに洗濯物。"""
    img = vgrad((W, H), (150, 196, 236), (214, 230, 240))
    d = _d(img)
    for k, (x, w, top) in enumerate(((60, 700, 260), (840, 520, 320), (1420, 480, 280))):
        d.rectangle([x, top, x + w, 860], fill=(236, 234, 226), outline=(170, 168, 160), width=3)
        for r in range((860 - top) // 90):
            y = top + 30 + r * 90
            for c in range(w // 110):
                d.rectangle([x + 20 + c * 110, y, x + 100 + c * 110, y + 50], fill=(170, 196, 214))
                if (r + c + k) % 3 == 0:
                    d.line([(x + 20 + c * 110, y + 56), (x + 100 + c * 110, y + 56)], fill=(120, 120, 120), width=2)
                    d.rectangle([x + 34 + c * 110, y + 56, x + 54 + c * 110, y + 80],
                                fill=[(240, 120, 120), (120, 160, 230), (250, 230, 120)][(r + c) % 3])
    d.rectangle([0, 860, W, H], fill=(150, 170, 120))
    return img


def bf_shiten(kyugyo=False):
    """2000年代の消費者金融の支店の窓口。仕切りのあるカウンターと椅子、壁にポスター（文字なし）。
    kyugyo は窓口のシャッターが下りる（業務停止）。"""
    img = _rgb(base((240, 240, 236), (226, 226, 222)))
    wood_floor(img, FLOOR, col=(200, 200, 196), line=(186, 186, 182))
    d = _d(img)
    for k in range(4):
        d.rectangle([180 + k * 440, 150, 420 + k * 440, 380], fill=(250, 250, 250), outline=(200, 200, 200), width=3)
        d.rectangle([200 + k * 440, 170, 400 + k * 440, 220], fill=(250, 210, 40) if k % 2 else (60, 120, 200))
    d.rectangle([120, 560, 1800, 620], fill=(214, 214, 220), outline=(170, 170, 176), width=3)    # カウンター
    d.rectangle([120, 620, 1800, FLOOR], fill=(196, 196, 204))
    for k in range(1, 5):
        d.rectangle([120 + k * 336 - 6, 430, 120 + k * 336 + 6, 620], fill=(170, 176, 186))      # 仕切り
    if kyugyo:
        d.rectangle([120, 400, 1800, FLOOR], fill=(170, 172, 176))
        for k in range(14):
            d.line([(120, 420 + k * 30), (1800, 420 + k * 30)], fill=(140, 142, 146), width=3)
    else:
        for k in range(5):
            d.rectangle([200 + k * 336, 700, 300 + k * 336, 780], fill=(60, 100, 160))            # 椅子
    return img


def bf_kaichoshitsu():
    """新宿の高層ビルの会長室。窓いっぱいのビル街、重い机、壁ぎわに金庫。"""
    img = yakuin(view=(184, 200, 220), city=True)
    d = _d(img)
    d.rectangle([1640, 560, 1840, FLOOR], fill=(90, 96, 100), outline=(60, 64, 68), width=4)
    return img


# ---------------------------------------------------------------- NOVA・猿橋望
def nv_heya():
    """今の部屋。机に分厚い回数券の束と、習い事のパンフレット（文字は線）。"""
    img = heya2("none")
    d = _d(img)
    for k in range(5):                                                                           # 回数券の束
        d.rectangle([220 + k * 3, 610 - k * 6, 360 + k * 3, 640 - k * 6], fill=(250, 220, 120), outline=(170, 140, 60))
    d.rectangle([420, 590, 600, 640], fill=(250, 250, 246), outline=(170, 170, 166), width=2)
    d.rectangle([430, 598, 590, 614], fill=(230, 90, 140))
    return img


def nv_ekimae():
    """駅前の通り。高架の駅と、看板（色の板だけ）がびっしり付いた雑居ビル。"""
    img = vgrad((W, H), (160, 196, 230), (214, 228, 238))
    d = _d(img)
    for k, (x, w, top) in enumerate(((40, 360, 220), (440, 300, 300), (780, 380, 180), (1200, 320, 260), (1560, 340, 230))):
        d.rectangle([x, top, x + w, 820], fill=(206, 204, 198), outline=(150, 148, 142), width=3)
        for r in range((820 - top) // 90):
            col = [(230, 90, 140), (60, 120, 200), (250, 200, 40), (90, 170, 90)][(r + k) % 4]
            d.rectangle([x + 20, top + 20 + r * 90, x + w - 20, top + 70 + r * 90],
                        fill=col if (r + k) % 2 == 0 else (170, 190, 206))
    d.rectangle([0, 700, W, 760], fill=(120, 120, 126))                                           # 高架
    for x in range(100, W, 300):
        d.rectangle([x, 760, x + 40, 900], fill=(110, 110, 116))
    d.rectangle([0, 900, W, H], fill=(150, 150, 154))
    _person_line(d, 80, 1060, 14, 0.9)
    return img


def nv_lobby(ippai=False):
    """英会話教室の受付。カウンターと、壁に予約の表（色のマス）。ippai は表のマスが全部赤い（予約がいっぱい）。"""
    img = _rgb(base((246, 240, 244), (232, 226, 230)))
    wood_floor(img, FLOOR, col=(214, 206, 210), line=(200, 192, 196))
    d = _d(img)
    d.rectangle([980, 140, 1800, 520], fill=(250, 250, 250), outline=(170, 170, 176), width=4)    # 予約の表
    for r in range(6):
        for c in range(10):
            x, y = 1000 + c * 80, 160 + r * 58
            full = ippai or (r * 7 + c * 3) % 4 == 0
            d.rectangle([x, y, x + 70, y + 50], fill=(220, 50, 60) if full else (210, 236, 214))
    d.rectangle([120, 600, 900, 660], fill=(230, 90, 140), outline=(180, 60, 100), width=3)       # 受付の台
    d.rectangle([120, 660, 900, FLOOR], fill=(240, 220, 230))
    for k in range(3):
        d.rectangle([180 + k * 220, 610, 340 + k * 220, 650], fill=(250, 250, 246), outline=(180, 180, 176))
    return img


def nv_booth(kara=False):
    """駅前の教室のレッスン室。ガラスの仕切りの小部屋に、丸テーブルと椅子。kara は灯りが消え、椅子が机の上に上がる。"""
    img = _rgb(base((236, 240, 246) if not kara else (150, 152, 160), (222, 226, 232) if not kara else (136, 138, 146)))
    wood_floor(img, FLOOR, col=(200, 196, 200) if not kara else (120, 118, 122), line=(186, 182, 186))
    d = _d(img)
    for k in range(3):
        x = 140 + k * 580
        d.rectangle([x, 160, x + 520, 820], fill=(214, 230, 240) if not kara else (120, 126, 136),
                    outline=(160, 170, 180), width=6)
        d.ellipse([x + 160, 600, x + 360, 660], fill=(250, 250, 250) if not kara else (170, 170, 176))
        d.rectangle([x + 250, 650, x + 270, 820], fill=(150, 150, 156))
        for cx in (x + 110, x + 380):
            if kara:
                d.rectangle([cx + 40, 540, cx + 100, 600], fill=(90, 90, 96))
            else:
                d.rectangle([cx, 660, cx + 60, 760], fill=(230, 90, 140))
    return img


def nv_shachoshitsu():
    """報道陣に公開された社長室の入口（廊下から見た扉と、並んだカメラ）。中の設備は描かない。"""
    img = _rgb(base((226, 220, 210), (212, 206, 196)))
    wood_floor(img, FLOOR, col=(150, 120, 90), line=(134, 106, 78))
    d = _d(img)
    d.rectangle([760, 160, 1160, 820], fill=(110, 80, 56), outline=(70, 50, 34), width=8)        # 扉
    d.line([(960, 160), (960, 820)], fill=(70, 50, 34), width=6)
    d.ellipse([920, 470, 940, 490], fill=(220, 190, 110))
    d.ellipse([980, 470, 1000, 490], fill=(220, 190, 110))
    for k in range(6):                                                                           # カメラの列
        x = 120 + k * 300
        d.rectangle([x, 860, x + 120, 930], fill=(40, 40, 44))
        d.rectangle([x + 120, 880, x + 170, 910], fill=(60, 60, 66))
        d.line([(x + 60, 930), (x + 60, H)], fill=(60, 60, 66), width=6)
    return img


LOCATIONS = {
    # NOVA・猿橋望
    "nv_heya": nv_heya, "nv_ekimae": nv_ekimae, "nv_lobby": nv_lobby, "nv_lobby_ippai": lambda: nv_lobby(ippai=True),
    "nv_booth": nv_booth, "nv_booth_kara": lambda: nv_booth(kara=True), "nv_shachoshitsu": nv_shachoshitsu,
    "nv_kaiken": _sega_kaiken, "nv_kaigi": kaigi, "nv_kaigi_akaji": lambda: kaigi(akaji=True),
    "nv_honbu_yoru": lambda: jimusho90(yoru=True), "nv_jimusho": jimusho90, "nv_shoken": shoken,
    "nv_houtei": _sogo_saibansho, "nv_saikosai": cg_saikosai, "nv_gendai": _sega_gendai,
    # 武富士・武井保雄
    "bf_heya": bf_heya, "bf_4tsubo": bf_4tsubo, "bf_danchi": bf_danchi,
    "bf_shiten": bf_shiten, "bf_shiten_kyugyo": lambda: bf_shiten(kyugyo=True), "bf_kaicho": bf_kaichoshitsu,
    "bf_kaigi": kaigi, "bf_kaigi_akaji": lambda: kaigi(akaji=True), "bf_shoken": shoken,
    "bf_kokkai": _sogo_kokkai, "bf_houtei": _sogo_saibansho, "bf_saikosai": cg_saikosai,
    "bf_kaiken": _sega_kaiken, "bf_jimusho": jimusho90, "bf_gendai": _sega_gendai,
    # 大塚家具・大塚久美子
    "ok_heya": ok_heya, "ok_kobo": ok_kobo, "ok_showroom": ok_showroom,
    "ok_showroom_uketsuke": lambda: ok_showroom(uketsuke=True), "ok_showroom_sale": lambda: ok_showroom(sale=True),
    "ok_kaiken": _sega_kaiken, "ok_kaiken_kanbu": ok_kaiken_kanbu, "ok_soukai": kabunushi_kaijo,
    "ok_kaigi": kaigi, "ok_kaigi_akaji": lambda: kaigi(akaji=True), "ok_houtei": _sogo_saibansho,
    "ok_depart": ok_depart, "ok_tenpo": ok_tenpo, "ok_tenpo_kara": lambda: ok_tenpo(kara=True),
    "ok_aoyama": ok_aoyama, "ok_kaden": ok_kaden, "ok_gendai": _sega_gendai,
    # 船場吉兆・湯木佐知子
    "sk_heya": sk_heya, "sk_ryotei": sk_ryotei, "sk_ryotei_kyugyo": lambda: sk_ryotei(kyugyo=True),
    "sk_ryotei_kara": lambda: sk_ryotei(kara=True), "sk_zashiki": sk_zashiki, "sk_itaba": sk_itaba,
    "sk_uriba": sk_urba, "sk_uriba_kara": lambda: sk_urba(kara=True), "sk_hotel": sk_hotel,
    "sk_kaiken": _sega_kaiken, "sk_jimusho": jimusho90, "sk_kaigi": kaigi, "sk_houtei": _sogo_saibansho,
    "sk_tenant": sk_tenant, "sk_gendai": _sega_gendai,
}

# 年号カード。接頭辞ごとに "sk_card_2007" のように作る
CARDS = {"nv": ["1981", "1993", "1996", "2005", "2006", "2007", "2008", "2009", "2012", "2014", "2025", "2026"],
         "bf": ["1966", "1977", "1983", "1994", "2000", "2003", "2004", "2006", "2010", "2012", "2017", "2026"],
         "ok": ["1969", "1993", "2009", "2014", "2015", "2016", "2018", "2019", "2020", "2022", "2026"],
         "sk": ["1930", "1991", "1995", "1999", "2007", "2008", "2010", "2026"]}


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1:])
    for name, fn in LOCATIONS.items():
        if only and name not in only:
            continue
        fn().save(OUT / f"{name}.png")
        print(f"生成完了: {name}.png")
    for pre, years in CARDS.items():
        for y in years:
            nm = f"{pre}_card_{y}"
            if only and nm not in only:
                continue
            year_card(f"{y}年").save(OUT / f"{nm}.png")
            print(f"生成完了: {nm}.png")
