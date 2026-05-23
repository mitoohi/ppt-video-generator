# 口播脚本与 slides.json 产出格式

## 概述

提问结束后，根据 `brief.md` 生成两个产物：
1. `script.md` — 人类可读的完整口播脚本
2. `slides.json` — 机器可读的结构化数据，驱动 PPT 渲染和 TTS 生成

## script.md 格式

```markdown
# {视频标题}

## 封面页
[口播] 大家好，今天我们来聊一个...

## 第 1 页：{小标题}
[页面文字] 要点一：xxx
[口播] 首先我们来看第一个要点...

## 第 2 页：{小标题}
[页面文字] 要点二：xxx
[口播] 接下来...

...

## 收尾页
[口播] 好了，今天的分享就到这里...
```

## slides.json 格式

```json
{
  "title": "视频标题",
  "voice": "zh-CN-XiaoxiaoNeural",
  "rate": "+0%",
  "template": "modern-minimal",
  "slides": [
    {
      "id": 1,
      "type": "cover",
      "title": "视频主标题",
      "subtitle": "副标题或一句话描述",
      "narration": "大家好，今天我们来聊一个非常有意思的话题..."
    },
    {
      "id": 2,
      "type": "section",
      "title": "第一部分标题",
      "narration": "首先我们来看第一个核心概念..."
    },
    {
      "id": 3,
      "type": "content",
      "title": "页面标题",
      "bullets": [
        "要点一：简短文字",
        "要点二：简短文字",
        "要点三：简短文字"
      ],
      "narration": "这一页我想重点讲三个方面。第一个是..."
    },
    {
      "id": 4,
      "type": "content",
      "title": "对比/表格页",
      "table": {
        "headers": ["维度", "方案A", "方案B"],
        "rows": [
          ["性能", "高", "中"],
          ["成本", "低", "高"]
        ]
      },
      "narration": "我们来对比一下这两个方案..."
    },
    {
      "id": 5,
      "type": "quote",
      "text": "一句金句或核心观点",
      "source": "来源（可选）",
      "narration": "有一句话我特别想分享给大家..."
    },
    {
      "id": 6,
      "type": "ending",
      "title": "感谢观看",
      "bullets": [
        "关注频道获取更多内容",
        "评论区留下你的想法"
      ],
      "narration": "好了，今天的分享就到这里。如果觉得有帮助..."
    }
  ]
}
```

## 页类型说明

| type | 用途 | 必填字段 | 可选字段 |
|---|---|---|---|
| `cover` | 封面 | title, narration | subtitle |
| `section` | 章节分隔 | title, narration | — |
| `content` | 正文（要点） | title, narration | bullets, table, image_prompt |
| `quote` | 金句/强调 | text, narration | source |
| `ending` | 收尾 | title, narration | bullets |

## 写作规范

### 页面文字（bullets / title）
- 每条 ≤ 15 字，最多 4 条
- 用关键词而非完整句子
- 不要把口播内容搬到页面上

### 口播文字（narration）
- 每页 80-150 字（对应 15-30 秒）
- 口语化，像在跟朋友聊天
- 避免书面语和长从句
- 适当加入过渡词（"那么"、"接下来"、"说到这里"）
- 总字数控制在 800-1500 字（对应 3-5 分钟）

### 页数控制
- 封面 1 页 + 正文 6-9 页 + 收尾 1 页 = 总计 8-11 页
- 章节分隔页（section）不超过 2 页

## voice 字段可选值

| ID | 描述 |
|---|---|
| `zh-CN-XiaoxiaoNeural` | 温柔女声（默认） |
| `zh-CN-XiaoyiNeural` | 活力女声 |
| `zh-CN-YunxiNeural` | 沉稳男声 |
| `zh-CN-YunyangNeural` | 年轻男声 |

## rate 字段可选值

| 值 | 含义 |
|---|---|
| `+0%` | 正常语速（默认） |
| `+15%` | 稍快 |
| `-10%` | 稍慢 |
