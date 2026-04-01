#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


LANGUAGE_MAP = {
    "zh": ["zh-Hans", "zh-Hant"],
    "en": ["en", "en-orig"],
    "bilingual": ["en", "en-orig", "zh-Hans", "zh-Hant"],
}


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=check)


def ensure_binary(name: str) -> None:
    if shutil.which(name) is None:
        raise SystemExit(json.dumps({"status": "error", "message": f"Missing dependency: {name}"}, ensure_ascii=False))


def list_subs(url: str) -> str:
    cmd = ["yt-dlp", "--cookies-from-browser", "chrome", "--list-subs", "--skip-download", "--no-playlist", url]
    result = run(cmd, check=False)
    return (result.stdout or "") + "\n" + (result.stderr or "")


def download_subs(url: str, languages: list[str], output_dir: Path) -> list[str]:
    cmd = [
        "yt-dlp",
        "--cookies-from-browser",
        "chrome",
        "--skip-download",
        "--ignore-no-formats-error",
        "--write-auto-sub",
        "--write-sub",
        "--sub-lang",
        ",".join(languages),
        "--sub-format",
        "vtt",
        "--convert-subs",
        "srt",
        "-o",
        str(output_dir / "%(title)s.%(ext)s"),
        url,
    ]
    run(cmd)
    return sorted(str(path) for path in output_dir.glob("*.srt"))


def run_whisper(video: Path, output_dir: Path, language: str | None) -> list[str]:
    ensure_binary("whisper")
    cmd = ["whisper", str(video), "--output_dir", str(output_dir), "--output_format", "srt", "--task", "transcribe"]
    if language:
        cmd.extend(["--language", language])
    run(cmd)
    return sorted(str(path) for path in output_dir.glob("*.srt"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch YouTube subtitles or prepare a Whisper fallback")
    parser.add_argument("--url", required=True)
    parser.add_argument("--video", required=True)
    parser.add_argument("--subtitle-mode", required=True, choices=["none", "zh", "en", "bilingual"])
    parser.add_argument("--subtitle-source", required=True, choices=["youtube", "ask_if_missing", "whisper"])
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    if args.subtitle_mode == "none":
        print(json.dumps({"status": "ok", "subtitle_mode": "none", "files": []}, ensure_ascii=False, indent=2))
        return

    ensure_binary("yt-dlp")
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    subtitle_listing = list_subs(args.url)
    languages = LANGUAGE_MAP[args.subtitle_mode]
    found_on_youtube = any(lang in subtitle_listing for lang in languages)

    if found_on_youtube:
        files = download_subs(args.url, languages, output_dir)
        print(json.dumps({
            "status": "ok",
            "subtitle_source": "youtube",
            "files": files,
            "listed_subtitles": subtitle_listing.strip(),
        }, ensure_ascii=False, indent=2))
        return

    if args.subtitle_source == "ask_if_missing":
        print(json.dumps({
            "status": "needs_user_input",
            "message": "No matching YouTube subtitles were found. Ask the user whether Whisper should be used.",
            "listed_subtitles": subtitle_listing.strip(),
        }, ensure_ascii=False, indent=2))
        raise SystemExit(3)

    if args.subtitle_source == "youtube":
        print(json.dumps({
            "status": "error",
            "message": "No matching YouTube subtitles were found and Whisper was not allowed.",
            "listed_subtitles": subtitle_listing.strip(),
        }, ensure_ascii=False, indent=2))
        raise SystemExit(1)

    video_path = Path(args.video).expanduser().resolve()
    language = "zh" if args.subtitle_mode == "zh" else "en"
    files = run_whisper(video_path, output_dir, language if args.subtitle_mode != "bilingual" else None)
    print(json.dumps({
        "status": "ok",
        "subtitle_source": "whisper",
        "files": files,
        "listed_subtitles": subtitle_listing.strip(),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
