# -*- coding: utf-8 -*-
"""
Newsletter Agent - AI生成工具
基于大语言模型的内容生成、摘要和增强工具
"""

from typing import Type, Optional, List
from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field
from langchain.callbacks.manager import CallbackManagerForToolRun

try:
    from langchain_openai import ChatOpenAI
    from langchain.schema import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    ChatOpenAI = object

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

try:
    from newsletter_agent.config.settings import settings
except ImportError:
    class MockSettings:
        OPENAI_API_KEY = "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"
        OPENAI_API_BASE = "https://openrouter.ai/api/v1/chat/completions"
    settings = MockSettings()


class NewsletterGenerationInput(BaseModel):
    """新闻简报生成工具输入"""
    prompt: str = Field(description="简报生成提示，包含主题、风格、长度等要求")


class NewsletterGenerationTool(BaseTool):
    """新闻简报生成工具
    
    基于研究内容生成个性化新闻简报
    """
    
    name: str = "newsletter_generation"
    description: str = """基于提供的内容和主题生成个性化新闻简报。输入应该是包含完整要求的提示文本。"""
    args_schema: Type[BaseModel] = NewsletterGenerationInput

    def _run(
        self,
        prompt: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """执行简报生成"""
        try:
            if not LANGCHAIN_AVAILABLE or not settings.OPENAI_API_KEY:
                return self._generate_fallback_newsletter(prompt)
            
            llm = ChatOpenAI(
                model="openai/gpt-4.1",
                openai_api_key=settings.OPENAI_API_KEY,
                openai_api_base=settings.OPENAI_API_BASE,
                temperature=0.7,
                max_tokens=2000
            )
            
            system_prompt = """你是一个专业的新闻简报编辑。请根据用户要求生成高质量的新闻简报。

要求：
1. 内容结构清晰，分段合理
2. 语言简洁明了，信息准确
3. 包含标题、摘要和主要内容
4. 格式规范，易于阅读
5. 保持客观中立的立场

请根据用户的具体要求生成相应的简报内容。"""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt)
            ]
            
            response = llm.invoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"简报生成失败: {e}")
            return f"抱歉，简报生成过程中遇到错误: {str(e)}"
    
    def _generate_fallback_newsletter(self, prompt: str) -> str:
        """生成后备简报（当AI不可用时）"""
        return f"""
# 智能新闻简报

## 主题概述
根据您的要求：{prompt[:100]}...

## 简报内容
由于AI服务暂时不可用，这是一个示例简报。

### 科技动态
- 人工智能技术持续发展
- 新兴科技产品不断涌现
- 数字化转型加速推进

### 商业资讯  
- 市场趋势变化明显
- 企业创新能力增强
- 投资环境持续优化

### 行业洞察
- 各行业竞争加剧
- 新商业模式涌现
- 可持续发展受关注

---
*本简报由Newsletter Agent生成*
"""


class ContentSummaryInput(BaseModel):
    """内容摘要工具输入"""
    text: str = Field(description="需要摘要的完整文本内容")


class ContentSummaryTool(BaseTool):
    """内容摘要工具
    
    使用AI生成内容摘要
    """
    
    name: str = "content_summary"
    description: str = """为长文本内容生成高质量摘要。输入应该是需要摘要的完整文本。"""
    args_schema: Type[BaseModel] = ContentSummaryInput

    def _run(
        self,
        text: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """生成内容摘要"""
        try:
            if not LANGCHAIN_AVAILABLE or not settings.OPENAI_API_KEY:
                return self._generate_simple_summary(text)
            
            llm = ChatOpenAI(
                model="openai/gpt-4.1",
                openai_api_key=settings.OPENAI_API_KEY,
                openai_api_base=settings.OPENAI_API_BASE,
                temperature=0.3,
                max_tokens=500
            )
            
            prompt = f"""请为以下内容生成一个简洁准确的摘要：

内容：
{text[:1500]}

要求：
1. 提取核心信息和关键点
2. 保持客观中立
3. 长度控制在200字以内
4. 语言简洁清晰

摘要："""
            
            response = llm.invoke([HumanMessage(content=prompt)])
            return response.content
            
        except Exception as e:
            logger.error(f"摘要生成失败: {e}")
            return self._generate_simple_summary(text)
    
    def _generate_simple_summary(self, text: str, max_length: int = 200) -> str:
        """生成简单摘要"""
        if len(text) <= max_length:
            return text
        
        # 简单截取前部分内容
        summary = text[:max_length]
        # 在合适位置断开
        last_period = summary.rfind('。')
        if last_period > max_length * 0.7:
            summary = summary[:last_period + 1]
        else:
            summary = summary + "..."
        
        return summary


class HeadlineGenerationInput(BaseModel):
    """标题生成工具输入"""
    content: str = Field(description="文章内容，用于生成标题")


class HeadlineGenerationTool(BaseTool):
    """标题生成工具
    
    为文章内容生成吸引人的标题
    """
    
    name: str = "headline_generation"
    description: str = """为文章内容生成吸引人的标题。输入应该是文章的主要内容。"""
    args_schema: Type[BaseModel] = HeadlineGenerationInput

    def _run(
        self,
        content: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """生成标题"""
        try:
            if not LANGCHAIN_AVAILABLE or not settings.OPENAI_API_KEY:
                return self._generate_simple_headline(content)
            
            llm = ChatOpenAI(
                model="openai/gpt-4.1", 
                openai_api_key=settings.OPENAI_API_KEY,
                openai_api_base=settings.OPENAI_API_BASE,
                temperature=0.8,
                max_tokens=100
            )
            
            prompt = f"""基于以下内容，生成3个吸引人的标题：

内容：
{content[:800]}

要求：
1. 标题要准确反映内容要点
2. 语言简洁有力，吸引读者
3. 长度适中（10-30字）
4. 每个标题单独一行

标题："""
            
            response = llm.invoke([HumanMessage(content=prompt)])
            return response.content
            
        except Exception as e:
            logger.error(f"标题生成失败: {e}")
            return self._generate_simple_headline(content)
    
    def _generate_simple_headline(self, content: str) -> str:
        """生成简单标题"""
        # 提取关键词生成标题
        words = content.split()[:10]
        headline = " ".join(words)
        if len(headline) > 50:
            headline = headline[:50] + "..."
        
        return f"要闻：{headline}"


class ContentEnhancementInput(BaseModel):
    """内容增强工具输入"""
    content: str = Field(description="需要增强的内容文本")


class ContentEnhancementTool(BaseTool):
    """内容增强工具
    
    改进、扩展或优化现有内容
    """
    
    name: str = "content_enhancement"
    description: str = """改进、扩展或优化现有内容质量。输入应该是需要改进的内容文本。"""
    args_schema: Type[BaseModel] = ContentEnhancementInput

    def _run(
        self,
        content: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """增强内容"""
        try:
            if not LANGCHAIN_AVAILABLE or not settings.OPENAI_API_KEY:
                return self._enhance_content_simple(content)
            
            llm = ChatOpenAI(
                model="openai/gpt-4.1",
                openai_api_key=settings.OPENAI_API_KEY,
                openai_api_base=settings.OPENAI_API_BASE,
                temperature=0.5,
                max_tokens=1000
            )
            
            prompt = f"""请改进以下内容，使其更加清晰、准确和吸引人：

原内容：
{content}

改进要求：
1. 优化语言表达，使其更流畅
2. 增强内容逻辑性和可读性
3. 保持原意不变
4. 适当扩展重要信息
5. 确保语法正确

改进后的内容："""
            
            response = llm.invoke([HumanMessage(content=prompt)])
            return response.content
            
        except Exception as e:
            logger.error(f"内容增强失败: {e}")
            return self._enhance_content_simple(content)
    
    def _enhance_content_simple(self, content: str) -> str:
        """简单内容增强"""
        # 基本的格式化改进
        enhanced = content.strip()
        
        # 添加适当的分段
        if len(enhanced) > 200:
            sentences = enhanced.split('。')
            if len(sentences) > 3:
                mid = len(sentences) // 2
                enhanced = '。'.join(sentences[:mid]) + '。\n\n' + '。'.join(sentences[mid:])
        
        return enhanced


def get_ai_tools() -> List[BaseTool]:
    """获取所有AI工具"""
    tools = []
    
    try:
        # 新闻简报生成工具
        newsletter_tool = NewsletterGenerationTool()
        tools.append(newsletter_tool)
        logger.info("AI工具 newsletter_generation 初始化成功")
        
        # 内容摘要工具
        summary_tool = ContentSummaryTool()
        tools.append(summary_tool)
        logger.info("AI工具 content_summary 初始化成功")
        
        # 标题生成工具
        headline_tool = HeadlineGenerationTool()
        tools.append(headline_tool)
        logger.info("AI工具 headline_generation 初始化成功")
        
        # 内容增强工具
        enhancement_tool = ContentEnhancementTool()
        tools.append(enhancement_tool)
        logger.info("AI工具 content_enhancement 初始化成功")
        
    except Exception as e:
        logger.error(f"AI工具初始化失败: {e}")
    
    return tools


def test_ai_connection() -> bool:
    """测试AI连接"""
    try:
        if not LANGCHAIN_AVAILABLE or not settings.OPENAI_API_KEY:
            return False
        
        llm = ChatOpenAI(
            model="openai/gpt-4.1",
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_API_BASE,
            max_tokens=10
        )
        
        response = llm.invoke([HumanMessage(content="Hello")])
        return True
        
    except Exception as e:
        logger.error(f"AI连接测试失败: {e}")
        return False 