#!/usr/bin/env python3
"""第10弾3本（2026-12-03〜05。方向転換の実験の17〜19本目：会社の転落・破綻・裁判）の背景を生成する。

接頭辞: mu_（村上ファンド事件）/ hn_（はれのひの破綻）/ ep_（エルピーダメモリの破綻）
方針は gen_now9_bgs.py と同じ。実在の会社のロゴ・社名の文字・店の意匠・商品のパッケージは描かない。
実在の人の写真や肖像は描かない（壁の写真は人の形だけ）。差し替え用は元の絵に要素を足すか減らす。

実行: PYTHONPATH=. python scripts/gen_now10_bgs.py [名前...]
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.gen_drama_bgs import H, OUT, W, base, tatami_floor, vgrad, wood_floor  # noqa: E402
from scripts.gen_famicom_bgs import year_card  # noqa: E402
from scripts.gen_now_bgs import FLOOR, _d, _rgb, kaigi, yakuin  # noqa: E402
from scripts.gen_now2_bgs import getsurei, heya2, kabunushi_kaijo, shingikai, shoken  # noqa: E402
from scripts.gen_now3_bgs import choin, heya3, jimusho90, kaigai_kojo, kenkyujo, roko_shitsu, wafer  # noqa: E402
from scripts.gen_now5_bgs import cg_saikosai, ya_hk_office  # noqa: E402
from scripts.gen_now3_bgs import kojo_soto  # noqa: E402
from scripts.gen_now7_bgs import ik_mise, kb_soko  # noqa: E402
from scripts.gen_now8_bgs import ld_gamen, ld_kanmae, ld_radio, ld_tower, tj_kaiken, tj_shinbun  # noqa: E402
from scripts.gen_now3_bgs import kuko_lobby  # noqa: E402
from scripts.gen_now8_bgs import tj_osetsu  # noqa: E402
from scripts.gen_now9_bgs import _light, _press, tm_kessan  # noqa: E402
from scripts.gen_sega_bgs import _person_line, gendai as _sega_gendai, kaiken as _sega_kaiken  # noqa: E402
from scripts.gen_sogo_bgs import saibansho as _sogo_saibansho  # noqa: E402

FURI = [(200, 40, 70), (240, 120, 160), (60, 80, 160), (230, 190, 60), (120, 40, 120), (40, 130, 110), (250, 250, 250), (210, 70, 40)]


def _furisode(d, x, y, s=1.0, col=(200, 40, 70), obi=(230, 190, 60)):
    """衣紋掛けに掛けた振袖（正面）。x, y は掛けの中央の上。"""
    d.line([(x - 120 * s, y), (x + 120 * s, y)], fill=(120, 90, 60), width=int(8 * s))
    d.polygon([(x - 120 * s, y + 6 * s), (x + 120 * s, y + 6 * s), (x + 90 * s, y + 360 * s), (x - 90 * s, y + 360 * s)], fill=col)
    d.rectangle([x - 60 * s, y + 140 * s, x + 60 * s, y + 190 * s], fill=obi)
    d.polygon([(x - 120 * s, y + 6 * s), (x - 170 * s, y + 220 * s), (x - 110 * s, y + 230 * s)], fill=col)
    d.polygon([(x + 120 * s, y + 6 * s), (x + 170 * s, y + 220 * s), (x + 110 * s, y + 230 * s)], fill=col)
    for k in range(5):
        d.ellipse([x - 70 * s + k * 30 * s, y + 230 * s + (k % 2) * 40 * s, x - 50 * s + k * 30 * s, y + 250 * s + (k % 2) * 40 * s],
                  fill=(255, 240, 240))


# ---------------------------------------------------------------- はれのひの破綻
def hn_heya():
    """今の部屋。机にスマホと、たたんだ着物の箱（無地）。"""
    img = heya2("none")
    d = _d(img)
    d.rounded_rectangle([230, 560, 300, 640], radius=10, fill=(30, 30, 34))
    d.rectangle([238, 570, 292, 630], fill=(240, 180, 200))
    d.rectangle([340, 590, 600, 640], fill=(250, 246, 236), outline=(170, 150, 120), width=3)
    d.rectangle([340, 606, 600, 616], fill=(200, 60, 80))
    return img


def hn_mise(kara=False):
    """振袖の店の中。衣紋掛けの振袖が壁一面に並び、手前に試着の鏡と台。kara は振袖が1枚も無く、衣紋掛けだけが残る。"""
    img = _rgb(base((240, 232, 222), (226, 218, 208)))
    wood_floor(img, FLOOR, col=(190, 160, 120), line=(170, 140, 100))
    d = _d(img)
    d.rectangle([0, 120, W, 150], fill=(150, 110, 70))
    for k in range(7):
        x = 160 + k * 270
        if kara:
            d.line([(x - 120, 170), (x + 120, 170)], fill=(120, 90, 60), width=8)
        else:
            _furisode(d, x, 170, 0.95, col=FURI[k % len(FURI)], obi=FURI[(k + 3) % len(FURI)])
    d.rectangle([840, 620, 1080, 900], fill=(200, 210, 220), outline=(150, 120, 80), width=10)
    d.rectangle([600, 760, 1320, 820], fill=(170, 130, 90))
    return img


def hn_kitsuke(kara=False):
    """着付けの会場（ホテルの宴会場を仕切った部屋）。鏡台がずらりと並び、ハンガーラックに振袖。
    kara は鏡台の前に誰もいない、ラックも空（会社の人が来なかった朝）。"""
    img = _rgb(base((226, 214, 198), (212, 200, 184)))
    d = _d(img)
    d.rectangle([0, 700, W, H], fill=(150, 80, 70))
    for k in range(5):
        d.line([(k * 400, 0), (k * 400 + 60, 80)], fill=(220, 200, 150), width=4)
    for k in range(6):
        x = 120 + k * 300
        d.rectangle([x, 300, x + 200, 560], fill=(210, 224, 236), outline=(160, 130, 90), width=8)
        d.rectangle([x - 20, 560, x + 220, 600], fill=(170, 130, 90))
        d.rectangle([x + 60, 640, x + 140, 700], fill=(120, 60, 60))
    d.line([(160, 640), (1760, 640)], fill=(150, 150, 156), width=8)
    if not kara:
        for k in range(8):
            _furisode(d, 260 + k * 200, 640, 0.42, col=FURI[k % len(FURI)], obi=FURI[(k + 2) % len(FURI)])
    return img


def hn_shiki(harezuki=True):
    """成人式の式場の外（冬の晴れた朝）。大きな建物の入口と植え込み。harezuki は晴れ着の人の形（振袖の色）が集まる。
    False はスーツ・普段着の色の人の形が多い。"""
    img = vgrad((W, H), (160, 196, 232), (226, 232, 238))
    d = _d(img)
    d.rectangle([360, 180, 1560, 700], fill=(200, 196, 188), outline=(150, 146, 138), width=6)
    for r in range(4):
        for c in range(10):
            d.rectangle([420 + c * 112, 220 + r * 100, 500 + c * 112, 290 + r * 100], fill=(140, 170, 196))
    d.rectangle([820, 560, 1100, 700], fill=(90, 110, 130))
    d.rectangle([0, 700, W, H], fill=(186, 184, 178))
    for k in range(5):
        d.ellipse([20 + k * 420, 600, 260 + k * 420, 720], fill=(70, 120, 80))
    cols = [(200, 40, 70), (240, 120, 160), (60, 80, 160), (230, 190, 60), (120, 40, 120), (40, 130, 110)] if harezuki \
        else [(60, 64, 80), (90, 90, 100), (130, 110, 90), (200, 40, 70), (70, 80, 110)]
    _person_line(d, 40, 1020, 26, 1.0, cols=cols)
    return img


def hn_shutter(harigami=False):
    """店の正面（シャッターが下りている）。harigami はシャッターに白い張り紙と、前に報道のカメラ。"""
    img = ik_mise(heiten=True)
    if harigami:
        d = _d(img)
        for x0 in (700, 1030):
            d.rectangle([x0, 430, x0 + 190, 660], fill=(252, 252, 250), outline=(160, 160, 160), width=3)
            for j in range(5):
                d.line([(x0 + 24, 470 + j * 34), (x0 + 166, 470 + j * 34)], fill=(60, 60, 60), width=5)
        _press(d, 40, 1060, 7, 1.1)
        _press(d, 1400, 1060, 7, 1.1)
    return img


def hn_dm():
    """事務所の机の上に、高校生あての封筒の束（色つきの封筒が山）。文字は描かない。"""
    img = vgrad((W, H), (150, 120, 90), (120, 92, 66))
    d = _d(img)
    rnd = random.Random(12)
    for k in range(60):
        x, y = rnd.randint(200, 1600), rnd.randint(160, 860)
        col = FURI[k % len(FURI)]
        d.rectangle([x, y, x + 260, y + 160], fill=(250, 248, 240), outline=(170, 160, 140), width=3)
        d.rectangle([x + 10, y + 10, x + 70, y + 60], fill=col)
        d.line([(x + 100, y + 80), (x + 230, y + 80)], fill=(120, 120, 120), width=4)
        d.line([(x + 100, y + 110), (x + 200, y + 110)], fill=(120, 120, 120), width=4)
    return img


def hn_hako():
    """倉庫の床に積まれた段ボール箱。いくつかの箱から振袖の色がのぞく（返ってきた振袖）。"""
    img = _rgb(base((200, 198, 192), (186, 184, 178)))
    wood_floor(img, FLOOR, col=(150, 146, 140), line=(134, 130, 124))
    d = _d(img)
    rnd = random.Random(21)
    for r in range(4):
        for c in range(9):
            if rnd.random() < 0.12:
                continue
            x, y = 40 + c * 205, FLOOR - (r + 1) * 140
            d.rectangle([x, y, x + 190, y + 132], fill=(196, 160, 110), outline=(140, 110, 70), width=3)
            if rnd.random() < 0.5:
                col = FURI[rnd.randint(0, len(FURI) - 1)]
                d.polygon([(x + 30, y), (x + 90, y - 30), (x + 160, y)], fill=col)
    return img


# ---------------------------------------------------------------- エルピーダメモリの破綻
def ep_heya():
    """今の部屋。机にノートパソコンとスマホ、パソコンの中のメモリの部品（緑の細長い板）。"""
    img = heya3("sumaho")
    d = _d(img)
    d.rectangle([420, 610, 600, 640], fill=(40, 120, 70), outline=(30, 80, 50), width=2)
    for k in range(6):
        d.rectangle([432 + k * 28, 616, 452 + k * 28, 632], fill=(30, 30, 34))
    for k in range(8):
        d.line([(430 + k * 21, 640), (430 + k * 21, 646)], fill=(220, 190, 80), width=3)
    return img


def ep_ringi():
    """本社の机。電話帳ほどの厚さの稟議書の束と、ずらりと並ぶ判子の枠（文字は描かない）。"""
    img = vgrad((W, H), (150, 120, 90), (120, 92, 66))
    d = _d(img)
    for k in range(9):
        y = 860 - k * 64
        d.rectangle([560 + (k % 3) * 6, y, 1160 + (k % 2) * 8, y + 60], fill=(250, 248, 240), outline=(170, 160, 140), width=3)
    d.rectangle([560, 300, 1170, 330], fill=(60, 80, 140))
    for k in range(12):
        x = 1240 + (k % 4) * 140
        y = 260 + (k // 4) * 140
        d.rectangle([x, y, x + 110, y + 110], outline=(180, 60, 60), width=4)
        d.ellipse([x + 25, y + 25, x + 85, y + 85], outline=(200, 50, 50), width=5)
    return img


def ep_kojo(koji=False):
    """大きな半導体工場の外観（緑の丘）。koji は隣の敷地にクレーンと建設中の骨組み（新しい棟）。"""
    img = kojo_soto(umi=False)
    if koji:
        d = _d(img)
        for k in range(3):
            x = 1300 + k * 200
            d.line([(x, 720), (x, 260)], fill=(230, 180, 40), width=14)
            d.line([(x - 160, 280), (x + 120, 280)], fill=(230, 180, 40), width=10)
            d.line([(x + 100, 280), (x + 100, 420)], fill=(80, 80, 86), width=3)
        for r in range(4):
            d.line([(1200, 700 - r * 90), (1800, 700 - r * 90)], fill=(140, 140, 146), width=8)
        for c in range(7):
            d.line([(1200 + c * 100, 700), (1200 + c * 100, 430)], fill=(140, 140, 146), width=8)
    return img


# ---------------------------------------------------------------- 村上ファンド事件
def mu_heya():
    """今の部屋。机にスマホ（株価のアプリ＝線のグラフ）と、小さな貯金箱。"""
    img = heya2("none")
    d = _d(img)
    d.rounded_rectangle([230, 560, 300, 640], radius=10, fill=(30, 30, 34))
    d.rectangle([238, 570, 292, 630], fill=(240, 244, 248))
    d.line([(242, 620), (256, 600), (268, 610), (288, 580)], fill=(220, 60, 50), width=4)
    d.ellipse([360, 580, 460, 640], fill=(240, 150, 170), outline=(180, 100, 120), width=3)
    d.rectangle([396, 584, 424, 590], fill=(120, 60, 80))
    return img


def mu_kyujo():
    """野球場の外（夏の昼）。れんが色の外壁に茂るつた、大きな照明塔、入口の前の広場。名前・看板の文字は描かない。"""
    img = vgrad((W, H), (120, 180, 236), (210, 228, 240))
    d = _d(img)
    d.rectangle([0, 300, W, 760], fill=(150, 80, 60), outline=(110, 60, 44), width=6)
    rnd = random.Random(31)
    for _ in range(900):
        x, y = rnd.randint(0, W), rnd.randint(300, 760)
        d.ellipse([x, y, x + 26, y + 20], fill=(50 + rnd.randint(0, 40), 120 + rnd.randint(0, 40), 60))
    for k in range(6):
        d.rectangle([140 + k * 300, 560, 260 + k * 300, 760], fill=(70, 60, 56))
    for x in (260, 1660):
        d.line([(x, 300), (x, 60)], fill=(150, 150, 156), width=14)
        d.rectangle([x - 90, 30, x + 90, 110], fill=(230, 230, 236), outline=(150, 150, 156), width=4)
    d.rectangle([0, 760, W, H], fill=(196, 190, 176))
    return img


LOCATIONS = {
    # はれのひの破綻
    "hn_heya": hn_heya, "hn_mise": hn_mise, "hn_mise_kara": lambda: hn_mise(kara=True),
    "hn_kitsuke": hn_kitsuke, "hn_kitsuke_kara": lambda: hn_kitsuke(kara=True),
    "hn_shiki": hn_shiki, "hn_shutter": hn_shutter, "hn_shutter_harigami": lambda: hn_shutter(harigami=True),
    "hn_jimusho": jimusho90, "hn_kaiken": _sega_kaiken, "hn_houtei": _sogo_saibansho, "hn_shinbun": tj_shinbun,
    "hn_kaigi": kaigi, "hn_gendai": _sega_gendai,
    "hn_dm": hn_dm, "hn_hako": hn_hako, "hn_osetsu": tj_osetsu, "hn_kessan": tm_kessan,
    "hn_kessan_kuro": lambda: tm_kessan(kuro=True), "hn_jimusho_yoru": lambda: jimusho90(yoru=True),
    "hn_hall": kabunushi_kaijo, "hn_kuko": lambda: kuko_lobby(sukunai=True), "hn_kaigi_akaji": lambda: kaigi(akaji=True),
    # エルピーダメモリの破綻
    "ep_heya": ep_heya, "ep_cleanroom": roko_shitsu, "ep_cleanroom_kara": lambda: roko_shitsu(kara=True),
    "ep_wafer": wafer, "ep_kenkyujo": kenkyujo, "ep_getsurei": getsurei, "ep_getsurei_akaji": lambda: getsurei(akaji=True),
    "ep_kaigai": kaigai_kojo, "ep_choin": choin, "ep_shingikai": shingikai, "ep_kaiken": _sega_kaiken,
    "ep_kaigi": kaigi, "ep_kaigi_akaji": lambda: kaigi(akaji=True), "ep_yakuin": lambda: yakuin(),
    "ep_honsha": ld_tower, "ep_shinbun": tj_shinbun, "ep_houtei": _sogo_saibansho, "ep_gendai": _sega_gendai,
    "ep_soko": kb_soko, "ep_ringi": ep_ringi, "ep_kojo": ep_kojo, "ep_kojo_koji": lambda: ep_kojo(koji=True),
    "ep_osetsu": tj_osetsu, "ep_yakuin_yoru": lambda: yakuin(view=(24, 30, 56), city=True), "ep_shoken": shoken,
    "ep_jimusho": jimusho90,
    # 村上ファンド事件
    "mu_heya": mu_heya, "mu_tower": ld_tower, "mu_tower_yoru": lambda: ld_tower(sosaku=True),
    "mu_office": ya_hk_office, "mu_sokai": kabunushi_kaijo, "mu_shingikai": shingikai,
    "mu_kaiken": tj_kaiken, "mu_kaiken2": _sega_kaiken, "mu_kanmae": ld_kanmae, "mu_houtei": _sogo_saibansho,
    "mu_saikosai": cg_saikosai, "mu_shoken": shoken, "mu_shinbun": tj_shinbun, "mu_kaigi": kaigi,
    "mu_yakuin": lambda: yakuin(view=(170, 196, 230), city=True), "mu_jimusho": jimusho90, "mu_gendai": _sega_gendai,
    "mu_radio": ld_radio, "mu_radio_nuri": lambda: ld_radio(nuri=True), "mu_gamen": ld_gamen,
    "mu_gamen_aka": lambda: ld_gamen(aka=True), "mu_kyujo": mu_kyujo, "mu_kaigi_akaji": lambda: kaigi(akaji=True),
}

# 年号カード。接頭辞ごとに "mu_card_2006" のように作る（台帳を見て足す）
CARDS = {"mu": ["1999", "2002", "2004", "2005", "2006", "2007", "2009", "2011", "2026"], "hn": ["2011", "2015", "2016", "2017", "2018", "2019", "2026"],
         "ep": ["1999", "2002", "2003", "2004", "2007", "2009", "2011", "2012", "2013", "2024", "2026"]}


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
