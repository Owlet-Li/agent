# -*- coding: utf-8 -*-
"""
Newsletter Agent - 数据源聚合器
统一管理和聚合多个数据源的内容获取
"""

import asyncio
import time
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from loguru import logger
except ImportError:
    logger = logging.getLogger(__name__)

try:
    from newsletter_agent.config.settings import settings
    from .news_api import news_client, NewsArticle
    from .reddit_api import reddit_client, RedditPost
    from .rss_parser import rss_parser, RSSArticle
except ImportError:
    logger.warning("数据源模块导入失败，使用模拟数据")
    settings = None
    news_client = None
    reddit_client = None
    rss_parser = None


@dataclass
class UnifiedContent:
    """统一的内容数据结构"""
    title: str
    content: str
    url: str
    source: str
    source_type: str  # 'news', 'reddit', 'rss'
    published_at: datetime
    author: Optional[str] = None
    category: Optional[str] = None
    score: Optional[int] = None  # Reddit评分
    engagement: Optional[int] = None  # 互动数（评论数等）
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'title': self.title,
            'content': self.content,
            'url': self.url,
            'source': self.source,
            'source_type': self.source_type,
            'published_at': self.published_at.isoformat(),
            'author': self.author,
            'category': self.category,
            'score': self.score,
            'engagement': self.engagement
        }


class ImprovedDataAggregator:
    """
    改进的数据聚合器
    参考AI研究代理模式，实现多源数据聚合和故障恢复
    """
    
    def __init__(self):
        """初始化数据聚合器"""
        self.news_client = news_client
        self.reddit_client = reddit_client
        self.rss_parser = rss_parser
        
        # 请求速率限制
        self.last_request_times = {}
        self.default_delay = 2.0
        
        # 线程池用于并行处理
        self.max_workers = 5
        
        # 数据源优先级（分数越高优先级越高）
        self.source_priorities = {
            'news': 3,
            'rss': 2, 
            'reddit': 1
        }
        
        logger.info("数据聚合器初始化完成")
    
    def _rate_limit(self, source_type: str):
        """按数据源类型实现速率限制"""
        now = time.time()
        last_time = self.last_request_times.get(source_type, 0)
        
        if now - last_time < self.default_delay:
            sleep_time = self.default_delay - (now - last_time)
            time.sleep(sleep_time)
        
        self.last_request_times[source_type] = time.time()
    
    def _convert_news_article(self, article: 'NewsArticle') -> UnifiedContent:
        """转换NewsAPI文章为统一格式"""
        return UnifiedContent(
            title=article.title,
            content=article.description or article.content or "",
            url=article.url,
            source=article.source,
            source_type='news',
            published_at=article.published_at,
            author=article.author,
            category=article.category
        )
    
    def _convert_reddit_post(self, post: 'RedditPost') -> UnifiedContent:
        """转换Reddit帖子为统一格式"""
        content = post.selftext if post.is_self else post.content
        return UnifiedContent(
            title=post.title,
            content=content or "",
            url=post.url,
            source=f"reddit/r/{post.subreddit}",
            source_type='reddit',
            published_at=post.created_utc,
            author=post.author,
            score=post.score,
            engagement=post.num_comments
        )
    
    def _convert_rss_article(self, article: 'RSSArticle') -> UnifiedContent:
        """转换RSS文章为统一格式"""
        return UnifiedContent(
            title=article.title,
            content=article.description or article.content or "",
            url=article.url,
            source=article.feed_name,
            source_type='rss',
            published_at=article.published,
            author=article.author,
            category=article.category
        )
    
    def safe_news_search(self, query: str, max_articles: int = 10) -> List[UnifiedContent]:
        """
        安全的新闻搜索（带故障恢复）
        
        Args:
            query: 搜索查询
            max_articles: 最大文章数
            
        Returns:
            List[UnifiedContent]: 统一格式的内容列表
        """
        if not self.news_client or not self.news_client.is_available():
            logger.warning("NewsAPI不可用，跳过新闻搜索")
            return []
        
        try:
            self._rate_limit('news')
            logger.info(f"NewsAPI搜索: {query}")
            
            articles = self.news_client.search_everything(
                query=query,
                page_size=max_articles,
                language='en'
            )
            
            results = [self._convert_news_article(article) for article in articles]
            logger.info(f"NewsAPI返回 {len(results)} 个结果")
            return results
            
        except Exception as e:
            logger.error(f"NewsAPI搜索失败: {e}")
            return []
    
    def safe_reddit_search(self, query: str, subreddits: Optional[List[str]] = None, max_posts: int = 10) -> List[UnifiedContent]:
        """
        安全的Reddit搜索（带故障恢复）
        
        Args:
            query: 搜索查询
            subreddits: 子版块列表
            max_posts: 最大帖子数
            
        Returns:
            List[UnifiedContent]: 统一格式的内容列表
        """
        if not self.reddit_client or not self.reddit_client.is_available():
            logger.warning("Reddit API不可用，跳过Reddit搜索")
            return []
        
        try:
            self._rate_limit('reddit')
            logger.info(f"Reddit搜索: {query}")
            
            results = []
            if subreddits:
                for subreddit in subreddits:
                    posts = self.reddit_client.search_posts(
                        query=query,
                        subreddit_name=subreddit,
                        limit=max_posts // len(subreddits) + 1
                    )
                    results.extend([self._convert_reddit_post(post) for post in posts])
            else:
                posts = self.reddit_client.search_posts(query=query, limit=max_posts)
                results = [self._convert_reddit_post(post) for post in posts]
            
            logger.info(f"Reddit返回 {len(results)} 个结果")
            return results[:max_posts]
            
        except Exception as e:
            logger.error(f"Reddit搜索失败: {e}")
            return []
    
    def safe_rss_search(self, keywords: List[str], feed_urls: Optional[List[str]] = None, max_articles: int = 10) -> List[UnifiedContent]:
        """
        安全的RSS搜索（带故障恢复）
        
        Args:
            keywords: 关键词列表
            feed_urls: RSS feed URL列表
            max_articles: 最大文章数
            
        Returns:
            List[UnifiedContent]: 统一格式的内容列表
        """
        if not self.rss_parser or not self.rss_parser.is_available():
            logger.warning("RSS解析器不可用，跳过RSS搜索")
            return []
        
        try:
            self._rate_limit('rss')
            logger.info(f"RSS搜索: {keywords}")
            
            if feed_urls is None and settings:
                feed_urls = settings.DEFAULT_RSS_FEEDS
            elif feed_urls is None:
                feed_urls = [
                    "https://feeds.bbci.co.uk/news/rss.xml",
                    "http://rss.cnn.com/rss/edition.rss"
                ]
            
            feeds_data = self.rss_parser.search_feeds_by_keywords(
                feed_urls=feed_urls,
                keywords=keywords,
                max_articles_per_feed=max_articles
            )
            
            results = []
            for articles in feeds_data.values():
                results.extend([self._convert_rss_article(article) for article in articles])
            
            logger.info(f"RSS返回 {len(results)} 个结果")
            return results[:max_articles]
            
        except Exception as e:
            logger.error(f"RSS搜索失败: {e}")
            return []
    
    def multi_source_search(
        self,
        query: str,
        sources: Optional[List[str]] = None,
        max_results_per_source: int = 10,
        parallel: bool = True
    ) -> Dict[str, List[UnifiedContent]]:
        """
        多数据源搜索
        
        Args:
            query: 搜索查询
            sources: 要搜索的数据源列表 ['news', 'reddit', 'rss']
            max_results_per_source: 每个数据源的最大结果数
            parallel: 是否并行搜索
            
        Returns:
            Dict[str, List[UnifiedContent]]: 按数据源分组的结果
        """
        if sources is None:
            sources = ['news', 'reddit', 'rss']
        
        logger.info(f"多数据源搜索: query='{query}', sources={sources}")
        
        results = {}
        
        if parallel:
            # 并行搜索
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {}
                
                if 'news' in sources:
                    futures['news'] = executor.submit(
                        self.safe_news_search, query, max_results_per_source
                    )
                
                if 'reddit' in sources:
                    subreddits = settings.DEFAULT_REDDIT_SUBREDDITS if settings else ['technology', 'science']
                    futures['reddit'] = executor.submit(
                        self.safe_reddit_search, query, subreddits, max_results_per_source
                    )
                
                if 'rss' in sources:
                    futures['rss'] = executor.submit(
                        self.safe_rss_search, [query], None, max_results_per_source
                    )
                
                # 收集结果
                for source, future in futures.items():
                    try:
                        results[source] = future.result(timeout=60)  # 60秒超时
                    except Exception as e:
                        logger.error(f"{source}搜索失败: {e}")
                        results[source] = []
        else:
            # 顺序搜索
            if 'news' in sources:
                results['news'] = self.safe_news_search(query, max_results_per_source)
            
            if 'reddit' in sources:
                subreddits = settings.DEFAULT_REDDIT_SUBREDDITS if settings else ['technology', 'science']
                results['reddit'] = self.safe_reddit_search(query, subreddits, max_results_per_source)
            
            if 'rss' in sources:
                results['rss'] = self.safe_rss_search([query], None, max_results_per_source)
        
        # 统计结果
        total_results = sum(len(content_list) for content_list in results.values())
        logger.info(f"多数据源搜索完成: 总共获取 {total_results} 个结果")
        
        return results
    
    def get_trending_content(
        self,
        topics: List[str],
        sources: Optional[List[str]] = None,
        hours_back: int = 24,
        max_per_topic: int = 5
    ) -> Dict[str, List[UnifiedContent]]:
        """
        获取趋势内容
        
        Args:
            topics: 话题列表
            sources: 数据源列表
            hours_back: 向前搜索的小时数
            max_per_topic: 每个话题的最大内容数
            
        Returns:
            Dict[str, List[UnifiedContent]]: 按话题分组的趋势内容
        """
        if sources is None:
            sources = ['news', 'reddit', 'rss']
        
        trending_content = {}
        
        for topic in topics:
            logger.info(f"获取趋势内容: {topic}")
            
            # 多源搜索
            search_results = self.multi_source_search(
                query=topic,
                sources=sources,
                max_results_per_source=max_per_topic
            )
            
            # 合并并排序结果
            topic_content = []
            for source_results in search_results.values():
                topic_content.extend(source_results)
            
            # 按时间和相关性排序
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            recent_content = [
                content for content in topic_content 
                if content.published_at >= cutoff_time
            ]
            
            # 按评分和时间排序
            recent_content.sort(
                key=lambda x: (
                    x.score or 0,  # Reddit评分
                    x.published_at
                ), 
                reverse=True
            )
            
            trending_content[topic] = recent_content[:max_per_topic]
        
        return trending_content
    
    def aggregate_content_by_topics(
        self,
        topics: List[str],
        sources: Optional[List[str]] = None,
        max_articles_per_topic: int = 10
    ) -> Dict[str, List[UnifiedContent]]:
        """
        按话题聚合内容
        
        Args:
            topics: 话题列表
            sources: 数据源列表
            max_articles_per_topic: 每个话题的最大文章数
            
        Returns:
            Dict[str, List[UnifiedContent]]: 按话题分组的内容
        """
        logger.info(f"按话题聚合内容: {topics}")
        
        aggregated_content = {}
        
        for topic in topics:
            # 多源搜索
            search_results = self.multi_source_search(
                query=topic,
                sources=sources,
                max_results_per_source=max_articles_per_topic
            )
            
            # 合并结果并去重
            all_content = []
            seen_urls = set()
            
            for source_results in search_results.values():
                for content in source_results:
                    if content.url not in seen_urls:
                        all_content.append(content)
                        seen_urls.add(content.url)
            
            # 按优先级和时间排序
            all_content.sort(
                key=lambda x: (
                    self.source_priorities.get(x.source_type, 0),
                    x.published_at
                ),
                reverse=True
            )
            
            aggregated_content[topic] = all_content[:max_articles_per_topic]
        
        return aggregated_content
    
    def get_data_sources_status(self) -> Dict[str, Dict[str, Any]]:
        """
        获取数据源状态
        
        Returns:
            Dict[str, Dict]: 各数据源的状态信息
        """
        status = {}
        
        # NewsAPI状态
        status['news'] = {
            'available': self.news_client.is_available() if self.news_client else False,
            'client': 'NewsAPI',
            'last_request': self.last_request_times.get('news', 0)
        }
        
        # Reddit API状态
        status['reddit'] = {
            'available': self.reddit_client.is_available() if self.reddit_client else False,
            'client': 'PRAW',
            'last_request': self.last_request_times.get('reddit', 0)
        }
        
        # RSS解析器状态
        status['rss'] = {
            'available': self.rss_parser.is_available() if self.rss_parser else False,
            'client': 'FeedParser',
            'last_request': self.last_request_times.get('rss', 0)
        }
        
        return status


# 创建全局实例
data_aggregator = ImprovedDataAggregator() 