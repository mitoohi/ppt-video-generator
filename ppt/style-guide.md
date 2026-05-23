# PPT 视觉规范

## 通用规范（所有模板共享）

### 画布
- 分辨率：1920 × 1080 px
- 安全区：四周留 80px padding
- 字体渲染：-webkit-font-smoothing: antialiased

### 页型与布局

| 页型 | 用途 | 布局特征 |
|---|---|---|
| `cover` | 封面 | 主标题居中偏上，副标题居中偏下 |
| `section` | 章节分隔 | 大号标题垂直居中 |
| `content` | 正文 | 左侧标题 + 右侧/下方要点列表 |
| `quote` | 金句 | 引号装饰 + 大号文字居中 |
| `ending` | 收尾 | 感谢语 + CTA 列表居中 |

### 字号规范

| 元素 | 字号 | 字重 |
|---|---|---|
| 封面主标题 | 72px | Bold |
| 封面副标题 | 36px | Regular |
| 章节标题 | 64px | Bold |
| 页面标题 | 48px | Bold |
| 正文要点 | 36px | Regular |
| 金句文字 | 44px | Medium |
| 表格文字 | 28px | Regular |

### 字幕安全区

视频底部 120px 高度为字幕区域，**正文内容不得侵入此区域**。

---

## 三套模板

### 1. modern-minimal（现代极简）

**色板**
| 角色 | 色值 |
|---|---|
| 背景 | `#0D0D0D` |
| 主文字 | `#FFFFFF` |
| 强调色 | `#3B82F6`（蓝） |
| 次要文字 | `#9CA3AF` |
| 分隔线 | `#1F2937` |

**字体**：`Inter`, `Noto Sans SC`, sans-serif

**特征**：
- 大量留白，信息密度低
- 要点前用蓝色圆点标记
- 封面用细线框装饰
- 无渐变、无阴影

**适合**：技术、AI、产品、编程

---

### 2. warm-soft（温暖柔和）

**色板**
| 角色 | 色值 |
|---|---|
| 背景 | `#FFFBF5` |
| 主文字 | `#1F1F1F` |
| 强调色 | `#E07A5F`（暖橙） |
| 次要文字 | `#6B7280` |
| 装饰色 | `#F2CC8F`（暖黄） |

**字体**：`Noto Serif SC`, `Georgia`, serif（标题）；`Noto Sans SC`, sans-serif（正文）

**特征**：
- 圆角色块背景
- 标题下方有暖色装饰线
- 要点前用暖橙色方块标记
- 整体柔和、有呼吸感

**适合**：人文、生活、管理、教育

---

### 3. cyber-tech（赛博科技）

**色板**
| 角色 | 色值 |
|---|---|
| 背景 | `#0A0A0F` |
| 主文字 | `#E0E0E0` |
| 强调色 | `#00FF88`（霓虹绿） |
| 辅助色 | `#00D4FF`（离子蓝） |
| 光效 | `rgba(0,255,136,0.1)` glow |

**字体**：`JetBrains Mono`, `Noto Sans SC`, monospace

**特征**：
- 文字带微弱 glow 效果（text-shadow）
- 边框用 1px 霓虹绿细线
- 要点前用 `>` 或 `//` 前缀（代码感）
- 背景有极淡的网格线

**适合**：互联网、赛博朋克、未来感、黑客文化

---

## 模板文件结构

每套模板目录下包含：

```
templates/{name}/
├── cover.html       # 封面页模板
├── section.html     # 章节分隔页模板
├── content.html     # 正文页模板
├── quote.html       # 金句页模板
├── ending.html      # 收尾页模板
└── base.css         # 共享样式
```

## 模板占位符

HTML 模板使用 `{{变量名}}` 占位符，由 `render_slides.py` 替换：

| 占位符 | 来源 |
|---|---|
| `{{title}}` | slide.title |
| `{{subtitle}}` | slide.subtitle |
| `{{bullets}}` | slide.bullets → 生成 `<li>` 列表 |
| `{{text}}` | slide.text（金句） |
| `{{source}}` | slide.source |
| `{{table}}` | slide.table → 生成 `<table>` |

## 转场效果

仅页间 fade，由 ffmpeg 在合成阶段实现（`xfade=transition=fade:duration=0.4`），模板本身不含动画 CSS。
