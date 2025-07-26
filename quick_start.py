#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Newsletter Agent - Quick Start Script
Helps users quickly configure and start the system
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create environment config file"""
    env_content = """# Newsletter Agent Environment Config File
# Simplified version - core features only

# Required settings - minimum requirements for system operation

# NewsAPI Configuration (Required)
# Get API key: https://newsapi.org/
NEWSAPI_KEY=your_newsapi_key_here

# OpenAI API Configuration (Required for AI features)
# Get API key: https://platform.openai.com/
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1

# Optional settings - enhance system features

# Reddit API Configuration (Optional)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=newsletter_agent/1.0.0

# Application Settings
APP_NAME=Newsletter Agent
APP_VERSION=1.0.0
DEBUG=false
CONTENT_LANGUAGE=zh
MAX_ARTICLES_PER_SOURCE=10
DEFAULT_TOPICS=technology,business,health

# Notes:
# 1. Replace your_newsapi_key_here with your real NewsAPI key
# 2. Replace your_openai_api_key_here with your real OpenAI API key
# 3. Reddit API is optional, can be left unconfigured if not used
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(env_content)
        print("✅ Created .env config file")
        return True
    else:
        print("ℹ️  .env file already exists, skipping creation")
        return False

def check_dependencies():
    """Check dependencies"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "gradio", "langchain", "langchain-openai", "loguru", 
        "pydantic", "requests", "python-dotenv"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing_packages)}")
        print("Please run the following command to install:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    else:
        print("✅ All dependencies are installed")
        return True

def check_api_keys():
    """Check API key configuration"""
    print("\n🔑 Checking API key configuration...")
    
    newsapi_key = os.getenv("NEWSAPI_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    
    if not newsapi_key or newsapi_key == "your_newsapi_key_here":
        print("  ❌ NewsAPI key not configured")
        print("     Please register at https://newsapi.org/ to get an API key")
        return False
    else:
        print("  ✅ NewsAPI key configured")
    
    if not openai_key or openai_key == "your_openai_api_key_here":
        print("  ❌ OpenAI API key not configured")
        print("     Please get an API key from https://platform.openai.com/")
        return False
    else:
        print("  ✅ OpenAI API key configured")
    
    return True

def main():
    """Main function"""
    print("🚀 Newsletter Agent - Quick Start Wizard")
    print("=" * 50)
    
    # 1. Create environment file
    print("\n📋 Step 1: Create config file")
    env_created = create_env_file()
    
    # 2. Check dependencies
    print("\n📦 Step 2: Check dependencies")
    deps_ok = check_dependencies()
    
    if not deps_ok:
        print("\n❌ Please install missing dependencies first, then rerun this script")
        return
    
    # 3. Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("\n✅ Environment variables loaded successfully")
    except ImportError:
        print("\n❌ Failed to load environment variables, please install python-dotenv")
        return
    
    # 4. Check API keys
    print("\n🔑 Step 3: Check API keys")
    keys_ok = check_api_keys()
    
    if not keys_ok:
        print("\n⚠️  Please configure required API keys and rerun")
        print("1. Edit .env file")
        print("2. Replace your_newsapi_key_here with real NewsAPI key")
        print("3. Replace your_openai_api_key_here with real OpenAI API key")
        print("4. Save file and rerun this script")
        return
    
    # 5. Start application
    print("\n🎯 Step 4: Start application")
    print("Starting Newsletter Agent...")
    
    try:
        # Start main application
        import main
        main.main()
    except KeyboardInterrupt:
        print("\n👋 User interrupted, exiting application")
    except Exception as e:
        print(f"\n❌ Failed to start: {e}")
        print("Please check configuration or view error logs")

if __name__ == "__main__":
    main()
