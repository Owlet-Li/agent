# -*- coding: utf-8 -*-
"""
Newsletter Agent - 格式化工具
提供HTML和Markdown格式转换和处理功能
"""

from typing import Dict, Any, List, Optional
import re
import html
from datetime import datetime

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class ContentFormatter:
    """通用内容格式化器"""
    
    def __init__(self):
        self.html_formatter = HTMLFormatter()
        self.markdown_formatter = MarkdownFormatter()
        logger.info("内容格式化器初始化完成")
    
    def format_content(
        self,
        content: Dict[str, Any],
        output_format: str = "html",
        style: str = "standard"
    ) -> str:
        """格式化内容到指定格式"""
        if output_format.lower() == "html":
            return self.html_formatter.format(content, style)
        elif output_format.lower() == "markdown":
            return self.markdown_formatter.format(content, style)
        else:
            raise ValueError(f"不支持的输出格式: {output_format}")
    
    def clean_text(self, text: str) -> str:
        """清理文本内容"""
        if not text:
            return ""
        
        # 移除多余空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 移除特殊字符
        text = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:\-()"\']', '', text)
        
        return text.strip()
    
    def truncate_text(self, text: str, max_length: int = 200, suffix: str = "...") -> str:
        """截断文本到指定长度"""
        if not text or len(text) <= max_length:
            return text
        
        # 尝试在句号或逗号处截断
        for punct in ['. ', '。', ', ', '，']:
            pos = text.rfind(punct, 0, max_length - len(suffix))
            if pos > max_length * 0.7:  # 至少保留70%的内容
                return text[:pos + 1] + suffix
        
        # 如果找不到合适的标点，就直接截断
        return text[:max_length - len(suffix)] + suffix
    
    def extract_summary(self, content: str, max_sentences: int = 3) -> str:
        """提取内容摘要"""
        if not content:
            return ""
        
        # 按句号分割
        sentences = re.split(r'[.。!！?？]', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # 取前几句
        summary_sentences = sentences[:max_sentences]
        return '。'.join(summary_sentences) + '。' if summary_sentences else ""
    
    def format_date(self, date_str: str, format_type: str = "friendly") -> str:
        """格式化日期"""
        if not date_str:
            return ""
        
        try:
            if format_type == "friendly":
                # 友好格式: 今天, 昨天, 或具体日期
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                now = datetime.now()
                delta = now - date_obj
                
                if delta.days == 0:
                    return "今天"
                elif delta.days == 1:
                    return "昨天"
                else:
                    return date_obj.strftime("%m月%d日")
            else:
                # 标准格式
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return date_obj.strftime("%Y年%m月%d日 %H:%M")
        
        except Exception as e:
            logger.warning(f"日期格式化失败: {e}")
            return date_str


class HTMLFormatter:
    """HTML格式化器"""
    
    def format(self, content: Dict[str, Any], style: str = "standard") -> str:
        """将内容格式化为HTML"""
        if isinstance(content, list):
            return self._format_article_list(content, style)
        elif isinstance(content, dict):
            return self._format_single_article(content, style)
        else:
            return self._format_text_content(str(content), style)
    
    def _format_article_list(self, articles: List[Dict[str, Any]], style: str) -> str:
        """格式化文章列表"""
        html_parts = []
        
        for i, article in enumerate(articles, 1):
            article_html = self._format_single_article(article, style, index=i)
            html_parts.append(article_html)
        
        return '\n'.join(html_parts)
    
    def _format_single_article(self, article: Dict[str, Any], style: str, index: int = None) -> str:
        """格式化单篇文章"""
        title = html.escape(article.get('title', '无标题'))
        url = article.get('url', '#')
        summary = html.escape(article.get('summary', article.get('content', ''))[:200] + '...')
        source = html.escape(article.get('source', '未知来源'))
        published_at = article.get('published_at', '')
        category = article.get('category', '')
        
        # 格式化日期
        date_display = ContentFormatter().format_date(published_at) if published_at else ""
        
        if style == "card":
            return f'''
            <div class="article-card" style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-bottom: 15px; background: white;">
                <h3 style="margin: 0 0 10px; color: #333;">
                    {f"{index}. " if index else ""}<a href="{url}" target="_blank" style="text-decoration: none; color: inherit;">{title}</a>
                </h3>
                <p style="color: #666; margin: 0 0 10px; line-height: 1.5;">{summary}</p>
                <div style="font-size: 0.9em; color: #999; border-top: 1px solid #eee; padding-top: 8px;">
                    <span>📰 {source}</span>
                    {f" | 📅 {date_display}" if date_display else ""}
                    {f" | 🏷️ {category}" if category else ""}
                </div>
            </div>
            '''
        else:  # standard
            return f'''
            <div class="article" style="margin-bottom: 20px; padding: 15px; background: #fafafa; border-left: 4px solid #667eea; border-radius: 5px;">
                <h4 style="margin: 0 0 8px; color: #333;">
                    {f"{index}. " if index else ""}<a href="{url}" target="_blank" style="color: #667eea; text-decoration: none;">{title}</a>
                </h4>
                <p style="color: #555; margin: 0 0 8px; line-height: 1.6;">{summary}</p>
                <small style="color: #888;">
                    来源: {source}
                    {f" | {date_display}" if date_display else ""}
                    {f" | {category}" if category else ""}
                </small>
            </div>
            '''
    
    def _format_text_content(self, text: str, style: str) -> str:
        """格式化纯文本内容"""
        # 转义HTML特殊字符
        escaped_text = html.escape(text)
        
        # 转换换行为HTML段落
        paragraphs = escaped_text.split('\n\n')
        html_paragraphs = [f'<p>{p.replace(chr(10), "<br>")}</p>' for p in paragraphs if p.strip()]
        
        return '\n'.join(html_paragraphs)
    
    def wrap_in_container(self, content: str, title: str = "", container_class: str = "content-container") -> str:
        """将内容包装在HTML容器中"""
        title_html = f'<h2 class="container-title">{html.escape(title)}</h2>' if title else ""
        
        return f'''
        <div class="{container_class}">
            {title_html}
            <div class="container-content">
                {content}
            </div>
        </div>
        '''


class MarkdownFormatter:
    """Markdown格式化器"""
    
    def format(self, content: Dict[str, Any], style: str = "standard") -> str:
        """将内容格式化为Markdown"""
        if isinstance(content, list):
            return self._format_article_list(content, style)
        elif isinstance(content, dict):
            return self._format_single_article(content, style)
        else:
            return self._format_text_content(str(content), style)
    
    def _format_article_list(self, articles: List[Dict[str, Any]], style: str) -> str:
        """格式化文章列表"""
        markdown_parts = []
        
        for i, article in enumerate(articles, 1):
            article_md = self._format_single_article(article, style, index=i)
            markdown_parts.append(article_md)
        
        return '\n\n'.join(markdown_parts)
    
    def _format_single_article(self, article: Dict[str, Any], style: str, index: int = None) -> str:
        """格式化单篇文章"""
        title = article.get('title', '无标题')
        url = article.get('url', '#')
        summary = article.get('summary', article.get('content', ''))[:200] + '...'
        source = article.get('source', '未知来源')
        published_at = article.get('published_at', '')
        category = article.get('category', '')
        
        # 格式化日期
        date_display = ContentFormatter().format_date(published_at) if published_at else ""
        
        if style == "detailed":
            return f'''
### {f"{index}. " if index else ""}[{title}]({url})

**摘要:** {summary}

**详情:**
- 📰 **来源:** {source}
{f"- 📅 **发布时间:** {date_display}" if date_display else ""}
{f"- 🏷️ **分类:** {category}" if category else ""}

---
            '''
        else:  # standard
            return f'''
{f"{index}. " if index else ""}**[{title}]({url})**

{summary}

*来源: {source}{f" | {date_display}" if date_display else ""}{f" | {category}" if category else ""}*
            '''
    
    def _format_text_content(self, text: str, style: str) -> str:
        """格式化纯文本内容"""
        # 将文本按段落分割
        paragraphs = text.split('\n\n')
        return '\n\n'.join(paragraphs)
    
    def create_table_of_contents(self, sections: List[Dict[str, Any]]) -> str:
        """创建目录"""
        toc_lines = ["## 📑 目录\n"]
        
        for i, section in enumerate(sections, 1):
            title = section.get('title', f'第{i}部分')
            anchor = title.replace(' ', '-').lower()
            article_count = len(section.get('articles', []))
            
            toc_lines.append(f"{i}. [{title}](#{anchor}) ({article_count}篇)")
        
        return '\n'.join(toc_lines)
    
    def format_stats(self, stats: Dict[str, Any]) -> str:
        """格式化统计信息"""
        return f'''
**📊 本期统计**

| 指标 | 数值 |
|------|------|
| 文章总数 | {stats.get('total_articles', 0)} |
| 分类数量 | {stats.get('total_sections', 0)} |
| 数据源 | {stats.get('sources_count', 0)} |
| 生成时间 | {stats.get('generated_at', 'N/A')} |
| 语言 | {stats.get('language', '中文')} |
        '''


class CategoryFormatter:
    """分类格式化器"""
    
    CATEGORY_EMOJIS = {
        'tech': '💻',
        'business': '💼', 
        'health': '🏥',
        'sports': '⚽',
        'entertainment': '🎬',
        'science': '🔬',
        'politics': '🏛️',
        'general': '📰',
        'world': '🌍',
        'local': '🏙️'
    }
    
    CATEGORY_NAMES = {
        'tech': '科技',
        'business': '商业',
        'health': '健康',
        'sports': '体育',
        'entertainment': '娱乐',
        'science': '科学',
        'politics': '政治',
        'general': '综合',
        'world': '国际',
        'local': '本地'
    }
    
    def format_category_title(self, category: str) -> str:
        """格式化分类标题"""
        emoji = self.CATEGORY_EMOJIS.get(category.lower(), '📰')
        name = self.CATEGORY_NAMES.get(category.lower(), category.title())
        return f"{emoji} {name}"
    
    def get_category_description(self, category: str) -> str:
        """获取分类描述"""
        descriptions = {
            'tech': '最新科技动态和创新趋势',
            'business': '商业新闻和市场分析',
            'health': '健康资讯和医疗进展',
            'sports': '体育赛事和运动新闻',
            'entertainment': '娱乐资讯和文化动态',
            'science': '科学发现和研究成果',
            'politics': '政治新闻和政策动态',
            'general': '综合新闻和社会热点',
            'world': '国际新闻和全球动态',
            'local': '本地新闻和社区资讯'
        }
        return descriptions.get(category.lower(), '相关新闻资讯')
    
    def sort_categories_by_priority(self, categories: List[str]) -> List[str]:
        """按优先级排序分类"""
        priority_order = ['tech', 'business', 'world', 'science', 'health', 'sports', 'entertainment', 'politics', 'local', 'general']
        
        # 创建优先级映射
        priority_map = {cat: i for i, cat in enumerate(priority_order)}
        
        # 排序，未知分类放在最后
        return sorted(categories, key=lambda x: priority_map.get(x.lower(), 999)) 