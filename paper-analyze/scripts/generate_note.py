#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Obsidian笔记生成脚本 - 正确处理frontmatter格式
支持中英文报告生成
"""

import sys
import os
import argparse
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def get_vault_path(cli_vault=None):
    """从CLI参数或环境变量获取vault路径"""
    if cli_vault:
        return cli_vault
    env_path = os.environ.get('OBSIDIAN_VAULT_PATH')
    if env_path:
        return env_path
    logger.error("未指定 vault 路径。请通过 --vault 参数或 OBSIDIAN_VAULT_PATH 环境变量设置。")
    sys.exit(1)


def generate_note_content(paper_id, title, authors, domain, date, language="zh"):
    """生成笔记的 Markdown 内容"""

    # 中文模板
    if language == "zh":
        domain_tags = {
            "大模型": ["大模型", "LLM"],
            "多模态技术": ["多模态", "Vision-Language"],
            "智能体": ["智能体", "Agent"],
        }
        tags = ["论文笔记"] + domain_tags.get(domain, [domain])
        tags_yaml = "\n".join(f'  - {tag}' for tag in tags)

        return f'''---
date: "{date}"
paper_id: "{paper_id}"
title: "{title}"
authors: "{authors}"
domain: "{domain}"
tags:
{tags_yaml}
quality_score: "[SCORE]/10"
related_papers: []
created: "{date}"
updated: "{date}"
status: analyzed
feedback: ""
feedback_reasons: []
feedback_date: ""
---

# {title}

> **论文ID**：{paper_id} | **作者**：{authors} | **链接**：[arXiv](https://arxiv.org/abs/{paper_id}) | [PDF](https://arxiv.org/pdf/{paper_id})

## 一句话总结

[用一句话概括这篇论文做了什么、解决了什么问题、达到了什么效果]

## 背景：作者想解决什么问题？

[简要介绍研究背景，让读者快速理解：]
[- 这个领域现在是什么状况？]
[- 现有方法有什么痛点或瓶颈？]
[- 作者的出发点是什么？]

## 贡献与方法：怎么解决的？

### 核心贡献

[列出论文的主要贡献，通常 2-4 点]

### 方法详解

[这一部分是重点，需要详细展开，让读者能看懂作者的思路]
[不要过度简化——如果方法有多个关键模块，逐一解释清楚]
[善用论文中的图来辅助说明]

[插入论文架构图/方法图：]
![[figure_name.png|800]]

[如果有重要的数学公式，用 LaTeX 展示：]
[行内公式 $L(\\theta)$，块级公式：]
$$\\theta^* = \\arg\\min_\\theta L(\\theta)$$

[如果方法有多个阶段/模块，分小节展开：]

#### [模块/阶段1名称]

[详细说明这个模块做了什么、为什么这样设计]

#### [模块/阶段2名称]

[详细说明]

#### [模块/阶段3名称]

[详细说明]

## 实验结果

[简述关键实验结果，不需要贴所有表格，抓重点：]
[- 在哪些数据集/任务上测试？]
[- 跟哪些方法比？结果如何？]
[- 有没有值得关注的消融实验结论？]

[可以插入关键结果图表：]
![[results_figure.png|800]]

## 锐评

[一段客观但有态度的点评，例如：]
[- 这篇论文的核心价值在哪里？是方法创新、工程突破还是纯堆工作量？]
[- 实验是否有说服力？有没有明显的问题或遗漏？]
[- 对这个领域有多大影响？值不值得跟进？]
[- 一句话定性：开创性/扎实推进/中规中矩/增量灌水/纯工程堆量]

**总体评分**：[X.X/10]

## Benchmark 记录

| Benchmark | 任务类型 | 本文结果 | SOTA 参考 |
|-----------|----------|----------|-----------|
| [benchmark] | [类型] | [结果] | [参考值] |

## 技术感悟

[2-3 段个人技术洞察：]
[- 这篇工作给我什么启发？]
[- 哪些思路可以借鉴到自己的研究中？]
[- 这个方向接下来可能往哪走？]

## 我的笔记

[阅读后手动补充的想法、启发、可借鉴的点]

## 论文反馈

在 frontmatter 中编辑以下字段来记录你的反馈：

- **feedback**: 填写 `like` 或 `dislike`
- **feedback_reasons**: 从以下标签中选择（可多选）
- **feedback_date**: 填写评价日期

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
- [[相关论文1]] - [关系]
- [[相关论文2]] - [关系]

## 外部资源
- [代码链接（如果有）]
- [项目主页（如果有）]
'''
    else:
        # English template
        domain_tags_en = {
            "LLM": ["LLM", "Large Language Model"],
            "Multimodal": ["Multimodal", "Vision-Language"],
            "Agent": ["Agent", "Multi-Agent"],
            "Other": ["Paper Notes"],
        }
        tags = ["paper-notes"] + domain_tags_en.get(domain, [domain])
        tags_yaml = "\n".join(f'  - {tag}' for tag in tags)

        return f'''---
date: "{date}"
paper_id: "{paper_id}"
title: "{title}"
authors: "{authors}"
domain: "{domain}"
tags:
{tags_yaml}
quality_score: "[SCORE]/10"
related_papers: []
created: "{date}"
updated: "{date}"
status: analyzed
feedback: ""
feedback_reasons: []
feedback_date: ""
---

# {title}

> **Paper ID**: {paper_id} | **Authors**: {authors} | **Links**: [arXiv](https://arxiv.org/abs/{paper_id}) | [PDF](https://arxiv.org/pdf/{paper_id})

## TL;DR

[One sentence summary: what this paper does, what problem it solves, what it achieves]

## Background: What Problem Are They Solving?

[Brief introduction to set the context:]
[- What is the current state of this field?]
[- What are the pain points or bottlenecks of existing methods?]
[- What motivated the authors?]

## Contributions & Method: How Do They Solve It?

### Key Contributions

[List the main contributions, typically 2-4 points]

### Method Details

[This is the core section — explain in detail so readers can understand the approach]
[Don't oversimplify — if the method has multiple key modules, explain each clearly]
[Use figures from the paper to aid explanation]

[Insert architecture/method figures:]
![[figure_name.png|800]]

[Important math formulas in LaTeX:]
[Inline $L(\\theta)$, block:]
$$\\theta^* = \\arg\\min_\\theta L(\\theta)$$

[If the method has multiple stages/modules, use subsections:]

#### [Module/Stage 1 Name]

[Detailed explanation of what this module does and why]

#### [Module/Stage 2 Name]

[Detailed explanation]

#### [Module/Stage 3 Name]

[Detailed explanation]

## Experimental Results

[Summarize key results — focus on what matters:]
[- Which datasets/tasks were used?]
[- What baselines were compared? How did it perform?]
[- Any notable ablation findings?]

[Insert key results figures/tables:]
![[results_figure.png|800]]

## Verdict

[An objective but opinionated critique, e.g.:]
[- Where is the core value? Methodological innovation, engineering breakthrough, or brute-force effort?]
[- Are the experiments convincing? Any obvious gaps?]
[- How impactful is this for the field? Worth following up?]
[- One-line verdict: Groundbreaking / Solid advance / Average / Incremental / Engineering-heavy]

**Overall Score**: [X.X/10]

## Benchmark Records

| Benchmark | Task Type | This Paper | SOTA Reference |
|-----------|-----------|------------|----------------|
| [benchmark] | [type] | [result] | [reference] |

## Technical Insights

[2-3 paragraphs of personal technical observations:]
[- What inspiration does this work provide?]
[- Which ideas could be applied to my own research?]
[- Where might this direction go next?]

## My Notes

[Personal thoughts, inspirations, takeaways after reading]

## Paper Feedback

Edit these fields in the frontmatter to record your feedback:

- **feedback**: Set to `like` or `dislike`
- **feedback_reasons**: Pick from the tags below (multiple allowed)
- **feedback_date**: Date of your feedback

**Positive tags:**
| Tag | Meaning |
|-----|---------|
| `topic_match` | Matches my research interests |
| `known_researcher` | Well-known author/institution |
| `novel_methodology` | Novel and inspiring approach |
| `practical` | Highly practical, directly applicable |
| `good_writing` | Clear and well-written |
| `comprehensive_experiments` | Thorough experiments |

**Negative tags:**
| Tag | Meaning |
|-----|---------|
| `topic_mismatch` | Not relevant to my interests |
| `incremental` | Too incremental |
| `poor_quality` | Low quality |
| `already_known` | Already familiar content |

## Related Papers
- [[Related Paper 1]] - [Relationship]
- [[Related Paper 2]] - [Relationship]

## External Resources
- [Code links (if available)]
- [Project homepage (if available)]
'''


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S',
        stream=sys.stderr,
    )

    parser = argparse.ArgumentParser(description='生成论文分析笔记 / Generate paper analysis notes')
    parser.add_argument('--paper-id', type=str, default='[PAPER_ID]', help='论文 arXiv ID / Paper arXiv ID')
    parser.add_argument('--title', type=str, default='[论文标题]', help='论文标题 / Paper title')
    parser.add_argument('--authors', type=str, default='[Authors]', help='论文作者 / Paper authors')
    parser.add_argument('--domain', type=str, default='其他', help='论文领域 / Paper domain')
    parser.add_argument('--vault', type=str, default=None, help='Obsidian vault 路径 / Obsidian vault path')
    parser.add_argument('--language', type=str, default='zh', choices=['zh', 'en'], help='语言 / Language: zh (中文) or en (English)')
    args = parser.parse_args()

    vault_root = get_vault_path(args.vault)
    papers_dir = os.path.join(vault_root, "20_Research", "Papers")
    date = datetime.now().strftime("%Y-%m-%d")

    # 清理文件名中的非法字符
    import re
    paper_title_safe = re.sub(r'[ /\\:*?"<>|]+', '_', args.title).strip('_')

    # 校验域名，防止路径穿越
    domain = args.domain.strip('/\\').replace('..', '')
    if not domain:
        domain = '其他' if args.language == 'zh' else 'Other'

    note_dir = os.path.join(papers_dir, domain)
    os.makedirs(note_dir, exist_ok=True)

    note_path = os.path.join(note_dir, f"{paper_title_safe}.md")
    content = generate_note_content(args.paper_id, args.title, args.authors, domain, date, args.language)

    try:
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except IOError as e:
        logger.error("写入笔记失败: %s", e)
        sys.exit(1)

    print(f"笔记已生成: {note_path}" if args.language == 'zh' else f"Note generated: {note_path}")
    print(f"请手动编辑笔记内容，替换占位符为实际分析结果" if args.language == 'zh' else "Please manually edit the note content, replacing placeholders with actual analysis results")


if __name__ == '__main__':
    main()
