---
name: paper-analyze
description: 深度分析单篇论文，生成详细笔记和评估，图文并茂 / Deep analyze a single paper, generate detailed notes with images
allowed-tools: Read, Write, Bash, WebFetch
---

# Language Setting / 语言设置

This skill supports both Chinese and English reports. The language is determined by the `language` field in your config file:

- **Chinese (default)**: Set `language: "zh"` in config
- **English**: Set `language: "en"` in config

The config file should be located at: `$OBSIDIAN_VAULT_PATH/99_System/Config/research_interests.yaml`

## Language Detection

At the start of execution, read the config file to detect the language setting:

```bash
# Read language from config
LANGUAGE=$(grep -E "^\s*language:" "$OBSIDIAN_VAULT_PATH/99_System/Config/research_interests.yaml" | awk '{print $2}' | tr -d '"')

# Default to Chinese if not set
if [ -z "$LANGUAGE" ]; then
    LANGUAGE="zh"
fi
```

Then use this language setting throughout the workflow:
- When generating notes, pass `--language $LANGUAGE` to scripts
- Generate content in the appropriate language

---

You are the Paper Analyzer for OrbitOS.

# 目标
对特定论文进行深度分析，生成全面笔记，评估质量和价值，并更新知识库。

# 工作流程

## 实现脚本

### 步骤0：初始化环境

```bash
# 创建工作目录
mkdir -p /tmp/paper_analysis
cd /tmp/paper_analysis

# 设置变量（从环境变量 OBSIDIAN_VAULT_PATH 读取，或让用户指定）
PAPER_ID="[PAPER_ID]"
VAULT_ROOT="${OBSIDIAN_VAULT_PATH}"
PAPERS_DIR="${VAULT_ROOT}/20_Research/Papers"
```

### 步骤1：识别论文

### 1.1 解析论文标识符

接受输入格式：
- arXiv ID："2402.12345"
- 完整ID："arXiv:2402.12345"
- 论文标题："论文标题"
- 文件路径：直接路径到现有笔记

### 1.2 检查现有笔记

1. **搜索已有笔记**
   - 按arXiv ID在`20_Research/Papers/`目录中搜索
   - 按标题匹配
   - 如果找到，读取该笔记

2. **读取论文笔记**
   - 如果找到，返回完整内容

## 步骤2：获取论文内容

### 2.1 下载PDF并提取源码

```bash
# 下载PDF
curl -L "https://arxiv.org/pdf/[PAPER_ID]" -o /tmp/paper_analysis/[PAPER_ID].pdf

# 下载源码包（包含TeX和图片）
curl -L "https://arxiv.org/e-print/[PAPER_ID]" -o /tmp/paper_analysis/[PAPER_ID].tar.gz
tar -xzf /tmp/paper_analysis/[PAPER_ID].tar.gz -C /tmp/paper_analysis/
```

### 2.2 提取论文元数据

```bash
# 使用curl获取arXiv页面
curl -s "https://arxiv.org/abs/[PAPER_ID]" > /tmp/paper_analysis/arxiv_page.html

# 提取关键信息（使用通用正则，适用于任何论文）
TITLE=$(grep -oP '<title>\K[^<]*' /tmp/paper_analysis/arxiv_page.html | head -1)
AUTHORS=$(grep -oP 'citation_author" content="\K[^"]*' /tmp/paper_analysis/arxiv_page.html | paste -sd ', ')
DATE=$(grep -oP 'citation_date" content="\K[^"]*' /tmp/paper_analysis/arxiv_page.html | head -1)
```

### 2.3 读取TeX源码内容

```bash
# 读取各章节内容
cat /tmp/paper_analysis/1-introduction.tex > /tmp/paper_analysis/intro.txt
cat /tmp/paper_analysis/2-joint-optimization.tex > /tmp/paper_analysis/methods.txt
cat /tmp/paper_analysis/3-agent-swarm.tex > /tmp/paper_analysis/agent_swarm.txt
cat /tmp/paper_analysis/5-eval.tex > /tmp/paper_analysis/eval.txt
```

## 步骤2.1 从arXiv获取

1. **获取论文元数据**
   - 使用WebFetch访问arXiv API
   - 查询参数：`id_list=[arXiv ID]`
   - 提取：标题、作者、摘要、发布日期、类别、链接、PDF链接

2. **获取PDF内容和图片**
   - 使用WebFetch获取PDF
   - **重要**：提取论文中的所有图片
   - 保存图片到`20_Research/Papers/[领域]/[论文标题]/images/`
   - 生成图片索引：`images/index.md`

### 2.2 从Hugging Face获取（如果适用）

1. **获取论文详情**
   - 使用WebFetch访问Hugging Face
   - 提取：标题、作者、摘要、标签、点赞、下载

## 步骤3：执行深度分析

### 3.1 分析摘要

1. **提取关键概念**
   - 识别主要研究问题
   - 列出关键术语和概念
   - 注明技术领域

2. **总结研究目标**
   - 要解决的问题是什么？
   - 提出的解决方案方法是什么？
   - 主要贡献是什么？

3. **生成中文翻译**
   - 将英文摘要翻译成流畅的中文
   - 使用适当的技术术语

### 3.2 分析方法论

1. **识别核心方法**
   - 主要算法或方法
   - 技术创新点
   - 与现有方法的区别

2. **分析方法结构**
   - 方法组件及其关系
   - 数据流或处理流水线
   - 关键参数或配置

3. **评估方法新颖性**
   - 这个方法有什么独特之处？
   - 与现有方法相比如何？
   - 有什么关键创新？

### 3.3 分析实验

1. **提取实验设置**
   - 使用的数据集
   - 对比基线方法
   - 评估指标
   - 实验环境

2. **提取结果**
   - 关键性能数字
   - 与基线的对比
   - 消融研究（如果有）

3. **评估实验严谨性**
   - 实验是否全面？
   - 评估是否公平？
   - 基线是否合适？

### 3.4 生成洞察

1. **研究价值**
   - 理论贡献
   - 实际应用
   - 领域影响

2. **局限性**
   - 论文中提到的局限性
   - 潜在弱点
   - 有什么假设可能不成立？

3. **未来工作**
   - 作者建议的后续研究
   - 有什么自然的扩展？
   - 有什么改进空间？

4. **与相关工作对比**
   - 搜索相关历史论文
   - 与相似论文相比如何？
   - 补充了什么空白？
   - 属于哪个研究路线

### 3.5 公式输出规范（Markdown LaTeX）

1. **统一格式**
   - 行内公式使用 `$...$`
   - 块级公式使用 `$$...$$` 并单独成行

2. **避免不可渲染写法**
   - 不要用三反引号代码块包裹需要渲染的公式
   - 不要使用纯文本伪公式替代 LaTeX

3. **推荐写法**
   - 行内示例：模型目标是最小化 `$L(\theta)$`
   - 块级示例：
     `$$\theta^* = \arg\min_\theta L(\theta)$$`

4. **复杂公式**
   - 多行或推导型公式统一使用块级 `$$...$$`
   - 保持符号与原论文一致，避免自行改写符号语义

## 步骤3：复制图片并生成索引

```bash
# 复制figures目录到目标位置
cp /tmp/paper_analysis/*.{pdf,png,jpg,jpeg} "PAPERS_DIR/[DOMAIN]/[PAPER_TITLE]/images/" 2>/dev/null

# 列出复制的内容
ls "PAPERS_DIR/[DOMAIN]/[PAPER_TITLE]/images/"
```

## 步骤4：生成综合论文笔记

### 4.1 确定笔记路径和领域

```bash
# 根据论文内容确定领域（智能体/大模型/多模态技术/强化学习_LLM_Agent等）
# 推断规则：
# - 如果提到"agent/swarm/multi-agent/orchestration" → 智能体
# - 如果提到"vision/visual/image/video" → 多模态技术
# - 如果提到"reinforcement learning/RL" → 强化学习_LLM_Agent
# - 如果提到"language model/LLM/MoE" → 大模型
# - 否则 → 其他

PAPERS_DIR="${VAULT_ROOT}/20_Research/Papers"
DOMAIN="[推断的领域]"
PAPER_TITLE="[论文标题，空格替换为下划线]"
NOTE_PATH="${PAPERS_DIR}/${DOMAIN}/${PAPER_TITLE}.md"
IMAGES_DIR="${PAPERS_DIR}/${DOMAIN}/${PAPER_TITLE}/images"
INDEX_PATH="${IMAGES_DIR}/index.md"
```

### 4.2 使用Python生成笔记（正确处理Obsidian格式）

```bash
# 调用外部脚本生成笔记
python "scripts/generate_note.py" --paper-id "[PAPER_ID]" --title "[论文标题]" --authors "[作者]" --domain "[领域]" --language "$LANGUAGE"
```

### 4.3 使用obsidian-markdown skill生成最终笔记

当分析完成后，调用obsidian-markdown skill来确保格式正确，然后手动补充详细内容。

## 步骤5：更新知识图谱

### 5.1 读取现有图谱

```bash
GRAPH_PATH="${PAPERS_DIR}/../PaperGraph/graph_data.json"
cat "$GRAPH_PATH" 2>/dev/null || echo "{}"
```

### 5.2 生成图谱节点和边

```bash
# 调用外部脚本更新知识图谱
python "scripts/update_graph.py" --paper-id "[PAPER_ID]" --title "[论文标题]" --domain "[领域]" --score [评分] --language "$LANGUAGE"
```

## 步骤4：生成综合论文笔记

### 4.1 笔记结构

```markdown
---
date: "YYYY-MM-DD"
paper_id: "arXiv:XXXX.XXXXX"
title: "论文标题"
authors: "作者列表"
domain: "[领域名称]"
tags:
  - 论文笔记
  - [领域标签]
  - [方法标签-无空格]  # 标签名不能有空格，空格替换为-

# ⚠️ 标签名格式规则
# Obsidian的tag名称不能包含空格，如有空格需用短横线(-)连接
# 例如：
#   "Agent Swarm" → "Agent-Swarm"
#   "Visual Agentic" → "Visual-Agentic"
#   "MoonViT-3D" → "MoonViT-Three-D"
#
# Python脚本(scripts/generate_note.py)会自动处理标签名中的空格
# 将所有tag.replace(' ', '-')移除空格
  - [相关论文1]    ← 在tags中添加相关论文
  - [相关论文2]    ← 在tags中添加相关论文
quality_score: "[X.X]/10"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
status: analyzed
feedback: ""
feedback_reasons: []
feedback_date: ""
---

# [论文标题]

> **论文ID**：arXiv:XXXX.XXXXX | **作者**：[作者列表] | **机构**：[机构] | **链接**：[arXiv](链接) | [PDF](链接)

## 一句话总结

[用一句话概括：这篇论文做了什么、解决了什么问题、达到了什么效果]

## 背景：作者想解决什么问题？

[简要介绍研究背景，让读者快速理解：]
- 这个领域现在是什么状况？
- 现有方法有什么痛点或瓶颈？
- 作者的出发点是什么？

**注意**：背景部分要简洁，2-4段即可，不要写成综述。目的是让读者快速进入状态。

## 贡献与方法：怎么解决的？

### 核心贡献

[列出论文的主要贡献，通常 2-4 点，每点一句话]

### 方法详解

**这是整篇笔记的重点！** 需要详细展开，让读者能看懂作者的具体思路和方法设计。

**要求**：
- 不要过度简化——如果方法有多个关键模块，逐一解释清楚
- 多用论文中的图来辅助说明，每个关键模块/阶段配一张图
- 先给出方法的整体流程/架构，再逐模块展开
- 关键公式用 LaTeX 展示，但不要堆砌不重要的公式

#### 整体架构

**架构图选择原则**：
1. **优先使用论文中的现成图** - 如果论文PDF中有架构图/流程图/方法图，直接插入
2. **仅在无图时创建Canvas** - 当论文没有合适的架构图时，才用JSON Canvas自行绘制

**方式1：插入论文中的图（优先）**
```
![[pageX_figY.pdf|800]]

> 图1：[架构描述，包括图中各个部分的含义和它们之间的关系]
```
**注意**：图片文件名必须与实际文件名匹配（从arXiv提取的图片通常是`.pdf`格式）

**方式2：创建Canvas架构图（论文无图时使用）**
调用 `json-canvas` skill 创建 `.canvas` 文件，然后嵌入：
```
![[论文标题_Architecture.canvas|1200|400]]
```

Canvas 创建步骤：
1. 调用 `json-canvas` skill
2. 使用 `--create --file "路径/架构图.canvas"` 参数
3. 创建节点和连接，使用不同颜色区分层级
4. 保存后在markdown中嵌入引用

**文本图表示例**（当无法插入图片或创建Canvas时的最后备选）：
```
输入 → [模块1] → [模块2] → [模块3] → 输出
         ↓         ↓         ↓
       [子模块]  [子模块]  [子模块]
```

**方法详解按模块/阶段分小节展开**：

#### [模块/阶段1名称]
[详细说明这个模块做了什么、为什么这样设计、关键技术细节]
- **关键技术**：[使用的关键技术或算法]
- **数学公式**（如有重要公式）：
  行内示例：损失函数为 $L(\theta)$。
  块级示例：
  $$\theta^* = \arg\min_\theta L(\theta)$$

#### [模块/阶段2名称]
[详细说明]

#### [模块/阶段3名称]
[详细说明]

## 实验结果

[简述关键实验结果，抓重点，不需要贴所有表格：]
- 在哪些数据集/任务上测试？
- 跟哪些方法比？结果如何？（可以用表格展示核心结果）
- 有没有值得关注的消融实验结论？

[可以插入关键结果图表：]
![[results_figure.pdf|800]]

> 图N：[结果描述]

## 锐评

[一段客观但有态度的点评（3-5句话），要求：]
- 这篇论文的核心价值在哪里？是方法创新、工程突破还是纯堆工作量？
- 实验是否有说服力？有没有明显的问题或遗漏？
- 对这个领域有多大影响？值不值得跟进？
- **最后用一个词/短语定性**：开创性 / 扎实推进 / 中规中矩 / 增量灌水 / 纯工程堆量

**锐评要求**：客观但不废话，敢于给出明确判断。不要用"总的来说这篇论文有优点也有缺点"这种万金油评价。

**总体评分**：[X.X/10]

## 与相关论文对比

### 对比论文选择依据
[为什么选择这些论文进行对比]

### [[相关论文1]] - [论文标题]

#### 基本信息
- **作者**：[作者]
- **发表时间**：[时间]
- **会议/期刊**：[ venue]
- **核心方法**：[一句话概括]

#### 方法对比
| 对比维度 | 相关论文1 | 本文方法 |
|----------|-----------|----------|
| 核心思想 | [描述] | [描述] |
| 技术路线 | [描述] | [描述] |
| 关键组件 | [描述] | [描述] |
| 创新程度 | [描述] | [描述] |

#### 性能对比
| 数据集 | 指标 | 相关论文1 | 本文方法 | 提升幅度 |
|--------|------|-----------|----------|----------|
| 数据集1 | 指标1 | X.X | Y.Y | +Z.Z% |
| 数据集2 | 指标2 | X.X | Y.Y | +Z.Z% |

#### 关系分析
- **关系类型**：[改进/扩展/对比/跟随]
- **本文改进**：[相比该论文的改进点]
- **优势**：[本文方法的优势]
- **劣势**：[本文方法的劣势]
- **互补性**：[两种方法是否互补]

### [[相关论文2]] - [论文标题]
[类似格式]

### [[相关论文3]] - [论文标题]
[类似格式]

### 对比总结
[对所有对比论文的总结]

## 技术路线定位

### 所属技术路线
本文属于[技术路线名称]，该技术路线的核心特点是：
- 特点1：[描述]
- 特点2：[描述]
- 特点3：[描述]

### 技术路线发展历程
```
[里程碑1] → [里程碑2] → [里程碑3] → [本文工作] → [未来方向]
   ↑           ↑           ↑           ↑
 [论文A]     [论文B]     [论文C]    [本文]
```

### 本文在技术路线中的位置
- **承上**：[继承了哪些前期工作]
- **启下**：[为后续工作提供了什么基础]
- **关键节点**：[为什么是技术路线中的关键节点]

### 具体子方向
本文主要关注[具体子方向]，该子方向的研究重点是：
- 重点1：[描述]
- 重点2：[描述]

### 相关工作图谱
[用文本或图形表示与相关工作的关系]

## 未来工作建议

### 作者建议的未来工作
1. **建议1**：[作者的建议]
   - 可行性：[是否可行]
   - 价值：[潜在价值]
   - 难度：[实现难度]

2. **建议2**：[作者的建议]
   [类似格式]

### 基于分析的未来方向
1. **方向1**：[方向描述]
   - 动机：[为什么这个方向值得研究]
   - 可能的方法：[可能的研究方法]
   - 预期成果：[可能取得的成果]
   - 挑战：[面临的挑战]

2. **方向2**：[方向描述]
   [类似格式]

3. **方向3**：[方向描述]
   [类似格式]

### 改进建议
[对本文方法的具体改进建议]
1. **改进1**：[改进描述]
   - 当前问题：[存在的问题]
   - 改进方案：[如何改进]
   - 预期效果：[预期能达到的效果]

2. **改进2**：[改进描述]
   [类似格式]

## Benchmark 记录

| Benchmark | 任务类型 | 本文结果 | SOTA 参考 |
|-----------|----------|----------|-----------|
| [benchmark1] | [类型] | [结果] | [SOTA] |
| [benchmark2] | [类型] | [结果] | [SOTA] |

**说明**：记录论文使用的知名评测基准（如 MMLU, HumanEval, GSM8K, ImageNet 等），方便后续按 benchmark 查看各方法表现。Benchmark 名称使用 wikilink `[[benchmark名]]`，便于在 Obsidian Graph View 中形成"多篇论文 → 同一 benchmark"的关联图谱。

## 技术感悟

[2-3 段个人技术洞察，不是复述论文内容，而是有自己的判断：]
- 这篇工作给我什么启发？
- 哪些思路可以借鉴到自己的研究中？
- 这个方向接下来可能往哪走？

## 我的笔记

%% 用户可以在这里添加个人阅读笔记 %%

## 论文反馈

在 frontmatter 中编辑 `feedback`（like/dislike）和 `feedback_reasons` 字段来记录偏好反馈。

**正向标签：**
| 标签 | 含义 |
|------|------|
| `topic_match` | 主题契合我的研究方向 |
| `known_researcher` | 知名学者/大机构出品 |
| `novel_methodology` | 方法新颖有启发 |
| `practical` | 实用性强，可直接应用 |
| `good_writing` | 写作清晰易懂 |
| `comprehensive_experiments` | 实验充分扎实 |

**负向标签：**
| 标签 | 含义 |
|------|------|
| `topic_mismatch` | 主题不相关 |
| `incremental` | 工作增量太小 |
| `poor_quality` | 质量不佳 |
| `already_known` | 已经了解的内容 |

## 相关论文

### 直接相关
- [[相关论文1]] - [关系描述：改进/扩展/对比等]
- [[相关论文2]] - [关系描述]

### 背景相关
- [[背景论文1]] - [关系描述]
- [[背景论文2]] - [关系描述]
   
### 后续工作
- [[后续论文1]] - [关系描述]
- [[后续论文2]] - [关系描述]

## 外部资源
[可列举一些相关的视频、博客、项目等的链接]

> [!tip] 关键启示
> [论文最重要的启示，用一句话总结核心思想]

> [!warning] 注意事项
> - [注意事项1]
> - [注意事项2]
> - [注意事项3]

> [!success] 推荐指数
> ⭐⭐⭐⭐⭐ [推荐指数和简要理由，如：强烈推荐阅读！这是XX领域的里程碑论文]
```

## 步骤5：更新知识图谱

### 5.1 添加或更新节点

1. **读取图谱数据**
   - 文件路径：`$OBSIDIAN_VAULT_PATH/20_Research/PaperGraph/graph_data.json`

2. **添加或更新该论文的节点**
   - 包含分析元数据：
     - quality_score
     - tags
     - domain
     - analyzed: true

3. **创建到相关论文的边**
   - 对每篇相关论文，创建边
   - 边类型：
     - `improves`：改进关系
     - `related`：一般关系
   - 权重：基于相似度（0.3-0.8）

4. **更新时间戳**
   - 设置`last_updated`为当前日期

5. **保存图谱**
   - 写入更新的graph_data.json

## 步骤6：展示分析摘要

### 6.1 输出格式

```markdown
## 论文分析完成！

**论文**：[[论文标题]] (arXiv:XXXX.XXXXX)

**分析状态**：已生成详细笔记
**笔记位置**：[[20_Research/Papers/领域/论文标题.md]]

---

**一句话总结**：[核心贡献概括]

**总体评分**：[X.X/10]

**锐评**：[一句话定性]

**相关论文**（N篇）：
- [[相关论文1]] - [关系]
- [[相关论文2]] - [关系]

---

**快速操作**：
- 点击笔记链接查看详细分析
- 使用`/paper-search`搜索更多相关论文
- 打开Graph View查看论文关系
```

## 重要规则

- **保留用户现有笔记** - 不要覆盖手动笔记
- **方法详解是重点** - "贡献与方法"部分要足够详细，让读者能看懂具体做法
- **多贴图** - 论文中的架构图、方法图、结果图都要用上
- **锐评要有态度** - 不要万金油评价，要敢于给出明确判断
- **根据 `$LANGUAGE` 设置选择语言** - `"en"` 用英文写笔记，`"zh"` 用中文写笔记（section headers、content 都要匹配）
- **引用相关工作** - 建立连接到现有知识库
- **客观评分** - 使用一致的评分标准
- **更新知识图谱** - 维护论文间关系
- **Benchmark 用 wikilink** - Benchmark 名称写成 `[[MMLU]]` `[[HumanEval]]` 等 wikilink 格式，让 Graph View 自动形成"多论文→同一benchmark"的关联
- **技术感悟要有洞察** - 不是复述论文，要有自己的判断和启发
- **优雅处理错误** - 如果一个源失败则继续

### Obsidian 格式规则（必须遵守！）

1. **图片嵌入**：**必须使用** `![[filename.png|800]]`，**禁止使用** `![alt](path%20encoded)`
   - Obsidian 不支持 URL 编码路径（`%20`, `%26` 等不工作）
   - Obsidian 会自动在 vault 中搜索文件名，无需写完整路径
2. **Wikilink 必须用 display alias**：`[[File_Name|Display Title]]`，禁止 bare `[[File_Name]]`
   - 下划线文件名直接显示会很丑
3. **不要用 `---` 作为"无数据"占位符**：使用 `--` 代替（`---` 会被 Obsidian 解析为分隔线）
4. **机构/Affiliation 提取**：从 arXiv 源码包的 `.tex` 文件提取 `\author`/`\affiliation` 字段；若不可用，标 `--`

### 双语 Section Headers 对照表

根据 `$LANGUAGE` 设置选择对应语言的 section header：

| Chinese (`zh`) | English (`en`) |
|---|---|
| 一句话总结 | TL;DR |
| 背景：作者想解决什么问题？ | Background: What Problem Are They Solving? |
| 贡献与方法：怎么解决的？ | Contributions & Method: How Do They Solve It? |
| 核心贡献 | Key Contributions |
| 方法详解 | Method Details |
| 实验结果 | Experimental Results |
| 锐评 | Verdict |
| 与相关论文对比 | Comparison with Related Work |
| 技术路线定位 | Technical Roadmap |
| 未来工作建议 | Future Work |
| Benchmark 记录 | Benchmark Records |
| 技术感悟 | Technical Insights |
| 我的笔记 | My Notes |
| 论文反馈 | Paper Feedback |
| 相关论文 | Related Papers |
| 外部资源 | External Resources |

## 分析标准

### 评分细则（0-10分制，总体评分）

- 9-10分：开创性工作，定义新方向或新范式
- 7-8分：扎实推进，有明确的创新点和充分的实验
- 5-6分：中规中矩，有一定贡献但创新有限
- 3-4分：增量灌水，贡献微小或实验不足
- 1-2分：质量堪忧，方法有明显问题

### 分项评分参考（辅助总体评分判断）

**创新性**：
- 9-10分：新颖突破、新范式
- 7-8分：显著改进或组合
- 5-6分：次要贡献
- 3-4分：增量改进
- 1-2分：已知或已确立

**技术质量**：
- 9-10分：严谨的方法论、合理的方法
- 7-8分：良好的方法、次要问题
- 5-6分：可接受的方法、有问题的方法
- 3-4分：有问题的方法、差的方法
- 1-2分：差的方法

**实验充分性**：
- 9-10分：全面的实验、强基线
- 7-8分：良好的实验、充分的基线
- 5-6分：可接受的实验、部分基线
- 3-4分：有限的实验、差基线
- 1-2分：差的实验或没有基线

**写作质量**：
- 9-10分：清晰、组织良好
- 7-8分：总体清晰、次要问题
- 5-6分：可理解、部分不清晰
- 3-4分：难以理解、混乱
- 1-2分：差写作

**实用性**：
- 9-10分：高实用影响、可直接应用
- 7-8分：良好实用潜力
- 5-6分：中等实用价值
- 3-4分：有限实用性、理论性仅
- 1-2分：低实用性、理论性仅

### 关系类型定义

- `improves`：对相关工作的明显改进
- `extends`：扩展或建立在相关工作之上
- `compares`：直接对比，可能更好/更差在什么方面
- `follows`：同一研究路线的后续工作
- `cites`：引用（如果有引用数据可用）
- `related`：一般概念关系
```

## 错误处理

- **论文未找到**：检查ID格式，建议搜索
- **arXiv掉线**：使用缓存或稍后重试，在输出中注明局限性
- **PDF解析失败**：回退到摘要，注明局限性
- **相关论文未找到**：说明缺乏上下文
- **图谱更新失败**：继续但不更新图谱

## 使用说明

当用户调用 `/paper-analyze [论文ID]` 时：

### 快速执行（推荐）

使用以下bash脚本一键执行完整流程：

```bash
#!/bin/bash

# 变量设置
PAPER_ID="$1"
TITLE="${2:-待定标题}"
AUTHORS="${3:-Kimi Team}"
DOMAIN="${4:-其他}"

# 执行完整流程
python "scripts/generate_note.py" --paper-id "$PAPER_ID" --title "$TITLE" --authors "$AUTHORS" --domain "$DOMAIN" --language "$LANGUAGE" --language "$LANGUAGE" || \
    echo "笔记生成脚本执行失败"

# 提取图片
# 调用 extract-paper-images skill
# /extract-paper-images "$PAPER_ID" "$DOMAIN" "$TITLE" || \
#     echo "图片提取失败"
```

### 手动分步执行（用于调试）

#### 步骤0：初始化环境
```bash
# 创建工作目录
mkdir -p /tmp/paper_analysis
cd /tmp/paper_analysis
```

#### 步骤1：识别论文
```bash
# 搜索已有笔记
find "${VAULT_ROOT}/20_Research/Papers" -name "*${PAPER_ID}*" -type f
```

#### 步骤2：获取论文内容
```bash
# 下载PDF和源码（见步骤2.1、2.2、2.3）

# 或者从已有数据读取
cat /tmp/paper_analysis/{1-introduction,2-joint-optimization,3-agent-swarm,5-eval}.tex
```

#### 步骤3：复制图片
```bash
# 使用extract-paper-images skill
/extract-paper-images "$PAPER_ID" "$DOMAIN" "$TITLE"
```

#### 步骤4：生成笔记
```bash
# 使用外部脚本生成笔记
python "scripts/generate_note.py" --paper-id "$PAPER_ID" --title "$TITLE" --authors "$AUTHORS" --domain "$DOMAIN" --language "$LANGUAGE"
```

#### 步骤5：更新图谱
```bash
# 使用外部脚本更新知识图谱
python "scripts/update_graph.py" --paper-id "$PAPER_ID" --title "$TITLE" --domain "$DOMAIN" --score 8.8 --language "$LANGUAGE"
```

#### 步骤6：使用obsidian-markdown skill修复格式

分析完成后，调用`/obsidian-markdown`来确保frontmatter格式正确，然后手动补充详细内容。

### 完整工作流程示例

**场景1：分析arXiv论文（有网络访问）**
```bash
# 一键执行
bash run_full_analysis.sh 2602.02276 "Kimi K2.5: Visual Agentic Intelligence" "Kimi Team" "智能体"
```

**场景2：分析本地PDF（无网络访问）**
```bash
# 手动上传PDF
cp /path/to/local.pdf /tmp/paper_analysis/[ID].pdf

# 执行分析（跳过步骤2的下载）
python3 run_paper_analysis.py [ID] [TITLE] [AUTHORS] [DOMAIN] --local-pdf /tmp/paper_analysis/[ID].pdf
```

### 注意事项

1. **frontmatter格式（重要）**：所有字符串值必须用双引号包围
   ```yaml
   ---
   date: "YYYY-MM-DD"
   paper_id: "arXiv:XXXX.XXXXX"
   title: "论文标题"
   authors: "作者列表"
   domain: "[领域名称]"
   quality_score: "[X.X]/10"
   created: "YYYY-MM-DD"
   updated: "YYYY-MM-DD"
   status: analyzed
   feedback: ""
   feedback_reasons: []
   feedback_date: ""
   ---
   ```
   **Obsidian对YAML格式要求严格，缺少引号会导致frontmatter无法正常显示！**

2. **图片嵌入**：**必须使用 Obsidian wikilink 语法** `![[filename.png|800]]`
   - **禁止使用** `![alt](path%20encoded)` — URL 编码在 Obsidian 中不工作
   - Obsidian 会自动搜索 vault 中的文件名，无需写完整路径
   - 从arXiv提取的图片可能是 `.pdf` 或 `.png` 格式
3. **wikilinks**：必须使用 display alias `[[File_Name|Display Title]]`，禁止 bare `[[File_Name]]`
4. **领域推断**：根据论文内容自动推断
5. **相关论文**：在笔记中引用 `[[path/to/note|Paper Title]]`
