# neego-skills

一个面向公开发布的多 skill 仓库，聚焦创作者和自媒体工作流。

这个仓库的结构设计目标是：
- 本地可以直接开发和测试
- 可以方便复制到 Codex skills 目录
- 后续公开到 GitHub 时不需要再重构目录

## 仓库结构

```text
neego-skills/
├── README.md
├── README.zh-CN.md
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

## 当前 skill

### `youtube-video-packager`

这个 skill 用来完成一整套 YouTube 视频打包流程：
- 下载原始 YouTube 视频
- 获取或生成字幕
- 输出带字幕的视频成品
- 同时始终保留原视频

当前支持的能力包括：
- 使用 `yt-dlp` 下载原视频
- 优先抓取 YouTube 官方字幕或自动字幕
- 字幕缺失时，先停下来询问是否启用 Whisper
- 根据用户提问习惯优先选择简体或繁体中文字幕
- 输出 `srt` / `ass` 字幕文件
- 输出 `original`、`xiaohongshu-3x4`、`vertical-9x16` 三种成片预设

## 本地安装到 Codex

### 从 GitHub 安装到 Codex

先克隆仓库，再把 skill 复制到 Codex 的 skills 目录：

```bash
git clone https://github.com/Dying5566/neego-skills.git /tmp/neego-skills
cp -R /tmp/neego-skills/skills/youtube-video-packager ~/.codex/skills/
```

或者直接使用 Codex 自带的 GitHub 安装脚本：

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo Dying5566/neego-skills \
  --path skills/youtube-video-packager
```

安装完成后，重启 Codex，让新 skill 被正确加载。

### 本地开发方式安装到 Codex

直接复制：

```bash
cp -R skills/youtube-video-packager ~/.codex/skills/
```

或者开发时用软链接：

```bash
ln -s "$(pwd)/skills/youtube-video-packager" ~/.codex/skills/youtube-video-packager
```

## 给 Claude Code 使用

这个仓库现在也附带了一个 Claude Code 的 slash command 版本：

- `claude-code/commands/youtube-video-packager.md`

### 从 GitHub 安装到 Claude Code

先克隆仓库，再把命令文件复制到 Claude Code 的 commands 目录：

```bash
git clone https://github.com/Dying5566/neego-skills.git /tmp/neego-skills
mkdir -p ~/.claude/commands
cp /tmp/neego-skills/claude-code/commands/youtube-video-packager.md ~/.claude/commands/
```

### 本地开发方式安装到 Claude Code

要在 Claude Code 里使用，可以把它复制或软链接到：

```bash
~/.claude/commands/
```

然后通过下面这种方式调用：

```text
/youtube-video-packager
```

如果你想在开发时保持仓库修改自动生效，也可以用软链接：

```bash
mkdir -p ~/.claude/commands
ln -s "$(pwd)/claude-code/commands/youtube-video-packager.md" ~/.claude/commands/youtube-video-packager.md
```

## 工作流示例

1. 先下载原视频
2. 检查 YouTube 是否已有可用字幕
3. 下载字幕，或者在缺字幕时询问是否启用 Whisper
4. 生成清洗后的字幕资产
5. 导出原始版或平台成片版

## 输出目录约定

每个视频都会生成一个独立主目录：

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
```

目录职责固定如下：
- `source/`：原视频
- `subtitles/`：字幕文件
- `renders/`：烧录版或平台成片

## 示例命令

### 1. 只下载原视频

```bash
python3 skills/youtube-video-packager/scripts/download_youtube.py \
  --url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --output-dir ./outputs/example-video/source \
  --video-slug example-video
```

### 2. 下载并获取中文字幕

```bash
python3 skills/youtube-video-packager/scripts/fetch_or_prepare_subtitles.py \
  --url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --video ./outputs/example-video/source/example-video.mp4 \
  --subtitle-mode zh \
  --subtitle-source ask_if_missing \
  --script-preference zh-Hans \
  --output-dir ./outputs/example-video/subtitles \
  --video-slug example-video
```

### 3. 生成可烧录字幕

```bash
python3 skills/youtube-video-packager/scripts/compose_subtitles.py \
  --subtitle-mode zh \
  --zh-srt ./outputs/example-video/subtitles/example-video.zh-Hans.srt \
  --output-dir ./outputs/example-video/subtitles \
  --video-slug example-video \
  --lang-tag zh-Hans \
  --preset xiaohongshu-3x4 \
  --emit-ass
```

### 4. 导出带字幕的小红书版本

```bash
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

## 示例提问

### 示例 1：只下载视频

```text
YouTube Video Packager 帮我下载这个视频：
https://www.youtube.com/watch?v=VIDEO_ID
只保留原视频。
```

### 示例 2：下载并配上简体中文字幕

```text
YouTube Video Packager 帮我下载这个视频：
https://www.youtube.com/watch?v=VIDEO_ID
并配上中文字幕，保留原视频，也给我最终带字幕的视频。
```

默认会输出：
- 原视频
- 中文字幕文件
- 烧录字幕版视频

### 示例 3：只要字幕文件

```text
YouTube Video Packager 帮我下载这个视频：
https://www.youtube.com/watch?v=VIDEO_ID
我只要中英文字幕文件，不要烧录进视频。
```

### 示例 4：繁体中文字幕

```text
YouTube Video Packager，幫我下載這支影片：
https://www.youtube.com/watch?v=VIDEO_ID
並配上繁體中文字幕，保留原影片，也輸出最終帶字幕影片。
```

这个请求会优先使用 `zh-Hant`。

### 示例 5：导出小红书版

```text
YouTube Video Packager 帮我下载这个视频：
https://www.youtube.com/watch?v=VIDEO_ID
并配上中文字幕，输出一个小红书 3:4 版本。
```

## 默认行为说明

- 当用户说“配上中文字幕”时，默认理解为：输出带中文字幕的最终视频
- 如果用户明确说“只要字幕文件”，才不做烧录
- 如果无法判断用户要简体还是繁体，默认使用简体中文
- 如果用户要小红书版或短视频版，但没有明确指定背景，默认使用纯黑背景
- 如果用户要小红书版或短视频版，但没有明确指定字幕字号，默认中文字幕字号使用 `50`

## 新增 skill

后续新增 skill 时，可以直接从 `templates/skill-template/` 开始。

建议每个 skill 都保持这个最小结构：
- `SKILL.md`
- `agents/openai.yaml`
- `scripts/`

## 说明

这个仓库目前保持轻量：
- 还没有 CI
- 还没有自动发布流程
- 还没有单独补 license

第一阶段目标是先把结构、文档和首个 skill 做扎实。
