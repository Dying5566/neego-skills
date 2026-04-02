---
description: Download a YouTube video, prepare subtitles, and export a subtitled deliverable.
---

Use the `youtube-video-packager` workflow for YouTube packaging requests.

## What This Command Does

1. Download the original YouTube video first.
2. Resolve subtitle requirements from the user's request.
3. Fetch YouTube subtitles when available.
4. If subtitles are missing, ask whether Whisper should be used unless the user already requested Whisper.
5. Compose subtitle assets for standalone delivery and burned rendering.
6. Export a burned subtitle video when the user asks to “配上中文字幕” unless they explicitly say they only want subtitle files.

## Default Rules

- Preserve the original video.
- If the user asks for Chinese subtitles:
  - simplified Chinese wording -> prefer `zh-Hans`
  - traditional Chinese wording -> prefer `zh-Hant`
  - unclear wording -> default `zh-Hans`
- If the user says “配上中文字幕”, treat it as a request for a final burned subtitle video by default.
- If the user explicitly says they only want subtitle files, skip the burned video.
- If the user asks for a Xiaohongshu version or a short-video version and does not specify background, default to pure black background.
- For Xiaohongshu or short-video single-language Chinese subtitle outputs, default Chinese subtitle size is `50`.

## Output Structure

Create one root directory per video slug:

- `<output_root>/<video_slug>/source/`
- `<output_root>/<video_slug>/subtitles/`
- `<output_root>/<video_slug>/renders/`

Use these file types:

- `source/<video_slug>.mp4`
- `subtitles/<video_slug>.<lang>.srt`
- `subtitles/<video_slug>.<lang>.<preset>.ass`
- `renders/<video_slug>.<preset>.<lang>.burned.mp4`

## Script Order

Run the scripts in this order from the repository root when needed:

1. `python3 skills/youtube-video-packager/scripts/download_youtube.py`
2. `python3 skills/youtube-video-packager/scripts/fetch_or_prepare_subtitles.py`
3. `python3 skills/youtube-video-packager/scripts/compose_subtitles.py`
4. `python3 skills/youtube-video-packager/scripts/render_platform_video.py`

## Required Response Format

Always report:

- whether the video download succeeded
- which subtitle language and script were used
- the absolute path to the original video
- the absolute path to subtitle files
- the absolute path to the burned render, if created
- if YouTube official or auto subtitles were used, add one short sentence about what the video is mainly about

## Example Requests

```text
/youtube-video-packager 帮我下载视频：https://www.youtube.com/watch?v=VIDEO_ID，并配上中文字幕
```

```text
/youtube-video-packager 幫我下載這支影片，並配上繁體中文字幕，保留原影片，也輸出最終帶字幕影片
```

```text
/youtube-video-packager Download this YouTube video, keep the original file, and only give me English subtitle files
```
