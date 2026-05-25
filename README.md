# 口播视频自动生成 SKILL

> 一个智能口播视频生成SKILL，将任何想法创建为 **1920×1080 横屏 MP4 口播视频**，全程自动化。

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/playwright-✓-green.svg)](https://playwright.dev/)
[![Edge TTS](https://img.shields.io/badge/edge--tts-✓-green.svg)](https://github.com/rany2/edge-tts)
[![FFmpeg](https://img.shields.io/badge/ffmpeg-✓-green.svg)](https://ffmpeg.org/)

只需给出一个主题或创作方向，AI 智能体通过递进式提问挖掘需求，自动生成口播脚本、渲染精美 PPT 页面、合成 TTS 配音，最终输出一部完整的口播视频。

**完整工作流**：`问需求 → 写脚本 → 渲染 PPT → 合成 TTS → 规划时间线 → 渲染视频`

**生成样例**：![auto-video-skill-demo](auto-video-skill-demo/final.mp4)

---

## 特性

- **全自动管线** — 从主题到 MP4，5 步一键完成，中间产物全部保留，支持人工干预后重跑
- **递进式提问** — 智能体自动通过 4 轮 ≥10 题挖掘需求，避免直接生成导致质量塌方
- **三套视觉风格** — 现代极简、温暖柔和、赛博科技，满足不同内容调性
- **词级时间戳同步** — 基于 edge-tts 的 WordBoundary 事件，字幕精确到毫秒
- **xfade 平滑转场** — 页间 fade 过渡，消除停顿感
- **硬字幕烧录** — SRT 字幕直接烧入视频，播放器无关
- **保留所有中间产物** — 脚本、截图、音频、时间线均可独立修改后重跑后续步骤
- **视频多样化生成** — 同一内容可用不同风格分别生成，快速对比选优

## 快速开始

### 前置要求

- **Python ≥ 3.10**
- **FFmpeg**（需含 libx264 和 libass 支持）

### 一键安装

```powershell
# Windows PowerShell
.\setup\setup.ps1
```

```bash
# macOS / Linux
bash ./setup/setup.sh
```

安装脚本会完成：`ffmpeg`、`playwright`（含 chromium）、`edge-tts`、`Pillow`、`mutagen`。

### 使用方式

> 以claude code为例，其他智能体均可

#### 方式一：Claude Code SKILL（推荐）

将本项目配置为 [Claude Code](https://claude.ai/code) 的 SKILL，然后在对话中触发：

> 做一期讲 XXX 的口播视频
> 生成一个知识分享视频

SKILL 会自动启动完整的递进式提问 → 生成 → 合成流程。详见 [SKILL.md](SKILL.md)。

#### 方式二：手动分步执行

```bash
PROJ="videos/my-video"

# 1. 渲染 PPT 为 PNG 序列
python scripts/render_slides.py "$PROJ"

# 2. 生成每页 TTS 配音（含词级时间戳）
python scripts/tts_generate.py "$PROJ"

# 3. 规划全局时间线（音画同步基准）★
python scripts/plan_timeline.py "$PROJ"

# 4. 从时间线生成 SRT 字幕
python scripts/make_srt.py "$PROJ"

# 5. 合成最终视频（xfade 拼接 + 烧字幕）
python scripts/compose_video.py "$PROJ"
```

> **关键**：每次重新生成 TTS 后必须重新运行 `plan_timeline.py`，否则字幕和视频会不同步。

## 项目结构

```
├── SKILL.md                    # Claude Code SKILL 入口（触发条件 + 工作流）
├── interview/
│   ├── flow.md                 # 递进式提问流程（4 轮 ≥10 题）
│   ├── question-bank.md        # 问题库（选项+文本混合）
│   └── script-spec.md          # slides.json 产出格式
├── ppt/
│   ├── style-guide.md          # 视觉规范（画布、字号、色板）
│   └── templates/              # 三套现成模板
│       ├── modern-minimal/     # 现代极简（深蓝 + 几何）
│       ├── warm-soft/          # 温暖柔和（米白 + 暖橙）
│       └── cyber-tech/         # 赛博科技（黑底 + 霓虹绿）
├── tts/
│   ├── edge-tts.md             # 默认在线 TTS（中文音色 + 词级时间戳）
│   └── local-models.md         # CosyVoice2 / IndexTTS2 备选方案
├── video/
│   └── pipeline.md             # 5 步合成管线详解
├── scripts/
│   ├── render_slides.py        # Playwright 截图（5 种页型）
│   ├── tts_generate.py         # edge-tts + WordBoundary 词级时间戳
│   ├── plan_timeline.py        # ★ 生成 timeline.json（音画同步基准）
│   ├── make_srt.py             # 从 timeline.json 生成精确 SRT
│   └── compose_video.py        # xfade 拼接 + 烧字幕
├── setup/
│   ├── setup.ps1               # Windows 一键安装
│   ├── setup.sh                # macOS/Linux 一键安装
│   └── README.md               # 安装说明
└── LICENSE                     # MIT 开源协议
```

## 视频产物结构

```
videos/<slug>/
├── brief.md            # 需求简报（提问环节）
├── script.md           # 人类可读的口播脚本
├── slides.json         # 结构化数据（驱动一切）
├── ppt/
│   ├── slide-001.html ... slide-NNN.html
│   └── images/slide-001.png ... slide-NNN.png
├── audio/
│   └── slide-001.mp3 ... slide-NNN.mp3
├── word_timings.json   # 词级时间戳（TTS 产物）
├── timeline.json       # ★ 全局时间线（唯一数据源）
├── subtitles.srt       # 精确字幕
└── final.mp4           # 最终视频
```

## 配置

| 项目 | 默认值 | 修改位置 |
|---|---|---|
| 分辨率 | 1920×1080 | `render_slides.py` 顶部常量 |
| 视频时长 | 3–5 分钟，8–12 页 | 提问环节确认 |
| 模板风格 | modern-minimal | `slides.json` 顶层 `template` 字段 |
| TTS 音色 | zh-CN-XiaoxiaoNeural | `slides.json` 顶层 `voice` 字段 |
| 语速 | +0% | `slides.json` 顶层 `rate` 字段 |
| 转场 | fade 0.6s | `timeline.json` → `compose_video.py` |
| 字幕样式 | 底部居中，半透明背景 | `compose_video.py` |
| BGM | 无 | 用户后期自行混入 |

## 技术栈

| 组件 | 技术 |
|---|---|
| PPT 渲染 | HTML + CSS + `Playwright` 截图 |
| 语音合成 | `edge-tts`（在线）/ CosyVoice2、IndexTTS2（本地） |
| 时间线 | `ffprobe` + 词级时间戳分组算法 |
| 视频合成 | `ffmpeg` xfade 过渡 + concat 音频拼接 |
| 字幕 | SRT 格式，`ffmpeg subtitles` 滤镜烧入 |

## 常见问题

| 问题 | 原因 | 解决 |
|---|---|---|
| 字幕与口播不同步 | `timeline.json` 未重新生成 | 重跑 `plan_timeline.py` |
| 字体显示为方块 | Playwright 缺少中文字体 | 安装 Noto Sans SC 等中文字体 |
| 音频生成超时 | 网络不稳定 | 脚本自动重试 3 次 |
| 字幕不显示 | ffmpeg 未编译 libass | 用 `winget install ffmpeg`（Win）或 `brew install ffmpeg`（macOS）安装完整版 |
| 视频花屏 | 图片尺寸不一致 | 确保所有 PNG 均为 1920×1080 |

## 自定义

### 新增模板

1. 在 `ppt/templates/` 下创建新目录
2. 按需添加 `cover.html`、`section.html`、`content.html`、`quote.html`、`ending.html` 和 `base.css`
3. 在 `slides.json` 中将 `template` 字段设为目录名即可

详见 [style-guide.md](ppt/style-guide.md) 获取占位符规范和视觉约定。

### 使用本地 TTS

如需离线语音合成，可选用 CosyVoice2 或 IndexTTS2，详见 [local-models.md](tts/local-models.md)。

## 贡献

欢迎提交 Issue 和 Pull Request！

- 提交 Bug 或功能建议 → [New Issue](https://github.com/forward/skills/issues/new)
- 代码风格遵循 PEP 8，提交前请用 `black` 和 `ruff` 格式化
- 重大变更请先开 Issue 讨论

## 协议

[MIT](LICENSE) © 2025-present forward
