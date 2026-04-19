#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户偏好学习脚本 - 从论文笔记的反馈中学习用户偏好

扫描 Obsidian vault 中的论文笔记，读取 frontmatter 中的 feedback 字段，
使用 EMA（指数移动平均）算法聚合为偏好档案，供推荐评分使用。
"""

import json
import os
import re
import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

# EMA 学习率：越小越平滑，需要更多反馈才能改变偏好
EMA_ALPHA = 0.15

# 偏好评分相关常量（供搜索脚本导入）
SCORE_MAX = 3.0
PREFERENCE_MIN_FEEDBACK = 5
PREFERENCE_MAX_WEIGHT = 0.15
PREFERENCE_RAMP_FEEDBACK = 30

# 偏好评分内部权重
PREF_KEYWORD_WEIGHT = 0.40
PREF_AUTHOR_WEIGHT = 0.25
PREF_DOMAIN_WEIGHT = 0.20
PREF_CATEGORY_WEIGHT = 0.15

# 从标题中提取关键词时忽略的常见词
STOP_WORDS = {
    'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'can', 'shall', 'not', 'no',
    'as', 'it', 'its', 'this', 'that', 'these', 'those', 'than', 'more',
    'via', 'using', 'based', 'towards', 'toward', 'into', 'between',
    'through', 'during', 'before', 'after', 'above', 'below', 'up', 'down',
    'about', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
    'there', 'when', 'where', 'why', 'how', 'all', 'each', 'every',
    'both', 'few', 'many', 'some', 'other', 'new', 'old',
}


def parse_frontmatter(content: str) -> Optional[Dict]:
    """解析 markdown 文件的 YAML frontmatter"""
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None

    fm = {}
    current_key = None
    current_list = None

    for line in match.group(1).split('\n'):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue

        # 列表项
        if stripped.startswith('- '):
            if current_key and current_list is not None:
                val = stripped[2:].strip().strip('"').strip("'")
                if val:
                    current_list.append(val)
            continue

        # 键值对
        if ':' in stripped:
            key, _, value = stripped.partition(':')
            key = key.strip()
            raw_value = value.strip()

            current_key = key
            # 显式空列表 [] 或无值（纯 key:）表示列表
            if raw_value == '[]':
                current_list = []
                fm[key] = current_list
            elif raw_value == '' and not stripped.endswith(':'):
                # 不太可能，但安全起见
                current_list = None
                fm[key] = ''
            elif raw_value == '':
                # 纯 key: 无值，可能是列表的开始
                current_list = []
                fm[key] = current_list
            elif raw_value in ('""', "''"):
                # 显式空字符串
                current_list = None
                fm[key] = ''
            else:
                current_list = None
                fm[key] = raw_value.strip('"').strip("'")

    return fm


def extract_keywords_from_title(title: str) -> List[str]:
    """从论文标题中提取有意义的关键词/短语"""
    if not title:
        return []

    keywords = []

    # 提取大写缩写（如 LLM, GPT, BERT）
    acronyms = re.findall(r'\b[A-Z]{2,}(?:\d+(?:\.\d+)?)?\b', title)
    keywords.extend(a.lower() for a in acronyms)

    # 提取连字符短语（如 Vision-Language, Multi-Agent）
    hyphenated = re.findall(r'\b[A-Za-z]+-[A-Za-z]+(?:-[A-Za-z]+)*\b', title)
    keywords.extend(h.lower() for h in hyphenated)

    # 提取普通词（过滤停用词，保留 3+ 字符）
    words = re.findall(r'\b[a-zA-Z]{3,}\b', title.lower())
    keywords.extend(w for w in words if w not in STOP_WORDS and w not in keywords)

    return keywords


def extract_authors_list(authors_str: str) -> List[str]:
    """从 authors 字符串中提取作者列表"""
    if not authors_str:
        return []
    # 支持逗号分隔和 "and" 分隔
    authors = re.split(r',\s*|\s+and\s+', authors_str)
    return [a.strip() for a in authors if a.strip() and a.strip() != '[Authors]']


def ema_update(old_score: float, signal: float, alpha: float = EMA_ALPHA) -> float:
    """EMA 更新，结果限制在 [-1, 1]"""
    new_score = alpha * signal + (1 - alpha) * old_score
    return max(-1.0, min(1.0, new_score))


def scan_feedback(vault_path: str) -> List[Dict]:
    """扫描 vault 中所有论文笔记的反馈"""
    papers_dir = os.path.join(vault_path, '20_Research', 'Papers')
    if not os.path.isdir(papers_dir):
        logger.warning("Papers directory not found: %s", papers_dir)
        return []

    feedbacks = []
    for root, _, files in os.walk(papers_dir):
        for fname in files:
            if not fname.endswith('.md'):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except (IOError, UnicodeDecodeError):
                continue

            fm = parse_frontmatter(content)
            if not fm:
                continue

            feedback = fm.get('feedback', '').strip().lower()
            if feedback not in ('like', 'dislike'):
                continue

            paper_id = fm.get('paper_id', '').strip()
            if not paper_id or paper_id == '[PAPER_ID]':
                # 用文件名作为 ID
                paper_id = fname.replace('.md', '')

            feedbacks.append({
                'paper_id': paper_id,
                'feedback': feedback,
                'reasons': fm.get('feedback_reasons', []),
                'title': fm.get('title', ''),
                'authors': fm.get('authors', ''),
                'domain': fm.get('domain', ''),
                'tags': fm.get('tags', []),
                'feedback_date': fm.get('feedback_date', ''),
                'file': fpath,
            })

    logger.info("Found %d papers with feedback", len(feedbacks))
    return feedbacks


def learn_preferences(feedbacks: List[Dict], existing_prefs: Optional[Dict] = None) -> Dict:
    """从反馈中学习偏好档案"""

    if existing_prefs and existing_prefs.get('version') == 1:
        prefs = existing_prefs
    else:
        prefs = {
            'version': 1,
            'last_updated': '',
            'total_feedback_count': 0,
            'keyword_preferences': {},
            'author_preferences': {},
            'domain_preferences': {},
            'category_preferences': {},
            'reason_stats': {},
            'processed_papers': [],
        }

    processed = set(prefs.get('processed_papers', []))

    new_count = 0
    for fb in feedbacks:
        pid = fb['paper_id']
        if pid in processed:
            continue

        processed.add(pid)
        new_count += 1
        signal = 1.0 if fb['feedback'] == 'like' else -1.0

        # 1. 关键词偏好：从标题和 tags 提取
        keywords = extract_keywords_from_title(fb.get('title', ''))
        tags = fb.get('tags', [])
        if isinstance(tags, list):
            for tag in tags:
                if isinstance(tag, str) and tag not in ('论文笔记', 'paper-notes'):
                    keywords.append(tag.lower().replace('-', ' ').replace('_', ' '))

        kw_prefs = prefs['keyword_preferences']
        for kw in set(keywords):
            if kw not in kw_prefs:
                kw_prefs[kw] = {'score': 0.0, 'like_count': 0, 'dislike_count': 0}
            entry = kw_prefs[kw]
            entry['score'] = ema_update(entry['score'], signal)
            if signal > 0:
                entry['like_count'] += 1
            else:
                entry['dislike_count'] += 1

        # 2. 作者偏好
        authors = extract_authors_list(fb.get('authors', ''))
        author_prefs = prefs['author_preferences']
        for author in authors:
            key = author.strip()
            if not key:
                continue
            if key not in author_prefs:
                author_prefs[key] = {'score': 0.0, 'like_count': 0, 'dislike_count': 0}
            entry = author_prefs[key]
            entry['score'] = ema_update(entry['score'], signal)
            if signal > 0:
                entry['like_count'] += 1
            else:
                entry['dislike_count'] += 1

        # 3. 领域偏好
        domain = fb.get('domain', '').strip()
        if domain and domain not in ('其他', 'Other', '[Domain]'):
            domain_prefs = prefs['domain_preferences']
            if domain not in domain_prefs:
                domain_prefs[domain] = {'score': 0.0, 'like_count': 0, 'dislike_count': 0}
            entry = domain_prefs[domain]
            entry['score'] = ema_update(entry['score'], signal)
            if signal > 0:
                entry['like_count'] += 1
            else:
                entry['dislike_count'] += 1

        # 4. 原因统计
        reasons = fb.get('reasons', [])
        if isinstance(reasons, list):
            reason_stats = prefs['reason_stats']
            for reason in reasons:
                if not isinstance(reason, str):
                    continue
                reason = reason.strip()
                if not reason:
                    continue
                if reason not in reason_stats:
                    reason_stats[reason] = {'like_count': 0, 'dislike_count': 0}
                if signal > 0:
                    reason_stats[reason]['like_count'] += 1
                else:
                    reason_stats[reason]['dislike_count'] += 1

    prefs['processed_papers'] = sorted(processed)
    prefs['total_feedback_count'] = len(processed)
    prefs['last_updated'] = datetime.now().strftime('%Y-%m-%d')

    if new_count > 0:
        logger.info("Processed %d new feedback entries (total: %d)", new_count, len(processed))
    else:
        logger.info("No new feedback to process (total: %d)", len(processed))

    return prefs


# ---------------------------------------------------------------------------
# 供搜索脚本导入的函数
# ---------------------------------------------------------------------------

def load_preferences(path: str) -> Optional[Dict]:
    """加载偏好档案，不存在则返回 None"""
    if not path or not os.path.isfile(path):
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            prefs = json.load(f)
        if prefs.get('version') != 1:
            logger.warning("Unknown preferences version: %s", prefs.get('version'))
            return None
        return prefs
    except (json.JSONDecodeError, IOError) as e:
        logger.warning("Failed to load preferences: %s", e)
        return None


def get_preference_weight(total_feedback_count: int) -> float:
    """根据反馈数量计算偏好维度权重（渐进式）"""
    if total_feedback_count < PREFERENCE_MIN_FEEDBACK:
        return 0.0
    ramp = min(
        (total_feedback_count - PREFERENCE_MIN_FEEDBACK)
        / (PREFERENCE_RAMP_FEEDBACK - PREFERENCE_MIN_FEEDBACK),
        1.0,
    )
    return PREFERENCE_MAX_WEIGHT * ramp


def calculate_preference_score(paper: Dict, preferences: Dict) -> float:
    """
    计算论文的用户偏好分 (0 ~ SCORE_MAX)

    综合关键词、作者、领域等维度的偏好匹配。
    无匹配时返回中性分 SCORE_MAX/2。

    Args:
        paper: 论文字典，包含 title, authors, matched_domain, matched_keywords, categories 等
        preferences: 偏好档案字典

    Returns:
        偏好分 (0 ~ SCORE_MAX)
    """
    components = []  # (name, raw_score_in_[-1,1], weight)

    kw_prefs = preferences.get('keyword_preferences', {})
    author_prefs = preferences.get('author_preferences', {})
    domain_prefs = preferences.get('domain_preferences', {})

    # 1. 关键词匹配
    paper_keywords = set()
    # 从 matched_keywords 获取
    for kw in paper.get('matched_keywords', []):
        paper_keywords.add(kw.lower())
    # 从标题补充
    title = paper.get('title', '')
    paper_keywords.update(extract_keywords_from_title(title))

    kw_scores = [kw_prefs[kw]['score'] for kw in paper_keywords if kw in kw_prefs]
    if kw_scores:
        components.append(('keyword', sum(kw_scores) / len(kw_scores), PREF_KEYWORD_WEIGHT))

    # 2. 作者匹配
    authors_raw = paper.get('authors', [])
    if isinstance(authors_raw, str):
        authors_list = extract_authors_list(authors_raw)
    elif isinstance(authors_raw, list):
        authors_list = []
        for a in authors_raw:
            if isinstance(a, dict):
                authors_list.append(a.get('name', ''))
            else:
                authors_list.append(str(a))
    else:
        authors_list = []

    author_scores = [
        author_prefs[a]['score']
        for a in authors_list
        if a.strip() and a.strip() in author_prefs
    ]
    if author_scores:
        components.append(('author', max(author_scores), PREF_AUTHOR_WEIGHT))

    # 3. 领域匹配
    domain = paper.get('matched_domain', '') or paper.get('domain', '')
    if domain and domain in domain_prefs:
        components.append(('domain', domain_prefs[domain]['score'], PREF_DOMAIN_WEIGHT))

    # 4. 分类匹配
    cat_prefs = preferences.get('category_preferences', {})
    categories = paper.get('categories', [])
    if isinstance(categories, str):
        categories = [c.strip() for c in categories.split(',')]
    cat_scores = [cat_prefs[c]['score'] for c in categories if c in cat_prefs]
    if cat_scores:
        components.append(('category', sum(cat_scores) / len(cat_scores), PREF_CATEGORY_WEIGHT))

    # 综合
    if not components:
        return SCORE_MAX / 2.0  # 中性

    total_weight = sum(w for _, _, w in components)
    raw = sum(s * w for _, s, w in components) / total_weight  # [-1, 1]

    # 映射 [-1, 1] -> [0, SCORE_MAX]
    return (raw + 1.0) / 2.0 * SCORE_MAX


# ---------------------------------------------------------------------------
# 主函数
# ---------------------------------------------------------------------------

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S',
        stream=sys.stderr,
    )

    parser = argparse.ArgumentParser(description='Learn user preferences from paper feedback')
    parser.add_argument('--vault', type=str,
                        default=os.environ.get('OBSIDIAN_VAULT_PATH', ''),
                        help='Obsidian vault path')
    parser.add_argument('--output', type=str, default=None,
                        help='Output preferences JSON path (default: vault/99_System/Config/user_preferences.json)')
    parser.add_argument('--alpha', type=float, default=EMA_ALPHA,
                        help=f'EMA learning rate (default: {EMA_ALPHA})')
    args = parser.parse_args()

    if not args.vault:
        logger.error("Vault path not specified. Use --vault or set OBSIDIAN_VAULT_PATH.")
        return 1

    output_path = args.output or os.path.join(
        args.vault, '99_System', 'Config', 'user_preferences.json'
    )

    # 加载已有偏好（增量更新）
    existing = load_preferences(output_path)

    # 扫描反馈
    feedbacks = scan_feedback(args.vault)
    if not feedbacks:
        logger.info("No feedback found in vault. Nothing to learn.")
        if not existing:
            # 创建空偏好文件
            empty_prefs = learn_preferences([], None)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(empty_prefs, f, ensure_ascii=False, indent=2)
            logger.info("Created empty preferences file: %s", output_path)
        return 0

    # 学习偏好
    prefs = learn_preferences(feedbacks, existing)

    # 保存
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(prefs, f, ensure_ascii=False, indent=2)

    logger.info("Preferences saved to: %s", output_path)
    logger.info("Total feedback: %d, Keywords tracked: %d, Authors tracked: %d, Domains tracked: %d",
                prefs['total_feedback_count'],
                len(prefs['keyword_preferences']),
                len(prefs['author_preferences']),
                len(prefs['domain_preferences']))

    return 0


if __name__ == '__main__':
    sys.exit(main() or 0)
