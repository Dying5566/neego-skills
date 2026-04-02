#!/usr/bin/env python3

from __future__ import annotations

import re
from pathlib import Path


LEAF_DIRS = {
    "en": {
        "source": "source",
        "subtitles": "subtitles",
        "renders": "renders",
    },
    "zh-Hans": {
        "source": "原视频",
        "subtitles": "字幕",
        "renders": "成片",
    },
    "zh-Hant": {
        "source": "原影片",
        "subtitles": "字幕",
        "renders": "成片",
    },
}

ALL_LEAF_NAMES = {value for mapping in LEAF_DIRS.values() for value in mapping.values()}


def normalize_dir_language(value: str | None) -> str:
    if value in LEAF_DIRS:
        return value
    return "en"


def get_dir_name(leaf_key: str, dir_language: str | None) -> str:
    language = normalize_dir_language(dir_language)
    return LEAF_DIRS[language][leaf_key]


def resolve_output_dir(base_dir: Path, leaf_key: str, video_slug: str | None, dir_language: str | None) -> Path:
    target = get_dir_name(leaf_key, dir_language)
    if base_dir.name == target:
        return base_dir
    if base_dir.name in ALL_LEAF_NAMES:
        return base_dir
    if video_slug:
        if base_dir.name == video_slug:
            return base_dir / target
        return base_dir / video_slug / target
    return base_dir / target


def abbreviate_title(title: str, max_words: int = 5, max_chars: int = 24) -> str:
    normalized = re.sub(r"[^\w\u4e00-\u9fff]+", " ", title, flags=re.UNICODE).strip()
    if not normalized:
        return "video"

    chinese_only = re.sub(r"\s+", "", normalized)
    if re.fullmatch(r"[\u4e00-\u9fff]+", chinese_only):
        return chinese_only[:12] or "视频"

    tokens = [token for token in normalized.split() if token]
    if not tokens:
        return "video"

    chosen: list[str] = []
    for token in tokens:
        if chosen and len(chosen) >= 3 and (token.isdigit() or re.fullmatch(r"\d{4}", token)):
            continue
        candidate = "-".join(chosen + [token])
        if chosen and len(candidate) > max_chars:
            break
        chosen.append(token)
        if len(chosen) >= max_words:
            break

    if not chosen:
        chosen = [tokens[0]]

    slug = "-".join(chosen)
    slug = re.sub(r"-{2,}", "-", slug).strip("-_")
    return slug[:max_chars].rstrip("-_") or "video"
