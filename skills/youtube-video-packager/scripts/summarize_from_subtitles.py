#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_srt_text(path: Path) -> str:
    blocks = []
    for block in path.read_text(encoding="utf-8").strip().split("\n\n"):
        lines = block.splitlines()
        if len(lines) < 3:
            continue
        body = " ".join(line.strip() for line in lines[2:] if line.strip())
        if body:
            blocks.append(body)
    return "\n".join(blocks)


def split_sentences(text: str) -> list[str]:
    normalized = text.replace("?", ".").replace("!", ".").replace("？", "。").replace("！", "。")
    parts = []
    for chunk in normalized.replace("\n", " ").split("."):
        value = " ".join(chunk.split()).strip()
        if value:
            parts.append(value)
    return parts


def summarize(text: str) -> str:
    sentences = split_sentences(text)
    if not sentences:
        topic = "未能从字幕中提取出足够内容。"
        bullets = ["字幕内容不足，暂时无法稳定总结核心要点。"]
        usage = "适合先补充更完整的字幕后再做内容判断。"
    else:
        topic = sentences[0]
        bullet_candidates = sentences[1:6] if len(sentences) > 1 else sentences[:1]
        bullets = bullet_candidates[:5]
        usage = "适合快速判断视频主题、做选题筛选或决定是否进一步剪辑。"
    lines = ["# 视频总结", "", f"## 主题", topic, "", "## 核心要点"]
    for bullet in bullets:
        lines.append(f"- {bullet}")
    lines.extend(["", "## 适合用途", usage, ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a concise summary from subtitle content")
    parser.add_argument("--subtitle", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--video-slug", required=True)
    args = parser.parse_args()

    subtitle = Path(args.subtitle).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    text = read_srt_text(subtitle)
    summary = summarize(text)
    output_path = output_dir / f"{args.video_slug}.summary.md"
    output_path.write_text(summary, encoding="utf-8")

    print(json.dumps({"status": "ok", "files": [str(output_path)]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
