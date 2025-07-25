# -*- coding: utf-8 -*-
"""
Newsletter Agent - 数据源工具
将数据源包装为LangChain工具
"""

from typing import List, Dict, Any, Optional, Type
from pydantic import BaseModel, Field

try:
    from langchain.tools import BaseTool
    from langchain.callbacks.manager import CallbackManagerForToolRun
    LANGCHAIN_AVAILABLE = True
except ImportError:
    # 降级处理
    LANGCHAIN_AVAILABLE = False
    BaseTool = object
    CallbackManagerForToolRun = object

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class NewsSearchInput(BaseModel):
    """新闻搜索工具输入"""
    query: str = Field(description="搜索关键词或主题")
    max_results: int = Field(default=10, description="最大结果数量")
    language: str = Field(default="zh", description="内容语言")


class NewsSearchTool(BaseTool):
    """新闻搜索工具
    
    从NewsAPI搜索相关新闻内容
    """
    
    name: str = "news_search"
    description: str = """搜索最新新闻内容。使用此工具可以获取特定主题或关键词的新闻文章。输入应该是一个包含搜索查询的字符串。"""
    args_schema: Type[BaseModel] = NewsSearchInput
    
    def _run(
        self,
        query: str,
        max_results: int = 10,
        language: str = "zh",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """执行新闻搜索"""
        try:
            # 导入数据聚合器
            from newsletter_agent.src.data_sources import data_aggregator
            
            # 使用数据聚合器搜索新闻
            search_results = data_aggregator.multi_source_search(
                query=query,
                sources=["news", "rss"],  # 专注于新闻和RSS搜索
                max_results_per_source=max_results
            )
            
            # 合并所有数据源的结果
            results = []
            for source_name, source_results in search_results.items():
                results.extend(source_results)
            
            if not results:
                return f"未找到关于'{query}'的新闻内容"
            
            # 格式化搜索结果
            formatted_results = []
            for item in results[:max_results]:
                title = item.get('title', '无标题')
                content = item.get('content', '无内容')[:200] + "..."
                source = item.get('source', '未知来源')
                url = item.get('url', '')
                
                formatted_results.append(f"""
标题: {title}
来源: {source}
内容摘要: {content}
链接: {url}
---""")
            
            return f"找到 {len(results)} 条关于'{query}'的新闻:\n" + "\n".join(formatted_results)
            
        except Exception as e:
            logger.error(f"新闻搜索失败: {e}")
            return f"搜索'{query}'时发生错误: {str(e)}"


class TrendingTopicsInput(BaseModel):
    """热门话题工具输入"""
    category: str = Field(default="all", description="分类筛选 (all, tech, business, health, etc.)")
    max_results: int = Field(default=10, description="最大结果数量")


class TrendingTopicsTool(BaseTool):
    """热门话题工具
    
    获取当前热门话题和趋势
    """
    
    name: str = "trending_topics"
    description: str = """获取当前热门话题和趋势新闻。使用此工具可以发现正在流行的新闻话题。可以指定分类来筛选特定领域的热门话题。"""
    args_schema: Type[BaseModel] = TrendingTopicsInput
    
    def _run(
        self,
        category: str = "all",
        max_results: int = 10,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """获取热门话题"""
        try:
            from newsletter_agent.src.data_sources import data_aggregator
            
            # 获取热门内容
            trending_results = data_aggregator.get_trending_content(
                topics=["科技", "商业", "健康", "娱乐", "体育"],  # 默认热门话题
                max_per_topic=max_results // 2 + 1
            )
            
            # 合并所有话题的结果
            trending_content = []
            for topic_name, topic_results in trending_results.items():
                trending_content.extend(topic_results)
            
            if not trending_content:
                return "当前没有发现热门话题"
            
            # 按分类筛选（如果指定）
            if category != "all":
                # 这里可以扩展分类筛选逻辑
                pass
            
            # 格式化热门话题
            formatted_topics = []
            for item in trending_content[:max_results]:
                title = item.get('title', '无标题')
                source = item.get('source', '未知来源')
                
                formatted_topics.append(f"• {title} (来源: {source})")
            
            return f"当前热门话题 ({category} 分类):\n" + "\n".join(formatted_topics)
            
        except Exception as e:
            logger.error(f"获取热门话题失败: {e}")
            return f"获取热门话题时发生错误: {str(e)}"


class ContentAnalysisInput(BaseModel):
    """内容分析工具输入"""
    content: str = Field(description="要分析的文本内容")
    analysis_type: str = Field(default="summary", description="分析类型: summary, keywords, sentiment, classification")


class ContentAnalysisTool(BaseTool):
    """内容分析工具
    
    对文本内容进行分析，包括摘要、关键词提取、情感分析等
    """
    
    name: str = "content_analysis"
    description: str = """分析文本内容，提供摘要、关键词、分类等信息。可以指定分析类型：summary(摘要)、keywords(关键词)、classification(分类)。"""
    args_schema: Type[BaseModel] = ContentAnalysisInput
    
    def _run(
        self,
        content: str,
        analysis_type: str = "summary",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """执行内容分析"""
        try:
            from newsletter_agent.src.content import (
                text_processor, 
                content_formatter, 
                content_classifier
            )
            
            if analysis_type == "summary":
                # 生成摘要
                summary = content_formatter.generate_summary(content, max_length=200)
                return f"内容摘要:\n{summary}"
                
            elif analysis_type == "keywords":
                # 提取关键词
                processed = text_processor.preprocess_text(content)
                keywords = processed.get('keywords', [])
                return f"关键词: {', '.join(keywords[:10])}"
                
            elif analysis_type == "classification":
                # 内容分类
                classification = content_classifier.classify_content({
                    'title': content[:100],  # 使用前100字符作为标题
                    'content': content
                })
                category = classification.get('category', '未分类')
                confidence = classification.get('confidence', 0)
                return f"内容分类: {category} (置信度: {confidence:.2f})"
                
            else:
                # 综合分析
                processed = text_processor.preprocess_text(content)
                summary = content_formatter.generate_summary(content, max_length=150)
                classification = content_classifier.classify_content({
                    'title': content[:100],
                    'content': content
                })
                
                return f"""综合分析结果:
摘要: {summary}
关键词: {', '.join(processed.get('keywords', [])[:5])}
分类: {classification.get('category', '未分类')} (置信度: {classification.get('confidence', 0):.2f})
语言: {processed.get('language', '未知')}
字数: {processed.get('length', 0)}"""
                
        except Exception as e:
            logger.error(f"内容分析失败: {e}")
            return f"分析内容时发生错误: {str(e)}"


class TopicResearchInput(BaseModel):
    """主题研究工具输入"""
    topic: str = Field(description="要研究的主题")
    depth: str = Field(default="medium", description="研究深度: light, medium, deep")
    max_sources: int = Field(default=20, description="最大数据源数量")


class TopicResearchTool(BaseTool):
    """主题研究工具
    
    对特定主题进行深度研究，整合多个数据源的信息
    """
    
    name: str = "topic_research"
    description: str = """对特定主题进行深度研究，整合来自新闻、社交媒体、RSS等多个数据源的信息。可以指定研究深度：light(轻度)、medium(中度)、deep(深度)。"""
    args_schema: Type[BaseModel] = TopicResearchInput
    
    def _run(
        self,
        topic: str,
        depth: str = "medium",
        max_sources: int = 20,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """执行主题研究"""
        try:
            from newsletter_agent.src.data_sources import data_aggregator
            from newsletter_agent.src.content import content_deduplicator, content_formatter
            
            # 根据深度确定搜索策略
            search_strategies = {
                "light": {"max_results": 5, "sources": ["news"]},
                "medium": {"max_results": 10, "sources": ["news", "rss"]},
                "deep": {"max_results": 20, "sources": ["news", "rss", "reddit"]}
            }
            
            strategy = search_strategies.get(depth, search_strategies["medium"])
            
            # 执行多源搜索
            search_results = data_aggregator.multi_source_search(
                query=topic,
                sources=strategy["sources"],
                max_results_per_source=strategy["max_results"]
            )
            
            # 合并所有数据源的结果
            raw_results = []
            for source_name, source_results in search_results.items():
                raw_results.extend(source_results)
            
            if not raw_results:
                return f"未找到关于'{topic}'的研究资料"
            
            # 去重处理
            dedup_result = content_deduplicator.deduplicate_batch(raw_results)
            unique_results = dedup_result['unique_items']
            
            # 格式化研究报告
            research_report = f"""
主题研究报告: {topic}
研究深度: {depth}
数据源: {', '.join(strategy["sources"])}
=====================

找到 {len(raw_results)} 条原始资料，去重后保留 {len(unique_results)} 条独特内容。

主要发现:
"""
            
            # 添加前几条重要内容
            for i, item in enumerate(unique_results[:5], 1):
                title = item.get('title', '无标题')
                content = item.get('content', '')[:200] + "..."
                source = item.get('source', '未知来源')
                
                research_report += f"""
{i}. {title}
   来源: {source}
   摘要: {content}
"""
            
            # 添加统计信息
            if len(unique_results) > 5:
                research_report += f"\n... 还有 {len(unique_results) - 5} 条相关内容。"
            
            research_report += f"""

去重统计:
- 原始内容: {dedup_result['statistics']['total_items']}
- 唯一内容: {dedup_result['statistics']['unique_items']}
- 重复内容: {dedup_result['statistics']['duplicate_items']}
"""
            
            return research_report
            
        except Exception as e:
            logger.error(f"主题研究失败: {e}")
            return f"研究'{topic}'时发生错误: {str(e)}"


# 工具注册表
AVAILABLE_TOOLS = [
    NewsSearchTool,
    TrendingTopicsTool,
    ContentAnalysisTool,
    TopicResearchTool
]


def get_all_tools() -> List[BaseTool]:
    """获取所有可用工具实例"""
    if not LANGCHAIN_AVAILABLE:
        logger.warning("LangChain不可用，无法创建工具")
        return []
    
    tools = []
    for tool_class in AVAILABLE_TOOLS:
        try:
            tool = tool_class()
            tools.append(tool)
            logger.info(f"工具 {tool.name} 初始化成功")
        except Exception as e:
            logger.error(f"工具 {tool_class.__name__} 初始化失败: {e}")
    
    return tools


def get_tool_by_name(name: str) -> Optional[BaseTool]:
    """根据名称获取特定工具"""
    tools = get_all_tools()
    for tool in tools:
        if tool.name == name:
            return tool
    return None 