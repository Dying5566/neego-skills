#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

from path_policy import abbreviate_title, resolve_output_dir


YT_DLP_BASE = ["yt-dlp", "--cookies-from-browser", "chrome", "--no-playlist"]
YT_DLP_FALLBACK = [
    "yt-dlp",
    "--cookies-from-browser",
    "chrome",
    "--js-runtimes",
    "node",
    "--remote-components",
    "ejs:github",
    "--extractor-args",
    "youtube:player_client=web",
    "--no-playlist",
]
QUALITY_MAP = {
    "best": "bv*+ba/b",
    "1080p": "bv*[height<=1080]+ba/b[height<=1080]",
    "720p": "bv*[height<=720]+ba/b[height<=720]",
    "480p": "bv*[height<=480]+ba/b[height<=480]",
    "360p": "bv*[height<=360]+ba/b[height<=360]",
}


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, capture_output=True)


def ensure_binary(name: str) -> None:
    if shutil.which(name) is None:
        raise SystemExit(json.dumps({"status": "error", "message": f"Missing dependency: {name}"}, ensure_ascii=False))


def discover_output(output_dir: Path) -> Path | None:
    candidates = sorted(output_dir.glob("*"), key=lambda path: path.stat().st_mtime, reverse=True)
    for candidate in candidates:
        if candidate.is_file() and candidate.suffix.lower() in {".mp4", ".mkv", ".webm", ".mp3"}:
            return candidate
    return None


def fetch_video_title(url: str) -> str:
    commands = [
        YT_DLP_BASE + ["--print", "%(title)s", "--skip-download", url],
        YT_DLP_FALLBACK + ["--print", "%(title)s", "--skip-download", url],
    ]
    for cmd in commands:
        try:
            result = run(cmd)
            title = result.stdout.strip().splitlines()[0].strip()
            if title:
                return title
        except subprocess.CalledProcessError:
            continue
    return "video"


def main() -> None:
    parser = argparse.ArgumentParser(description="Download a YouTube video while preserving the original source")
    parser.add_argument("--url", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--video-slug")
    parser.add_argument("--quality", default="best", choices=sorted(QUALITY_MAP))
    parser.add_argument("--format", dest="format_type", default="mp4", choices=["mp4", "webm", "mkv"])
    parser.add_argument("--audio-only", action="store_true")
    parser.add_argument("--dir-language", choices=["en", "zh-Hans", "zh-Hant"], default="en")
    args = parser.parse_args()

    ensure_binary("yt-dlp")
    video_slug = args.video_slug or abbreviate_title(fetch_video_title(args.url))
    output_dir = resolve_output_dir(Path(args.output_dir).expanduser().resolve(), "source", video_slug, args.dir_language)
    output_dir.mkdir(parents=True, exist_ok=True)
    template_name = f"{video_slug}.%(ext)s"
    template = str(output_dir / template_name)

    if args.audio_only:
        cmd = YT_DLP_BASE + ["-x", "--audio-format", "mp3", "--audio-quality", "0", "-o", template, args.url]
        fallback = YT_DLP_FALLBACK + ["-x", "--audio-format", "mp3", "--audio-quality", "0", "-o", template, args.url]
    else:
        format_selector = QUALITY_MAP[args.quality]
        cmd = YT_DLP_BASE + ["-f", format_selector, "--merge-output-format", args.format_type, "-o", template, args.url]
        fallback = YT_DLP_FALLBACK + ["-f", format_selector, "--merge-output-format", args.format_type, "-o", template, args.url]

    attempted = []
    for candidate in (cmd, fallback):
        attempted.append(candidate)
        try:
            run(candidate)
            output_file = discover_output(output_dir)
            print(json.dumps({
                "status": "ok",
                "url": args.url,
                "output": str(output_file) if output_file else None,
                "video_slug": video_slug,
                "quality": args.quality,
                "format": "mp3" if args.audio_only else args.format_type,
                "used_fallback": candidate is fallback,
            }, ensure_ascii=False, indent=2))
            return
        except subprocess.CalledProcessError as exc:
            last_error = exc.stderr.strip() or exc.stdout.strip() or str(exc)

    print(json.dumps({
        "status": "error",
        "url": args.url,
        "message": last_error,
        "attempted": attempted,
    }, ensure_ascii=False, indent=2))
    raise SystemExit(1)


if __name__ == "__main__":
    main()
