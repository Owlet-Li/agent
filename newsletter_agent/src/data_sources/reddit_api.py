# -*- coding: utf-8 -*-
"""
Newsletter Agent - Reddit API数据源
实现Reddit API的数据获取和处理功能
"""

import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

try:
    import praw
    from loguru import logger
except ImportError:
    logger = logging.getLogger(__name__)
    praw = None

try:
    from newsletter_agent.config.settings import settings
except ImportError:
    class MockSettings:
        REDDIT_CLIENT_ID = None
        REDDIT_CLIENT_SECRET = None
        REDDIT_USER_AGENT = "newsletter_agent_v1.0"
        DEFAULT_REDDIT_SUBREDDITS = ["technology", "science", "worldnews"]
        MAX_ARTICLES_PER_SOURCE = 10
    settings = MockSettings()


@dataclass
class RedditPost:
    """Reddit帖子数据结构"""
    title: str
    content: str
    url: str
    subreddit: str
    author: str
    score: int
    num_comments: int
    created_utc: datetime
    permalink: str
    is_self: bool
    selftext: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'title': self.title,
            'content': self.content,
            'url': self.url,
            'subreddit': self.subreddit,
            'author': self.author,
            'score': self.score,
            'num_comments': self.num_comments,
            'created_utc': self.created_utc.isoformat(),
            'permalink': self.permalink,
            'is_self': self.is_self,
            'selftext': self.selftext
        }


class RedditAPIClient:
    """
    Reddit API客户端
    提供Reddit数据获取、过滤和处理功能
    """
    
    def __init__(
        self, 
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """
        初始化Reddit API客户端
        
        Args:
            client_id: Reddit应用程序ID
            client_secret: Reddit应用程序密钥
            user_agent: 用户代理字符串
        """
        self.client_id = client_id or settings.REDDIT_CLIENT_ID
        self.client_secret = client_secret or settings.REDDIT_CLIENT_SECRET
        self.user_agent = user_agent or settings.REDDIT_USER_AGENT
        
        self.reddit = None
        self.last_request_time = 0
        self.request_delay = 2.0  # Reddit API建议的请求间隔
        
        if self.client_id and self.client_secret and praw:
            try:
                self.reddit = praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent
                )
                # 测试连接
                self.reddit.user.me()
                logger.info("Reddit API客户端初始化成功")
            except Exception as e:
                if "401" in str(e) or "Unauthorized" in str(e):
                    logger.warning("Reddit API认证失败，但客户端已创建（只读模式）")
                    # 对于只读访问，即使认证失败也可以继续
                    self.reddit = praw.Reddit(
                        client_id=self.client_id,
                        client_secret=self.client_secret,
                        user_agent=self.user_agent
                    )
                else:
                    logger.error(f"Reddit API客户端初始化失败: {e}")
                    self.reddit = None
        else:
            logger.warning("Reddit API客户端未初始化：缺少配置或依赖项")
    
    def _rate_limit(self):
        """实现请求速率限制"""
        now = time.time()
        time_since_last = now - self.last_request_time
        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def _parse_submission(self, submission) -> RedditPost:
        """解析Reddit提交数据"""
        try:
            created_utc = datetime.fromtimestamp(submission.created_utc)
        except (ValueError, AttributeError):
            created_utc = datetime.now()
        
        # 获取内容：优先使用selftext，否则使用URL
        content = ""
        if submission.is_self and submission.selftext:
            content = submission.selftext[:500]  # 限制长度
        elif hasattr(submission, 'url'):
            content = f"链接: {submission.url}"
        
        return RedditPost(
            title=submission.title or "",
            content=content,
            url=submission.url if hasattr(submission, 'url') else "",
            subreddit=submission.subreddit.display_name if hasattr(submission, 'subreddit') else "",
            author=str(submission.author) if submission.author else "[deleted]",
            score=submission.score if hasattr(submission, 'score') else 0,
            num_comments=submission.num_comments if hasattr(submission, 'num_comments') else 0,
            created_utc=created_utc,
            permalink=f"https://reddit.com{submission.permalink}" if hasattr(submission, 'permalink') else "",
            is_self=submission.is_self if hasattr(submission, 'is_self') else False,
            selftext=submission.selftext if hasattr(submission, 'selftext') else None
        )
    
    def get_hot_posts(
        self, 
        subreddit_name: str, 
        limit: int = 10,
        time_filter: str = "day"
    ) -> List[RedditPost]:
        """
        获取热门帖子
        
        Args:
            subreddit_name: 子版块名称
            limit: 获取数量限制
            time_filter: 时间过滤器 (hour, day, week, month, year, all)
            
        Returns:
            List[RedditPost]: Reddit帖子列表
        """
        if not self.reddit:
            logger.error("Reddit API客户端未初始化")
            return []
        
        self._rate_limit()
        
        try:
            logger.info(f"获取热门帖子: r/{subreddit_name}, limit={limit}")
            
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []
            
            for submission in subreddit.hot(limit=limit):
                try:
                    post = self._parse_submission(submission)
                    posts.append(post)
                except Exception as e:
                    logger.warning(f"解析帖子失败: {e}")
                    continue
            
            logger.info(f"成功获取 {len(posts)} 个热门帖子 from r/{subreddit_name}")
            return posts
            
        except Exception as e:
            logger.error(f"获取热门帖子失败: {e}")
            return []
    
    def get_top_posts(
        self, 
        subreddit_name: str, 
        limit: int = 10,
        time_filter: str = "day"
    ) -> List[RedditPost]:
        """
        获取顶级帖子
        
        Args:
            subreddit_name: 子版块名称
            limit: 获取数量限制
            time_filter: 时间过滤器
            
        Returns:
            List[RedditPost]: Reddit帖子列表
        """
        if not self.reddit:
            logger.error("Reddit API客户端未初始化")
            return []
        
        self._rate_limit()
        
        try:
            logger.info(f"获取顶级帖子: r/{subreddit_name}, time_filter={time_filter}")
            
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []
            
            for submission in subreddit.top(time_filter=time_filter, limit=limit):
                try:
                    post = self._parse_submission(submission)
                    posts.append(post)
                except Exception as e:
                    logger.warning(f"解析帖子失败: {e}")
                    continue
            
            logger.info(f"成功获取 {len(posts)} 个顶级帖子 from r/{subreddit_name}")
            return posts
            
        except Exception as e:
            logger.error(f"获取顶级帖子失败: {e}")
            return []
    
    def search_posts(
        self, 
        query: str,
        subreddit_name: Optional[str] = None,
        sort: str = "relevance",
        time_filter: str = "all",
        limit: int = 10
    ) -> List[RedditPost]:
        """
        搜索帖子
        
        Args:
            query: 搜索查询
            subreddit_name: 子版块名称（如果为None则搜索全站）
            sort: 排序方式 (relevance, hot, top, new, comments)
            time_filter: 时间过滤器
            limit: 获取数量限制
            
        Returns:
            List[RedditPost]: Reddit帖子列表
        """
        if not self.reddit:
            logger.error("Reddit API客户端未初始化")
            return []
        
        self._rate_limit()
        
        try:
            logger.info(f"搜索帖子: query='{query}', subreddit={subreddit_name}")
            
            if subreddit_name:
                subreddit = self.reddit.subreddit(subreddit_name)
                search_results = subreddit.search(
                    query, 
                    sort=sort, 
                    time_filter=time_filter, 
                    limit=limit
                )
            else:
                search_results = self.reddit.subreddit("all").search(
                    query,
                    sort=sort,
                    time_filter=time_filter,
                    limit=limit
                )
            
            posts = []
            for submission in search_results:
                try:
                    post = self._parse_submission(submission)
                    posts.append(post)
                except Exception as e:
                    logger.warning(f"解析搜索结果失败: {e}")
                    continue
            
            logger.info(f"搜索到 {len(posts)} 个相关帖子")
            return posts
            
        except Exception as e:
            logger.error(f"搜索帖子失败: {e}")
            return []
    
    def get_trending_topics(
        self, 
        subreddits: Optional[List[str]] = None,
        limit_per_subreddit: int = 5
    ) -> Dict[str, List[RedditPost]]:
        """
        获取趋势话题
        
        Args:
            subreddits: 要监控的子版块列表
            limit_per_subreddit: 每个子版块的帖子数量限制
            
        Returns:
            Dict[str, List[RedditPost]]: 按子版块分组的热门帖子
        """
        if subreddits is None:
            subreddits = settings.DEFAULT_REDDIT_SUBREDDITS
        
        trending = {}
        for subreddit_name in subreddits:
            logger.info(f"获取趋势话题: r/{subreddit_name}")
            posts = self.get_hot_posts(subreddit_name, limit=limit_per_subreddit)
            if posts:
                trending[subreddit_name] = posts
        
        return trending
    
    def get_posts_by_keywords(
        self,
        keywords: List[str],
        subreddits: Optional[List[str]] = None,
        time_filter: str = "day",
        max_posts_per_keyword: int = 5
    ) -> Dict[str, List[RedditPost]]:
        """
        根据关键词获取帖子
        
        Args:
            keywords: 关键词列表
            subreddits: 要搜索的子版块列表
            time_filter: 时间过滤器
            max_posts_per_keyword: 每个关键词的最大帖子数
            
        Returns:
            Dict[str, List[RedditPost]]: 按关键词分组的帖子
        """
        if subreddits is None:
            subreddits = settings.DEFAULT_REDDIT_SUBREDDITS
        
        results = {}
        for keyword in keywords:
            keyword_posts = []
            for subreddit_name in subreddits:
                posts = self.search_posts(
                    query=keyword,
                    subreddit_name=subreddit_name,
                    time_filter=time_filter,
                    limit=max_posts_per_keyword // len(subreddits) + 1
                )
                keyword_posts.extend(posts)
            
            # 按评分排序并限制数量
            keyword_posts.sort(key=lambda x: x.score, reverse=True)
            results[keyword] = keyword_posts[:max_posts_per_keyword]
        
        return results
    
    def is_available(self) -> bool:
        """检查Reddit API是否可用"""
        return self.reddit is not None


# 创建全局实例
reddit_client = RedditAPIClient() 