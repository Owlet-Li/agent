# -*- coding: utf-8 -*-
"""
Newsletter Agent - 新闻简报模板引擎
提供专业的HTML和Markdown格式模板
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import json

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


@dataclass
class NewsletterSection:
    """简报章节数据结构"""
    title: str
    articles: List[Dict[str, Any]]
    category: str
    priority: int = 1
    summary: Optional[str] = None


@dataclass
class NewsletterData:
    """简报数据结构"""
    title: str
    subtitle: str
    sections: List[NewsletterSection]
    metadata: Dict[str, Any]
    generated_at: datetime
    user_preferences: Optional[Dict[str, Any]] = None


class NewsletterTemplateEngine:
    """新闻简报模板引擎"""
    
    def __init__(self):
        self.templates = {
            'html': self._load_html_templates(),
            'markdown': self._load_markdown_templates()
        }
        logger.info("简报模板引擎初始化完成")
    
    def _load_html_templates(self) -> Dict[str, str]:
        """加载HTML模板"""
        return {
            'professional': '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .newsletter-container {{
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0;
            opacity: 0.9;
            font-size: 1.2em;
        }}
        .content {{
            padding: 30px;
        }}
        .section {{
            margin-bottom: 40px;
            border-bottom: 2px solid #eee;
            padding-bottom: 30px;
        }}
        .section:last-child {{
            border-bottom: none;
        }}
        .section-title {{
            color: #667eea;
            font-size: 1.8em;
            margin-bottom: 20px;
            border-left: 4px solid #667eea;
            padding-left: 15px;
        }}
        .article {{
            margin-bottom: 25px;
            padding: 20px;
            background-color: #fafafa;
            border-radius: 8px;
            border-left: 4px solid #764ba2;
        }}
        .article-title {{
            font-size: 1.3em;
            font-weight: 600;
            margin-bottom: 10px;
            color: #333;
        }}
        .article-title a {{
            text-decoration: none;
            color: #333;
            transition: color 0.3s;
        }}
        .article-title a:hover {{
            color: #667eea;
        }}
        .article-summary {{
            color: #666;
            margin-bottom: 15px;
            line-height: 1.7;
        }}
        .article-meta {{
            font-size: 0.9em;
            color: #999;
            border-top: 1px solid #ddd;
            padding-top: 10px;
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 20px 30px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        .stats {{
            background-color: #e7f3ff;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
        }}
        .category-tag {{
            display: inline-block;
            background-color: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.8em;
            margin-right: 10px;
        }}
    </style>
</head>
<body>
    <div class="newsletter-container">
        <div class="header">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        
        <div class="content">
            <div class="stats">
                <strong>📊 本期统计:</strong> 共 {total_articles} 篇文章 | {total_sections} 个分类 | 生成时间: {generated_at}
            </div>
            
            {sections_html}
        </div>
        
        <div class="footer">
            <p>🤖 由 Newsletter Agent 智能生成 | 📧 如需调整偏好设置或取消订阅，请联系管理员</p>
            <p>数据来源: NewsAPI, Reddit, RSS Feeds | Powered by OpenRouter AI</p>
        </div>
    </div>
</body>
</html>
            ''',
            
            'casual': '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Comic Sans MS', cursive, sans-serif;
            line-height: 1.6;
            color: #444;
            max-width: 700px;
            margin: 0 auto;
            padding: 15px;
            background: linear-gradient(45deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
        }}
        .newsletter-container {{
            background-color: white;
            border-radius: 20px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #ff6b6b, #feca57);
            color: white;
            padding: 25px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.2em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .content {{
            padding: 25px;
        }}
        .section {{
            margin-bottom: 30px;
            background: linear-gradient(135deg, #667eea20, #764ba220);
            border-radius: 15px;
            padding: 20px;
        }}
        .section-title {{
            color: #ff6b6b;
            font-size: 1.6em;
            margin-bottom: 15px;
            text-align: center;
        }}
        .article {{
            margin-bottom: 20px;
            padding: 15px;
            background-color: white;
            border-radius: 10px;
            border: 2px solid #feca57;
        }}
        .article-title {{
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 8px;
            color: #ff6b6b;
        }}
        .footer {{
            background: linear-gradient(135deg, #ff6b6b, #feca57);
            padding: 15px;
            text-align: center;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="newsletter-container">
        <div class="header">
            <h1>🎉 {title} 🎉</h1>
            <p>✨ {subtitle} ✨</p>
        </div>
        
        <div class="content">
            {sections_html}
        </div>
        
        <div class="footer">
            <p>😊 希望您喜欢今天的内容! 💖</p>
        </div>
    </div>
</body>
</html>
            '''
        }
    
    def _load_markdown_templates(self) -> Dict[str, str]:
        """加载Markdown模板"""
        return {
            'standard': '''
# {title}

> {subtitle}

**📊 本期统计:** {total_articles} 篇文章 | {total_sections} 个分类 | 生成时间: {generated_at}

---

{sections_markdown}

---

**🤖 Newsletter Agent 智能生成**
- 数据来源: NewsAPI, Reddit, RSS Feeds
- AI驱动: OpenRouter API
- 个性化推荐基于您的偏好设置

*如需调整偏好或取消订阅，请联系管理员*
            ''',
            
            'detailed': '''
# 📰 {title}

## 📋 简报概览

**主题:** {subtitle}  
**生成时间:** {generated_at}  
**文章总数:** {total_articles}  
**分类数量:** {total_sections}  

---

## 📑 目录

{table_of_contents}

---

{sections_markdown}

---

## 📈 本期亮点

{highlights}

## 🔗 相关链接

- [NewsAPI](https://newsapi.org/) - 实时新闻数据
- [Reddit](https://reddit.com/) - 社区讨论
- [OpenRouter](https://openrouter.ai/) - AI内容生成

---

**⚙️ 技术信息**  
本简报由 Newsletter Agent 使用 LangChain 和多个数据源智能生成。内容经过去重、分类和质量评估。

*📧 邮件发送 | 🎯 个性化推荐 | 🤖 AI驱动*
            '''
        }
    
    def generate_newsletter(
        self,
        data: NewsletterData,
        template_style: str = "professional",
        output_format: str = "html"
    ) -> str:
        """生成完整的新闻简报"""
        try:
            if output_format == "html":
                return self._generate_html_newsletter(data, template_style)
            elif output_format == "markdown":
                return self._generate_markdown_newsletter(data, template_style)
            else:
                raise ValueError(f"不支持的输出格式: {output_format}")
                
        except Exception as e:
            logger.error(f"简报生成失败: {e}")
            return self._generate_error_newsletter(str(e))
    
    def _generate_html_newsletter(self, data: NewsletterData, style: str) -> str:
        """生成HTML格式简报"""
        template = self.templates['html'].get(style, self.templates['html']['professional'])
        
        # 生成章节HTML
        sections_html = ""
        for section in sorted(data.sections, key=lambda x: x.priority):
            sections_html += f'''
            <div class="section">
                <h2 class="section-title">
                    <span class="category-tag">{section.category}</span>
                    {section.title}
                </h2>
                {f'<p class="section-summary">{section.summary}</p>' if section.summary else ''}
                
                <div class="articles">
            '''
            
            for article in section.articles:
                article_html = f'''
                <div class="article">
                    <h3 class="article-title">
                        <a href="{article.get('url', '#')}" target="_blank">
                            {article.get('title', '无标题')}
                        </a>
                    </h3>
                    <div class="article-summary">
                        {article.get('summary', article.get('content', '')[:200] + '...')}
                    </div>
                    <div class="article-meta">
                        <span>📰 来源: {article.get('source', '未知')}</span>
                        {f" | 📅 {article.get('published_at', '')}" if article.get('published_at') else ""}
                        {f" | 🏷️ {article.get('category', '')}" if article.get('category') else ""}
                    </div>
                </div>
                '''
                sections_html += article_html
            
            sections_html += "</div></div>"
        
        # 填充模板变量
        return template.format(
            title=data.title,
            subtitle=data.subtitle,
            total_articles=sum(len(section.articles) for section in data.sections),
            total_sections=len(data.sections),
            generated_at=data.generated_at.strftime("%Y年%m月%d日 %H:%M"),
            sections_html=sections_html
        )
    
    def _generate_markdown_newsletter(self, data: NewsletterData, style: str) -> str:
        """生成Markdown格式简报"""
        template = self.templates['markdown'].get(style, self.templates['markdown']['standard'])
        
        # 生成章节Markdown
        sections_markdown = ""
        table_of_contents = ""
        highlights = []
        
        for i, section in enumerate(sorted(data.sections, key=lambda x: x.priority), 1):
            # 目录
            table_of_contents += f"{i}. [{section.title}](#{section.title.replace(' ', '-').lower()})\n"
            
            # 章节内容
            sections_markdown += f"\n## {i}. {section.title}\n\n"
            if section.summary:
                sections_markdown += f"*{section.summary}*\n\n"
            
            # 文章列表
            for j, article in enumerate(section.articles, 1):
                title = article.get('title', '无标题')
                url = article.get('url', '#')
                summary = article.get('summary', article.get('content', ''))[:150] + '...'
                source = article.get('source', '未知来源')
                
                sections_markdown += f"### {i}.{j} [{title}]({url})\n\n"
                sections_markdown += f"{summary}\n\n"
                sections_markdown += f"**来源:** {source}"
                
                if article.get('published_at'):
                    sections_markdown += f" | **时间:** {article.get('published_at')}"
                
                sections_markdown += "\n\n---\n\n"
                
                # 收集亮点
                if len(highlights) < 3:
                    highlights.append(f"- **{title}** - {summary[:100]}...")
        
        # 生成亮点
        highlights_text = "\n".join(highlights) if highlights else "本期内容精彩丰富，涵盖多个重要话题。"
        
        # 填充模板变量
        return template.format(
            title=data.title,
            subtitle=data.subtitle,
            total_articles=sum(len(section.articles) for section in data.sections),
            total_sections=len(data.sections),
            generated_at=data.generated_at.strftime("%Y年%m月%d日 %H:%M"),
            sections_markdown=sections_markdown,
            table_of_contents=table_of_contents,
            highlights=highlights_text
        )
    
    def _generate_error_newsletter(self, error_msg: str) -> str:
        """生成错误简报"""
        return f"""
# ❌ 简报生成失败

很抱歉，在生成简报时遇到了问题：

**错误信息:** {error_msg}

请稍后重试或联系技术支持。

---

**🤖 Newsletter Agent**  
*智能新闻简报生成系统*
        """
    
    def create_newsletter_data(
        self,
        title: str,
        subtitle: str,
        content_sections: List[Dict[str, Any]],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> NewsletterData:
        """创建简报数据结构"""
        sections = []
        
        for section_data in content_sections:
            section = NewsletterSection(
                title=section_data.get('title', '未分类'),
                articles=section_data.get('articles', []),
                category=section_data.get('category', 'general'),
                priority=section_data.get('priority', 1),
                summary=section_data.get('summary')
            )
            sections.append(section)
        
        return NewsletterData(
            title=title,
            subtitle=subtitle,
            sections=sections,
            metadata={
                'generator': 'Newsletter Agent',
                'version': '1.0.0',
                'ai_powered': True
            },
            generated_at=datetime.now(),
            user_preferences=user_preferences
        )
    
    def get_available_templates(self) -> Dict[str, List[str]]:
        """获取可用模板列表"""
        return {
            'html': list(self.templates['html'].keys()),
            'markdown': list(self.templates['markdown'].keys())
        } 