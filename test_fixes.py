#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Newsletter Agent - 修复验证测试
验证系统修复是否成功
"""

import os
import sys
from pathlib import Path

def test_imports():
    """测试模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        # 测试基础模块导入
        from newsletter_agent.config.settings import settings
        print("  ✅ 配置模块导入成功")
        
        from newsletter_agent.src.agents import get_global_agent, get_agent_status
        print("  ✅ 代理模块导入成功")
        
        from newsletter_agent.src.tools.ai_generation_tools import get_ai_tools
        print("  ✅ AI工具模块导入成功")
        
        from newsletter_agent.src.tools.data_source_tools import get_all_tools
        print("  ✅ 数据源工具模块导入成功")
        
        from newsletter_agent.src.ui.app import create_app
        print("  ✅ UI模块导入成功")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 模块导入失败: {e}")
        return False

def test_tools():
    """测试工具初始化"""
    print("\n🔧 测试工具初始化...")
    
    try:
        from newsletter_agent.src.tools.ai_generation_tools import get_ai_tools
        from newsletter_agent.src.tools.data_source_tools import get_all_tools
        
        ai_tools = get_ai_tools()
        data_tools = get_all_tools()
        
        print(f"  ✅ AI工具: {len(ai_tools)} 个")
        print(f"  ✅ 数据源工具: {len(data_tools)} 个")
        
        # 测试工具名称
        for tool in ai_tools:
            print(f"    - {tool.name}")
        
        for tool in data_tools:
            print(f"    - {tool.name}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 工具初始化失败: {e}")
        return False

def test_agent():
    """测试代理创建"""
    print("\n🤖 测试代理创建...")
    
    try:
        from newsletter_agent.src.agents import create_newsletter_agent
        
        # 不需要真实API密钥也能创建代理
        agent = create_newsletter_agent()
        status = agent.get_agent_status()
        
        print(f"  ✅ 代理创建成功")
        print(f"  📊 代理状态: {'就绪' if status.get('is_ready') else '未就绪'}")
        print(f"  🔧 工具数量: {status.get('tools_count', 0)}")
        print(f"  🧠 LLM可用: {'是' if status.get('llm_available') else '否'}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 代理创建失败: {e}")
        return False

def test_ui():
    """测试UI创建"""
    print("\n🎨 测试UI创建...")
    
    try:
        from newsletter_agent.src.ui.app import create_app
        
        app = create_app()
        
        print("  ✅ UI创建成功")
        print("  📱 Gradio应用已准备就绪")
        
        return True
        
    except Exception as e:
        print(f"  ❌ UI创建失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 Newsletter Agent 修复验证测试")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("工具初始化", test_tools),
        ("代理创建", test_agent),
        ("UI创建", test_ui)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {test_name} 测试通过")
            else:
                print(f"\n❌ {test_name} 测试失败")
        except Exception as e:
            print(f"\n💥 {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统修复成功！")
        print("\n下一步：")
        print("1. 配置 .env 文件中的API密钥")
        print("2. 运行 python main.py 启动应用")
        print("3. 访问 http://localhost:7860 使用系统")
    else:
        print("⚠️  部分测试失败，请检查错误信息")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 