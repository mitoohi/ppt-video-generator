# 视频合成管线

## 完整流程（5 步）

```
slides.json
    │
    ├──► [render_slides.py]  ──► ppt/images/slide-001.png ... slide-NNN.png
    │                            (Playwright 截图 1920×1080)
    │
    ├──► [tts_generate.py]   ──► audio/slide-001.mp3 ... slide-NNN.mp3
    │                            + word_timings.json (词级时间戳)
    │
    ├──► [plan_timeline.py]  ──► timeline.json  ★ 音画同步基准
    │                            读取实际 mp3 时长 + 词级时间戳
    │                            计算全局时间线（含 xfade 偏移）
    │
    ├──► [make_srt.py]       ──► subtitles.srt
    │                            从 timeline.json 读取字幕时间
    │
    └──► [compose_video.py]  ──► final.mp4
                                 从 timeline.json 读取片段时长
                                 xfade 视频过渡 + concat 音频拼接
```

**关键设计**: `timeline.json` 是音画同步的唯一数据源。`make_srt.py` 和 `compose_video.py` 都从中读取时间数据，确保字幕和画面严格对应。

## 步骤详解

### Step 1: 渲染 PPT 为 PNG

```bash
python scripts/render_slides.py videos/<slug>
```

- 读取 `slides.json`，确定模板目录
- 对每页：填充占位符 → 写入 `ppt/slide-NNN.html` → Playwright 截图为 PNG
- 输出：`ppt/images/slide-001.png` ... `slide-NNN.png`

关键参数：
- viewport: 1920×1080
- wait_until: "networkidle"（等待字体加载）
- 额外等待 500ms（确保渲染完成）

### Step 2: 生成 TTS 音频 + 词级时间戳

```bash
python scripts/tts_generate.py videos/<slug>
```

- 读取 `slides.json` 中每页的 `narration` 字段
- 调用 edge-tts 生成 mp3，同时捕获 `WordBoundary` 事件
- 输出：
  - `audio/slide-001.mp3` ... `slide-NNN.mp3`
  - `word_timings.json` — 每个词的 offset + duration（秒，精度到毫秒）

关键参数：
- voice: 从 `slides.json` 顶层 `voice` 字段读取
- rate: 从 `slides.json` 顶层 `rate` 字段读取
- 重试: 失败自动重试 3 次

### Step 3: 规划全局时间线 ★

```bash
python scripts/plan_timeline.py videos/<slug>
```

- 用 ffprobe 读取每个 mp3 的实际时长（精确到毫秒）
- 将词级时间戳按标点分组为字幕段（≤24 字/段）
- 计算全局时间线：
  - 字幕时间 = 累计音频偏移 + 词偏移（不受 xfade 影响）
  - 片段时长 = 实际 mp3 时长
- 输出：`timeline.json`

```json
{
  "meta": {
    "fade_duration": 0.6,
    "total_audio_duration": 185.3,
    "total_video_duration": 179.9,
    "segment_count": 10,
    "subtitle_count": 52
  },
  "segments": [
    {
      "slide_id": 1,
      "image": "ppt/images/slide-001.png",
      "audio": "audio/slide-001.mp3",
      "narration": "大家好，今天...",
      "audio_duration": 18.5,
      "audio_start": 0.0,
      "audio_end": 18.5
    }
  ],
  "subtitles": [
    {"index": 1, "text": "大家好", "start": 0.0, "end": 0.85, "belongs_to_slide": 1},
    {"index": 2, "text": "今天我们聊一个", "start": 0.85, "end": 2.3, "belongs_to_slide": 1}
  ]
}
```

### Step 4: 生成 SRT 字幕

```bash
python scripts/make_srt.py videos/<slug>
```

- 从 `timeline.json` 的 `subtitles` 字段直接生成 SRT
- 不再自行计算时长——完全信任 timeline
- 输出：`subtitles.srt`

### Step 5: 合成最终视频

```bash
python scripts/compose_video.py videos/<slug>
```

流程：
1. 按 `timeline.json` 中每个 `segment.audio_duration` 生成片段视频（图片 + 音频）
2. xfade 拼接视频轨道（fade 0.6s 重叠），音频直接 concat 拼接
3. `tpad` 补帧对齐音视频总时长
4. 烧入 SRT 字幕 → 输出 `final.mp4`

## ffmpeg 关键命令

### xfade 视频拼接 + concat 音频拼接

```bash
ffmpeg -y \
  -i seg-001.mp4 -i seg-002.mp4 ... -i seg-NNN.mp4 \
  -filter_complex "
    [0:v][1:v]xfade=transition=fade:duration=0.6:offset=17.9[v1];
    [v1][2:v]xfade=transition=fade:duration=0.6:offset=39.3[v2];
    ...
    [vN-1]tpad=stop_mode=clone:stop_duration=5.4[outv];
    [0:a][1:a]...[N:a]concat=n=N:v=0:a=1[outa]
  " \
  -map "[outv]" -map "[outa]" \
  -c:v libx264 -c:a aac -r 30 \
  no_sub.mp4
```

- 视频: xfade 逐对过渡，offset = 前面所有片段的时长和 - 已处理 transition 数 × fade时长
- 音频: 直接拼接不做淡化（口播不能有音频重叠）
- tpad: 最后补帧使总时长对齐

### 烧入字幕

```bash
ffmpeg -y \
  -i no_sub.mp4 \
  -vf "subtitles='subtitles.srt':force_style='FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H80000000,Outline=2,Alignment=2,MarginV=50'" \
  -c:a copy -c:v libx264 -r 30 \
  final.mp4
```

## 一键执行

```bash
python scripts/render_slides.py "videos/<slug>"
python scripts/tts_generate.py "videos/<slug>"
python scripts/plan_timeline.py "videos/<slug>"
python scripts/make_srt.py "videos/<slug>"
python scripts/compose_video.py "videos/<slug>"
```

## 常见问题

| 问题 | 原因 | 解决 |
|---|---|---|
| 字幕与口播不同步 | timeline.json 未重新生成 | 每次重新生成 TTS 后必须重新执行 plan_timeline.py |
| 字体显示为方块 | Playwright 缺少中文字体 | 安装 Noto Sans SC 字体到系统 |
| 音频生成超时 | 网络不稳定 | 脚本自动重试 3 次 |
| 字幕不显示 | ffmpeg 未编译 libass | 用 `winget install ffmpeg` 安装完整版 |
| 视频花屏 | 图片尺寸不一致 | 确保所有 PNG 都是 1920×1080 |
