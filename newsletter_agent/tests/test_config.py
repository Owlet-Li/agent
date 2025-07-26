# -*- coding: utf-8 -*-
"""
Configuration module tests
"""

import pytest
from pathlib import Path
import os
import tempfile


def test_settings_import():
    """Test settings module import"""
    try:
        from newsletter_agent.config.settings import settings
        assert settings is not None
        assert settings.APP_NAME == "Newsletter Agent"
    except ImportError:
        # Skip test if dependencies are not installed
        pytest.skip("Dependencies not installed")


def test_default_values():
    """Test default configuration values"""
    try:
        from newsletter_agent.config.settings import settings
        
        assert settings.APP_VERSION == "1.0.0"
        assert settings.DEBUG is False
        assert settings.CONTENT_LANGUAGE == "zh"
        assert settings.MAX_ARTICLES_PER_SOURCE == 10
        
    except ImportError:
        pytest.skip("Dependencies not installed")


def test_paths_exist():
    """Test path configuration"""
    try:
        from newsletter_agent.config.settings import settings
        
        assert isinstance(settings.LOGS_DIR, Path)
        
    except ImportError:
        pytest.skip("Dependencies not installed")