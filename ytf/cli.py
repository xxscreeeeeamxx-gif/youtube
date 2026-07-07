"""ytf コマンド: 動画量産パイプラインの入口。

典型的な1本のフロー:
    ytf ideas                 # ネタ出し（ストックに追加）
    ytf script --idea <id>    # 台本生成 -> projects/<slug>/script.yaml
    ytf make <slug>           # 音声→映像→サムネ→メタデータ→ショート 一括
"""

from __future__ import annotations

import argparse
import shutil
import sys

from .config import Config, Project


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="ytf", description="動画量産パイプライン")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("ideas", help="ネタ出し（LLM）/ 一覧")
    sp.add_argument("-n", "--count", type=int, default=15)
    sp.add_argument("--list", action="store_true")
    sp.add_argument("--response", help="manualモード: LLM返答ファイル")

    sp = sub.add_parser("script", help="台本生成（LLM）")
    sp.add_argument("--idea", help="backlogのネタID")
    sp.add_argument("--topic", help="ネタIDを使わず直接テーマ指定")
    sp.add_argument("--response", help="manualモード: LLM返答ファイル")

    sp = sub.add_parser("voice", help="VOICEVOXで音声合成 + タイミング確定")
    sp.add_argument("project")
    sp.add_argument("--tts", choices=["voicevox", "dummy"], default="voicevox")

    sp = sub.add_parser("render", help="本編mp4の書き出し")
    sp.add_argument("project")

    sp = sub.add_parser("shorts", help="ショート動画の切り出し")
    sp.add_argument("project")

    sp = sub.add_parser("thumbnail", help="サムネイル生成")
    sp.add_argument("project")

    sp = sub.add_parser("meta", help="タイトル・概要欄・タグ生成")
    sp.add_argument("project")

    sp = sub.add_parser("qc", help="品質チェック")
    sp.add_argument("project")
    sp.add_argument("--whisper", action="store_true", help="Whisperで誤読検出")

    sp = sub.add_parser("make", help="voice→render→thumbnail→meta→shorts 一括実行")
    sp.add_argument("project")
    sp.add_argument("--tts", choices=["voicevox", "dummy"], default="voicevox")
    sp.add_argument("--skip-shorts", action="store_true")

    sp = sub.add_parser("approve", help="台本レビュー完了マーク（n8nが自動ビルドする対象になる）")
    sp.add_argument("project")
    sp.add_argument("--revoke", action="store_true", help="承認を取り消す")

    sp = sub.add_parser("release", help="動画確認完了マーク（n8nがアップロードする対象になる）")
    sp.add_argument("project")
    sp.add_argument("--revoke", action="store_true")

    sub.add_parser("status", help="全プロジェクトの進行状況を一覧")

    sp = sub.add_parser("assets", help="素材管理")
    sp.add_argument("--init", action="store_true", help="プレースホルダー素材を生成")
    sp.add_argument("--force", action="store_true")

    sub.add_parser("voices", help="VOICEVOXの話者スタイル一覧")
    sub.add_parser("doctor", help="環境チェック")

    args = p.parse_args(argv)
    cfg = Config.load()

    if args.cmd == "ideas":
        from .ideas import list_ideas, run_ideas
        if args.list:
            list_ideas(cfg)
        else:
            run_ideas(cfg, args.count, args.response)

    elif args.cmd == "script":
        from .scripting import run_script
        run_script(cfg, args.idea, args.topic, args.response)

    elif args.cmd == "voice":
        from .voice import run_voice
        run_voice(cfg, Project.resolve(cfg, args.project), tts=args.tts)

    elif args.cmd == "render":
        from .build import render_main
        from .voice import load_timings
        proj = Project.resolve(cfg, args.project)
        render_main(cfg, proj, load_timings(proj))

    elif args.cmd == "shorts":
        from .build import render_shorts
        from .voice import load_timings
        proj = Project.resolve(cfg, args.project)
        render_shorts(cfg, proj, load_timings(proj))

    elif args.cmd == "thumbnail":
        from .thumbnail import run_thumbnail
        run_thumbnail(cfg, Project.resolve(cfg, args.project))

    elif args.cmd == "meta":
        from .metadata import run_metadata
        from .voice import load_timings
        proj = Project.resolve(cfg, args.project)
        run_metadata(cfg, proj, load_timings(proj))

    elif args.cmd == "qc":
        from .qc import run_qc
        run_qc(cfg, Project.resolve(cfg, args.project), use_whisper=args.whisper)

    elif args.cmd == "make":
        from .build import render_main, render_shorts
        from .metadata import run_metadata
        from .thumbnail import run_thumbnail
        from .voice import run_voice
        proj = Project.resolve(cfg, args.project)
        timings = run_voice(cfg, proj, tts=args.tts)
        render_main(cfg, proj, timings)
        run_thumbnail(cfg, proj)
        run_metadata(cfg, proj, timings)
        if not args.skip_shorts:
            render_shorts(cfg, proj, timings)
        print("\n✅ 完了。out/ の中身を確認して投稿してください。")

    elif args.cmd == "approve":
        proj = Project.resolve(cfg, args.project)
        marker = proj.root / ".approved"
        if args.revoke:
            marker.unlink(missing_ok=True)
            print(f"承認を取り消しました: {proj.root.name}")
        else:
            marker.touch()
            print(f"承認しました: {proj.root.name}（次回の自動ビルドで処理されます）")

    elif args.cmd == "release":
        proj = Project.resolve(cfg, args.project)
        marker = proj.root / ".release"
        if args.revoke:
            marker.unlink(missing_ok=True)
            print(f"リリースを取り消しました: {proj.root.name}")
        else:
            if not (proj.root / "out" / "video.mp4").exists():
                raise SystemExit("out/video.mp4 がありません。先にビルドしてください。")
            marker.touch()
            print(f"リリース待ちにしました: {proj.root.name}（n8nがアップロードします）")

    elif args.cmd == "status":
        _status(cfg)

    elif args.cmd == "assets":
        from .assets_gen import init_assets
        if args.init or args.force:
            init_assets(cfg, force=args.force)
        else:
            print("使い方: ytf assets --init")

    elif args.cmd == "voices":
        from .voice import VoicevoxClient
        client = VoicevoxClient(cfg.get("voicevox", "url", default="http://127.0.0.1:50021"))
        if not client.ping():
            raise SystemExit("VOICEVOX Engine に接続できません")
        for sp_ in client.speakers():
            for st in sp_["styles"]:
                print(f"{st['id']:4d}  {sp_['name']} / {st['name']}")

    elif args.cmd == "doctor":
        _doctor(cfg)


def _status(cfg: Config) -> None:
    projects = sorted((cfg.root / "projects").glob("*/script.yaml"))
    if not projects:
        print("プロジェクトがありません")
        return
    for sp in projects:
        d = sp.parent
        if (d / ".uploaded").exists():
            state = "🚀 アップロード済み"
        elif (d / ".release").exists():
            state = "📤 リリース待ち（n8nがアップロード）"
        elif (d / "out" / "video.mp4").exists():
            state = "🎞  ビルド済み → 確認して ytf release"
        elif (d / ".approved").exists():
            state = "⏳ 承認済み（自動ビルド待ち）"
        else:
            state = "📝 台本レビュー待ち → ytf approve"
        print(f"{d.name:24s} {state}")


def _doctor(cfg: Config) -> None:
    import os

    from .config import ffmpeg_bin

    def check(label: str, ok: bool, hint: str = "") -> None:
        mark = "✅" if ok else "❌"
        print(f"{mark} {label}" + (f" — {hint}" if not ok and hint else ""))

    check("ffmpeg", shutil.which(ffmpeg_bin()) is not None, "brew install ffmpeg")
    try:
        cfg.find_pillow_font()
        check("日本語フォント", True)
    except SystemExit:
        check("日本語フォント", False, "channel.yaml の fonts.paths を確認")

    from .voice import VoicevoxClient
    vv = VoicevoxClient(cfg.get("voicevox", "url", default="http://127.0.0.1:50021"))
    check("VOICEVOX Engine", vv.ping(), "VOICEVOXアプリを起動（:50021）")

    check("ANTHROPIC_API_KEY", bool(os.environ.get("ANTHROPIC_API_KEY")),
          "未設定でもコピペ半自動モードで運用可能")
    try:
        import anthropic  # noqa: F401
        check("anthropic SDK", True)
    except ImportError:
        check("anthropic SDK", False, "pip install anthropic（APIモード用）")
    try:
        import whisper  # noqa: F401
        check("whisper (QC用)", True)
    except ImportError:
        check("whisper (QC用)", False, "pip install openai-whisper（任意）")

    if cfg.get("video", "show_characters", default=True):
        sprite_ok = all(
            (cfg.root / ch["sprite_dir"] / "normal.png").exists()
            for ch in cfg.characters.values()
            if "sprite_dir" in ch
        )
        check("立ち絵素材", sprite_ok, "ytf assets --init でプレースホルダー生成")
    else:
        check("立ち絵素材", True, "")
        print("   （show_characters: false のため立ち絵は不要）")


if __name__ == "__main__":
    main()
