# -*- coding: utf-8 -*-
"""
配置模块测试
"""

import pytest
from pathlib import Path
import os
import tempfile


def test_settings_import():
    """测试设置模块导入"""
    try:
        from newsletter_agent.config.settings import settings
        assert settings is not None
        assert settings.APP_NAME == "Newsletter Agent"
    except ImportError:
        # 如果依赖未安装，跳过测试
        pytest.skip("依赖项未安装")


def test_default_values():
    """测试默认配置值"""
    try:
        from newsletter_agent.config.settings import settings
        
        assert settings.APP_VERSION == "1.0.0"
        assert settings.DEBUG is False
        assert settings.CONTENT_LANGUAGE == "zh"
        assert settings.MAX_ARTICLES_PER_SOURCE == 10
        assert len(settings.DEFAULT_NEWS_SOURCES) > 0
        
    except ImportError:
        pytest.skip("依赖项未安装")


def test_paths_exist():
    """测试路径配置"""
    try:
        from newsletter_agent.config.settings import settings
        
        assert isinstance(settings.BASE_DIR, Path)
        assert isinstance(settings.TEMPLATES_DIR, Path)
        assert isinstance(settings.LOGS_DIR, Path)
        
    except ImportError:
        pytest.skip("依赖项未安装") 