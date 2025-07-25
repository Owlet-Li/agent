# -*- coding: utf-8 -*-
"""
Newsletter Agent - 配置设置
使用Pydantic进行配置管理
"""

import os
from pathlib import Path
from typing import Optional

# 尝试导入Pydantic
try:
    from pydantic import BaseSettings, validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    # Pydantic不可用时的备用方案
    PYDANTIC_AVAILABLE = False
    from dotenv import load_dotenv
    
    # 手动加载.env文件
    env_file = Path(__file__).parent.parent.parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent


if PYDANTIC_AVAILABLE:
    class Settings(BaseSettings):
        """应用程序设置"""
        
        # 基本应用信息
        APP_NAME: str = "Newsletter Agent"
        APP_VERSION: str = "1.0.0"
        DEBUG: bool = False
        
        # API密钥配置
        NEWSAPI_KEY: str = ""
        REDDIT_CLIENT_ID: str = ""
        REDDIT_CLIENT_SECRET: str = ""
        REDDIT_USER_AGENT: str = "newsletter_agent/1.0.0"
        OPENAI_API_KEY: str = ""
        OPENAI_API_BASE: str = "https://api.openai.com/v1"  # 支持OpenRouter等替代服务
        SENDGRID_API_KEY: str = ""
        
        # 邮件配置
        EMAIL_FROM: str = ""
        EMAIL_SUBJECT: str = "您的个性化新闻简报"
        
        # 目录配置
        LOGS_DIR: Path = PROJECT_ROOT / "logs"
        CACHE_DIR: Path = PROJECT_ROOT / "cache"
        OUTPUT_DIR: Path = PROJECT_ROOT / "output"
        
        # 内容配置
        MAX_ARTICLES_PER_SOURCE: int = 10
        CONTENT_LANGUAGE: str = "zh"
        DEFAULT_TOPICS: list = ["科技", "商业", "健康"]
        
        @validator("LOGS_DIR", "CACHE_DIR", "OUTPUT_DIR", pre=True)
        @classmethod
        def create_directories(cls, v):
            """确保目录存在"""
            if isinstance(v, str):
                v = Path(v)
            v.mkdir(parents=True, exist_ok=True)
            return v
        
        class Config:
            env_file = PROJECT_ROOT / ".env"
            env_file_encoding = "utf-8"
            case_sensitive = True

else:
    # Pydantic不可用时的备用Settings类
    class Settings:
        """备用设置类（当Pydantic不可用时）"""
        
        def __init__(self):
            # 基本应用信息
            self.APP_NAME = "Newsletter Agent"
            self.APP_VERSION = "1.0.0"
            self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
            
            # API密钥配置
            self.NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
            self.REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
            self.REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
            self.REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "newsletter_agent/1.0.0")
            self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
            self.OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
            self.SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
            
            # 邮件配置
            self.EMAIL_FROM = os.getenv("EMAIL_FROM", "")
            self.EMAIL_SUBJECT = os.getenv("EMAIL_SUBJECT", "您的个性化新闻简报")
            
            # 目录配置
            self.LOGS_DIR = self._create_dir(PROJECT_ROOT / "logs")
            self.CACHE_DIR = self._create_dir(PROJECT_ROOT / "cache")
            self.OUTPUT_DIR = self._create_dir(PROJECT_ROOT / "output")
            
            # 内容配置
            self.MAX_ARTICLES_PER_SOURCE = int(os.getenv("MAX_ARTICLES_PER_SOURCE", "10"))
            self.CONTENT_LANGUAGE = os.getenv("CONTENT_LANGUAGE", "zh")
            self.DEFAULT_TOPICS = ["科技", "商业", "健康"]
        
        def _create_dir(self, path):
            """创建目录"""
            path.mkdir(parents=True, exist_ok=True)
            return path


# 创建全局设置实例
settings = Settings() 