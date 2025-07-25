# -*- coding: utf-8 -*-
"""
Newsletter Agent - 内容去重器
基于多种算法的智能去重功能
"""

import re
import hashlib
from typing import List, Dict, Any, Set, Tuple, Optional
from urllib.parse import urlparse, parse_qs
from difflib import SequenceMatcher

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class ContentDeduplicator:
    """内容去重器
    
    提供多种去重算法：
    1. URL去重
    2. 标题相似度去重
    3. 内容相似度去重
    4. 哈希去重
    5. 时间窗口去重
    """
    
    def __init__(self, similarity_threshold: float = 0.8):
        """初始化去重器
        
        Args:
            similarity_threshold: 相似度阈值 (0-1)，超过此阈值视为重复
        """
        self.similarity_threshold = similarity_threshold
        self.url_cache: Set[str] = set()
        self.content_hashes: Set[str] = set()
        self.title_cache: List[str] = []
        
        # TF-IDF向量化器
        if SKLEARN_AVAILABLE:
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words=None,  # 我们已经在预处理中处理了停用词
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.95
            )
        
        logger.info(f"内容去重器初始化完成，相似度阈值: {similarity_threshold}")
    
    def normalize_url(self, url: str) -> str:
        """标准化URL
        
        移除查询参数中的追踪参数、时间戳等
        """
        if not url:
            return ""
        
        try:
            parsed = urlparse(url)
            
            # 移除常见的追踪参数
            tracking_params = {
                'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
                'fbclid', 'gclid', 'msclkid', 'ref', 'source', 'from'
            }
            
            query_params = parse_qs(parsed.query)
            filtered_params = {k: v for k, v in query_params.items() 
                             if k.lower() not in tracking_params}
            
            # 重新构建URL
            query_string = '&'.join(f"{k}={v[0]}" for k, v in filtered_params.items())
            
            normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if query_string:
                normalized += f"?{query_string}"
            
            return normalized.lower()
            
        except Exception as e:
            logger.warning(f"URL标准化失败: {url}, 错误: {e}")
            return url.lower()
    
    def calculate_text_hash(self, text: str) -> str:
        """计算文本内容的哈希值"""
        if not text:
            return ""
        
        # 标准化文本（移除空白、转小写）
        normalized_text = re.sub(r'\s+', ' ', text.lower().strip())
        
        # 计算MD5哈希
        return hashlib.md5(normalized_text.encode('utf-8')).hexdigest()
    
    def calculate_title_similarity(self, title1: str, title2: str) -> float:
        """计算标题相似度"""
        if not title1 or not title2:
            return 0.0
        
        # 预处理标题
        def preprocess_title(title):
            # 移除标点符号和多余空白
            cleaned = re.sub(r'[^\w\s]', ' ', title.lower())
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            return cleaned
        
        cleaned_title1 = preprocess_title(title1)
        cleaned_title2 = preprocess_title(title2)
        
        # 使用SequenceMatcher计算相似度
        similarity = SequenceMatcher(None, cleaned_title1, cleaned_title2).ratio()
        
        return similarity
    
    def calculate_content_similarity_simple(self, content1: str, content2: str) -> float:
        """简单内容相似度计算（基于词汇重叠）"""
        if not content1 or not content2:
            return 0.0
        
        # 简单分词
        words1 = set(re.findall(r'\w+', content1.lower()))
        words2 = set(re.findall(r'\w+', content2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        # 计算Jaccard相似度
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def calculate_content_similarity_advanced(self, content1: str, content2: str) -> float:
        """高级内容相似度计算（基于TF-IDF和余弦相似度）"""
        if not SKLEARN_AVAILABLE:
            return self.calculate_content_similarity_simple(content1, content2)
        
        if not content1 or not content2:
            return 0.0
        
        try:
            # 使用TF-IDF向量化
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([content1, content2])
            
            # 计算余弦相似度
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # 返回两个文档之间的相似度
            return similarity_matrix[0][1]
            
        except Exception as e:
            logger.warning(f"TF-IDF相似度计算失败: {e}")
            return self.calculate_content_similarity_simple(content1, content2)
    
    def is_duplicate_by_url(self, url: str) -> bool:
        """基于URL检查是否重复"""
        if not url:
            return False
        
        normalized_url = self.normalize_url(url)
        
        if normalized_url in self.url_cache:
            return True
        
        self.url_cache.add(normalized_url)
        return False
    
    def is_duplicate_by_hash(self, content: str) -> bool:
        """基于内容哈希检查是否重复"""
        if not content:
            return False
        
        content_hash = self.calculate_text_hash(content)
        
        if content_hash in self.content_hashes:
            return True
        
        self.content_hashes.add(content_hash)
        return False
    
    def is_duplicate_by_title(self, title: str, threshold: Optional[float] = None) -> Tuple[bool, float]:
        """基于标题相似度检查是否重复
        
        Returns:
            (is_duplicate, max_similarity)
        """
        if not title:
            return False, 0.0
        
        if threshold is None:
            threshold = self.similarity_threshold
        
        max_similarity = 0.0
        
        for cached_title in self.title_cache:
            similarity = self.calculate_title_similarity(title, cached_title)
            max_similarity = max(max_similarity, similarity)
            
            if similarity >= threshold:
                return True, similarity
        
        self.title_cache.append(title)
        return False, max_similarity
    
    def is_duplicate_by_content(self, content: str, existing_contents: List[str], 
                              threshold: Optional[float] = None, use_advanced: bool = True) -> Tuple[bool, float]:
        """基于内容相似度检查是否重复
        
        Args:
            content: 待检查的内容
            existing_contents: 已存在的内容列表
            threshold: 相似度阈值
            use_advanced: 是否使用高级算法
            
        Returns:
            (is_duplicate, max_similarity)
        """
        if not content or not existing_contents:
            return False, 0.0
        
        if threshold is None:
            threshold = self.similarity_threshold
        
        max_similarity = 0.0
        
        for existing_content in existing_contents:
            if use_advanced:
                similarity = self.calculate_content_similarity_advanced(content, existing_content)
            else:
                similarity = self.calculate_content_similarity_simple(content, existing_content)
            
            max_similarity = max(max_similarity, similarity)
            
            if similarity >= threshold:
                return True, similarity
        
        return False, max_similarity
    
    def check_duplicate(self, content_item: Dict[str, Any], existing_items: List[Dict[str, Any]], 
                       check_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """综合去重检查
        
        Args:
            content_item: 待检查的内容项
            existing_items: 已存在的内容项列表
            check_options: 检查选项
            
        Returns:
            去重检查结果
        """
        # 默认检查选项
        default_options = {
            "check_url": True,
            "check_hash": True,
            "check_title": True,
            "check_content": True,
            "title_threshold": self.similarity_threshold,
            "content_threshold": self.similarity_threshold,
            "use_advanced_similarity": True
        }
        
        if check_options:
            default_options.update(check_options)
        
        result = {
            "is_duplicate": False,
            "duplicate_type": [],
            "similarity_scores": {},
            "duplicate_sources": []
        }
        
        title = content_item.get("title", "")
        content = content_item.get("content", "")
        url = content_item.get("url", "")
        
        # URL去重
        if default_options["check_url"] and url:
            if self.is_duplicate_by_url(url):
                result["is_duplicate"] = True
                result["duplicate_type"].append("url")
        
        # 内容哈希去重
        if default_options["check_hash"] and content:
            if self.is_duplicate_by_hash(content):
                result["is_duplicate"] = True
                result["duplicate_type"].append("hash")
        
        # 标题相似度去重
        if default_options["check_title"] and title:
            existing_titles = [item.get("title", "") for item in existing_items]
            is_dup, similarity = self.is_duplicate_by_title(title, default_options["title_threshold"])
            result["similarity_scores"]["title"] = similarity
            
            if is_dup:
                result["is_duplicate"] = True
                result["duplicate_type"].append("title")
        
        # 内容相似度去重
        if default_options["check_content"] and content:
            existing_contents = [item.get("content", "") for item in existing_items]
            is_dup, similarity = self.is_duplicate_by_content(
                content, existing_contents, 
                default_options["content_threshold"],
                default_options["use_advanced_similarity"]
            )
            result["similarity_scores"]["content"] = similarity
            
            if is_dup:
                result["is_duplicate"] = True
                result["duplicate_type"].append("content")
        
        return result
    
    def deduplicate_batch(self, content_items: List[Dict[str, Any]], 
                         dedup_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """批量去重
        
        Args:
            content_items: 内容项列表
            dedup_options: 去重选项
            
        Returns:
            去重结果
        """
        # 默认去重选项
        default_options = {
            "preserve_order": True,
            "keep_highest_quality": True,
            "check_url": True,
            "check_hash": True,
            "check_title": True,
            "check_content": True,
            "title_threshold": self.similarity_threshold,
            "content_threshold": self.similarity_threshold,
            "use_advanced_similarity": True
        }
        
        if dedup_options:
            default_options.update(dedup_options)
        
        # 重置缓存
        self.url_cache.clear()
        self.content_hashes.clear()
        self.title_cache.clear()
        
        unique_items = []
        duplicate_items = []
        dedup_stats = {
            "total_items": len(content_items),
            "unique_items": 0,
            "duplicate_items": 0,
            "duplicate_types": {
                "url": 0,
                "hash": 0,
                "title": 0,
                "content": 0
            }
        }
        
        for i, item in enumerate(content_items):
            # 检查是否与已处理的项重复
            check_result = self.check_duplicate(item, unique_items, default_options)
            
            if check_result["is_duplicate"]:
                duplicate_items.append({
                    "item": item,
                    "index": i,
                    "duplicate_info": check_result
                })
                
                # 统计重复类型
                for dup_type in check_result["duplicate_type"]:
                    dedup_stats["duplicate_types"][dup_type] += 1
                
            else:
                unique_items.append(item)
        
        dedup_stats["unique_items"] = len(unique_items)
        dedup_stats["duplicate_items"] = len(duplicate_items)
        
        return {
            "unique_items": unique_items,
            "duplicate_items": duplicate_items,
            "statistics": dedup_stats
        }
    
    def deduplicate_by_time_window(self, content_items: List[Dict[str, Any]], 
                                  window_hours: int = 24) -> List[Dict[str, Any]]:
        """基于时间窗口去重
        
        在指定时间窗口内，相同或相似的内容只保留一个
        
        Args:
            content_items: 内容项列表
            window_hours: 时间窗口（小时）
            
        Returns:
            去重后的内容列表
        """
        from datetime import datetime, timedelta
        
        if not content_items:
            return []
        
        # 按发布时间排序
        sorted_items = sorted(content_items, 
                            key=lambda x: x.get("published_at", datetime.now()), 
                            reverse=True)
        
        unique_items = []
        
        for item in sorted_items:
            item_time = item.get("published_at")
            if isinstance(item_time, str):
                try:
                    item_time = datetime.fromisoformat(item_time.replace('Z', '+00:00'))
                except:
                    item_time = datetime.now()
            elif item_time is None:
                item_time = datetime.now()
            
            # 检查时间窗口内是否有相似内容
            is_duplicate = False
            
            for unique_item in unique_items:
                unique_time = unique_item.get("published_at")
                if isinstance(unique_time, str):
                    try:
                        unique_time = datetime.fromisoformat(unique_time.replace('Z', '+00:00'))
                    except:
                        unique_time = datetime.now()
                elif unique_time is None:
                    unique_time = datetime.now()
                
                # 检查是否在时间窗口内
                time_diff = abs((item_time - unique_time).total_seconds() / 3600)
                
                if time_diff <= window_hours:
                    # 在时间窗口内，检查内容相似度
                    title_similarity = self.calculate_title_similarity(
                        item.get("title", ""), 
                        unique_item.get("title", "")
                    )
                    
                    if title_similarity >= self.similarity_threshold:
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                unique_items.append(item)
        
        return unique_items
    
    def get_dedup_statistics(self) -> Dict[str, Any]:
        """获取去重统计信息"""
        return {
            "cached_urls": len(self.url_cache),
            "cached_hashes": len(self.content_hashes),
            "cached_titles": len(self.title_cache),
            "similarity_threshold": self.similarity_threshold,
            "sklearn_available": SKLEARN_AVAILABLE
        }
    
    def clear_cache(self):
        """清空缓存"""
        self.url_cache.clear()
        self.content_hashes.clear()
        self.title_cache.clear()
        logger.info("去重缓存已清空") 