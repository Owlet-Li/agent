# -*- coding: utf-8 -*-
"""
Newsletter Agent - User Management System
User preferences, subscription management, personalization settings
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
