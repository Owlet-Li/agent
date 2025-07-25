# -*- coding: utf-8 -*-
"""
Newsletter Agent - 内容格式化器
新闻内容结构化、摘要生成和格式转换
"""

import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
from urllib.parse import urlparse

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


@dataclass
class FormattedContent:
    """格式化后的内容数据结构"""
    
    # 基本信息
    title: str
    content: str
    summary: str
    source: str
    url: str
    
    # 时间信息
    published_at: Optional[datetime] = None
    formatted_date: str = ""
    
    # 分类和标签
    category: str = "未分类"
    tags: List[str] = None
    keywords: List[str] = None
    
    # 内容分析
    language: str = "unknown"
    reading_time: int = 0  # 预计阅读时间（分钟）
    word_count: int = 0
    
    # 质量指标
    quality_score: float = 0.0
    relevance_score: float = 0.0
    
    # 额外信息
    author: str = ""
    image_url: str = ""
    excerpt: str = ""
    
    def __post_init__(self):
        """初始化后处理"""
        if self.tags is None:
            self.tags = []
        if self.keywords is None:
            self.keywords = []
        
        # 格式化日期
        if self.published_at:
            self.formatted_date = self.published_at.strftime("%Y-%m-%d %H:%M")
        else:
            self.formatted_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        # 处理datetime对象
        if self.published_at:
            data['published_at'] = self.published_at.isoformat()
        return data
    
    def to_markdown(self) -> str:
        """转换为Markdown格式"""
        lines = []
        
        # 标题
        lines.append(f"# {self.title}")
        lines.append("")
        
        # 元信息
        lines.append(f"**来源**: {self.source}")
        if self.author:
            lines.append(f"**作者**: {self.author}")
        lines.append(f"**发布时间**: {self.formatted_date}")
        if self.category != "未分类":
            lines.append(f"**分类**: {self.category}")
        if self.tags:
            lines.append(f"**标签**: {', '.join(self.tags)}")
        lines.append("")
        
        # 摘要
        if self.summary:
            lines.append("## 摘要")
            lines.append(self.summary)
            lines.append("")
        
        # 正文
        lines.append("## 正文")
        lines.append(self.content)
        lines.append("")
        
        # 链接
        if self.url:
            lines.append(f"**原文链接**: [{self.url}]({self.url})")
        
        return "\n".join(lines)
    
    def to_html(self) -> str:
        """转换为HTML格式"""
        html_content = f"""
        <div class="news-article">
            <h2 class="title">{self.title}</h2>
            
            <div class="meta-info">
                <span class="source">来源: {self.source}</span>
                {f'<span class="author">作者: {self.author}</span>' if self.author else ''}
                <span class="date">{self.formatted_date}</span>
                {f'<span class="category">分类: {self.category}</span>' if self.category != "未分类" else ''}
            </div>
            
            {f'<div class="tags">标签: {", ".join(self.tags)}</div>' if self.tags else ''}
            
            {f'<div class="summary"><h3>摘要</h3><p>{self.summary}</p></div>' if self.summary else ''}
            
            <div class="content">
                <h3>正文</h3>
                <p>{self.content}</p>
            </div>
            
            {f'<div class="link"><a href="{self.url}" target="_blank">查看原文</a></div>' if self.url else ''}
        </div>
        """
        return html_content.strip()


class ContentFormatter:
    """内容格式化器
    
    负责新闻内容的结构化、摘要生成和格式转换
    """
    
    def __init__(self):
        """初始化格式化器"""
        self.reading_speed = 250  # 每分钟阅读词数（中文按字符计算）
        
        # 质量评估关键词
        self.quality_keywords = {
            "high_quality": ["独家", "深度", "分析", "调查", "专访", "评论"],
            "low_quality": ["转发", "转载", "广告", "推广", "营销"]
        }
        
        logger.info("内容格式化器初始化完成")
    
    def calculate_reading_time(self, text: str, language: str = "zh") -> int:
        """计算预计阅读时间（分钟）"""
        if not text:
            return 0
        
        if language.startswith("zh"):
            # 中文按字符数计算
            char_count = len(re.sub(r'\s+', '', text))
            reading_time = max(1, round(char_count / self.reading_speed))
        else:
            # 英文按单词数计算
            word_count = len(text.split())
            reading_time = max(1, round(word_count / self.reading_speed))
        
        return reading_time
    
    def generate_summary(self, content: str, max_length: int = 200) -> str:
        """生成内容摘要
        
        Args:
            content: 原始内容
            max_length: 摘要最大长度
        """
        if not content:
            return ""
        
        # 清理内容
        clean_content = re.sub(r'\s+', ' ', content).strip()
        
        # 如果内容本身就很短，直接返回
        if len(clean_content) <= max_length:
            return clean_content
        
        # 按句子分割
        sentences = re.split(r'[。！？.!?]', clean_content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return clean_content[:max_length] + "..."
        
        # 选择前几个句子作为摘要
        summary = ""
        for sentence in sentences:
            if len(summary + sentence) <= max_length:
                summary += sentence + "。"
            else:
                break
        
        # 如果没有选中任何句子，截取前面部分
        if not summary:
            summary = clean_content[:max_length] + "..."
        
        return summary.strip()
    
    def extract_excerpt(self, content: str, max_length: int = 100) -> str:
        """提取文章摘录"""
        if not content:
            return ""
        
        # 清理并截取
        clean_content = re.sub(r'\s+', ' ', content).strip()
        
        if len(clean_content) <= max_length:
            return clean_content
        
        # 在合适的位置截断
        excerpt = clean_content[:max_length]
        last_punct = max(
            excerpt.rfind('。'),
            excerpt.rfind('！'),
            excerpt.rfind('？'),
            excerpt.rfind('.'),
            excerpt.rfind('!'),
            excerpt.rfind('?')
        )
        
        if last_punct > max_length * 0.7:  # 如果标点符号位置合理
            excerpt = excerpt[:last_punct + 1]
        else:
            excerpt = excerpt + "..."
        
        return excerpt
    
    def assess_quality(self, title: str, content: str) -> float:
        """评估内容质量
        
        Returns:
            质量分数 (0-1)
        """
        score = 0.5  # 基础分数
        
        full_text = f"{title} {content}".lower()
        
        # 检查高质量关键词
        high_quality_count = sum(1 for keyword in self.quality_keywords["high_quality"] 
                                if keyword in full_text)
        score += high_quality_count * 0.1
        
        # 检查低质量关键词
        low_quality_count = sum(1 for keyword in self.quality_keywords["low_quality"] 
                               if keyword in full_text)
        score -= low_quality_count * 0.15
        
        # 根据内容长度调整
        content_length = len(content)
        if content_length < 100:
            score -= 0.2  # 内容太短
        elif content_length > 1000:
            score += 0.1  # 内容充实
        
        # 检查标题质量
        if len(title) < 10:
            score -= 0.1  # 标题太短
        elif len(title) > 100:
            score -= 0.1  # 标题太长
        
        # 确保分数在0-1范围内
        return max(0.0, min(1.0, score))
    
    def categorize_content(self, title: str, content: str, keywords: List[str] = None) -> str:
        """内容分类
        
        Returns:
            分类名称
        """
        if keywords is None:
            keywords = []
        
        full_text = f"{title} {content}".lower()
        keyword_text = " ".join(keywords).lower()
        
        # 定义分类关键词
        categories = {
            "科技": ["科技", "技术", "AI", "人工智能", "互联网", "软件", "硬件", "数字", "创新", "研发"],
            "财经": ["经济", "金融", "股票", "投资", "银行", "货币", "市场", "商业", "企业", "财政"],
            "政治": ["政府", "政策", "法律", "国际", "外交", "选举", "议会", "官员", "政治"],
            "体育": ["体育", "足球", "篮球", "奥运", "比赛", "运动", "球员", "赛事", "锻炼"],
            "娱乐": ["娱乐", "电影", "音乐", "明星", "演员", "综艺", "游戏", "文艺", "表演"],
            "健康": ["健康", "医疗", "病毒", "疫苗", "医院", "医生", "疾病", "治疗", "养生"],
            "教育": ["教育", "学校", "学生", "老师", "大学", "考试", "学习", "培训", "研究"],
            "社会": ["社会", "民生", "生活", "社区", "公益", "环境", "交通", "住房", "就业"],
            "国际": ["国际", "全球", "世界", "国外", "跨国", "国际组织", "外国", "海外"]
        }
        
        # 计算每个分类的匹配分数
        category_scores = {}
        for category, category_keywords in categories.items():
            score = 0
            for keyword in category_keywords:
                if keyword in full_text:
                    score += 2
                if keyword in keyword_text:
                    score += 3
            category_scores[category] = score
        
        # 返回得分最高的分类
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            if category_scores[best_category] > 0:
                return best_category
        
        return "综合"
    
    def extract_tags(self, title: str, content: str, keywords: List[str] = None) -> List[str]:
        """提取标签"""
        if keywords is None:
            keywords = []
        
        tags = set()
        
        # 从关键词中提取标签
        for keyword in keywords[:10]:  # 最多取前10个关键词
            if len(keyword) >= 2:  # 过滤太短的关键词
                tags.add(keyword)
        
        # 从标题中提取重要词汇
        title_words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', title)
        for word in title_words:
            if len(word) >= 2:
                tags.add(word)
        
        # 限制标签数量
        return list(tags)[:8]
    
    def format_content(self, raw_content: Dict[str, Any], processing_options: Optional[Dict[str, Any]] = None) -> FormattedContent:
        """格式化单个内容项
        
        Args:
            raw_content: 原始内容数据
            processing_options: 处理选项
        
        Returns:
            格式化后的内容对象
        """
        # 默认处理选项
        default_options = {
            "generate_summary": True,
            "max_summary_length": 200,
            "generate_excerpt": True,
            "max_excerpt_length": 100,
            "assess_quality": True,
            "auto_categorize": True,
            "extract_tags": True,
            "calculate_reading_time": True
        }
        
        if processing_options:
            default_options.update(processing_options)
        
        # 提取基本信息
        title = raw_content.get("title", "").strip()
        content = raw_content.get("content", "").strip()
        source = raw_content.get("source", "未知来源")
        url = raw_content.get("url", "")
        
        # 时间处理
        published_at = raw_content.get("published_at")
        if isinstance(published_at, str):
            try:
                published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                published_at = None
        
        # 初始化格式化内容对象
        formatted = FormattedContent(
            title=title,
            content=content,
            summary="",
            source=source,
            url=url,
            published_at=published_at,
            author=raw_content.get("author", ""),
            image_url=raw_content.get("image_url", ""),
            language=raw_content.get("language", "unknown"),
            word_count=len(content)
        )
        
        # 生成摘要
        if default_options["generate_summary"] and content:
            formatted.summary = self.generate_summary(content, default_options["max_summary_length"])
        
        # 生成摘录
        if default_options["generate_excerpt"] and content:
            formatted.excerpt = self.extract_excerpt(content, default_options["max_excerpt_length"])
        
        # 计算阅读时间
        if default_options["calculate_reading_time"]:
            formatted.reading_time = self.calculate_reading_time(content, formatted.language)
        
        # 质量评估
        if default_options["assess_quality"]:
            formatted.quality_score = self.assess_quality(title, content)
        
        # 自动分类
        keywords = raw_content.get("keywords", [])
        if default_options["auto_categorize"]:
            formatted.category = self.categorize_content(title, content, keywords)
        
        # 提取标签
        if default_options["extract_tags"]:
            formatted.tags = self.extract_tags(title, content, keywords)
        
        # 设置关键词
        formatted.keywords = keywords[:10] if keywords else []
        
        return formatted
    
    def batch_format(self, raw_contents: List[Dict[str, Any]], processing_options: Optional[Dict[str, Any]] = None) -> List[FormattedContent]:
        """批量格式化内容"""
        formatted_contents = []
        
        for raw_content in raw_contents:
            try:
                formatted = self.format_content(raw_content, processing_options)
                formatted_contents.append(formatted)
            except Exception as e:
                logger.error(f"内容格式化失败: {e}")
                # 创建一个基本的格式化对象
                basic_formatted = FormattedContent(
                    title=raw_content.get("title", "处理失败"),
                    content=raw_content.get("content", ""),
                    summary="处理失败",
                    source=raw_content.get("source", "未知"),
                    url=raw_content.get("url", "")
                )
                formatted_contents.append(basic_formatted)
        
        return formatted_contents
    
    def group_by_category(self, contents: List[FormattedContent]) -> Dict[str, List[FormattedContent]]:
        """按分类分组内容"""
        grouped = {}
        
        for content in contents:
            category = content.category
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(content)
        
        # 按质量分数排序每个分类中的内容
        for category in grouped:
            grouped[category].sort(key=lambda x: x.quality_score, reverse=True)
        
        return grouped
    
    def create_newsletter_structure(self, contents: List[FormattedContent]) -> Dict[str, Any]:
        """创建新闻简报结构"""
        grouped_contents = self.group_by_category(contents)
        
        newsletter = {
            "title": f"新闻简报 - {datetime.now().strftime('%Y年%m月%d日')}",
            "date": datetime.now().isoformat(),
            "total_articles": len(contents),
            "categories": {},
            "top_articles": [],
            "summary": ""
        }
        
        # 整理分类内容
        for category, category_contents in grouped_contents.items():
            newsletter["categories"][category] = {
                "articles": [content.to_dict() for content in category_contents],
                "count": len(category_contents)
            }
        
        # 选出顶级文章（质量分数最高的前5篇）
        all_contents_sorted = sorted(contents, key=lambda x: x.quality_score, reverse=True)
        newsletter["top_articles"] = [content.to_dict() for content in all_contents_sorted[:5]]
        
        # 生成简报摘要
        if contents:
            top_categories = sorted(grouped_contents.keys(), key=lambda x: len(grouped_contents[x]), reverse=True)[:3]
            newsletter["summary"] = f"本期简报包含 {len(contents)} 篇文章，主要涵盖 {', '.join(top_categories)} 等领域。"
        
        return newsletter 