---
name: youtube-video-packager
description: Download a YouTube video, prepare subtitles, and export platform-ready video deliverables. Use this skill when the user wants a YouTube source saved locally, wants English, Chinese, or bilingual subtitles, or wants the source repackaged for presets like Xiaohongshu 3:4 or generic 9:16 while still keeping the original video.
---

# YouTube Video Packager

## Overview

Use this skill for end-to-end YouTube packaging workflows: download the original source, prepare subtitle assets, and export a burned-subtitle deliverable for a target platform. The original video must always be kept.

## Workflow Decision Tree

1. Decide what the user wants:
   - download only
   - download plus subtitle files
   - download plus subtitles plus platform-ready video
2. Download the original video first with `scripts/download_youtube.py`.
3. Resolve subtitles with `scripts/fetch_or_prepare_subtitles.py`.
   - If YouTube already has subtitles, download them.
   - If subtitles are missing and `subtitle_source=ask_if_missing`, stop and ask whether Whisper should be used.
   - If the user already requested Whisper, run it only after the original video exists locally.
4. Normalize subtitle assets with `scripts/compose_subtitles.py`.
   - `subtitle_mode=none | zh | en | bilingual`
   - prefer `srt` outputs for editing
   - generate `ass` when the next step needs burned subtitles
5. If the user asked for a platform-ready output, export it with `scripts/render_platform_video.py`.
   - `preset=original | xiaohongshu-3x4 | vertical-9x16`
   - `background=black | blur`
   - `render_mode=none | burn`
6. Return a concise summary that always includes:
   - whether the download succeeded
   - which subtitles were found or generated
   - which deliverables were created
   - the absolute path for each output file

## Interface Contract

Use these parameters consistently across the workflow:

- `url`
- `subtitle_mode`: `none | zh | en | bilingual`
- `subtitle_source`: `youtube | ask_if_missing | whisper`
- `render_mode`: `none | burn`
- `preset`: `original | xiaohongshu-3x4 | vertical-9x16`
- `background`: `black | blur`

## Output Rules

Always preserve the original downloaded video.

Typical outputs:
- original video `mp4`
- standalone subtitle `srt`
- optional styled subtitle `ass`
- burned subtitle video for the selected preset

## Scripts

### `scripts/download_youtube.py`

Downloads the original video and prints a JSON summary with the saved file path.

### `scripts/fetch_or_prepare_subtitles.py`

Fetches YouTube subtitles when available. If subtitles are missing and `subtitle_source=ask_if_missing`, it exits with a machine-readable status that indicates the workflow should pause and ask the user whether Whisper should run.

### `scripts/compose_subtitles.py`

Creates cleaned subtitle assets for `zh`, `en`, or `bilingual` outputs. Use `--emit-ass` when the next step is a burned-subtitle render.

### `scripts/render_platform_video.py`

Renders the final preset output. Use `original` when the layout should stay unchanged, `xiaohongshu-3x4` for `1080x1440`, and `vertical-9x16` for `1080x1920`.

## Important Boundaries

This skill does not:
- automatically find highlight moments
- automatically cut long videos into short clips
- change the editorial meaning of the original source

It only packages a YouTube source into subtitle and delivery assets.
