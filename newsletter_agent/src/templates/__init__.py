# -*- coding: utf-8 -*-
"""
Newsletter Agent - 模板系统
提供HTML和Markdown格式的简报模板
"""

from .newsletter_templates import NewsletterTemplateEngine
from .email_templates import EmailTemplateEngine
from .formatting_utils import ContentFormatter, HTMLFormatter, MarkdownFormatter

__all__ = [
    'NewsletterTemplateEngine',
    'EmailTemplateEngine', 
    'ContentFormatter',
    'HTMLFormatter',
    'MarkdownFormatter'
]

# 全局模板引擎实例
newsletter_template_engine = NewsletterTemplateEngine()
email_template_engine = EmailTemplateEngine()
content_formatter = ContentFormatter()
html_formatter = HTMLFormatter()
markdown_formatter = MarkdownFormatter() 