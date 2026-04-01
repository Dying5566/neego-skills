# neego-skills

[中文说明](./README.zh-CN.md)

A public-ready multi-skill repository for creator and media workflows.

This repository is organized so each skill can be developed locally, copied into a Codex skills directory, and published to GitHub without changing the structure later.

## Repository layout

```text
neego-skills/
├── README.md
├── claude-code/
│   └── commands/
│       └── youtube-video-packager.md
├── skills/
│   └── youtube-video-packager/
│       ├── SKILL.md
│       ├── agents/openai.yaml
│       └── scripts/
└── templates/
    └── skill-template/
```

## Current skills

### `youtube-video-packager`

Download a YouTube video, prepare subtitles, generate a short video summary, and export platform-ready deliverables while always keeping the original video.

Capabilities:
- Download the original YouTube video with `yt-dlp`
- Fetch official or auto subtitles when available
- Stop and ask before using Whisper when subtitles are missing
- Infer simplified or traditional Chinese subtitle preference from the user's wording
- Build `srt` or `ass` subtitle assets for `zh`, `en`, and `bilingual`
- Generate a concise summary from subtitle content
- Export subtitled outputs for `original`, `xiaohongshu-3x4`, and `vertical-9x16`

## Install a skill locally

### Install into Codex from GitHub

Clone the repository and copy the skill into your Codex skills directory:

```bash
git clone https://github.com/Dying5566/neego-skills.git /tmp/neego-skills
cp -R /tmp/neego-skills/skills/youtube-video-packager ~/.codex/skills/
```

Or install it with the Codex GitHub installer:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo Dying5566/neego-skills \
  --path skills/youtube-video-packager
```

Restart Codex after installation so the new skill is loaded.

### Install into Codex for local development

Copy the skill folder into your Codex skills directory:

```bash
cp -R skills/youtube-video-packager ~/.codex/skills/
```

Or symlink it during development:

```bash
ln -s "$(pwd)/skills/youtube-video-packager" ~/.codex/skills/youtube-video-packager
```

## Use With Claude Code

This repository also includes a Claude Code slash command version:

- `claude-code/commands/youtube-video-packager.md`

### Install into Claude Code from GitHub

Clone the repository and copy the command file into your Claude Code commands directory:

```bash
git clone https://github.com/Dying5566/neego-skills.git /tmp/neego-skills
mkdir -p ~/.claude/commands
cp /tmp/neego-skills/claude-code/commands/youtube-video-packager.md ~/.claude/commands/
```

### Install into Claude Code for local development

To use it in Claude Code, copy or symlink that file into:

```bash
~/.claude/commands/
```

Then invoke it with:

```text
/youtube-video-packager
```

If you prefer a symlink during development:

```bash
mkdir -p ~/.claude/commands
ln -s "$(pwd)/claude-code/commands/youtube-video-packager.md" ~/.claude/commands/youtube-video-packager.md
```

## Example workflow

1. Download the original video.
2. Check whether YouTube already provides subtitles.
3. Download subtitles or stop and ask whether Whisper should be used.
4. Compose clean subtitle assets.
5. Generate a concise summary from subtitles.
6. Export either the original layout or a platform preset with burned subtitles.

Example output layout:

```text
outputs/
└── example-video/
    ├── source/
    │   └── example-video.mp4
    ├── subtitles/
    │   ├── example-video.zh-Hans.srt
    │   └── example-video.zh-Hans.xiaohongshu-3x4.ass
    ├── renders/
    │   └── example-video.xiaohongshu-3x4.zh-Hans.burned.mp4
    └── summary/
        └── example-video.summary.md
```

Example commands:

```bash
python3 skills/youtube-video-packager/scripts/download_youtube.py \
  --url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --output-dir ./outputs/example-video/source \
  --video-slug example-video

python3 skills/youtube-video-packager/scripts/fetch_or_prepare_subtitles.py \
  --url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --video ./outputs/example-video/source/example-video.mp4 \
  --subtitle-mode zh \
  --subtitle-source ask_if_missing \
  --script-preference zh-Hans \
  --output-dir ./outputs/example-video/subtitles \
  --video-slug example-video

python3 skills/youtube-video-packager/scripts/compose_subtitles.py \
  --subtitle-mode zh \
  --zh-srt ./outputs/example-video/subtitles/example-video.zh-Hans.srt \
  --output-dir ./outputs/example-video/subtitles \
  --video-slug example-video \
  --lang-tag zh-Hans \
  --preset xiaohongshu-3x4 \
  --emit-ass

python3 skills/youtube-video-packager/scripts/summarize_from_subtitles.py \
  --subtitle ./outputs/example-video/subtitles/example-video.zh-Hans.clean.srt \
  --output-dir ./outputs/example-video/summary \
  --video-slug example-video

python3 skills/youtube-video-packager/scripts/render_platform_video.py \
  --video ./outputs/example-video/source/example-video.mp4 \
  --subtitle-ass ./outputs/example-video/subtitles/example-video.zh-Hans.xiaohongshu-3x4.ass \
  --render-mode burn \
  --preset xiaohongshu-3x4 \
  --background black \
  --lang-tag zh-Hans \
  --output-dir ./outputs/example-video/renders \
  --video-slug example-video
```

Default behavior note:
- If the user says “配上中文字幕”, the skill should treat that as a request for a final burned-subtitle video by default.
- If the user only wants subtitle files, they should say so explicitly.

## Example requests

These are example prompts this skill is designed to handle well:

### 1. Download only

```text
YouTube Video Packager, download this video:
https://www.youtube.com/watch?v=VIDEO_ID
Keep the original video only.
```

Expected outputs:
- `source/<video_slug>.mp4`

### 2. Download and add simplified Chinese subtitles

```text
YouTube Video Packager, help me download this video and add simplified Chinese subtitles:
https://www.youtube.com/watch?v=VIDEO_ID
Keep the original video and also give me the final subtitled video.
```

Expected outputs:
- original video in `source/`
- Chinese subtitle files in `subtitles/`
- burned Chinese video in `renders/`
- summary file in `summary/`

### 3. Subtitle files only

```text
YouTube Video Packager, download this video:
https://www.youtube.com/watch?v=VIDEO_ID
I only want the English and Chinese subtitle files. Do not burn subtitles into the video.
```

Expected outputs:
- original video in `source/`
- English and Chinese subtitle files in `subtitles/`
- summary file in `summary/`

### 4. Traditional Chinese request

```text
YouTube Video Packager，幫我下載這支影片，並配上繁體中文字幕：
https://www.youtube.com/watch?v=VIDEO_ID
保留原影片，也輸出最終帶字幕影片。
```

Expected behavior:
- prefer `zh-Hant`
- keep the original video
- output the burned traditional Chinese version

### 5. Xiaohongshu export

```text
YouTube Video Packager, download this video, add Chinese subtitles, and export a Xiaohongshu 3:4 version:
https://www.youtube.com/watch?v=VIDEO_ID
```

Expected outputs:
- `source/<video_slug>.mp4`
- `subtitles/<video_slug>.<lang>.srt`
- `subtitles/<video_slug>.<lang>.xiaohongshu-3x4.ass`
- `renders/<video_slug>.xiaohongshu-3x4.<lang>.burned.mp4`
- `summary/<video_slug>.summary.md`

## Adding a new skill

Use `templates/skill-template/` as the starting point for the next skill. Keep each skill self-contained and prefer this shape:

- `SKILL.md` for workflow instructions
- `agents/openai.yaml` for UI metadata
- `scripts/` for deterministic helpers

## Notes

This repository intentionally starts simple:
- No CI yet
- No release automation yet
- No license chosen yet

The first goal is a clean public structure plus one fully documented, reusable skill.
