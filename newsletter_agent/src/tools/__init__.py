# -*- coding: utf-8 -*-
"""
Newsletter Agent - 工具模块
LangChain工具集合和工具管理功能
"""

# 导入工具类
from .data_source_tools import (
    NewsSearchTool,
    TrendingTopicsTool,
    ContentAnalysisTool,
    TopicResearchTool,
    get_all_tools,
    get_tool_by_name
)

from .ai_generation_tools import (
    NewsletterGenerationTool,
    ContentSummaryTool,
    HeadlineGenerationTool,
    ContentEnhancementTool,
    get_ai_tools,
    test_ai_connection
)

# 工具管理
def get_all_available_tools():
    """获取所有可用工具"""
    tools = []
    
    # 数据源工具
    data_tools = get_all_tools()
    tools.extend(data_tools)
    
    # AI工具
    ai_tools = get_ai_tools()
    tools.extend(ai_tools)
    
    return tools

def get_tools_by_category():
    """按类别获取工具"""
    return {
        "data_source": get_all_tools(),
        "ai_generation": get_ai_tools()
    }

def get_tool_names():
    """获取所有工具名称"""
    tools = get_all_available_tools()
    return [tool.name for tool in tools]

# 导出所有公共接口
__all__ = [
    # 数据源工具
    'NewsSearchTool',
    'TrendingTopicsTool', 
    'ContentAnalysisTool',
    'TopicResearchTool',
    
    # AI工具
    'NewsletterGenerationTool',
    'ContentSummaryTool',
    'HeadlineGenerationTool',
    'ContentEnhancementTool',
    
    # 工具管理函数
    'get_all_tools',
    'get_ai_tools',
    'get_all_available_tools',
    'get_tools_by_category',
    'get_tool_names',
    'get_tool_by_name',
    'test_ai_connection'
] 