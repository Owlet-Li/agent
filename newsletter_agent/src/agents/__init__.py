# -*- coding: utf-8 -*-
"""
Newsletter Agent - 代理模块
智能新闻简报生成代理的核心组件
"""

# 导入代理相关组件
from .newsletter_agent import (
    NewsletterAgent,
    create_newsletter_agent,
    test_agent_functionality
)

from .prompts import (
    NewsletterAgentPrompts,
    newsletter_prompts,
    get_agent_prompt_templates,
    create_chat_prompt_template,
    get_dynamic_prompt
)

# 创建全局代理实例（延迟初始化）
_global_agent = None

def get_global_agent():
    """获取全局代理实例"""
    global _global_agent
    if _global_agent is None:
        _global_agent = create_newsletter_agent()
    return _global_agent

def reset_global_agent():
    """重置全局代理实例"""
    global _global_agent
    _global_agent = None

def create_agent_with_config(config: dict):
    """根据配置创建代理"""
    api_key = config.get('api_key')
    api_base = config.get('api_base') 
    return create_newsletter_agent(api_key, api_base)

# 代理管理功能
def get_agent_status():
    """获取代理状态"""
    try:
        agent = get_global_agent()
        return agent.get_agent_status()
    except Exception as e:
        return {
            "error": str(e),
            "is_ready": False
        }

def test_full_agent_stack():
    """测试完整的代理堆栈"""
    try:
        # 测试代理创建
        agent = create_newsletter_agent()
        
        # 测试基本功能
        status = agent.get_agent_status()
        
        # 测试工具加载
        tools_available = len(agent.tools) > 0
        
        # 测试LLM连接
        llm_available = agent.llm is not None
        
        return {
            "agent_creation": True,
            "tools_loaded": tools_available,
            "llm_available": llm_available,
            "overall_ready": agent.is_ready,
            "status": status
        }
        
    except Exception as e:
        return {
            "agent_creation": False,
            "error": str(e),
            "overall_ready": False
        }

# 导出所有公共接口
__all__ = [
    # 核心代理类
    'NewsletterAgent',
    'create_newsletter_agent',
    
    # 提示模板
    'NewsletterAgentPrompts',
    'newsletter_prompts',
    'get_agent_prompt_templates',
    'create_chat_prompt_template',
    'get_dynamic_prompt',
    
    # 代理管理
    'get_global_agent',
    'reset_global_agent',
    'create_agent_with_config',
    'get_agent_status',
    
    # 测试功能
    'test_agent_functionality',
    'test_full_agent_stack'
]

__version__ = "1.0.0"
__author__ = "AI Assistant"
__description__ = "智能新闻简报生成代理系统" 