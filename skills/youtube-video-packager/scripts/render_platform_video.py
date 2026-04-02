#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


FFMPEG_CANDIDATES = [
    "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg",
    "ffmpeg",
]
FFPROBE_CANDIDATES = [
    "/opt/homebrew/bin/ffprobe",
    "ffprobe",
]
PRESETS = {
    "original": {"size": None},
    "xiaohongshu-3x4": {"size": "1080x1440"},
    "vertical-9x16": {"size": "1080x1920"},
}


def pick_binary(candidates: list[str]) -> str:
    for candidate in candidates:
        if candidate.startswith("/"):
            if Path(candidate).exists():
                return candidate
        elif shutil.which(candidate):
            return candidate
    raise SystemExit(json.dumps({"status": "error", "message": f"Missing binary: {candidates[-1]}"}, ensure_ascii=False))


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, text=True, capture_output=True)


def probe_duration(video: Path, ffprobe_bin: str) -> float:
    result = subprocess.run(
        [ffprobe_bin, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(video)],
        check=True,
        text=True,
        capture_output=True,
    )
    return float(result.stdout.strip())


def build_filter(video: Path, subtitle_ass: Path, preset: str, background: str, duration: float) -> tuple[list[str], str]:
    if preset == "original":
        vf = f"ass={subtitle_ass}"
        return ["-i", str(video), "-vf", vf], video.stem + ".burned.mp4"

    size = PRESETS[preset]["size"]
    canvas_w, canvas_h = size.split("x")
    if background == "blur":
        filter_complex = (
            f"[1:v]scale={canvas_w}:{canvas_h}:force_original_aspect_ratio=increase,crop={canvas_w}:{canvas_h},boxblur=20[bg];"
            f"[1:v]scale={canvas_w}:-2[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2,ass='{subtitle_ass}'[v]"
        )
    else:
        filter_complex = (
            f"[1:v]scale={canvas_w}:-2[fg];"
            f"[0:v][fg]overlay=(W-w)/2:(H-h)/2,ass='{subtitle_ass}'[v]"
        )
    prefix = ["-f", "lavfi", "-i", f"color=c=black:s={size}:d={duration:.6f}"] if background == "black" else ["-stream_loop", "-1", "-i", str(video)]
    return prefix + ["-i", str(video), "-filter_complex", filter_complex, "-map", "[v]", "-map", "1:a:0?"], f"{video.stem}.{preset}.{background}.mp4"


def resolve_output_dir(base_dir: Path, leaf: str) -> Path:
    return base_dir if base_dir.name == leaf else base_dir / leaf


def main() -> None:
    parser = argparse.ArgumentParser(description="Render platform-ready video outputs with burned subtitles")
    parser.add_argument("--video", required=True)
    parser.add_argument("--subtitle-ass", required=True)
    parser.add_argument("--render-mode", required=True, choices=["none", "burn"])
    parser.add_argument("--preset", required=True, choices=["original", "xiaohongshu-3x4", "vertical-9x16"])
    parser.add_argument("--background", default="black", choices=["black", "blur"])
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--video-slug")
    parser.add_argument("--lang-tag")
    args = parser.parse_args()

    video = Path(args.video).expanduser().resolve()
    subtitle_ass = Path(args.subtitle_ass).expanduser().resolve()
    output_dir = resolve_output_dir(Path(args.output_dir).expanduser().resolve(), "renders")
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.render_mode == "none":
        print(json.dumps({"status": "ok", "message": "Render skipped", "files": []}, ensure_ascii=False, indent=2))
        return

    ffmpeg_bin = pick_binary(FFMPEG_CANDIDATES)
    ffprobe_bin = pick_binary(FFPROBE_CANDIDATES)
    duration = probe_duration(video, ffprobe_bin)
    extra_args, filename = build_filter(video, subtitle_ass, args.preset, args.background, duration)
    if args.video_slug and args.lang_tag:
        filename = f"{args.video_slug}.{args.preset}.{args.lang_tag}.burned.mp4"
    elif args.video_slug:
        filename = f"{args.video_slug}.{args.preset}.burned.mp4"
    output_path = output_dir / filename

    cmd = [ffmpeg_bin, "-y", *extra_args, "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(output_path)]
    run(cmd)
    print(json.dumps({"status": "ok", "files": [str(output_path)]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
