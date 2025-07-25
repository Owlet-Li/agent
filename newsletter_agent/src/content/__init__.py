# -*- coding: utf-8 -*-
"""
Newsletter Agent - 内容处理模块
内容分析、处理、格式化和分类功能
"""

# 导入核心处理类
from .text_processor import TextProcessor
from .content_formatter import ContentFormatter, FormattedContent
from .deduplicator import ContentDeduplicator
from .classifier import ContentClassifier

# 创建全局实例
text_processor = TextProcessor()
content_formatter = ContentFormatter()
content_deduplicator = ContentDeduplicator()
content_classifier = ContentClassifier()

# 导出所有类和实例
__all__ = [
    # 类
    'TextProcessor',
    'ContentFormatter',
    'FormattedContent',
    'ContentDeduplicator',
    'ContentClassifier',
    
    # 全局实例
    'text_processor',
    'content_formatter',
    'content_deduplicator',
    'content_classifier'
] 