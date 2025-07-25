#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Newsletter Agent - 快速启动脚本
帮助用户快速配置和启动系统
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """创建环境配置文件"""
    env_content = """# Newsletter Agent 环境配置文件
# 简化版本 - 仅保留核心功能

# 必需配置 - 这些配置是系统运行的最低要求

# NewsAPI 配置 (必需)
# 获取地址: https://newsapi.org/
NEWSAPI_KEY=your_newsapi_key_here

# OpenAI API 配置 (必需，用于AI功能)  
# 获取地址: https://platform.openai.com/
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1

# 可选配置 - 增强系统功能

# Reddit API 配置 (可选)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=newsletter_agent/1.0.0

# 应用配置
APP_NAME=Newsletter Agent
APP_VERSION=1.0.0
DEBUG=false
CONTENT_LANGUAGE=zh
MAX_ARTICLES_PER_SOURCE=10
DEFAULT_TOPICS=科技,商业,健康

# 注意：
# 1. 请将 your_newsapi_key_here 替换为真实的NewsAPI密钥
# 2. 请将 your_openai_api_key_here 替换为真实的OpenAI API密钥
# 3. Reddit API是可选的，如果不使用可以不配置
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(env_content)
        print("✅ 已创建 .env 配置文件")
        return True
    else:
        print("ℹ️  .env 文件已存在，跳过创建")
        return False

def check_dependencies():
    """检查依赖项"""
    print("🔍 检查依赖项...")
    
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
        print(f"\n⚠️  缺少以下依赖项: {', '.join(missing_packages)}")
        print("请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    else:
        print("✅ 所有依赖项都已安装")
        return True

def check_api_keys():
    """检查API密钥配置"""
    print("\n🔑 检查API密钥配置...")
    
    newsapi_key = os.getenv("NEWSAPI_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    
    if not newsapi_key or newsapi_key == "your_newsapi_key_here":
        print("  ❌ NewsAPI密钥未配置")
        print("     请到 https://newsapi.org/ 注册并获取API密钥")
        return False
    else:
        print("  ✅ NewsAPI密钥已配置")
    
    if not openai_key or openai_key == "your_openai_api_key_here":
        print("  ❌ OpenAI API密钥未配置")
        print("     请到 https://platform.openai.com/ 获取API密钥")
        return False
    else:
        print("  ✅ OpenAI API密钥已配置")
    
    return True

def main():
    """主函数"""
    print("🚀 Newsletter Agent - 快速启动向导")
    print("=" * 50)
    
    # 1. 创建环境文件
    print("\n📋 步骤 1: 创建配置文件")
    env_created = create_env_file()
    
    # 2. 检查依赖项
    print("\n📦 步骤 2: 检查依赖项")
    deps_ok = check_dependencies()
    
    if not deps_ok:
        print("\n❌ 请先安装缺失的依赖项，然后重新运行此脚本")
        return
    
    # 3. 加载环境变量
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("\n✅ 环境变量加载成功")
    except ImportError:
        print("\n❌ 无法加载环境变量，请安装 python-dotenv")
        return
    
    # 4. 检查API密钥
    print("\n🔑 步骤 3: 检查API密钥")
    keys_ok = check_api_keys()
    
    if not keys_ok:
        print("\n⚠️  请配置必要的API密钥后重新运行")
        print("1. 编辑 .env 文件")
        print("2. 替换 your_newsapi_key_here 为真实的NewsAPI密钥")
        print("3. 替换 your_openai_api_key_here 为真实的OpenAI API密钥")
        print("4. 保存文件并重新运行此脚本")
        return
    
    # 5. 启动应用
    print("\n🎯 步骤 4: 启动应用")
    print("正在启动Newsletter Agent...")
    
    try:
        # 启动主应用
        import main
        main.main()
    except KeyboardInterrupt:
        print("\n👋 用户中断，退出应用")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        print("请检查配置或查看错误日志")

if __name__ == "__main__":
    main() 