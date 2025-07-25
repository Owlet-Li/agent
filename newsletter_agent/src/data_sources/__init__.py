# -*- coding: utf-8 -*-
"""
Newsletter Agent - 数据源模块
多种数据源的集成和管理
"""

# 导入数据结构
from .news_api import NewsArticle, NewsAPIClient, news_client
from .reddit_api import RedditPost, RedditAPIClient, reddit_client
from .rss_parser import RSSArticle, RSSParser, rss_parser
from .aggregator import UnifiedContent, ImprovedDataAggregator, data_aggregator

# 导出主要接口
__all__ = [
    # 数据结构
    'NewsArticle',
    'RedditPost', 
    'RSSArticle',
    'UnifiedContent',
    
    # 客户端类
    'NewsAPIClient',
    'RedditAPIClient',
    'RSSParser',
    'ImprovedDataAggregator',
    
    # 全局实例
    'news_client',
    'reddit_client',
    'rss_parser',
    'data_aggregator'
] 