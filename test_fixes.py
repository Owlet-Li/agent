#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Newsletter Agent - Fix Verification Tests
Verify if system fixes are successful
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test module imports"""
    print("🔍 Testing module imports...")
    
    try:
        # 测试基础模块导入
        from newsletter_agent.config.settings import settings
        print("  ✅ Config module imported successfully")
        
        from newsletter_agent.src.agents import get_global_agent, get_agent_status
        print("  ✅ Agent module imported successfully")
        
        from newsletter_agent.src.tools.ai_generation_tools import get_ai_tools
        print("  ✅ AI tools module imported successfully")
        
        from newsletter_agent.src.tools.data_source_tools import get_all_tools
        print("  ✅ Data source tools module imported successfully")
        
        from newsletter_agent.src.ui.app import create_app
        print("  ✅ UI module imported successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Module import failed: {e}")
        return False

def test_tools():
    """Test tools initialization"""
    print("\n🔧 Testing tools initialization...")
    
    try:
        from newsletter_agent.src.tools.ai_generation_tools import get_ai_tools
        from newsletter_agent.src.tools.data_source_tools import get_all_tools
        
        ai_tools = get_ai_tools()
        data_tools = get_all_tools()
        
        print(f"  ✅ AI tools: {len(ai_tools)} available")
        print(f"  ✅ Data source tools: {len(data_tools)} available")
        
        # 测试工具名称
        for tool in ai_tools:
            print(f"    - {tool.name}")
        
        for tool in data_tools:
            print(f"    - {tool.name}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Tools initialization failed: {e}")
        return False

def test_agent():
    """Test agent creation"""
    print("\n🤖 Testing agent creation...")
    
    try:
        from newsletter_agent.src.agents import create_newsletter_agent
        
        # 不需要真实API密钥也能创建代理
        agent = create_newsletter_agent()
        status = agent.get_agent_status()
        
        print(f"  ✅ Agent created successfully")
        print(f"  📊 Agent status: {'Ready' if status.get('is_ready') else 'Not ready'}")
        print(f"  🔧 Tools count: {status.get('tools_count', 0)}")
        print(f"  🧠 LLM available: {'Yes' if status.get('llm_available') else 'No'}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Agent creation failed: {e}")
        return False

def test_ui():
    """Test UI creation"""
    print("\n🎨 Testing UI creation...")
    
    try:
        from newsletter_agent.src.ui.app import create_app
        
        app = create_app()
        
        print("  ✅ UI created successfully")
        print("  📱 Gradio app is ready")
        
        return True
        
    except Exception as e:
        print(f"  ❌ UI creation failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Newsletter Agent Fix Verification Tests")
    print("=" * 50)
    
    tests = [
        ("Module imports", test_imports),
        ("Tools initialization", test_tools),
        ("Agent creation", test_agent),
        ("UI creation", test_ui)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {test_name} test passed")
            else:
                print(f"\n❌ {test_name} test failed")
        except Exception as e:
            print(f"\n💥 {test_name} test exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! System fixes successful!")
        print("\nNext steps:")
        print("1. Configure API keys in .env file")
        print("2. Run python main.py to start the application")
        print("3. Access http://localhost:7860 to use the system")
    else:
        print("⚠️  Some tests failed, please check error messages")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
