#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import math
import textwrap
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Cue:
    start: float
    end: float
    text: str


def parse_ts(value: str) -> float:
    hh, mm, rest = value.split(":")
    ss, ms = rest.split(",")
    return int(hh) * 3600 + int(mm) * 60 + int(ss) + int(ms) / 1000


def format_ts(value: float) -> str:
    total = int(round(value * 1000))
    hh, rem = divmod(total, 3600 * 1000)
    mm, rem = divmod(rem, 60 * 1000)
    ss, ms = divmod(rem, 1000)
    return f"{hh:02d}:{mm:02d}:{ss:02d},{ms:03d}"


def ass_ts(value: float) -> str:
    total = int(round(value * 100))
    hh, rem = divmod(total, 360000)
    mm, rem = divmod(rem, 6000)
    ss, cs = divmod(rem, 100)
    return f"{hh}:{mm:02d}:{ss:02d}.{cs:02d}"


def clean_text(value: str) -> str:
    return " ".join(value.split()).strip()


def parse_srt(path: Path) -> list[Cue]:
    content = path.read_text(encoding="utf-8").strip()
    cues: list[Cue] = []
    if not content:
        return cues
    for block in content.split("\n\n"):
        lines = [line.rstrip() for line in block.splitlines()]
        if len(lines) < 2:
            continue
        ts_line = lines[1].strip()
        if " --> " not in ts_line:
            continue
        body_lines = [line.strip() for line in lines[2:] if line.strip()]
        if not body_lines:
            continue
        start_s, end_s = ts_line.split(" --> ", 1)
        body = " ".join(body_lines)
        cues.append(Cue(parse_ts(start_s), parse_ts(end_s), body))
    return cues


def cue_key(cue: Cue) -> tuple[int, int]:
    return int(round(cue.start * 1000)), int(round(cue.end * 1000))


def wrap_en(value: str, width: int = 40) -> str:
    return "\n".join(textwrap.wrap(value, width=width, break_long_words=False)) or value


def wrap_zh(value: str, width: int = 18) -> str:
    return "\n".join(value[i:i + width] for i in range(0, len(value), width)) or value


def escape_ass(value: str) -> str:
    return value.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}")


def write_srt(cues: list[Cue], target: Path) -> None:
    blocks = []
    for index, cue in enumerate(cues, start=1):
        blocks.append(f"{index}\n{format_ts(cue.start)} --> {format_ts(cue.end)}\n{cue.text}\n")
    target.write_text("\n".join(blocks), encoding="utf-8")


def build_bilingual_cues(en_cues: list[Cue], zh_cues: list[Cue], preset: str, group_size: int = 2) -> list[Cue]:
    zh_map = {cue_key(cue): cue for cue in zh_cues}
    total_groups = math.ceil(len(en_cues) / group_size)
    result: list[Cue] = []
    for group_index in range(total_groups):
        start_idx = group_index * group_size
        end_idx = min(start_idx + group_size, len(en_cues))
        en_group = [clean_text(cue.text) for cue in en_cues[start_idx:end_idx] if clean_text(cue.text)]
        zh_group = []
        for cue in en_cues[start_idx:end_idx]:
            match = zh_map.get(cue_key(cue))
            if match and clean_text(match.text):
                zh_group.append(clean_text(match.text))
        if not en_group and not zh_group:
            continue
        start = en_cues[start_idx].start
        end = en_cues[end_idx].start if end_idx < len(en_cues) else en_cues[end_idx - 1].end
        body = "\n".join(filter(None, [
            wrap_text("".join(zh_group), "zh", preset),
            wrap_text(" ".join(en_group), "en", preset),
        ]))
        result.append(Cue(start, end, body))
    return result


def build_ass_header(preset: str, bilingual: bool) -> str:
    if preset == "xiaohongshu-3x4":
        width, height = 1080, 1440
        if bilingual:
            styles = [
                "Style: Default,Arial Unicode MS,24,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,3,0,2,70,70,74,1",
                "Style: ZH,Arial Unicode MS,38,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,3,0,2,70,70,128,1",
                "Style: EN,Arial Unicode MS,26,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,3,0,2,70,70,74,1",
            ]
        else:
            styles = [
                "Style: Default,Arial Unicode MS,50,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,3,0,8,70,70,930,1",
            ]
    elif preset == "vertical-9x16":
        width, height = 1080, 1920
        styles = [
            "Style: Default,Arial Unicode MS,50,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,3,0,2,80,80,150,1",
            "Style: ZH,Arial Unicode MS,46,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,3,0,2,80,80,210,1",
            "Style: EN,Arial Unicode MS,30,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,3,0,2,80,80,150,1",
        ]
    else:
        width, height = 640, 360
        styles = [
            "Style: Default,Arial Unicode MS,50,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,2,0,2,20,20,40,1",
            "Style: ZH,Arial Unicode MS,20,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,2,0,2,20,20,52,1",
            "Style: EN,Arial Unicode MS,15,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,2,0,2,20,20,40,1",
        ]
    header = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {width}",
        f"PlayResY: {height}",
        "WrapStyle: 2",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        *styles,
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    return "\n".join(header) + "\n"


def write_ass(cues: list[Cue], target: Path, preset: str, bilingual: bool) -> None:
    lines = [build_ass_header(preset, bilingual)]
    for cue in cues:
        if bilingual and "\n" in cue.text:
            parts = cue.text.split("\n")
            zh_text = escape_ass(parts[0]).replace("\n", r"\N")
            en_text = escape_ass("\n".join(parts[1:])).replace("\n", r"\N")
            payload = rf"{{\rZH}}{zh_text}\N{{\rEN}}{en_text}"
        else:
            payload = escape_ass(cue.text).replace("\n", r"\N")
        lines.append(f"Dialogue: 0,{ass_ts(cue.start)},{ass_ts(cue.end)},Default,,0,0,0,,{payload}")
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def resolve_output_dir(base_dir: Path, leaf: str) -> Path:
    return base_dir if base_dir.name == leaf else base_dir / leaf


def wrap_text(value: str, language: str, preset: str) -> str:
    if language == "zh":
        widths = {
            "original": 18,
            "xiaohongshu-3x4": 16,
            "vertical-9x16": 16,
        }
        return wrap_zh(value, width=widths.get(preset, 18))
    widths = {
        "original": 40,
        "xiaohongshu-3x4": 28,
        "vertical-9x16": 26,
    }
    return wrap_en(value, width=widths.get(preset, 40))


def normalize_single_language_cues(cues: list[Cue], language: str, preset: str) -> list[Cue]:
    normalized: list[Cue] = []
    for cue in cues:
        text = clean_text(cue.text)
        if not text:
            continue
        normalized.append(Cue(cue.start, cue.end, wrap_text(text, language, preset)))
    return normalized


def main() -> None:
    parser = argparse.ArgumentParser(description="Compose standalone and styled subtitle assets")
    parser.add_argument("--subtitle-mode", required=True, choices=["zh", "en", "bilingual"])
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--video-slug")
    parser.add_argument("--lang-tag")
    parser.add_argument("--preset", default="original", choices=["original", "xiaohongshu-3x4", "vertical-9x16"])
    parser.add_argument("--emit-ass", action="store_true")
    parser.add_argument("--zh-srt")
    parser.add_argument("--en-srt")
    args = parser.parse_args()

    output_dir = resolve_output_dir(Path(args.output_dir).expanduser().resolve(), "subtitles")
    output_dir.mkdir(parents=True, exist_ok=True)
    created: list[str] = []

    if args.subtitle_mode == "zh":
        if not args.zh_srt:
            raise SystemExit("--zh-srt is required for zh mode")
        source = Path(args.zh_srt).expanduser().resolve()
        base_name = f"{args.video_slug}.{args.lang_tag}" if args.video_slug and args.lang_tag else source.stem
        srt_target = output_dir / f"{base_name}.clean.srt"
        cues = normalize_single_language_cues(parse_srt(source), "zh", args.preset)
        write_srt(cues, srt_target)
        created.append(str(srt_target))
        if args.emit_ass:
            ass_target = output_dir / f"{base_name}.{args.preset}.ass"
            write_ass(cues, ass_target, args.preset, bilingual=False)
            created.append(str(ass_target))
    elif args.subtitle_mode == "en":
        if not args.en_srt:
            raise SystemExit("--en-srt is required for en mode")
        source = Path(args.en_srt).expanduser().resolve()
        base_name = f"{args.video_slug}.{args.lang_tag}" if args.video_slug and args.lang_tag else source.stem
        srt_target = output_dir / f"{base_name}.clean.srt"
        cues = normalize_single_language_cues(parse_srt(source), "en", args.preset)
        write_srt(cues, srt_target)
        created.append(str(srt_target))
        if args.emit_ass:
            ass_target = output_dir / f"{base_name}.{args.preset}.ass"
            write_ass(cues, ass_target, args.preset, bilingual=False)
            created.append(str(ass_target))
    else:
        if not args.en_srt or not args.zh_srt:
            raise SystemExit("--en-srt and --zh-srt are required for bilingual mode")
        en_cues = parse_srt(Path(args.en_srt).expanduser().resolve())
        zh_cues = parse_srt(Path(args.zh_srt).expanduser().resolve())
        cues = build_bilingual_cues(en_cues, zh_cues, args.preset)
        base_name = f"{args.video_slug}.bilingual" if args.video_slug else "bilingual-clean"
        srt_target = output_dir / f"{base_name}.srt"
        write_srt(cues, srt_target)
        created.append(str(srt_target))
        if args.emit_ass:
            ass_target = output_dir / f"{base_name}.{args.preset}.ass"
            write_ass(cues, ass_target, args.preset, bilingual=True)
            created.append(str(ass_target))

    print(json.dumps({"status": "ok", "files": created}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
