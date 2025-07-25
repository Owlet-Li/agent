# -*- coding: utf-8 -*-
"""
Newsletter Agent - 代理提示模板
定义AI代理的行为、决策逻辑和交互模式
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    from langchain.prompts import PromptTemplate, ChatPromptTemplate
    from langchain.schema import SystemMessage, HumanMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    PromptTemplate = object
    ChatPromptTemplate = object
    SystemMessage = object
    HumanMessage = object

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class NewsletterAgentPrompts:
    """新闻简报代理提示模板集合"""
    
    def __init__(self):
        """初始化提示模板"""
        self.current_date = datetime.now().strftime("%Y年%m月%d日")
        self.agent_name = "Newsletter Agent"
        
    def get_system_prompt(self) -> str:
        """获取系统级提示"""
        return f"""你是 {self.agent_name}，一个专业的新闻简报生成助手。今天是{self.current_date}。

你的核心能力包括：
1. 🔍 新闻搜索和信息收集
2. 📊 内容分析和质量评估  
3. 📝 智能摘要和分类
4. 🎯 个性化简报生成
5. 🤖 多步骤推理和决策

你可以使用以下工具：
- news_search: 搜索最新新闻内容
- trending_topics: 获取热门话题
- content_analysis: 分析文本内容
- topic_research: 深度主题研究
- newsletter_generation: 生成个性化简报
- content_summary: 生成内容摘要
- headline_generation: 生成吸引人的标题
- content_enhancement: 改进现有内容

工作原则：
1. 始终以用户需求为导向
2. 确保信息准确性和时效性
3. 提供有价值的洞察和分析
4. 保持客观中立的立场
5. 生成高质量、有吸引力的内容

在执行任务时，请按照以下流程：
1. 理解用户需求和偏好
2. 制定信息收集策略
3. 使用适当的工具收集和分析信息
4. 整合信息并生成结构化内容
5. 根据反馈优化输出

请始终以专业、友好、高效的方式与用户互动。"""

    def get_task_planning_prompt(self) -> str:
        """获取任务规划提示"""
        return """作为Newsletter Agent，当用户提出需求时，请按以下步骤进行任务规划：

1. **需求分析**
   - 明确用户的具体需求
   - 识别目标受众和内容偏好
   - 确定简报的范围和深度

2. **信息收集策略**
   - 确定需要搜索的主题和关键词
   - 选择合适的数据源和工具
   - 设定搜索的广度和深度

3. **执行计划**
   - 制定详细的执行步骤
   - 估算所需时间和资源
   - 确定输出格式和结构

4. **质量控制**
   - 设定内容质量标准
   - 规划信息验证流程
   - 准备用户反馈机制

请在开始执行前，简要说明你的规划，然后开始逐步执行。"""

    def get_research_prompt(self, topic: str, depth: str = "medium") -> str:
        """获取研究任务提示"""
        depth_descriptions = {
            "light": "快速浏览，获取基本信息和要点",
            "medium": "中等深度研究，包含关键信息和一些分析",
            "deep": "深度研究，全面分析，包含背景、影响和展望"
        }
        
        return f"""请对主题"{topic}"进行{depth_descriptions.get(depth, "中等深度")}研究。

研究要求：
1. 使用topic_research工具收集基础信息
2. 分析收集到的信息质量和相关性
3. 识别关键趋势和重要发现
4. 总结核心观点和洞察

研究深度：{depth}
- {depth_descriptions.get(depth, "中等深度研究")}

请开始研究并提供详细的发现报告。"""

    def get_newsletter_generation_prompt(self, 
                                       topic: str, 
                                       style: str = "professional",
                                       audience: str = "general",
                                       length: str = "medium") -> str:
        """获取简报生成提示"""
        return f"""基于之前的研究结果，请生成关于"{topic}"的新闻简报。

简报要求：
- 主题：{topic}
- 风格：{style}
- 受众：{audience} 
- 长度：{length}

生成流程：
1. 首先使用headline_generation工具生成吸引人的标题
2. 使用content_summary工具为关键信息生成摘要
3. 使用newsletter_generation工具生成完整简报
4. 必要时使用content_enhancement工具优化内容质量

请确保简报内容：
- 结构清晰，逻辑连贯
- 信息准确，观点平衡
- 语言流畅，易于阅读
- 突出重点，有价值洞察

开始生成简报。"""

    def get_content_analysis_prompt(self, content: str) -> str:
        """获取内容分析提示"""
        return f"""请对以下内容进行全面分析：

内容：
{content[:500]}...

分析要求：
1. 使用content_analysis工具进行基础分析
2. 评估内容质量和可信度
3. 识别关键信息和观点
4. 分析潜在影响和意义
5. 提供改进建议

请提供详细的分析报告。"""

    def get_trending_analysis_prompt(self, category: str = "all") -> str:
        """获取热点分析提示"""
        return f"""请分析当前的热门话题和趋势。

分析范围：{category}

分析步骤：
1. 使用trending_topics工具获取热门话题
2. 分析话题的重要性和影响力
3. 识别潜在的新闻价值
4. 评估话题的持续性和发展趋势
5. 推荐最值得关注的话题

请提供热点分析报告和话题推荐。"""

    def get_error_handling_prompt(self, error_type: str, context: str) -> str:
        """获取错误处理提示"""
        error_prompts = {
            "tool_failure": "工具执行失败，请尝试其他方法或工具",
            "no_results": "未找到相关信息，请调整搜索策略",
            "api_error": "API服务暂时不可用，请使用备用方案",
            "content_quality": "内容质量不符合要求，请重新生成或优化"
        }
        
        base_prompt = error_prompts.get(error_type, "遇到未知错误，请分析并采取相应措施")
        
        return f"""执行过程中遇到问题：{base_prompt}

上下文：{context}

请采取以下措施：
1. 分析问题原因
2. 评估可用的替代方案
3. 选择最佳的解决策略
4. 继续完成任务目标
5. 向用户说明情况（如必要）

请继续处理并报告进展。"""

    def get_user_interaction_prompt(self, interaction_type: str) -> str:
        """获取用户交互提示"""
        interaction_prompts = {
            "clarification": "需要用户澄清需求或提供更多信息",
            "options": "为用户提供多个选项供选择",
            "feedback": "收集用户对输出结果的反馈",
            "confirmation": "确认是否继续执行或调整策略"
        }
        
        return f"""与用户交互：{interaction_prompts.get(interaction_type, '一般性交互')}

交互原则：
1. 保持友好和专业的语调
2. 清楚地说明当前情况
3. 提供具体的选项或建议
4. 尊重用户的偏好和决定
5. 及时响应用户的反馈

请以适当的方式与用户交互。"""

    def get_quality_check_prompt(self, content: str, criteria: List[str]) -> str:
        """获取质量检查提示"""
        criteria_text = "\n".join([f"- {criterion}" for criterion in criteria])
        
        return f"""请对以下内容进行质量检查：

内容：
{content[:300]}...

检查标准：
{criteria_text}

检查流程：
1. 逐项评估内容是否符合标准
2. 识别需要改进的方面
3. 提供具体的改进建议
4. 评估整体质量分数（1-10分）
5. 决定是否需要重新生成或优化

请提供详细的质量评估报告。"""


# 创建全局提示模板实例
newsletter_prompts = NewsletterAgentPrompts()


def get_agent_prompt_templates() -> Dict[str, str]:
    """获取所有代理提示模板"""
    if not LANGCHAIN_AVAILABLE:
        logger.warning("LangChain不可用，返回基础提示模板")
        return {}
    
    templates = {
        "system": newsletter_prompts.get_system_prompt(),
        "task_planning": newsletter_prompts.get_task_planning_prompt(),
        "research": "请对主题'{topic}'进行{depth}研究",
        "newsletter_generation": "生成关于'{topic}'的{style}风格简报",
        "content_analysis": "分析以下内容: {content}",
        "trending_analysis": "分析{category}领域的热门话题",
        "error_handling": "处理{error_type}错误: {context}",
        "user_interaction": "进行{interaction_type}类型的用户交互",
        "quality_check": "检查内容质量: {content}"
    }
    
    return templates


def create_chat_prompt_template(template_name: str, **kwargs) -> Optional[str]:
    """创建聊天提示模板"""
    if not LANGCHAIN_AVAILABLE:
        return None
    
    templates = get_agent_prompt_templates()
    template = templates.get(template_name)
    
    if not template:
        logger.warning(f"未找到模板: {template_name}")
        return None
    
    try:
        return template.format(**kwargs)
    except KeyError as e:
        logger.error(f"模板参数缺失: {e}")
        return None


def get_dynamic_prompt(task_type: str, context: Dict[str, Any]) -> str:
    """根据任务类型和上下文动态生成提示"""
    
    base_prompts = {
        "research": newsletter_prompts.get_research_prompt(
            context.get('topic', ''),
            context.get('depth', 'medium')
        ),
        "generate": newsletter_prompts.get_newsletter_generation_prompt(
            context.get('topic', ''),
            context.get('style', 'professional'),
            context.get('audience', 'general'),
            context.get('length', 'medium')
        ),
        "analyze": newsletter_prompts.get_content_analysis_prompt(
            context.get('content', '')
        ),
        "trending": newsletter_prompts.get_trending_analysis_prompt(
            context.get('category', 'all')
        )
    }
    
    return base_prompts.get(task_type, newsletter_prompts.get_system_prompt()) 