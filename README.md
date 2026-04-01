# neego-skills

A public-ready multi-skill repository for creator and media workflows.

This repository is organized so each skill can be developed locally, copied into a Codex skills directory, and published to GitHub without changing the structure later.

## Repository layout

```text
neego-skills/
├── README.md
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

Download a YouTube video, prepare subtitles, and export platform-ready deliverables while always keeping the original video.

Capabilities:
- Download the original YouTube video with `yt-dlp`
- Fetch official or auto subtitles when available
- Stop and ask before using Whisper when subtitles are missing
- Build `srt` or `ass` subtitle assets for `zh`, `en`, and `bilingual`
- Export subtitled outputs for `original`, `xiaohongshu-3x4`, and `vertical-9x16`

## Install a skill locally

Copy the skill folder into your Codex skills directory:

```bash
cp -R skills/youtube-video-packager ~/.codex/skills/
```

Or symlink it during development:

```bash
ln -s "$(pwd)/skills/youtube-video-packager" ~/.codex/skills/youtube-video-packager
```

## Example workflow

1. Download the original video.
2. Check whether YouTube already provides subtitles.
3. Download subtitles or stop and ask whether Whisper should be used.
4. Compose clean subtitle assets.
5. Export either the original layout or a platform preset with burned subtitles.

Example commands:

```bash
python3 skills/youtube-video-packager/scripts/download_youtube.py \
  --url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --output-dir ./outputs

python3 skills/youtube-video-packager/scripts/fetch_or_prepare_subtitles.py \
  --url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --video ./outputs/example.mp4 \
  --subtitle-mode zh \
  --subtitle-source ask_if_missing \
  --output-dir ./outputs

python3 skills/youtube-video-packager/scripts/compose_subtitles.py \
  --subtitle-mode zh \
  --zh-srt ./outputs/example.zh-Hans.srt \
  --output-dir ./outputs \
  --preset xiaohongshu-3x4

python3 skills/youtube-video-packager/scripts/render_platform_video.py \
  --video ./outputs/example.mp4 \
  --subtitle-ass ./outputs/example.zh-only.xiaohongshu-3x4.ass \
  --render-mode burn \
  --preset xiaohongshu-3x4 \
  --background black \
  --output-dir ./outputs
```

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
