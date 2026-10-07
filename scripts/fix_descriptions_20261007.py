# 2026-10-07 に全動画の概要欄を一度だけ直したときのスクリプト（記録用）。実行: python scripts/fix_descriptions_20261007.py [--apply]
"""概要欄の見直し（2026-10-07）。--apply を付けない限り書き換えない。
1) クレジットを規約の例どおり VOICEVOX:キャラ名 の並びに
2) クレジットの無い回に足す / ゆっくりナレの回にナレーションのクレジットを足す
3) 目次の無い回に目次（timing.json があり、長さが YouTube 上の動画と2秒以内で合う回だけ）
4) 再生リストとチャンネル登録のリンク
"""
import sys, re, json, glob, pathlib
sys.path.insert(0, "scripts")
sys.stdout.reconfigure(encoding="utf-8")
import yaml
from upload_youtube import service, _channel_videos

APPLY = "--apply" in sys.argv
PLAYLIST = "https://www.youtube.com/playlist?list=PLGcuoPXiBiXY"
yt = service()
ch_id = yt.channels().list(part="id", mine=True).execute()["items"][0]["id"]
SUB = f"https://www.youtube.com/channel/{ch_id}?sub_confirmation=1"
LINKS = f"▼ ほかの再現ドラマ（まとめて見る）\n{PLAYLIST}\n▼ チャンネル登録\n{SUB}"
NARR = "ナレーション: AquesTalk（株式会社アクエスト）"
VOICE_NAME = {3: "ずんだもん", 8: "春日部つむぎ", 11: "玄野武宏", 12: "白上虎太郎", 13: "青山龍星",
              21: "剣崎雌雄", 42: "ちび式じい", 67: "栗田まろん", 73: "満別花丸", 100: "黒沢冴白"}

# 動画ID → プロジェクト
proj_of = {}
for f in glob.glob("projects/*/*/*/youtube_video_id.txt") + glob.glob("projects/*/*/youtube_video_id.txt"):
    proj_of[pathlib.Path(f).read_text(encoding="utf-8").strip()] = pathlib.Path(f).parent

def iso_sec(d):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d)
    h, mi, s = (int(x or 0) for x in m.groups())
    return h * 3600 + mi * 60 + s

def chapters_for(pdir, dur):
    tp = pdir / "audio" / "timing.json"
    if not tp.exists():
        return None, "timing無し"
    cuts = json.loads(tp.read_text(encoding="utf-8"))
    end = cuts[-1]["start"] + cuts[-1]["total_dur"]
    if abs(end - dur) > 2.5:
        return None, f"長さ不一致 {end:.0f}s≠{dur}s"
    rows = [(int(c["start"]), c["scene_title"]) for c in cuts if c.get("scene_start") and c.get("scene_title")]
    rows = [(0, "オープニング")] + [r for r in rows if r[0] > 0]
    kept = [rows[0]]
    for s, n in rows[1:]:
        if s - kept[-1][0] >= 10:
            kept.append((s, n))
    if len(kept) < 3:
        return None, "章が3つ未満"
    return "▼ 目次\n" + "\n".join(f"{s // 60}:{s % 60:02d} {n}" for s, n in kept), "ok"

def credits_from_script(pdir):
    sc = yaml.safe_load((pdir / "script.yaml").read_text(encoding="utf-8"))
    names = []
    spk = set()
    for scene in sc.get("scenes", []):
        for cut in scene.get("cuts", []):
            spk.add(cut.get("speaker"))
            if cut.get("duet_with"):
                spk.add(cut["duet_with"])
    if "zundamon" in spk: names.append("ずんだもん")
    if "tsumugi" in spk: names.append("春日部つむぎ")
    for mob in (sc.get("meta", {}).get("mobs") or []):
        if mob.get("id") in spk:
            n = VOICE_NAME.get(mob.get("voice"))
            if n and n not in names:
                names.append(n)
    narr = "reimu" in spk or bool(sc.get("meta", {}).get("narrator"))
    return names, narr

vids = list(_channel_videos(yt))
items = []
for i in range(0, len(vids), 50):
    items += yt.videos().list(part="snippet,status,contentDetails", id=",".join(vids[i:i + 50])).execute()["items"]

changed = 0
for it in sorted(items, key=lambda x: x["status"].get("publishAt") or x["snippet"]["publishedAt"]):
    sn, st = it["snippet"], it["status"]
    if st["privacyStatus"] == "private" and not st.get("publishAt"):
        continue
    vid = it["id"]; desc = sn["description"]; new = desc; notes = []
    pdir = proj_of.get(vid)
    # 1) クレジットの書き方
    m = re.search(r"音声: VOICEVOX（([^）]+)）", new)
    if m:
        names = [n.strip() for n in m.group(1).split("、") if n.strip()]
        new = new.replace(m.group(0), "音声: " + " / ".join(f"VOICEVOX:{n}" for n in names))
        notes.append("クレジット形式")
    # 2) クレジットが無い回
    if "▼使用素材" not in new and pdir is not None:
        names, narr = credits_from_script(pdir)
        block = ["▼使用素材", "音声: " + " / ".join(f"VOICEVOX:{n}" for n in names)]
        if narr: block.append(NARR)
        block += ["効果音: 効果音ラボ / BGM: DOVA-SYNDROME", "※本動画は VOICEVOX の音声合成を使用しています。"]
        new = re.sub(r"(\n\n#[^\n]+\s*)$", "\n\n" + "\n".join(block) + r"\1", new) if re.search(r"\n\n#[^\n]+\s*$", new) else new.rstrip() + "\n\n" + "\n".join(block)
        notes.append("クレジット追加")
    elif "▼使用素材" in new and NARR not in new and pdir is not None:
        _, narr = credits_from_script(pdir)
        if narr:
            new = re.sub(r"(音声: [^\n]+\n)", r"\1" + NARR + "\n", new, count=1)
            notes.append("ナレのクレジット")
    # 3) 目次
    if "▼ 目次" not in new and pdir is not None:
        chap, why = chapters_for(pdir, iso_sec(it["contentDetails"]["duration"]))
        if chap:
            head, sep, rest = new.partition("\n\n")
            new = head + "\n\n" + chap + sep + rest
            notes.append("目次")
        else:
            notes.append(f"目次なし({why})")
    # 4) リンク（注記の直前）
    if PLAYLIST not in new:
        k = new.find("※台本は") if "※台本は" in new else new.find("※内容は")
        if k >= 0:
            new = new[:k] + LINKS + "\n\n" + new[k:]
        else:
            new = new.rstrip() + "\n\n" + LINKS
        notes.append("リンク")
    if pdir is None:
        notes.append("プロジェクト不明")
    if new != desc:
        changed += 1
    print(f'{(st.get("publishAt") or sn["publishedAt"])[:10]} {vid} {sn["title"][:18]} : {", ".join(notes)}')
    if APPLY and new != desc:
        body = {"title": sn["title"], "categoryId": sn["categoryId"], "description": new, "tags": sn.get("tags", [])}
        for k in ("defaultLanguage", "defaultAudioLanguage"):
            if sn.get(k): body[k] = sn[k]
        yt.videos().update(part="snippet", body={"id": vid, "snippet": body}).execute()
    if "--show" in sys.argv and vid in sys.argv:
        print("-----\n" + new + "\n-----")
print("変更", changed, "本", "（適用済み）" if APPLY else "（未適用・確認のみ）")
