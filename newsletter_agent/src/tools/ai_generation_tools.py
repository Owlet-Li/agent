# -*- coding: utf-8 -*-
"""
Newsletter Agent - AI内容生成工具
使用OpenRouter API进行智能内容生成
"""

from typing import List, Dict, Any, Optional, Type
from pydantic import BaseModel, Field

try:
    from langchain.tools import BaseTool
    from langchain.callbacks.manager import CallbackManagerForToolRun
    from langchain_openai import ChatOpenAI
    from langchain.schema import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    # 降级处理
    LANGCHAIN_AVAILABLE = False
    BaseTool = object
    CallbackManagerForToolRun = object
    ChatOpenAI = object

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class NewsletterGenerationInput(BaseModel):
    """新闻简报生成工具输入"""
    topic: str = Field(description="简报主题或关键词")
    style: str = Field(default="professional", description="写作风格: professional, casual, academic, creative")
    length: str = Field(default="medium", description="内容长度: short, medium, long")
    target_audience: str = Field(default="general", description="目标受众: general, tech, business, academic")


class NewsletterGenerationTool(BaseTool):
    """新闻简报生成工具
    
    基于研究内容生成个性化新闻简报
    """
    
    name: str = "newsletter_generation"
    description: str = """基于提供的内容和主题生成个性化新闻简报。可以指定写作风格、内容长度和目标受众来定制简报。"""
    args_schema: Type[BaseModel] = NewsletterGenerationInput
    
    def _run(
        self,
        topic: str,
        style: str = "professional",
        length: str = "medium",
        target_audience: str = "general",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """生成新闻简报"""
        try:
            # 初始化OpenAI客户端
            from newsletter_agent.config.settings import settings
            if not settings.OPENAI_API_KEY:
                return "AI内容生成服务不可用，请检查API密钥配置"
                
            llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                openai_api_key=settings.OPENAI_API_KEY,
                openai_api_base=settings.OPENAI_API_BASE,
                temperature=0.7
            )
            
            # 构建系统提示
            system_prompt = self._build_system_prompt(style, length, target_audience)
            
            # 构建用户提示
            user_prompt = f"""
请为主题"{topic}"生成一份新闻简报。

要求：
- 风格：{style}
- 长度：{length}
- 受众：{target_audience}

请确保内容结构清晰，包含摘要、主要内容和结论。
"""
            
            # 调用AI模型
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = llm(messages)
            
            return f"AI生成的新闻简报:\n\n{response.content}"
            
        except Exception as e:
            logger.error(f"AI内容生成失败: {e}")
            return f"生成简报时发生错误: {str(e)}"
    
    def _build_system_prompt(self, style: str, length: str, target_audience: str) -> str:
        """构建系统提示"""
        base_prompt = """你是一个专业的新闻简报写作助手。你的任务是根据给定的主题和内容生成高质量的新闻简报。

请遵循以下原则：
1. 内容准确、客观、有见解
2. 结构清晰，逻辑性强
3. 语言流畅，易于理解
4. 突出重点信息"""
        
        # 根据风格调整
        style_prompts = {
            "professional": "使用正式、专业的语言风格，适合商务环境。",
            "casual": "使用轻松、易懂的语言风格，适合一般读者。",
            "academic": "使用严谨、深入的语言风格，包含详细分析。",
            "creative": "使用富有创意、引人入胜的语言风格。"
        }
        
        # 根据长度调整
        length_prompts = {
            "short": "简报应简洁明了，控制在300-500字。",
            "medium": "简报应详略得当，控制在500-800字。",
            "long": "简报应详细深入，控制在800-1200字。"
        }
        
        # 根据受众调整
        audience_prompts = {
            "general": "面向普通读者，避免过多专业术语。",
            "tech": "面向技术人员，可以使用技术术语和深入分析。",
            "business": "面向商业人士，重点关注商业影响和机会。",
            "academic": "面向学术研究人员，注重数据和理论分析。"
        }
        
        return f"""{base_prompt}

写作风格：{style_prompts.get(style, style_prompts['professional'])}
内容长度：{length_prompts.get(length, length_prompts['medium'])}
目标受众：{audience_prompts.get(target_audience, audience_prompts['general'])}

请按照以下结构组织内容：
1. 标题
2. 核心摘要
3. 主要内容（分点阐述）
4. 关键洞察
5. 结论和展望"""


class ContentSummaryInput(BaseModel):
    """内容摘要工具输入"""
    content: str = Field(description="需要摘要的内容")
    max_length: int = Field(default=200, description="摘要最大长度")
    focus: str = Field(default="general", description="摘要重点: general, key_points, insights, implications")


class ContentSummaryTool(BaseTool):
    """内容摘要工具
    
    使用AI生成内容摘要
    """
    
    name: str = "content_summary"
    description: str = """使用AI为长文本内容生成高质量摘要。可以指定摘要长度和重点关注的方面。"""
    args_schema: Type[BaseModel] = ContentSummaryInput
    
    def _run(
        self,
        content: str,
        max_length: int = 200,
        focus: str = "general",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """生成内容摘要"""
        try:
            from newsletter_agent.config.settings import settings
            
            if not settings.OPENAI_API_KEY:
                # 使用本地摘要功能作为降级
                try:
                    from newsletter_agent.src.content import content_formatter
                    summary = content_formatter.generate_summary(content, max_length)
                    return f"本地生成摘要:\n{summary}"
                except:
                    return "摘要生成功能不可用"
            
            llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                openai_api_key=settings.OPENAI_API_KEY,
                openai_api_base=settings.OPENAI_API_BASE,
                temperature=0.3  # 较低的温度以确保摘要的准确性
            )
            
            # 构建摘要提示
            focus_prompts = {
                "general": "生成一个全面的内容摘要",
                "key_points": "重点提取关键要点和核心信息",
                "insights": "专注于深层洞察和重要发现",
                "implications": "强调内容的影响和意义"
            }
            
            user_prompt = f"""
请为以下内容生成摘要：

{content}

要求：
- 摘要长度：约{max_length}字
- 重点：{focus_prompts.get(focus, focus_prompts['general'])}
- 保持客观、准确
- 突出最重要的信息
"""
            
            messages = [
                SystemMessage(content="你是一个专业的内容摘要助手，擅长提取关键信息并生成简洁准确的摘要。"),
                HumanMessage(content=user_prompt)
            ]
            
            response = llm(messages)
            
            return f"AI生成摘要:\n{response.content}"
            
        except Exception as e:
            logger.error(f"AI摘要生成失败: {e}")
            # 降级到本地摘要
            try:
                from newsletter_agent.src.content import content_formatter
                summary = content_formatter.generate_summary(content, max_length)
                return f"本地生成摘要（AI服务暂时不可用）:\n{summary}"
            except:
                return f"摘要生成时发生错误: {str(e)}"


class HeadlineGenerationInput(BaseModel):
    """标题生成工具输入"""
    content: str = Field(description="文章内容")
    style: str = Field(default="informative", description="标题风格: informative, catchy, formal, creative")
    count: int = Field(default=3, description="生成标题数量")


class HeadlineGenerationTool(BaseTool):
    """标题生成工具
    
    为文章内容生成吸引人的标题
    """
    
    name: str = "headline_generation"
    description: str = """为文章内容生成多个高质量标题选项。可以指定标题风格和生成数量。"""
    args_schema: Type[BaseModel] = HeadlineGenerationInput
    
    def _run(
        self,
        content: str,
        style: str = "informative",
        count: int = 3,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """生成标题"""
        try:
            from newsletter_agent.config.settings import settings
            
            if not settings.OPENAI_API_KEY:
                return "AI标题生成服务不可用，请检查API密钥配置"
                
            llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                openai_api_key=settings.OPENAI_API_KEY,
                openai_api_base=settings.OPENAI_API_BASE,
                temperature=0.8  # 较高的温度以增加创意性
            )
            
            style_prompts = {
                "informative": "信息性强、准确描述内容要点",
                "catchy": "吸引眼球、容易记住",
                "formal": "正式、专业的表达方式",
                "creative": "富有创意、独特的表达"
            }
            
            user_prompt = f"""
请为以下内容生成{count}个标题：

{content[:500]}...

要求：
- 风格：{style_prompts.get(style, style_prompts['informative'])}
- 每个标题不超过30字
- 准确反映内容主题
- 具有吸引力

请按以下格式输出：
1. [标题1]
2. [标题2]
3. [标题3]
"""
            
            messages = [
                SystemMessage(content="你是一个专业的新闻标题创作者，擅长为各种内容创作吸引人且准确的标题。"),
                HumanMessage(content=user_prompt)
            ]
            
            response = llm(messages)
            
            return f"AI生成的标题建议:\n{response.content}"
            
        except Exception as e:
            logger.error(f"AI标题生成失败: {e}")
            return f"生成标题时发生错误: {str(e)}"


class ContentEnhancementInput(BaseModel):
    """内容增强工具输入"""
    content: str = Field(description="需要增强的内容")
    enhancement_type: str = Field(default="improve", description="增强类型: improve, expand, simplify, restructure")
    target_length: int = Field(default=0, description="目标长度（0表示不限制）")


class ContentEnhancementTool(BaseTool):
    """内容增强工具
    
    改进、扩展或优化现有内容
    """
    
    name: str = "content_enhancement"
    description: str = """改进、扩展或优化现有内容。可以选择不同的增强类型：改进质量、扩展内容、简化表达或重构结构。"""
    args_schema: Type[BaseModel] = ContentEnhancementInput
    
    def _run(
        self,
        content: str,
        enhancement_type: str = "improve",
        target_length: int = 0,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """增强内容"""
        try:
            from newsletter_agent.config.settings import settings
            
            if not settings.OPENAI_API_KEY:
                return "AI内容增强服务不可用，请检查API密钥配置"
                
            llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                openai_api_key=settings.OPENAI_API_KEY,
                openai_api_base=settings.OPENAI_API_BASE,
                temperature=0.5
            )
            
            enhancement_prompts = {
                "improve": "改进内容质量，使其更加准确、流畅和有说服力",
                "expand": "扩展内容，添加更多细节、例子和深入分析",
                "simplify": "简化内容表达，使其更易理解和阅读",
                "restructure": "重新组织内容结构，使逻辑更清晰"
            }
            
            length_instruction = f"目标长度约{target_length}字。" if target_length > 0 else "长度适中即可。"
            
            user_prompt = f"""
请对以下内容进行{enhancement_type}处理：

{content}

任务：{enhancement_prompts.get(enhancement_type, enhancement_prompts['improve'])}
{length_instruction}

请保持内容的核心信息不变，但提升整体质量和可读性。
"""
            
            messages = [
                SystemMessage(content="你是一个专业的内容编辑，擅长改进各种文本的质量、结构和表达效果。"),
                HumanMessage(content=user_prompt)
            ]
            
            response = llm(messages)
            
            return f"增强后的内容:\n{response.content}"
            
        except Exception as e:
            logger.error(f"AI内容增强失败: {e}")
            return f"增强内容时发生错误: {str(e)}"


# AI工具注册表
AI_TOOLS = [
    NewsletterGenerationTool,
    ContentSummaryTool,
    HeadlineGenerationTool,
    ContentEnhancementTool
]


def get_ai_tools() -> List[BaseTool]:
    """获取所有AI工具实例"""
    if not LANGCHAIN_AVAILABLE:
        logger.warning("LangChain不可用，无法创建AI工具")
        return []
    
    tools = []
    for tool_class in AI_TOOLS:
        try:
            tool = tool_class()
            tools.append(tool)
            logger.info(f"AI工具 {tool.name} 初始化成功")
        except Exception as e:
            logger.error(f"AI工具 {tool_class.__name__} 初始化失败: {e}")
    
    return tools


def test_ai_connection() -> bool:
    """测试AI服务连接"""
    try:
        from newsletter_agent.config.settings import settings
        if not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY未配置")
            return False
        
        # 创建简单的测试工具
        test_tool = ContentSummaryTool()
        
        # 执行简单测试
        test_result = test_tool._run("这是一个测试内容。", max_length=50)
        
        return "AI生成摘要" in test_result or "本地生成摘要" in test_result
        
    except Exception as e:
        logger.error(f"AI连接测试失败: {e}")
        return False 