#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Newsletter Agent - Main Entry Point
Intelligent Newsletter Generation Agent
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

# Add project root directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import configuration
try:
    from newsletter_agent.config.settings import settings
except ImportError:
    logger.error("Configuration module import failed, please ensure all dependencies are installed")
    sys.exit(1)


def setup_logging():
    """Setup logging system"""
    # Check if using loguru
    if hasattr(logger, 'remove'):
        # Using loguru
        logger.remove()  # Remove default handler
        
        # Console logging
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                   "<level>{message}</level>",
            level="DEBUG" if settings.DEBUG else "INFO"
        )
        
        # File logging
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
        # Using standard logging
        logging.basicConfig(
            level=logging.DEBUG if settings.DEBUG else logging.INFO,
            format='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(settings.LOGS_DIR / "newsletter_agent.log", encoding="utf-8")
            ]
        )


def check_environment():
    """Check environment configuration - Tiered checking strategy"""
    logger.info("Checking environment configuration...")
    
    # Data source related keys (core functionality)
    data_source_keys = ["NEWSAPI_KEY"]
    # AI functionality related keys (optional features)  
    ai_keys = ["OPENAI_API_KEY"]
    
    missing_data_keys = []
    missing_ai_keys = []
    
    # Check data source keys
    for key in data_source_keys:
        value = getattr(settings, key, None)
        if not value or value.strip() == "":
            missing_data_keys.append(key)
    
    # Check AI functionality keys
    for key in ai_keys:
        value = getattr(settings, key, None)
        if not value or value.strip() == "":
            missing_ai_keys.append(key)
    
    # Report check results
    if missing_data_keys:
        logger.error(f"❌ Missing core data source keys: {', '.join(missing_data_keys)}")
        logger.info("💡 These keys are required, please check .env file configuration")
        return False
    
    if missing_ai_keys:
        logger.warning(f"⚠️  Missing AI functionality keys: {', '.join(missing_ai_keys)}")
        logger.info("💡 AI features will be unavailable, but data source functionality will still work normally")
    else:
        logger.info("✅ AI functionality keys configuration complete")
    
    # Verify data source status
    try:
        from newsletter_agent.src.data_sources import data_aggregator
        status = data_aggregator.get_data_sources_status()
        
        available_sources = [name for name, available in status.items() if available]
        unavailable_sources = [name for name, available in status.items() if not available]
        
        if available_sources:
            logger.info(f"✅ Available data sources: {', '.join(available_sources)}")
        
        if unavailable_sources:
            logger.warning(f"⚠️  Unavailable data sources: {', '.join(unavailable_sources)}")
            
        if not available_sources:
            logger.error("❌ No available data sources!")
            return False
            
    except Exception as e:
        logger.warning(f"⚠️  Data source status check failed: {e}")
    
    logger.info("✅ Environment configuration check complete, application can start")
    return True


def main():
    """Main function"""
    # Setup logging
    setup_logging()
    
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Check environment
    if not check_environment():
        logger.error("💥 Environment check failed, cannot start application")
        sys.exit(1)
    
    try:
        # Import and start UI
        from newsletter_agent.src.ui.app import create_app
        
        logger.info("🎨 Starting user interface...")
        app = create_app()
        
        # Start Gradio application
        logger.info("🌐 Starting web server - http://localhost:7860")
        app.launch(
            server_name="127.0.0.1",
            server_port=7860,
            share=True,  # Create public link to solve proxy issues
            debug=settings.DEBUG
        )
        
    except ImportError as e:
        logger.error(f"💥 Module import failed: {e}")
        logger.info("💡 Please run: pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("👋 User interrupted, exiting...")
    except Exception as e:
        logger.error(f"💥 Application startup failed: {e}")
        import traceback
        logger.debug(f"Detailed error information:\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main() 