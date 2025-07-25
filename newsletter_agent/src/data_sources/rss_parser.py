# -*- coding: utf-8 -*-
"""
Newsletter Agent - RSS Feed解析器
实现RSS源的数据获取和处理功能
"""

import time
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
from urllib.parse import urljoin, urlparse

try:
    import feedparser
    from bs4 import BeautifulSoup
    from loguru import logger
except ImportError:
    logger = logging.getLogger(__name__)
    feedparser = None
    BeautifulSoup = None

try:
    from newsletter_agent.config.settings import settings
except ImportError:
    class MockSettings:
        DEFAULT_RSS_FEEDS = [
            "https://feeds.bbci.co.uk/news/rss.xml",
            "http://rss.cnn.com/rss/edition.rss"
        ]
        MAX_ARTICLES_PER_SOURCE = 10
    settings = MockSettings()


@dataclass 
class RSSArticle:
    """RSS文章数据结构"""
    title: str
    description: Optional[str]
    content: Optional[str]
    url: str
    feed_name: str
    feed_url: str
    published: datetime
    author: Optional[str] = None
    category: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'url': self.url,
            'feed_name': self.feed_name,
            'feed_url': self.feed_url,
            'published': self.published.isoformat(),
            'author': self.author,
            'category': self.category
        }


class RSSParser:
    """
    RSS解析器
    提供RSS feed的获取、解析和内容提取功能
    """
    
    def __init__(self):
        """初始化RSS解析器"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Newsletter Agent RSS Reader/1.0'
        })
        self.last_request_time = 0
        self.request_delay = 1.0  # 请求间隔
        
        self.timeout = 30  # 请求超时时间
        
        if not feedparser:
            logger.warning("feedparser未安装，RSS功能可能受限")
        if not BeautifulSoup:
            logger.warning("BeautifulSoup未安装，HTML解析功能可能受限")
    
    def _rate_limit(self):
        """实现请求速率限制"""
        now = time.time()
        time_since_last = now - self.last_request_time
        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def _clean_html(self, html_content: str) -> str:
        """清理HTML内容，提取纯文本"""
        if not html_content or not BeautifulSoup:
            return html_content or ""
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 移除脚本和样式元素
            for script in soup(["script", "style"]):
                script.extract()
            
            # 获取文本并清理
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text[:1000]  # 限制长度
            
        except Exception as e:
            logger.warning(f"HTML清理失败: {e}")
            return html_content
    
    def _parse_date(self, date_str: str) -> datetime:
        """解析日期字符串"""
        try:
            # feedparser通常会解析时间元组
            if hasattr(feedparser, 'time') and date_str:
                parsed_time = feedparser._parse_date(date_str)
                if parsed_time:
                    return datetime(*parsed_time[:6])
        except:
            pass
        
        # 回退到当前时间
        return datetime.now()
    
    def _parse_entry(self, entry, feed_info: Dict[str, Any]) -> RSSArticle:
        """解析单个RSS条目"""
        try:
            # 获取发布时间
            published = datetime.now()
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                try:
                    published = datetime(*entry.published_parsed[:6])
                except:
                    pass
            elif hasattr(entry, 'published'):
                published = self._parse_date(entry.published)
            
            # 获取内容
            content = ""
            if hasattr(entry, 'content') and entry.content:
                content = self._clean_html(entry.content[0].value)
            elif hasattr(entry, 'summary'):
                content = self._clean_html(entry.summary)
            elif hasattr(entry, 'description'):
                content = self._clean_html(entry.description)
            
            # 获取描述
            description = ""
            if hasattr(entry, 'summary'):
                description = self._clean_html(entry.summary)[:300]
            elif hasattr(entry, 'description'):
                description = self._clean_html(entry.description)[:300]
            
            # 获取分类
            category = None
            if hasattr(entry, 'tags') and entry.tags:
                category = entry.tags[0].get('term', '')
            
            return RSSArticle(
                title=getattr(entry, 'title', '').strip(),
                description=description,
                content=content,
                url=getattr(entry, 'link', ''),
                feed_name=feed_info.get('title', 'Unknown Feed'),
                feed_url=feed_info.get('url', ''),
                published=published,
                author=getattr(entry, 'author', None),
                category=category
            )
            
        except Exception as e:
            logger.error(f"解析RSS条目失败: {e}")
            # 返回基本信息
            return RSSArticle(
                title=getattr(entry, 'title', 'Untitled'),
                description=None,
                content=None,
                url=getattr(entry, 'link', ''),
                feed_name=feed_info.get('title', 'Unknown Feed'),
                feed_url=feed_info.get('url', ''),
                published=datetime.now()
            )
    
    def fetch_feed(self, feed_url: str, max_articles: int = 20) -> List[RSSArticle]:
        """
        获取单个RSS feed
        
        Args:
            feed_url: RSS feed URL
            max_articles: 最大文章数量
            
        Returns:
            List[RSSArticle]: RSS文章列表
        """
        if not feedparser:
            logger.error("feedparser未安装，无法解析RSS")
            return []
        
        self._rate_limit()
        
        try:
            logger.info(f"获取RSS feed: {feed_url}")
            
            # 获取RSS内容
            response = self.session.get(feed_url, timeout=self.timeout)
            response.raise_for_status()
            
            # 解析RSS
            feed = feedparser.parse(response.content)
            
            if feed.bozo and feed.bozo_exception:
                logger.warning(f"RSS解析警告: {feed.bozo_exception}")
            
            # 获取feed信息
            feed_info = {
                'title': getattr(feed.feed, 'title', 'Unknown Feed'),
                'url': feed_url,
                'description': getattr(feed.feed, 'description', ''),
                'link': getattr(feed.feed, 'link', '')
            }
            
            # 解析条目
            articles = []
            for entry in feed.entries[:max_articles]:
                try:
                    article = self._parse_entry(entry, feed_info)
                    if article.title and article.url:  # 确保有基本信息
                        articles.append(article)
                except Exception as e:
                    logger.warning(f"跳过无效条目: {e}")
                    continue
            
            logger.info(f"成功解析 {len(articles)} 篇文章 from {feed_info['title']}")
            return articles
            
        except requests.RequestException as e:
            logger.error(f"获取RSS feed失败 {feed_url}: {e}")
            return []
        except Exception as e:
            logger.error(f"解析RSS feed失败 {feed_url}: {e}")
            return []
    
    def fetch_multiple_feeds(
        self, 
        feed_urls: List[str], 
        max_articles_per_feed: int = 10
    ) -> Dict[str, List[RSSArticle]]:
        """
        获取多个RSS feeds
        
        Args:
            feed_urls: RSS feed URL列表
            max_articles_per_feed: 每个feed的最大文章数
            
        Returns:
            Dict[str, List[RSSArticle]]: 按feed分组的文章
        """
        results = {}
        
        for feed_url in feed_urls:
            try:
                articles = self.fetch_feed(feed_url, max_articles_per_feed)
                if articles:
                    feed_name = articles[0].feed_name if articles else feed_url
                    results[feed_name] = articles
                else:
                    logger.warning(f"未获取到文章: {feed_url}")
            except Exception as e:
                logger.error(f"处理feed失败 {feed_url}: {e}")
                continue
        
        return results
    
    def search_feeds_by_keywords(
        self,
        feed_urls: List[str],
        keywords: List[str],
        max_articles_per_feed: int = 20
    ) -> Dict[str, List[RSSArticle]]:
        """
        在RSS feeds中搜索关键词
        
        Args:
            feed_urls: RSS feed URL列表
            keywords: 关键词列表
            max_articles_per_feed: 每个feed的最大搜索文章数
            
        Returns:
            Dict[str, List[RSSArticle]]: 包含关键词的文章
        """
        keyword_lower = [kw.lower() for kw in keywords]
        results = {}
        
        feeds_data = self.fetch_multiple_feeds(feed_urls, max_articles_per_feed)
        
        for feed_name, articles in feeds_data.items():
            matching_articles = []
            
            for article in articles:
                # 在标题、描述和内容中搜索关键词
                search_text = f"{article.title} {article.description or ''} {article.content or ''}".lower()
                
                if any(keyword in search_text for keyword in keyword_lower):
                    matching_articles.append(article)
            
            if matching_articles:
                results[feed_name] = matching_articles
        
        return results
    
    def get_recent_articles(
        self,
        feed_urls: Optional[List[str]] = None,
        hours_back: int = 24,
        max_articles_per_feed: int = 10
    ) -> List[RSSArticle]:
        """
        获取最近的文章
        
        Args:
            feed_urls: RSS feed URL列表，如果为None则使用默认feeds
            hours_back: 向前搜索的小时数
            max_articles_per_feed: 每个feed的最大文章数
            
        Returns:
            List[RSSArticle]: 最近的文章列表
        """
        if feed_urls is None:
            feed_urls = settings.DEFAULT_RSS_FEEDS
        
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        recent_articles = []
        
        feeds_data = self.fetch_multiple_feeds(feed_urls, max_articles_per_feed)
        
        for articles in feeds_data.values():
            for article in articles:
                if article.published >= cutoff_time:
                    recent_articles.append(article)
        
        # 按发布时间排序
        recent_articles.sort(key=lambda x: x.published, reverse=True)
        
        return recent_articles
    
    def get_feeds_info(self, feed_urls: List[str]) -> List[Dict[str, Any]]:
        """
        获取RSS feeds的基本信息
        
        Args:
            feed_urls: RSS feed URL列表
            
        Returns:
            List[Dict]: feeds信息列表
        """
        feeds_info = []
        
        for feed_url in feed_urls:
            try:
                self._rate_limit()
                response = self.session.get(feed_url, timeout=self.timeout)
                response.raise_for_status()
                
                if feedparser:
                    feed = feedparser.parse(response.content)
                    
                    info = {
                        'url': feed_url,
                        'title': getattr(feed.feed, 'title', 'Unknown'),
                        'description': getattr(feed.feed, 'description', ''),
                        'link': getattr(feed.feed, 'link', ''),
                        'language': getattr(feed.feed, 'language', ''),
                        'updated': getattr(feed.feed, 'updated', ''),
                        'total_entries': len(feed.entries)
                    }
                    feeds_info.append(info)
                    
            except Exception as e:
                logger.error(f"获取feed信息失败 {feed_url}: {e}")
                feeds_info.append({
                    'url': feed_url,
                    'title': 'Error',
                    'error': str(e)
                })
        
        return feeds_info
    
    def is_available(self) -> bool:
        """检查RSS解析器是否可用"""
        return feedparser is not None


# 创建全局实例
rss_parser = RSSParser() 