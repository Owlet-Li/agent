#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Newsletter Agent - 主入口文件
智能新闻简报生成代理
"""

import sys
import os
from pathlib import Path
import asyncio
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入配置
try:
    from newsletter_agent.config.settings import settings
except ImportError:
    logger.error("配置模块导入失败，请确保已安装所有依赖项")
    sys.exit(1)


def setup_logging():
    """设置日志系统"""
    # 检查是否使用loguru
    if hasattr(logger, 'remove'):
        # 使用loguru
        logger.remove()  # 移除默认handler
        
        # 控制台日志
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                   "<level>{message}</level>",
            level="DEBUG" if settings.DEBUG else "INFO"
        )
        
        # 文件日志
        log_file = settings.LOGS_DIR / "newsletter_agent.log"
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            rotation="10 MB",
            retention="7 days",
            encoding="utf-8"
        )
    else:
        # 使用标准logging
        logging.basicConfig(
            level=logging.DEBUG if settings.DEBUG else logging.INFO,
            format='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(settings.LOGS_DIR / "newsletter_agent.log", encoding="utf-8")
            ]
        )


def check_environment():
    """检查环境配置 - 分级检查策略"""
    logger.info("检查环境配置...")
    
    # 数据源相关的密钥 (核心功能)
    data_source_keys = ["NEWSAPI_KEY"]
    # AI功能相关的密钥 (可选功能)  
    ai_keys = ["OPENAI_API_KEY"]
    
    missing_data_keys = []
    missing_ai_keys = []
    
    # 检查数据源密钥
    for key in data_source_keys:
        value = getattr(settings, key, None)
        if not value or value.strip() == "":
            missing_data_keys.append(key)
    
    # 检查AI功能密钥
    for key in ai_keys:
        value = getattr(settings, key, None)
        if not value or value.strip() == "":
            missing_ai_keys.append(key)
    
    # 报告检查结果
    if missing_data_keys:
        logger.error(f"❌ 缺少核心数据源密钥: {', '.join(missing_data_keys)}")
        logger.info("💡 这些密钥是必需的，请检查.env文件配置")
        return False
    
    if missing_ai_keys:
        logger.warning(f"⚠️  缺少AI功能密钥: {', '.join(missing_ai_keys)}")
        logger.info("💡 AI功能将不可用，但数据源功能仍可正常使用")
    else:
        logger.info("✅ AI功能密钥配置完整")
    
    # 验证数据源状态
    try:
        from newsletter_agent.src.data_sources import data_aggregator
        status = data_aggregator.get_data_sources_status()
        
        available_sources = [name for name, available in status.items() if available]
        unavailable_sources = [name for name, available in status.items() if not available]
        
        if available_sources:
            logger.info(f"✅ 可用数据源: {', '.join(available_sources)}")
        
        if unavailable_sources:
            logger.warning(f"⚠️  不可用数据源: {', '.join(unavailable_sources)}")
            
        if not available_sources:
            logger.error("❌ 没有可用的数据源！")
            return False
            
    except Exception as e:
        logger.warning(f"⚠️  数据源状态检查失败: {e}")
    
    logger.info("✅ 环境配置检查完成，应用可以启动")
    return True


def main():
    """主函数"""
    # 设置日志
    setup_logging()
    
    logger.info(f"🚀 启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # 检查环境
    if not check_environment():
        logger.error("💥 环境检查失败，无法启动应用")
        sys.exit(1)
    
    try:
        # 导入并启动UI
        from newsletter_agent.src.ui.app import create_app
        
        logger.info("🎨 正在启动用户界面...")
        app = create_app()
        
        # 启动Gradio应用
        logger.info("🌐 启动Web服务器 - http://localhost:7860")
        app.launch(
            server_name="127.0.0.1",
            server_port=7860,
            share=True,  # 创建公共链接以解决代理问题
            debug=settings.DEBUG
        )
        
    except ImportError as e:
        logger.error(f"💥 模块导入失败: {e}")
        logger.info("💡 请运行: pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("👋 用户中断，正在退出...")
    except Exception as e:
        logger.error(f"💥 应用启动失败: {e}")
        import traceback
        logger.debug(f"详细错误信息:\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main() 