# -*- coding: utf-8 -*-
"""
Newsletter Agent - 用户管理系统
用户偏好、订阅管理、个性化设置
"""

from .preferences import UserPreferencesManager, UserPreferences
from .subscription import SubscriptionManager, Subscription
from .storage import UserDataStorage

__all__ = [
    'UserPreferencesManager',
    'UserPreferences',
    'SubscriptionManager',
    'Subscription',
    'UserDataStorage'
]

# 全局实例
user_preferences_manager = UserPreferencesManager()
subscription_manager = SubscriptionManager()
user_storage = UserDataStorage() 