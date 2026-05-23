# 问题库

按轮次组织，每题标注交互方式。`[选项]` = AskUserQuestion，`[文本]` = 纯文本追问。

---

## 第 1 轮：主题与目标

### Q1 [选项] 内容领域
```
header: "内容领域"
question: "这个视频属于哪个领域？"
options:
  - label: "技术/编程"
    description: "编程语言、框架、工具、架构等"
  - label: "AI/人工智能"
    description: "大模型、机器学习、AI 应用、提示工程等"
  - label: "商业/职场"
    description: "管理、创业、职业发展、行业分析等"
  - label: "生活/通识"
    description: "科普、效率、健康、心理、教育等"
```

### Q2 [选项] 视频目的
```
header: "视频目的"
question: "这个视频的主要目的是什么？"
options:
  - label: "科普解释"
    description: "让观众理解一个概念或现象"
  - label: "教程指南"
    description: "教观众完成一个具体操作"
  - label: "观点输出"
    description: "分享你对某个话题的看法和分析"
  - label: "产品/工具介绍"
    description: "展示某个产品或工具的用法和价值"
```

### Q3 [文本] 核心内容
> 请用 1-3 句话描述你想讲的核心内容。比如："我想讲 Claude Code 的 Agent 模式怎么用，让开发者了解它能自动完成哪些复杂任务。"

### Q4 [文本] 关键信息
> 这个视频最想让观众记住的一个关键信息是什么？（一句话）

---

## 第 2 轮：受众与调性

### Q5 [选项] 目标受众
```
header: "目标受众"
question: "你的目标观众是谁？"
options:
  - label: "零基础小白"
    description: "完全不了解这个领域，需要从头讲起"
  - label: "有一定基础"
    description: "了解基本概念，想深入学习"
  - label: "专业从业者"
    description: "行业内人士，想获取新视角或高级技巧"
  - label: "通用大众"
    description: "不限背景，追求通俗易懂"
```

### Q6 [选项] 表达风格
```
header: "表达风格"
question: "你希望视频的表达风格是？"
options:
  - label: "严谨专业"
    description: "数据驱动、逻辑清晰、用词精准"
  - label: "轻松幽默"
    description: "口语化、有梗、节奏轻快"
  - label: "故事叙事"
    description: "用案例和故事串联知识点"
  - label: "干货密集"
    description: "信息量大、节奏快、无废话"
```

### Q7 [文本] 行动号召
> 观众看完这个视频后，你最希望他们做什么？（比如：去试用某个工具 / 改变某个习惯 / 关注你的频道 / 分享给朋友）

---

## 第 3 轮：内容结构

### Q8 [选项] 组织方式
```
header: "内容结构"
question: "内容用什么方式组织最合适？"
options:
  - label: "总分总"
    description: "先抛结论，展开论述，最后总结"
  - label: "递进式"
    description: "由浅入深，层层推进"
  - label: "问题→方案"
    description: "先讲痛点，再给解决方案"
  - label: "对比分析"
    description: "A vs B，优劣对比后给建议"
```

### Q9 [选项] 是否有必含要点
```
header: "必含要点"
question: "你有没有必须在视频中覆盖的具体要点？"
options:
  - label: "有，我来列"
    description: "我有明确的要点清单"
  - label: "没有，你来规划"
    description: "根据主题自动规划内容结构"
```

### Q10 [文本] 要点清单（仅当 Q9 选"有"时）
> 请列出你认为必须覆盖的 3-5 个要点（每个要点一行）。

### Q11 [文本] 反直觉点
> 关于这个主题，有没有什么常见误区或反直觉的点想特别强调？（没有可以跳过）

---

## 第 4 轮：风格与偏好

### Q12 [选项] PPT 模板
```
header: "视觉风格"
question: "选择 PPT 视觉风格："
options:
  - label: "现代极简"
    description: "黑底 + 单色强调 + 无衬线字体，适合技术/AI/产品类"
  - label: "温暖柔和"
    description: "白底 + 柔和色块 + 衬线字体，适合人文/生活/管理类"
  - label: "赛博科技"
    description: "黑底 + 霓虹绿/离子蓝 + 光效，适合互联网/未来感主题"
```

### Q13 [选项] 口播音色
```
header: "口播音色"
question: "选择口播音色："
options:
  - label: "晓晓（温柔女声）"
    description: "zh-CN-XiaoxiaoNeural — 自然温和，适合大多数场景"
  - label: "晓伊（活力女声）"
    description: "zh-CN-XiaoyiNeural — 年轻有活力，适合轻松话题"
  - label: "云希（沉稳男声）"
    description: "zh-CN-YunxiNeural — 成熟稳重，适合专业/商业内容"
  - label: "云扬（年轻男声）"
    description: "zh-CN-YunyangNeural — 清晰有力，适合教程/科普"
```

### Q14 [选项] 语速
```
header: "语速"
question: "口播语速偏好？"
options:
  - label: "正常"
    description: "标准语速，适合大多数内容"
  - label: "稍快"
    description: "信息密集型内容，节奏紧凑"
  - label: "稍慢"
    description: "需要观众消化的复杂概念"
```

---

## 补充问题（按需使用）

以下问题在特定场景下追加，不计入 4 轮主流程：

### QA [文本] 参考视频
> 有没有你喜欢的同类视频可以参考？（给链接或描述风格即可）

### QB [文本] 禁忌内容
> 有没有什么内容是绝对不能出现的？（比如不提竞品、不用某些术语）

### QC [选项] 开头方式
```
header: "开头方式"
question: "视频开头用什么方式吸引观众？"
options:
  - label: "抛出问题"
    description: "用一个引人思考的问题开场"
  - label: "惊人事实"
    description: "用一个反直觉的数据或事实开场"
  - label: "痛点共鸣"
    description: "描述观众的痛点引发共鸣"
  - label: "直接预告"
    description: "直接告诉观众这期讲什么、能学到什么"
```
