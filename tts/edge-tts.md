# edge-tts 使用指南

## 概述

[edge-tts](https://github.com/rany2/edge-tts) 是微软 Edge 浏览器内置 TTS 引擎的 Python 封装，完全免费、无需 API Key、中文音色质量极高。

## 安装

```bash
pip install edge-tts
```

## 可用中文音色

| 音色 ID | 性别 | 风格 | 推荐场景 |
|---|---|---|---|
| `zh-CN-XiaoxiaoNeural` | 女 | 温柔自然 | 通用（默认） |
| `zh-CN-XiaoyiNeural` | 女 | 年轻活力 | 轻松话题 |
| `zh-CN-YunxiNeural` | 男 | 沉稳成熟 | 专业/商业 |
| `zh-CN-YunyangNeural` | 男 | 清晰有力 | 教程/科普 |
| `zh-CN-YunjianNeural` | 男 | 浑厚大气 | 纪录片风格 |
| `zh-CN-XiaochenNeural` | 女 | 知性优雅 | 文化/人文 |

## 基本用法

### 命令行

```bash
# 生成单条音频
edge-tts --voice zh-CN-XiaoxiaoNeural --rate "+0%" --text "大家好" --write-media output.mp3

# 列出所有可用音色
edge-tts --list-voices
```

### Python API

```python
import asyncio
import edge_tts

async def generate_audio(text: str, output_path: str, voice: str, rate: str):
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output_path)

asyncio.run(generate_audio(
    text="大家好，今天我们来聊一个有意思的话题",
    output_path="slide-001.mp3",
    voice="zh-CN-XiaoxiaoNeural",
    rate="+0%"
))
```

### 获取字幕时间码

edge-tts 支持 word-level 时间戳，可用于精确字幕：

```python
import asyncio
import edge_tts

async def generate_with_subtitles(text: str, audio_path: str, srt_path: str, voice: str, rate: str):
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    submaker = edge_tts.SubMaker()
    
    with open(audio_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.create_sub(
                    (chunk["offset"], chunk["duration"]),
                    chunk["text"]
                )
    
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(submaker.generate_subs())

asyncio.run(generate_with_subtitles(
    text="大家好，今天我们来聊一个有意思的话题",
    audio_path="slide-001.mp3",
    srt_path="slide-001.srt",
    voice="zh-CN-XiaoxiaoNeural",
    rate="+0%"
))
```

## rate 参数

| 值 | 效果 |
|---|---|
| `+0%` | 正常语速 |
| `+15%` | 稍快（干货密集型） |
| `+25%` | 快速 |
| `-10%` | 稍慢（复杂概念） |
| `-20%` | 慢速 |

## 注意事项

- 需要联网（调用微软在线服务）
- 单次请求文本长度无硬性限制，但建议每页单独生成（便于对齐时间）
- 生成速度约 1-3 秒/页（取决于网络）
- 输出格式为 mp3（也可输出 webm）
- 如果网络不稳定，脚本内置重试机制（3 次）

## 切换到本地方案

如果需要离线使用或更高质量的音色克隆，参见 [local-models.md](local-models.md)。
