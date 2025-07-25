# -*- coding: utf-8 -*-
"""
Newsletter Agent - 数据源工具
集成各种数据源的搜索和信息获取工具
"""

from typing import Type, Optional, List
from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field
from langchain.callbacks.manager import CallbackManagerForToolRun

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

try:
    from newsletter_agent.src.data_sources.aggregator import data_aggregator
    from newsletter_agent.src.content import text_processor, content_formatter
except ImportError:
    logger.warning("数据源模块导入失败，使用模拟数据")
    data_aggregator = None
    text_processor = None
    content_formatter = None


class NewsSearchInput(BaseModel):
    """新闻搜索工具输入"""
    query: str = Field(description="搜索关键词或主题")


class NewsSearchTool(BaseTool):
    """新闻搜索工具
    
    从NewsAPI搜索相关新闻内容
    """
    
    name: str = "news_search"
    description: str = """搜索最新新闻内容。使用此工具可以获取特定主题或关键词的新闻文章。"""
    args_schema: Type[BaseModel] = NewsSearchInput

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """执行新闻搜索"""
        try:
            if not data_aggregator:
                return self._get_mock_news(query)
            
            # 使用数据聚合器搜索新闻
            results = data_aggregator.multi_source_search(
                query=query,
                sources=['news'],
                max_results_per_source=10
            )
            
            news_articles = results.get('news', [])
            
            if not news_articles:
                return f"未找到关于'{query}'的相关新闻。"
            
            # 格式化结果
            formatted_results = []
            for i, article in enumerate(news_articles[:5], 1):
                formatted_results.append(
                    f"{i}. **{article.title}**\n"
                    f"   来源: {article.source}\n"
                    f"   时间: {article.published_at.strftime('%Y-%m-%d %H:%M')}\n"
                    f"   摘要: {article.content[:200]}...\n"
                    f"   链接: {article.url}\n"
                )
            
            return f"找到 {len(news_articles)} 篇关于'{query}'的新闻：\n\n" + "\n".join(formatted_results)
            
        except Exception as e:
            logger.error(f"新闻搜索失败: {e}")
            return f"搜索新闻时出现错误: {str(e)}"
    
    def _get_mock_news(self, query: str) -> str:
        """获取模拟新闻数据"""
        return f"""找到 3 篇关于'{query}'的新闻：

1. **{query}技术突破引关注**
   来源: 科技日报
   时间: 2024-01-15 10:30
   摘要: 最新的{query}技术突破为行业带来新的发展机遇...
   
2. **{query}市场前景广阔**
   来源: 财经周刊
   时间: 2024-01-15 09:15
   摘要: 分析师认为{query}相关市场将迎来快速增长期...
   
3. **专家解读{query}发展趋势**
   来源: 行业观察
   时间: 2024-01-15 08:45
   摘要: 业内专家对{query}未来发展方向进行深入分析..."""


class TrendingTopicsInput(BaseModel):
    """热门话题工具输入"""
    category: str = Field(description="分类筛选，如：tech, business, health等，默认为all")


class TrendingTopicsTool(BaseTool):
    """热门话题工具
    
    获取当前热门话题和趋势
    """
    
    name: str = "trending_topics"
    description: str = """获取当前热门话题和趋势新闻。使用此工具可以发现正在流行的新闻话题。"""
    args_schema: Type[BaseModel] = TrendingTopicsInput

    def _run(
        self,
        category: str = "all",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """获取热门话题"""
        try:
            if not data_aggregator:
                return self._get_mock_trending(category)
            
            # 定义热门话题关键词
            trending_topics = ["人工智能", "区块链", "量子计算", "新能源", "元宇宙"]
            
            if category != "all":
                # 根据分类调整话题
                category_topics = {
                    "tech": ["人工智能", "量子计算", "机器学习", "5G", "物联网"],
                    "business": ["数字化转型", "电商", "供应链", "投资", "创业"],
                    "health": ["医疗科技", "疫苗", "健康管理", "生物技术", "医疗AI"]
                }
                trending_topics = category_topics.get(category.lower(), trending_topics)
            
            # 获取趋势内容
            trending_content = data_aggregator.get_trending_content(
                topics=trending_topics[:3],
                sources=['news', 'reddit'],
                max_per_topic=3
            )
            
            if not trending_content:
                return f"未找到{category}分类的热门话题。"
            
            # 格式化结果
            result_lines = [f"当前热门话题 ({category})：\n"]
            
            for topic, articles in trending_content.items():
                if articles:
                    result_lines.append(f"## {topic}")
                    for i, article in enumerate(articles[:2], 1):
                        result_lines.append(
                            f"{i}. {article.title}\n"
                            f"   来源: {article.source} | 时间: {article.published_at.strftime('%m-%d %H:%M')}"
                        )
                    result_lines.append("")
            
            return "\n".join(result_lines)
            
        except Exception as e:
            logger.error(f"获取热门话题失败: {e}")
            return self._get_mock_trending(category)
    
    def _get_mock_trending(self, category: str) -> str:
        """获取模拟热门话题"""
        topics_by_category = {
            "tech": ["人工智能突破", "量子计算进展", "5G应用扩展"],
            "business": ["数字化转型", "电商新模式", "绿色投资"],
            "health": ["精准医疗", "健康科技", "疫苗研发"],
            "all": ["AI技术发展", "新能源汽车", "数字货币"]
        }
        
        topics = topics_by_category.get(category.lower(), topics_by_category["all"])
        
        result = f"当前热门话题 ({category})：\n\n"
        for i, topic in enumerate(topics, 1):
            result += f"{i}. **{topic}**\n   讨论热度: ⭐⭐⭐⭐⭐\n   相关文章: 15+ 篇\n\n"
        
        return result


class ContentAnalysisInput(BaseModel):
    """内容分析工具输入"""
    content: str = Field(description="要分析的文本内容")


class ContentAnalysisTool(BaseTool):
    """内容分析工具
    
    对文本内容进行分析，包括摘要、关键词提取、情感分析等
    """
    
    name: str = "content_analysis"
    description: str = """分析文本内容，提供摘要、关键词、分类等信息。"""
    args_schema: Type[BaseModel] = ContentAnalysisInput

    def _run(
        self,
        content: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """分析内容"""
        try:
            if not text_processor:
                return self._analyze_content_simple(content)
            
            # 使用文本处理器分析内容
            analysis_result = text_processor.preprocess_text(
                content,
                options={
                    "extract_keywords": True,
                    "max_keywords": 10,
                    "remove_stopwords": True
                }
            )
            
            # 格式化分析结果
            result_lines = [
                "## 内容分析报告\n",
                f"**原文长度**: {analysis_result['length']} 字符",
                f"**语言**: {analysis_result['language']}",
                f"**词汇数量**: {analysis_result['token_count']}",
                ""
            ]
            
            if analysis_result['keywords']:
                result_lines.append("**关键词**:")
                for i, keyword in enumerate(analysis_result['keywords'], 1):
                    result_lines.append(f"{i}. {keyword}")
                result_lines.append("")
            
            # 生成摘要
            if content_formatter:
                summary = content_formatter.generate_summary(content, max_length=150)
                result_lines.append(f"**内容摘要**: {summary}")
            
            return "\n".join(result_lines)
            
        except Exception as e:
            logger.error(f"内容分析失败: {e}")
            return self._analyze_content_simple(content)
    
    def _analyze_content_simple(self, content: str) -> str:
        """简单内容分析"""
        word_count = len(content.split())
        char_count = len(content)
        
        # 简单关键词提取
        words = content.split()
        word_freq = {}
        for word in words:
            clean_word = word.strip(".,!?;:()[]{}\"'").lower()
            if len(clean_word) > 2:
                word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
        
        # 获取最频繁的词作为关键词
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return f"""## 内容分析报告

**文本长度**: {char_count} 字符
**词汇数量**: {word_count} 个
**主要关键词**: {', '.join([kw[0] for kw in keywords])}

**简要摘要**: {content[:100]}{'...' if len(content) > 100 else ''}"""


class TopicResearchInput(BaseModel):
    """主题研究工具输入"""
    topic: str = Field(description="要研究的主题")


class TopicResearchTool(BaseTool):
    """主题研究工具
    
    对特定主题进行深度研究，整合多个数据源的信息
    """
    
    name: str = "topic_research"
    description: str = """对特定主题进行深度研究，整合来自新闻、社交媒体、RSS等多个数据源的信息。"""
    args_schema: Type[BaseModel] = TopicResearchInput

    def _run(
        self,
        topic: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """执行主题研究"""
        try:
            if not data_aggregator:
                return self._research_topic_simple(topic)
            
            # 多源研究
            research_results = data_aggregator.multi_source_search(
                query=topic,
                sources=['news', 'reddit', 'rss'],
                max_results_per_source=5
            )
            
            # 整合研究结果
            result_lines = [f"# {topic} - 深度研究报告\n"]
            
            total_sources = 0
            for source_type, articles in research_results.items():
                if articles:
                    total_sources += len(articles)
                    result_lines.append(f"## {source_type.upper()} 数据源")
                    
                    for i, article in enumerate(articles[:3], 1):
                        result_lines.append(
                            f"{i}. **{article.title}**\n"
                            f"   来源: {article.source}\n"
                            f"   摘要: {article.content[:150]}...\n"
                        )
                    result_lines.append("")
            
            if total_sources == 0:
                return f"未找到关于'{topic}'的研究资料。"
            
            # 添加研究总结
            result_lines.extend([
                "## 研究总结",
                f"- 共整合 {total_sources} 个信息源",
                f"- 涵盖新闻、社交媒体、RSS等多个渠道",
                f"- 为'{topic}'主题提供全面的信息视角",
                "",
                "*本报告由Newsletter Agent自动生成*"
            ])
            
            return "\n".join(result_lines)
            
        except Exception as e:
            logger.error(f"主题研究失败: {e}")
            return self._research_topic_simple(topic)
    
    def _research_topic_simple(self, topic: str) -> str:
        """简单主题研究"""
        return f"""# {topic} - 研究报告

## 概述
{topic}是当前备受关注的重要话题，涉及多个领域和维度。

## 主要发现
1. **技术层面**: {topic}相关技术不断演进发展
2. **市场层面**: 相关市场规模持续扩大
3. **应用层面**: 实际应用场景日益丰富
4. **社会层面**: 对社会发展产生积极影响

## 发展趋势
- 技术成熟度不断提升
- 应用范围持续拓展
- 市场竞争日趋激烈
- 监管政策逐步完善

## 关键洞察
{topic}作为新兴领域，具有巨大的发展潜力和投资价值，值得持续关注。

*本报告为示例内容，实际研究需要更多数据支持*"""


def get_all_tools() -> List[BaseTool]:
    """获取所有数据源工具"""
    tools = []
    
    try:
        # 新闻搜索工具
        news_tool = NewsSearchTool()
        tools.append(news_tool)
        logger.info("工具 news_search 初始化成功")
        
        # 热门话题工具
        trending_tool = TrendingTopicsTool()
        tools.append(trending_tool)
        logger.info("工具 trending_topics 初始化成功")
        
        # 内容分析工具
        analysis_tool = ContentAnalysisTool()
        tools.append(analysis_tool)
        logger.info("工具 content_analysis 初始化成功")
        
        # 主题研究工具
        research_tool = TopicResearchTool()
        tools.append(research_tool)
        logger.info("工具 topic_research 初始化成功")
        
    except Exception as e:
        logger.error(f"工具初始化失败: {e}")
    
    return tools


def get_tool_by_name(name: str) -> Optional[BaseTool]:
    """根据名称获取工具"""
    all_tools = get_all_tools()
    for tool in all_tools:
        if tool.name == name:
            return tool
    return None 