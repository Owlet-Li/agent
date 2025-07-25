# -*- coding: utf-8 -*-
"""
Newsletter Agent - NewsAPI数据源
实现新闻API的数据获取和处理功能
"""

import time
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

try:
    from newsapi import NewsApiClient
    from loguru import logger
except ImportError:
    logger = logging.getLogger(__name__)
    NewsApiClient = None

try:
    from newsletter_agent.config.settings import settings
except ImportError:
    class MockSettings:
        NEWSAPI_KEY = None
        DEFAULT_NEWS_SOURCES = ["bbc-news", "cnn", "reuters"]
        MAX_ARTICLES_PER_SOURCE = 10
        CONTENT_LANGUAGE = "zh"
    settings = MockSettings()


@dataclass
class NewsArticle:
    """新闻文章数据结构"""
    title: str
    description: Optional[str]
    content: Optional[str]
    url: str
    source: str
    published_at: datetime
    author: Optional[str] = None
    category: Optional[str] = None
    language: str = "en"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'url': self.url,
            'source': self.source,
            'published_at': self.published_at.isoformat(),
            'author': self.author,
            'category': self.category,
            'language': self.language
        }


class NewsAPIClient:
    """
    NewsAPI客户端
    提供新闻数据获取、过滤和处理功能
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化NewsAPI客户端
        
        Args:
            api_key: NewsAPI密钥，如果不提供则从配置中获取
        """
        self.api_key = api_key or settings.NEWSAPI_KEY
        self.client = None
        self.last_request_time = 0
        self.request_delay = 1.0  # 请求间隔（秒）
        
        if self.api_key and NewsApiClient:
            try:
                self.client = NewsApiClient(api_key=self.api_key)
                logger.info("NewsAPI客户端初始化成功")
            except Exception as e:
                logger.error(f"NewsAPI客户端初始化失败: {e}")
        else:
            logger.warning("NewsAPI客户端未初始化：缺少API密钥或依赖项")
    
    def _rate_limit(self):
        """实现请求速率限制"""
        now = time.time()
        time_since_last = now - self.last_request_time
        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def _clean_content(self, content: str) -> str:
        """清理新闻内容"""
        if not content:
            return ""
        
        # 移除常见的无用后缀
        suffixes_to_remove = [
            " [+chars]", "...", " chars]", " characters]"
        ]
        
        for suffix in suffixes_to_remove:
            if content.endswith(suffix):
                content = content[:-len(suffix)]
        
        return content.strip()
    
    def _parse_article(self, article_data: Dict[str, Any], source: str = "newsapi") -> NewsArticle:
        """解析单个新闻文章数据"""
        try:
            published_at = datetime.fromisoformat(
                article_data['publishedAt'].replace('Z', '+00:00')
            )
        except (ValueError, KeyError):
            published_at = datetime.now()
        
        return NewsArticle(
            title=article_data.get('title', ''),
            description=article_data.get('description', ''),
            content=self._clean_content(article_data.get('content', '')),
            url=article_data.get('url', ''),
            source=source,
            published_at=published_at,
            author=article_data.get('author'),
            language=article_data.get('language', 'en')
        )
    
    def get_top_headlines(
        self, 
        sources: Optional[List[str]] = None,
        category: Optional[str] = None,
        country: str = 'us',
        page_size: int = 20
    ) -> List[NewsArticle]:
        """
        获取头条新闻
        
        Args:
            sources: 新闻源列表
            category: 新闻类别
            country: 国家代码
            page_size: 每页文章数量
            
        Returns:
            List[NewsArticle]: 新闻文章列表
        """
        if not self.client:
            logger.error("NewsAPI客户端未初始化")
            return []
        
        self._rate_limit()
        
        try:
            logger.info(f"获取头条新闻: sources={sources}, category={category}")
            
            response = self.client.get_top_headlines(
                sources=','.join(sources) if sources else None,
                category=category,
                country=country if not sources else None,
                page_size=min(page_size, 100)  # API限制
            )
            
            if response['status'] != 'ok':
                logger.error(f"NewsAPI请求失败: {response}")
                return []
            
            articles = []
            for article_data in response.get('articles', []):
                if article_data.get('title') and article_data.get('url'):
                    article = self._parse_article(article_data)
                    articles.append(article)
            
            logger.info(f"成功获取 {len(articles)} 篇头条新闻")
            return articles
            
        except Exception as e:
            logger.error(f"获取头条新闻失败: {e}")
            return []
    
    def search_everything(
        self,
        query: str,
        sources: Optional[List[str]] = None,
        domains: Optional[List[str]] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        language: str = 'en',
        sort_by: str = 'publishedAt',
        page_size: int = 20
    ) -> List[NewsArticle]:
        """
        搜索所有新闻
        
        Args:
            query: 搜索关键词
            sources: 新闻源列表
            domains: 域名列表
            from_date: 开始日期
            to_date: 结束日期
            language: 语言代码
            sort_by: 排序方式
            page_size: 每页文章数量
            
        Returns:
            List[NewsArticle]: 新闻文章列表
        """
        if not self.client:
            logger.error("NewsAPI客户端未初始化")
            return []
        
        self._rate_limit()
        
        try:
            logger.info(f"搜索新闻: query='{query}', sources={sources}")
            
            response = self.client.get_everything(
                q=query,
                sources=','.join(sources) if sources else None,
                domains=','.join(domains) if domains else None,
                from_param=from_date.isoformat() if from_date else None,
                to=to_date.isoformat() if to_date else None,
                language=language,
                sort_by=sort_by,
                page_size=min(page_size, 100)
            )
            
            if response['status'] != 'ok':
                logger.error(f"NewsAPI搜索失败: {response}")
                return []
            
            articles = []
            for article_data in response.get('articles', []):
                if article_data.get('title') and article_data.get('url'):
                    article = self._parse_article(
                        article_data, 
                        source=f"newsapi-search:{query}"
                    )
                    articles.append(article)
            
            logger.info(f"搜索到 {len(articles)} 篇相关新闻")
            return articles
            
        except Exception as e:
            logger.error(f"搜索新闻失败: {e}")
            return []
    
    def get_sources(self, category: Optional[str] = None, language: str = 'en') -> List[Dict[str, Any]]:
        """
        获取可用新闻源
        
        Args:
            category: 类别过滤
            language: 语言过滤
            
        Returns:
            List[Dict]: 新闻源列表
        """
        if not self.client:
            logger.error("NewsAPI客户端未初始化")
            return []
        
        self._rate_limit()
        
        try:
            response = self.client.get_sources(
                category=category,
                language=language
            )
            
            if response['status'] != 'ok':
                logger.error(f"获取新闻源失败: {response}")
                return []
            
            sources = response.get('sources', [])
            logger.info(f"获取到 {len(sources)} 个新闻源")
            return sources
            
        except Exception as e:
            logger.error(f"获取新闻源失败: {e}")
            return []
    
    def get_recent_news_by_topics(
        self, 
        topics: List[str], 
        hours_back: int = 24,
        max_articles_per_topic: int = 10
    ) -> Dict[str, List[NewsArticle]]:
        """
        根据话题获取最近的新闻
        
        Args:
            topics: 话题关键词列表
            hours_back: 向前搜索的小时数
            max_articles_per_topic: 每个话题的最大文章数
            
        Returns:
            Dict[str, List[NewsArticle]]: 按话题分组的新闻文章
        """
        from_date = datetime.now() - timedelta(hours=hours_back)
        
        results = {}
        for topic in topics:
            logger.info(f"搜索话题: {topic}")
            articles = self.search_everything(
                query=topic,
                from_date=from_date,
                language='en',  # 先获取英文新闻，后续可以翻译
                sort_by='publishedAt',
                page_size=max_articles_per_topic
            )
            results[topic] = articles[:max_articles_per_topic]
        
        return results
    
    def is_available(self) -> bool:
        """检查NewsAPI是否可用"""
        return self.client is not None and self.api_key is not None


# 创建全局实例
news_client = NewsAPIClient() 