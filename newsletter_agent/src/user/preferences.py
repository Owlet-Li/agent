# -*- coding: utf-8 -*-
"""
Newsletter Agent - 用户偏好管理
处理用户个性化设置和偏好
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


@dataclass
class UserPreferences:
    """用户偏好数据结构"""
    user_id: str
    email: str
    name: str = ""
    
    # 兴趣设置
    topics: List[str] = None
    categories: List[str] = None
    keywords: List[str] = None
    
    # 内容偏好
    language: str = "zh"
    content_length: str = "medium"  # short, medium, long
    content_style: str = "professional"  # professional, casual, academic, creative
    
    # 发送设置
    frequency: str = "daily"  # daily, weekly, bi-weekly, monthly
    preferred_time: str = "09:00"
    timezone: str = "Asia/Shanghai"
    
    # 格式设置
    email_format: str = "html"  # html, text, both
    newsletter_template: str = "professional"
    
    # 个性化设置
    max_articles_per_section: int = 5
    exclude_sources: List[str] = None
    priority_sources: List[str] = None
    
    # 元数据
    created_at: datetime = None
    updated_at: datetime = None
    is_active: bool = True
    
    def __post_init__(self):
        if self.topics is None:
            self.topics = ["科技", "商业"]
        if self.categories is None:
            self.categories = ["tech", "business"]
        if self.keywords is None:
            self.keywords = []
        if self.exclude_sources is None:
            self.exclude_sources = []
        if self.priority_sources is None:
            self.priority_sources = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        # 转换datetime为ISO字符串
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['updated_at'] = self.updated_at.isoformat() if self.updated_at else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserPreferences':
        """从字典创建实例"""
        # 转换ISO字符串为datetime
        if data.get('created_at'):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)


class UserPreferencesManager:
    """用户偏好管理器"""
    
    def __init__(self):
        self.preferences_cache: Dict[str, UserPreferences] = {}
        self.default_topics = [
            "科技", "人工智能", "商业", "创新", "互联网",
            "健康", "科学", "教育", "环境", "社会"
        ]
        self.default_categories = [
            "tech", "business", "science", "health", "world", 
            "entertainment", "sports", "politics", "general"
        ]
        logger.info("用户偏好管理器初始化完成")
    
    def create_user_preferences(
        self,
        user_id: str,
        email: str,
        name: str = "",
        **kwargs
    ) -> UserPreferences:
        """创建新用户偏好"""
        preferences = UserPreferences(
            user_id=user_id,
            email=email,
            name=name,
            **kwargs
        )
        
        self.preferences_cache[user_id] = preferences
        logger.info(f"创建用户偏好: {user_id} ({email})")
        
        return preferences
    
    def get_user_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """获取用户偏好"""
        if user_id in self.preferences_cache:
            return self.preferences_cache[user_id]
        
        # 这里可以从数据库加载
        # preferences = self._load_from_storage(user_id)
        # if preferences:
        #     self.preferences_cache[user_id] = preferences
        #     return preferences
        
        return None
    
    def update_user_preferences(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> Optional[UserPreferences]:
        """更新用户偏好"""
        preferences = self.get_user_preferences(user_id)
        if not preferences:
            logger.warning(f"用户偏好不存在: {user_id}")
            return None
        
        # 更新字段
        for key, value in updates.items():
            if hasattr(preferences, key):
                setattr(preferences, key, value)
        
        preferences.updated_at = datetime.now()
        
        # 保存到存储
        # self._save_to_storage(preferences)
        
        logger.info(f"更新用户偏好: {user_id}")
        return preferences
    
    def get_personalized_topics(self, user_id: str) -> List[str]:
        """获取用户个性化话题"""
        preferences = self.get_user_preferences(user_id)
        if preferences and preferences.topics:
            return preferences.topics
        return self.default_topics[:5]  # 返回默认前5个话题
    
    def get_personalized_categories(self, user_id: str) -> List[str]:
        """获取用户个性化分类"""
        preferences = self.get_user_preferences(user_id)
        if preferences and preferences.categories:
            return preferences.categories
        return self.default_categories[:5]  # 返回默认前5个分类
    
    def get_content_filters(self, user_id: str) -> Dict[str, Any]:
        """获取内容过滤器"""
        preferences = self.get_user_preferences(user_id)
        if not preferences:
            return {}
        
        return {
            'include_keywords': preferences.keywords,
            'exclude_sources': preferences.exclude_sources,
            'priority_sources': preferences.priority_sources,
            'max_articles_per_section': preferences.max_articles_per_section,
            'categories': preferences.categories,
            'language': preferences.language
        }
    
    def get_newsletter_settings(self, user_id: str) -> Dict[str, Any]:
        """获取简报设置"""
        preferences = self.get_user_preferences(user_id)
        if not preferences:
            return self._get_default_newsletter_settings()
        
        return {
            'content_length': preferences.content_length,
            'content_style': preferences.content_style,
            'email_format': preferences.email_format,
            'newsletter_template': preferences.newsletter_template,
            'language': preferences.language
        }
    
    def _get_default_newsletter_settings(self) -> Dict[str, Any]:
        """获取默认简报设置"""
        return {
            'content_length': 'medium',
            'content_style': 'professional',
            'email_format': 'html',
            'newsletter_template': 'professional',
            'language': 'zh'
        }
    
    def validate_preferences(self, preferences_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证偏好设置数据"""
        errors = {}
        
        # 验证必填字段
        required_fields = ['user_id', 'email']
        for field in required_fields:
            if field not in preferences_data or not preferences_data[field]:
                errors[field] = f"{field}是必填字段"
        
        # 验证邮箱格式
        import re
        email = preferences_data.get('email', '')
        if email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            errors['email'] = "邮箱格式不正确"
        
        # 验证频率选项
        valid_frequencies = ['daily', 'weekly', 'bi-weekly', 'monthly']
        frequency = preferences_data.get('frequency', 'daily')
        if frequency not in valid_frequencies:
            errors['frequency'] = f"频率必须是: {', '.join(valid_frequencies)}"
        
        # 验证内容长度
        valid_lengths = ['short', 'medium', 'long']
        content_length = preferences_data.get('content_length', 'medium')
        if content_length not in valid_lengths:
            errors['content_length'] = f"内容长度必须是: {', '.join(valid_lengths)}"
        
        # 验证风格
        valid_styles = ['professional', 'casual', 'academic', 'creative']
        content_style = preferences_data.get('content_style', 'professional')
        if content_style not in valid_styles:
            errors['content_style'] = f"内容风格必须是: {', '.join(valid_styles)}"
        
        return errors
    
    def get_recommended_topics(self, user_id: str) -> List[str]:
        """获取推荐话题（基于用户历史）"""
        preferences = self.get_user_preferences(user_id)
        current_topics = preferences.topics if preferences else []
        
        # 简单推荐逻辑：基于当前话题推荐相关话题
        related_topics = {
            "科技": ["人工智能", "机器学习", "区块链", "云计算"],
            "商业": ["创业", "投资", "市场营销", "金融"],
            "健康": ["医疗", "营养", "运动", "心理健康"],
            "科学": ["生物技术", "物理", "化学", "环境科学"]
        }
        
        recommendations = []
        for topic in current_topics:
            if topic in related_topics:
                recommendations.extend(related_topics[topic])
        
        # 去重并过滤已有话题
        recommendations = list(set(recommendations) - set(current_topics))
        
        return recommendations[:5]  # 返回前5个推荐
    
    def export_preferences(self, user_id: str) -> Optional[str]:
        """导出用户偏好为JSON"""
        preferences = self.get_user_preferences(user_id)
        if not preferences:
            return None
        
        return json.dumps(preferences.to_dict(), ensure_ascii=False, indent=2)
    
    def import_preferences(self, preferences_json: str) -> Optional[UserPreferences]:
        """从JSON导入用户偏好"""
        try:
            data = json.loads(preferences_json)
            preferences = UserPreferences.from_dict(data)
            self.preferences_cache[preferences.user_id] = preferences
            return preferences
        except Exception as e:
            logger.error(f"导入用户偏好失败: {e}")
            return None
    
    def get_all_available_topics(self) -> List[str]:
        """获取所有可用话题"""
        return self.default_topics
    
    def get_all_available_categories(self) -> List[str]:
        """获取所有可用分类"""
        return self.default_categories
    
    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """获取用户统计信息"""
        preferences = self.get_user_preferences(user_id)
        if not preferences:
            return {}
        
        return {
            'user_id': user_id,
            'email': preferences.email,
            'name': preferences.name,
            'topics_count': len(preferences.topics),
            'categories_count': len(preferences.categories),
            'created_at': preferences.created_at.isoformat() if preferences.created_at else None,
            'updated_at': preferences.updated_at.isoformat() if preferences.updated_at else None,
            'is_active': preferences.is_active,
            'frequency': preferences.frequency,
            'language': preferences.language
        } 