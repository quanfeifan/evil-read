# evil-read-arxiv

> 邪修的论文阅读工作流 - 自动化论文搜索、推荐、分析和整理

## 语言 / Language

- [中文版](README.md)
- [English Version](README_en.md)

## 简介

一套 Claude Code 技能（Skills）集合，自动化研究论文的搜索、推荐、分析和整理。通过 arXiv + Semantic Scholar API 每天推荐高质量论文，自动生成详细笔记，并通过反馈闭环持续优化推荐精度。

## 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-05-24 | v1.2 | 新增**反馈学习系统**：细粒度主题级反馈复选框、增量偏好收集、关键词权重自动调整 |
| 2026-03-13 | v1.1 | 新增 `conf-papers` 技能：顶会论文搜索，DBLP + Semantic Scholar 双数据源 |
| 2026-03-01 | v1.0 | 初始版本：start-my-day、paper-analyze、extract-paper-images、paper-search |

## 核心功能

### 1. start-my-day - 每日论文推荐

每天一条命令，获取个性化论文推荐：

- 搜索 arXiv 最近一个月的论文 + Semantic Scholar 过去一年的高热度论文
- 四维评分：相关性 40% + 热门度 30% + 新近性 20% + 质量 10%
- 生成今日概览 + 10 篇推荐列表
- 前 3 篇自动提取图片、生成详细分析报告
- 自动链接关键词到已有笔记

### 2. 反馈学习系统（v1.2 新增）

推荐不只是单向输出，系统会从你的反馈中学习：

**工作流程：**

```
今天：推荐 10 篇论文，每篇带细粒度主题复选框
        ↓
你在 Obsidian 中勾选感兴趣/不感兴趣 + 具体主题
        ↓
明天运行时：自动收集昨天的反馈（增量，不扫描全量历史）
        ↓
合并到累积偏好 → 调整关键词权重 → 影响今天的推荐排名
```

**细粒度主题反馈：**

每篇论文不是简单的"喜欢/不喜欢"，而是可以标记具体感兴趣的方向：

```markdown
**反馈**：
- [x] 感兴趣 ⬆️
  - [x] VLA模型           ← 勾选具体感兴趣的主题
  - [ ] 运行时验证/安全部署
  - [x] 世界模型
  - [ ] 动作质量评估
- [ ] 不感兴趣 ⬇️
  - [ ] VLA模型
  - [ ] 运行时验证/安全部署
  - [ ] 世界模型
  - [ ] 动作质量评估
```

**偏好存储：**

| 文件 | 作用 |
|------|------|
| `user_preferences_state.yaml` | 内部状态：累积的关键词正/负计数 + 已处理日期列表 |
| `user_preferences.yaml` | 给评分脚本用的：从累积计数计算出的 boosts/penalties |

两个文件都在 `$OBSIDIAN_VAULT_PATH/99_System/Config/` 下，增量更新，幂等（同一天重复运行不会重复计数）。

### 3. paper-analyze - 论文深度分析

```bash
/paper-analyze 2602.12345
```

- 生成结构化笔记：研究背景、方法架构、实验结果、价值评估、相关论文对比
- 自动提取所有论文图片并插入笔记
- 更新知识图谱

### 4. extract-paper-images - 论文图片提取

```bash
/extract-paper-images 2602.12345
```

- 优先从 arXiv 源码包提取（高质量原图）
- 回退到 PDF 提取
- 支持 TikZ/PGFplots 矢量图裁剪
- 自动过滤 logo 和小图标

### 5. paper-search - 论文笔记搜索

```bash
/paper-search "关键词"
```

在已有笔记中按标题、作者、关键词、领域搜索，相关性排序。

### 6. conf-papers - 顶会论文搜索

```bash
/conf-papers CVPR 2025
```

- 支持 CVPR/ICCV/ECCV/ICLR/AAAI/NeurIPS/ICML
- DBLP API 获取论文列表 + Semantic Scholar 补充引用和摘要
- 独立配置文件 `conf-papers.yaml`
- 三维评分：相关性 40% + 热门度 40% + 质量 20%

## 安装

### 前置要求

1. **Claude Code CLI** - 安装并配置
2. **Python 3.8+**
3. **依赖库**：
   ```bash
   pip install -r requirements.txt
   ```

### 安装步骤

1. 克隆仓库并复制技能到 Claude Code skills 目录：

   ```bash
   # macOS/Linux
   cp -r evil-read-arxiv/start-my-day ~/.claude/skills/
   cp -r evil-read-arxiv/paper-analyze ~/.claude/skills/
   cp -r evil-read-arxiv/extract-paper-images ~/.claude/skills/
   cp -r evil-read-arxiv/paper-search ~/.claude/skills/
   cp -r evil-read-arxiv/conf-papers ~/.claude/skills/

   # Windows PowerShell
   Copy-Item -Recurse evil-read-arxiv\start-my-day $env:USERPROFILE\.claude\skills\
   Copy-Item -Recurse evil-read-arxiv\paper-analyze $env:USERPROFILE\.claude\skills\
   Copy-Item -Recurse evil-read-arxiv\extract-paper-images $env:USERPROFILE\.claude\skills\
   Copy-Item -Recurse evil-read-arxiv\paper-search $env:USERPROFILE\.claude\skills\
   Copy-Item -Recurse evil-read-arxiv\conf-papers $env:USERPROFILE\.claude\skills\
   ```

2. 配置环境变量和研究兴趣（见下文"配置"部分）
3. 重启 Claude Code

## 配置

> **快速开始**：先阅读 [QUICKSTART.md](QUICKSTART.md)。

### 步骤 1：设置 Obsidian Vault 路径

```bash
# macOS/Linux（添加到 ~/.bashrc 或 ~/.zshrc）
export OBSIDIAN_VAULT_PATH="/path/to/your/obsidian/vault"

# Windows PowerShell（永久生效）
[System.Environment]::SetEnvironmentVariable("OBSIDIAN_VAULT_PATH", "C:/Users/YourName/Documents/Vault", "User")
```

### 步骤 2：创建研究兴趣配置

复制 `config.example.yaml` 并修改：

```bash
cp config.example.yaml "$OBSIDIAN_VAULT_PATH/99_System/Config/research_interests.yaml"
```

配置示例：

```yaml
language: "zh"  # 支持 "zh"（中文）或 "en"（英文）

research_domains:
  "VLA模型":
    priority: 5
    keywords:
      - "vision-language-action"
      - "VLA"
      - "robot manipulation"
    arxiv_categories:
      - "cs.RO"
      - "cs.AI"

  "世界模型":
    priority: 5
    keywords:
      - "world model"
      - "sim-to-real"
    arxiv_categories:
      - "cs.AI"
      - "cs.LG"
```

### Obsidian 目录结构

```
你的Vault/
├── Daily/                       # 每日推荐笔记
│   └── 2026-05-24论文推荐.md
├── Papers/                      # 论文详细笔记
│   ├── VLA模型/
│   │   └── Pre-VLA_.../
│   │       ├── Pre-VLA_...md    # 分析笔记
│   │       └── images/          # 论文图片
│   ├── 世界模型/
│   └── 3D视觉/
└── 99_System/
    └── Config/
        ├── research_interests.yaml      # 研究兴趣配置
        ├── user_preferences.yaml        # 反馈偏好（自动生成）
        └── user_preferences_state.yaml  # 偏好累积状态（自动生成）
```

## 使用方法

### 每日推荐

```bash
/start-my-day           # 生成今天的推荐
/start-my-day 2026-05-20  # 生成指定日期的推荐
```

执行流程：
1. 收集前一天的反馈（增量合并到偏好文件）
2. 搜索 arXiv + Semantic Scholar
3. 基于研究兴趣 + 用户偏好综合评分
4. 生成推荐笔记（含细粒度反馈复选框）
5. 前 3 篇自动提取图片 + 生成详细分析

### 反馈使用

1. 在 Obsidian 中打开今日推荐笔记
2. 对感兴趣的论文勾选 `[x] 感兴趣`，并勾选具体感兴趣的主题
3. 对不感兴趣的论文勾选 `[x] 不感兴趣`，同样可勾选具体主题
4. 下次运行 `/start-my-day` 时自动生效

### 单篇论文分析

```bash
/paper-analyze 2602.12345
/paper-analyze "论文标题"
```

### 顶会论文搜索

```bash
/conf-papers CVPR 2025
/conf-papers NeurIPS 2024 --top-n 20
```

## 评分机制

| 维度 | 权重 | 说明 |
|------|------|------|
| 相关性 | 40% | 关键词匹配（标题 +0.5/个，摘要 +0.3/个）+ 类别匹配（+1.0）+ **用户偏好加权** |
| 热门度 | 30% | 引用数 > 100（+3）、50-100（+2）、< 50（+1） |
| 新近性 | 20% | 30 天内（+3）、30-90 天（+2）、90-180 天（+1） |
| 质量 | 10% | 从摘要推断的方法创新性和实验质量 |

**用户偏好调整**：在基础评分之上，根据 `user_preferences.yaml` 中的关键词权重进行加减分。例如你多次对"VLA模型"主题点了感兴趣，后续含 VLA 关键词的论文会获得额外加分。

## 目录结构

```
evil-read-arxiv/
├── README.md
├── QUICKSTART.md
├── config.example.yaml           # 配置模板
├── requirements.txt
├── start-my-day/                 # 每日推荐
│   ├── SKILL.md
│   └── scripts/
│       ├── search_arxiv.py       # arXiv/S2 搜索 + 偏好加权评分
│       ├── collect_feedback.py   # 增量反馈收集
│       ├── scan_existing_notes.py
│       └── link_keywords.py
├── paper-analyze/                # 论文深度分析
│   ├── SKILL.md
│   └── scripts/
├── extract-paper-images/         # 图片提取
│   ├── SKILL.md
│   └── scripts/
├── paper-search/                 # 论文搜索
│   └── SKILL.md
└── conf-papers/                  # 顶会论文搜索
    ├── SKILL.md
    ├── conf-papers.yaml
    └── scripts/
```

## 工作原理

```
用户输入 /start-my-day
         │
         ▼
  ┌─────────────────────┐
  │ 1. 收集昨天的反馈    │ ← 增量：只读昨天的笔记
  │    合并到偏好文件    │   不扫描全量历史
  └─────────┬───────────┘
            ▼
  ┌─────────────────────┐
  │ 2. 搜索论文          │ ← arXiv（近30天）
  │    + 偏好加权评分    │   + S2（近1年高热度）
  └─────────┬───────────┘
            ▼
  ┌─────────────────────┐
  │ 3. 生成推荐笔记      │ ← 10篇，含细粒度反馈复选框
  │    前3篇深度分析     │   图片 + 详细报告
  └─────────┬───────────┘
            ▼
  ┌─────────────────────┐
  │ 4. 用户在 Obsidian   │ ← 勾选感兴趣的主题
  │    中给出反馈        │   明天自动生效
  └─────────────────────┘
```

## 常见问题

### 搜索没有结果？
1. 检查网络连接
2. 检查 `research_interests.yaml` 中的关键词和分类
3. Semantic Scholar API 偶尔会 429 限流，脚本会自动重试

### 图片提取失败？
1. 确保安装了 PyMuPDF：`pip install PyMuPDF`
2. 检查 arXiv ID 格式（如 `2602.12345`）

### 反馈没有生效？
1. 反馈在下次运行 `/start-my-day` 时才会收集，不是实时的
2. 检查 `user_preferences_state.yaml` 中的 `processed_dates` 确认日期是否已处理
3. 如需重新处理某天：从 `processed_dates` 列表中删除该日期后重新运行

### "Papers directory not found" 错误？
检查 `OBSIDIAN_VAULT_PATH` 环境变量和 Vault 中的目录结构。

## 许可证

MIT License

## 致谢

- [arXiv](https://arxiv.org/) - 开放获取的学术论文预印本平台
- [Semantic Scholar](https://www.semanticscholar.org/) - AI 驱动的学术研究平台
- [Claude Code](https://claude.ai/claude-code) - AI 辅助编程工具
- [Obsidian](https://obsidian.md/) - 知识管理工具
