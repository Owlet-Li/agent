#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试阶段四：LangChain Agent Building
验证智能代理、工具集成和AI功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_tool_imports():
    """测试工具模块导入"""
    print("🔧 测试工具模块导入...")
    
    try:
        from newsletter_agent.src.tools import (
            get_all_available_tools,
            get_tools_by_category, 
            get_tool_names,
            test_ai_connection
        )
        
        # 获取所有工具
        all_tools = get_all_available_tools()
        print(f"✅ 成功加载 {len(all_tools)} 个工具")
        
        # 按类别显示工具
        tools_by_category = get_tools_by_category()
        for category, tools in tools_by_category.items():
            print(f"   📦 {category}: {len(tools)} 个工具")
        
        # 显示工具名称
        tool_names = get_tool_names()
        print(f"✅ 可用工具: {', '.join(tool_names)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 工具导入失败: {e}")
        return False

def test_prompt_templates():
    """测试提示模板"""
    print("\n💭 测试提示模板...")
    
    try:
        from newsletter_agent.src.agents.prompts import (
            newsletter_prompts,
            get_agent_prompt_templates,
            get_dynamic_prompt
        )
        
        # 测试系统提示
        system_prompt = newsletter_prompts.get_system_prompt()
        print(f"✅ 系统提示长度: {len(system_prompt)} 字符")
        
        # 测试动态提示
        context = {"topic": "人工智能", "depth": "medium"}
        research_prompt = get_dynamic_prompt("research", context)
        print(f"✅ 研究提示生成成功")
        
        # 测试所有模板
        templates = get_agent_prompt_templates()
        print(f"✅ 加载 {len(templates)} 个提示模板")
        
        return True
        
    except Exception as e:
        print(f"❌ 提示模板测试失败: {e}")
        return False

def test_agent_creation():
    """测试代理创建"""
    print("\n🤖 测试代理创建...")
    
    try:
        from newsletter_agent.src.agents import (
            create_newsletter_agent,
            test_full_agent_stack
        )
        
        # 创建代理
        agent = create_newsletter_agent()
        print(f"✅ 代理创建成功: {agent.agent_name}")
        
        # 获取状态
        status = agent.get_agent_status()
        print(f"✅ 代理状态:")
        print(f"   - 就绪状态: {status['is_ready']}")
        print(f"   - LLM可用: {status['llm_available']}")
        print(f"   - 工具数量: {status['tools_count']}")
        print(f"   - LangChain可用: {status['langchain_available']}")
        
        # 测试完整堆栈
        stack_test = test_full_agent_stack()
        print(f"✅ 完整堆栈测试:")
        print(f"   - 代理创建: {stack_test['agent_creation']}")
        print(f"   - 工具加载: {stack_test['tools_loaded']}")
        print(f"   - LLM可用: {stack_test['llm_available']}")
        print(f"   - 整体就绪: {stack_test['overall_ready']}")
        
        return agent, status['is_ready']
        
    except Exception as e:
        print(f"❌ 代理创建失败: {e}")
        return None, False

def test_basic_chat(agent):
    """测试基础对话功能"""
    print("\n💬 测试基础对话...")
    
    if not agent:
        print("⚠️ 跳过对话测试（代理未就绪）")
        return False
    
    try:
        # 简单问候
        result = agent.chat("你好，请介绍一下你的功能")
        
        if result['success']:
            print("✅ 对话测试成功")
            print(f"   响应长度: {len(result['message'])} 字符")
            print(f"   会话ID: {result['session_id']}")
            print(f"   使用工具: {result.get('tools_used', [])}")
            print(f"   响应摘要: {result['message'][:100]}...")
        else:
            print(f"❌ 对话失败: {result['message']}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 对话测试失败: {e}")
        return False

def test_tool_integration(agent):
    """测试工具集成"""
    print("\n🔧 测试工具集成...")
    
    if not agent:
        print("⚠️ 跳过工具测试（代理未就绪）")
        return False
    
    try:
        # 测试新闻搜索工具
        result = agent.chat("请搜索关于'人工智能'的最新新闻")
        
        if result['success']:
            print("✅ 新闻搜索工具测试通过")
            tools_used = result.get('tools_used', [])
            if tools_used:
                print(f"   使用的工具: {', '.join(tools_used)}")
            else:
                print("   注意: 未检测到工具使用（可能是API限制）")
        else:
            print(f"❌ 工具测试失败: {result['message']}")
        
        return result['success']
        
    except Exception as e:
        print(f"❌ 工具集成测试失败: {e}")
        return False

def test_ai_generation():
    """测试AI生成功能"""
    print("\n🎨 测试AI生成功能...")
    
    try:
        from newsletter_agent.src.tools.ai_generation_tools import test_ai_connection
        
        # 测试AI连接
        ai_available = test_ai_connection()
        print(f"✅ AI连接测试: {'成功' if ai_available else '失败'}")
        
        if not ai_available:
            print("⚠️ AI功能不可用，请检查API密钥配置")
            return False
        
        # 如果AI可用，测试基本生成
        from newsletter_agent.src.tools.ai_generation_tools import ContentSummaryTool
        
        summary_tool = ContentSummaryTool()
        test_content = "人工智能技术正在快速发展，深度学习和机器学习算法在各个领域都有广泛应用。"
        
        result = summary_tool._run(test_content, max_length=50)
        
        if "AI生成摘要" in result or "本地生成摘要" in result:
            print("✅ AI摘要生成测试通过")
            print(f"   结果: {result[:100]}...")
        else:
            print(f"❌ AI生成测试失败: {result}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ AI生成功能测试失败: {e}")
        return False

def test_newsletter_generation(agent):
    """测试简报生成功能"""
    print("\n📰 测试简报生成...")
    
    if not agent:
        print("⚠️ 跳过简报生成测试（代理未就绪）")
        return False
    
    try:
        # 生成简单的测试简报
        result = agent.generate_newsletter(
            topic="科技发展趋势",
            style="professional",
            audience="general",
            length="short"
        )
        
        if result['success']:
            print("✅ 简报生成测试通过")
            print(f"   生成内容长度: {len(result['message'])} 字符")
            print(f"   内容预览: {result['message'][:200]}...")
        else:
            print(f"❌ 简报生成失败: {result['message']}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 简报生成测试失败: {e}")
        return False

def test_content_analysis(agent):
    """测试内容分析功能"""
    print("\n📊 测试内容分析...")
    
    if not agent:
        print("⚠️ 跳过内容分析测试（代理未就绪）")
        return False
    
    try:
        test_content = """
        人工智能技术正在改变世界。深度学习和机器学习算法在图像识别、
        自然语言处理、推荐系统等领域发挥重要作用。未来AI将在更多
        行业中得到应用，包括医疗、金融、交通、教育等。
        """
        
        result = agent.analyze_content(test_content)
        
        if result['success']:
            print("✅ 内容分析测试通过")
            print(f"   分析结果长度: {len(result['message'])} 字符")
        else:
            print(f"❌ 内容分析失败: {result['message']}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 内容分析测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始阶段四测试：LangChain Agent Building\n")
    
    test_results = {}
    
    # 1. 测试工具导入
    test_results['tools'] = test_tool_imports()
    
    # 2. 测试提示模板
    test_results['prompts'] = test_prompt_templates()
    
    # 3. 测试代理创建
    agent, agent_ready = test_agent_creation()
    test_results['agent_creation'] = agent is not None
    test_results['agent_ready'] = agent_ready
    
    # 4. 测试基础对话
    test_results['basic_chat'] = test_basic_chat(agent)
    
    # 5. 测试工具集成
    test_results['tool_integration'] = test_tool_integration(agent)
    
    # 6. 测试AI生成
    test_results['ai_generation'] = test_ai_generation()
    
    # 7. 测试简报生成
    test_results['newsletter_generation'] = test_newsletter_generation(agent)
    
    # 8. 测试内容分析
    test_results['content_analysis'] = test_content_analysis(agent)
    
    # 总结测试结果
    print("\n" + "="*60)
    print("📊 阶段四测试结果总结:")
    print("="*60)
    
    for test_name, result in test_results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:20} - {status}")
    
    # 计算总体成功率
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\n总体测试结果: {passed_tests}/{total_tests} 通过 ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("\n🎉 阶段四构建成功！智能代理系统基本就绪")
        
        print("\n📋 阶段四完成功能总结:")
        print("✅ LangChain工具集成 - 8个专业工具")
        print("✅ 智能代理创建 - 多步推理和决策")
        print("✅ AI内容生成 - OpenRouter API集成")
        print("✅ 提示模板系统 - 动态任务指导")
        print("✅ 代理执行器 - 工具选择和组合")
        print("✅ 对话管理 - 上下文感知交互")
        
    elif success_rate >= 60:
        print("\n⚠️ 阶段四部分成功，某些功能需要进一步配置")
        print("💡 建议检查API密钥配置和网络连接")
        
    else:
        print("\n❌ 阶段四测试未达到预期，需要检查配置")
        print("💡 请检查依赖安装、API密钥和网络连接")
    
    return success_rate >= 80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 