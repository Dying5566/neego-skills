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
   - download plus subtitles and a final subtitled video
2. Download the original video first with `scripts/download_youtube.py`.
3. Resolve subtitles with `scripts/fetch_or_prepare_subtitles.py`.
   - If YouTube already has subtitles, download them.
   - If the user asks for Chinese subtitles, infer the preferred script from the wording of the request.
   - If the request uses simplified Chinese, prefer `zh-Hans`.
   - If the request uses traditional Chinese, prefer `zh-Hant`.
   - If the request does not make the script obvious, default to `zh-Hans`.
   - If subtitles are missing and `subtitle_source=ask_if_missing`, stop and ask whether Whisper should be used.
   - If the user already requested Whisper, run it only after the original video exists locally.
4. Normalize subtitle assets with `scripts/compose_subtitles.py`.
   - `subtitle_mode=none | zh | en | bilingual`
   - prefer `srt` outputs for editing
   - generate `ass` when the next step needs burned subtitles
5. If the user asked to “配上中文字幕”, treat that as a request for a final burned-subtitle video by default.
   - Preserve the original video.
   - Keep standalone subtitle files.
   - Export a burned subtitle video unless the user explicitly says they only want subtitle files.
6. If the user asked for a platform-ready output, export it with `scripts/render_platform_video.py`.
   - `preset=original | xiaohongshu-3x4 | vertical-9x16`
   - if the user asked for a Xiaohongshu version or a short-video version and did not specify a background, default to `background=black`
   - if the output is a Xiaohongshu version or short-video version and the user did not specify subtitle size, default to Chinese subtitle size `50`
   - keep burned subtitles fixed inside the visible video content area near the bottom instead of letting them float in the outer canvas
   - if the user asks for subtitles and also asks for a Xiaohongshu version or short-video version, export two burned videos by default: one `preset=original` deliverable and one platform preset deliverable
   - `render_mode=none | burn`
7. Return a concise summary that always includes:
   - whether the download succeeded
   - which subtitles were found or generated
   - whether simplified or traditional Chinese was used
   - which deliverables were created
   - the absolute path for each output file
   - if YouTube official or auto subtitles were used, add one short sentence about what the video is mainly about

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

Create one root output directory per video slug:

- `<output_root>/<video_slug>/source/`
- `<output_root>/<video_slug>/subtitles/`
- `<output_root>/<video_slug>/renders/`

If the workflow starts from a YouTube URL and no slug is provided, derive the outer folder name from an abbreviated version of the video title and use that same slug for all files under `source/`, `subtitles/`, and `renders/`.

Use these fixed output types:

- `source/<video_slug>.mp4` for the original video
- `subtitles/<video_slug>.<lang>.srt` for standalone subtitles
- `subtitles/<video_slug>.<lang>.<preset>.ass` for styled subtitles
- `renders/<video_slug>.<preset>.<lang>.burned.mp4` for burned outputs
- for Xiaohongshu or short-video exports, use black background and default Chinese subtitle size `50` unless the user explicitly overrides them

## Scripts

### `scripts/download_youtube.py`

Downloads the original video and prints a JSON summary with the saved file path.

### `scripts/fetch_or_prepare_subtitles.py`

Fetches YouTube subtitles when available. If subtitles are missing and `subtitle_source=ask_if_missing`, it exits with a machine-readable status that indicates the workflow should pause and ask the user whether Whisper should run. For Chinese subtitle requests, it accepts a preferred script hint and returns the script that was actually chosen.

### `scripts/compose_subtitles.py`

Creates cleaned subtitle assets for `zh`, `en`, or `bilingual` outputs. Use `--emit-ass` when the next step is a burned-subtitle render. Outputs must go into the fixed `subtitles/` directory.

### `scripts/render_platform_video.py`

Renders the final preset output into the fixed `renders/` directory. Use `original` when the layout should stay unchanged, `xiaohongshu-3x4` for `1080x1440`, and `vertical-9x16` for `1080x1920`.

## Important Boundaries

This skill does not:
- automatically find highlight moments
- automatically cut long videos into short clips
- change the editorial meaning of the original source

It only packages a YouTube source into subtitle and delivery assets.
