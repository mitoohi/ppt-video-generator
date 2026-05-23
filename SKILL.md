---
name: ppt-video-generator
description: "知识分享类口播视频自动生成。用户给出主题/方向后，通过递进式提问挖掘需求，用 HTML 模板生成 PPT，配 TTS 口播，合成 1920x1080 横屏 MP4。触发词：口播视频、知识分享视频、PPT 视频、自动剪视频、TTS 配音视频、Knowledge video。"
---

# PPT 口播视频自动生成

把"主题/创作方向"变成 1920×1080 横屏 MP4。流程固定：**问需求 → 写脚本 → 生成 PPT → 合成 TTS → 规划时间线 → 渲染视频**。

## 何时触发

用户表达以下意图之一时启动本 skill：

- "做一期 XX 主题的口播视频"
- "我想做一个讲 XX 的知识分享视频"
- "生成一个 PPT 视频"
- 给出主题/方向并提到"视频"、"口播"、"PPT 视频"

## 工作流（5 步）

```
[1] 递进式提问  ──► [2] 生成大纲+口播脚本  ──► [3] 渲染 HTML PPT
                                                       │
                                                       ▼
                                       [4] TTS 生成每页口播音频 + 词级时间戳
                                                       │
                                                       ▼
                                       [5] 规划时间线 → 生成字幕 → ffmpeg 合成 MP4
```

每一步**必须读对应子文件**，不要凭印象做。子文件按需加载，遵循 progressive disclosure：

| 步骤 | 必读文件 | 作用 |
|---|---|---|
| 1 提问 | [interview/flow.md](interview/flow.md) | 递进式提问的判定逻辑与停止条件 |
| 1 提问 | [interview/question-bank.md](interview/question-bank.md) | 4 轮、≥10 题问题库（混合选项+文本） |
| 2 脚本 | [interview/script-spec.md](interview/script-spec.md) | 口播脚本与 slides.json 的产出格式 |
| 3 PPT | [ppt/style-guide.md](ppt/style-guide.md) | 模板选型与页型规范 |
| 3 PPT | `ppt/templates/{modern-minimal,warm-soft,cyber-tech}/` | 三套现成模板 |
| 4 TTS | [tts/edge-tts.md](tts/edge-tts.md) | 默认在线 TTS（中文音色 + word_timings） |
| 4 TTS | [tts/local-models.md](tts/local-models.md) | 本地开源 TTS 备选方案 |
| 5 时间线 | [video/pipeline.md](video/pipeline.md) | plan_timeline.py → timeline.json（音画同步基准） |
| 5 合成 | [video/pipeline.md](video/pipeline.md) | make_srt.py + compose_video.py（xfade 拼接 + 烧字幕） |

## 一次性环境准备（首次使用）

提示用户跑：

```powershell
# Windows PowerShell
.\setup\setup.ps1
```

```bash
# macOS/Linux
bash ./setup/setup.sh
```

脚本会装：`ffmpeg`、`playwright`（含 chromium）、`edge-tts`、`Pillow`。详见 [setup/README.md](setup/README.md)。

## 项目级产物结构

每个视频项目放在工作目录下的 `videos/<slug>/`：

```
videos/<slug>/
├── brief.md            # 提问收集到的完整需求
├── script.md           # 人类可读的口播脚本
├── slides.json         # 结构化页数据（驱动 PPT + TTS）
├── ppt/
│   ├── slide-001.html ... slide-NNN.html
│   └── images/         # 截图产物
├── audio/
│   └── slide-001.mp3 ... slide-NNN.mp3
├── word_timings.json   # 词级时间戳（TTS 产物）
├── timeline.json       # 全局时间线（音画同步的唯一数据源）
├── subtitles.srt       # 字幕文件
└── final.mp4           # 最终视频
```

**保留所有中间产物**——用户可以在任意环节人工修改后重跑后续步骤。

## 默认值

| 项 | 默认 | 在哪改 |
|---|---|---|
| 分辨率 | 1920×1080 (16:9) | `scripts/render_slides.py` 顶部常量 |
| 时长 | 3-5 分钟，8-12 页 | 提问环节确认 |
| 模板 | 现代极简 | 提问环节让用户选 |
| 转场 | 仅页间 fade（0.6s），画面重叠消除停顿 | `scripts/compose_video.py` |
| 字幕 | 烧入硬字幕，底部居中 | `scripts/compose_video.py` |
| BGM | 无 | 用户后期自行混入 |
| TTS | edge-tts，`zh-CN-XiaoxiaoNeural` | `slides.json` 顶部 `voice` 字段 |

## 严禁事项

- **不要跳过提问环节**——直接生成会让作品质量塌方。
- **不要修改三套模板的 CSS 结构**——只填内容到模板的占位符。如要新风格，新建模板目录。
- **不要把口播脚本写到模板 HTML 里**——口播放 `slides.json` 的 `narration` 字段，给 TTS 用；HTML 上呈现的是凝练的"页内文字"。两者长度比通常 3:1（口播 3 倍于页面文字）。
- **不要在脚本中硬编码音色或语速**——必须从 `slides.json` 读，便于切换。
- **生成完毕必须给用户最终 mp4 路径**，并主动询问是否需要二次调整某一页。
