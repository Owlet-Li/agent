# -*- coding: utf-8 -*-
"""
Newsletter Agent - 核心智能代理
整合工具、提示模板和决策逻辑的主要AI代理
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import json

# 先导入日志系统
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# 再导入LangChain组件
try:
    from langchain.agents import AgentExecutor, initialize_agent, AgentType
    from langchain_openai import ChatOpenAI
    from langchain.schema import BaseMessage, HumanMessage, SystemMessage, AIMessage
    from langchain.tools import BaseTool
    LANGCHAIN_AVAILABLE = True
    logger.info("LangChain导入成功")
except ImportError as e:
    LANGCHAIN_AVAILABLE = False
    AgentExecutor = object
    BaseTool = object
    ChatOpenAI = object
    logger.warning(f"LangChain导入失败: {e}")
    logger.info("代理将在受限模式下运行")


class NewsletterAgent:
    """新闻简报智能代理
    
    集成数据收集、内容分析、AI生成等功能的核心代理
    """
    
    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None):
        """初始化代理
        
        Args:
            api_key: OpenAI API密钥
            api_base: API基础URL
        """
        self.agent_name = "Newsletter Agent"
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.conversation_history = []
        
        # 初始化LLM
        self.llm = self._init_llm(api_key, api_base)
        
        # 初始化工具
        self.tools = self._init_tools()
        
        # 初始化提示模板
        self.prompts = self._init_prompts()
        
        # 初始化代理执行器
        self.agent_executor = self._init_agent_executor()
        
        # 代理状态
        self.is_ready = self.llm is not None and len(self.tools) > 0
        
        logger.info(f"Newsletter Agent 初始化完成，状态: {'就绪' if self.is_ready else '未就绪'}")
    
    def _init_llm(self, api_key: Optional[str], api_base: Optional[str]) -> Optional[ChatOpenAI]:
        """初始化语言模型"""
        try:
            # 检查LangChain是否可用
            if not LANGCHAIN_AVAILABLE:
                logger.warning("LangChain不可用，无法创建语言模型")
                return None
            
            # 从设置中获取API配置
            if not api_key or not api_base:
                from newsletter_agent.config.settings import settings
                api_key = api_key or settings.OPENAI_API_KEY
                api_base = api_base or settings.OPENAI_API_BASE
            
            if not api_key:
                logger.warning("API密钥未配置，代理将以受限模式运行")
                return None
            
            llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                openai_api_key=api_key,
                openai_api_base=api_base,
                temperature=0.7,
                max_tokens=2000,
                request_timeout=60
            )
            
            logger.info("语言模型初始化成功")
            return llm
            
        except Exception as e:
            logger.error(f"语言模型初始化失败: {e}")
            return None
    
    def _init_tools(self) -> List[BaseTool]:
        """初始化工具集"""
        tools = []
        
        try:
            # 加载数据源工具
            from newsletter_agent.src.tools.data_source_tools import get_all_tools
            data_tools = get_all_tools()
            tools.extend(data_tools)
            logger.info(f"加载数据源工具: {len(data_tools)} 个")
            
            # 加载AI工具
            from newsletter_agent.src.tools.ai_generation_tools import get_ai_tools
            ai_tools = get_ai_tools()
            tools.extend(ai_tools)
            logger.info(f"加载AI工具: {len(ai_tools)} 个")
            
        except Exception as e:
            logger.error(f"工具初始化失败: {e}")
        
        logger.info(f"总共加载工具: {len(tools)} 个")
        return tools
    
    def _init_prompts(self):
        """初始化提示模板"""
        try:
            from newsletter_agent.src.agents.prompts import newsletter_prompts
            return newsletter_prompts
        except Exception as e:
            logger.error(f"提示模板初始化失败: {e}")
            return None
    
    def _init_agent_executor(self) -> Optional[AgentExecutor]:
        """初始化代理执行器"""
        if not LANGCHAIN_AVAILABLE or not self.llm or not self.tools:
            logger.warning("无法创建代理执行器，缺少必要组件")
            return None
        
        try:
            # 创建系统提示
            system_prompt = self.prompts.get_system_prompt() if self.prompts else "你是一个新闻简报助手。"
            
            # 创建执行器
            executor = initialize_agent(
                tools=self.tools,
                llm=self.llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                max_iterations=10,
                max_execution_time=300,  # 5分钟超时
                return_intermediate_steps=True
            )
            
            logger.info("代理执行器创建成功")
            return executor
            
        except Exception as e:
            logger.error(f"代理执行器创建失败: {e}")
            return None
    
    def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """与代理对话
        
        Args:
            message: 用户消息
            context: 额外上下文信息
            
        Returns:
            代理响应结果
        """
        if not self.is_ready:
            return {
                "success": False,
                "message": "代理未就绪，请检查配置",
                "error": "Agent not ready"
            }
        
        try:
            # 记录对话历史
            self.conversation_history.append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat(),
                "context": context
            })
            
            # 构建完整的提示
            full_prompt = self._build_conversation_prompt(message, context)
            
            # 执行代理
            if self.agent_executor:
                result = self.agent_executor.invoke({
                    "input": full_prompt,
                    "chat_history": self._get_recent_history()
                })
                
                response_content = result.get("output", "抱歉，我无法生成回复。")
                intermediate_steps = result.get("intermediate_steps", [])
                
            else:
                # 降级模式：直接使用LLM
                response = self.llm([HumanMessage(content=full_prompt)])
                response_content = response.content
                intermediate_steps = []
            
            # 记录代理响应
            self.conversation_history.append({
                "role": "assistant",
                "content": response_content,
                "timestamp": datetime.now().isoformat(),
                "intermediate_steps": len(intermediate_steps)
            })
            
            return {
                "success": True,
                "message": response_content,
                "intermediate_steps": intermediate_steps,
                "session_id": self.session_id,
                "tools_used": self._extract_tools_used(intermediate_steps)
            }
            
        except Exception as e:
            logger.error(f"代理对话失败: {e}")
            return {
                "success": False,
                "message": "对话处理失败，请稍后重试",
                "error": str(e)
            }
    
    def generate_newsletter(self, 
                          topic: str,
                          style: str = "professional",
                          audience: str = "general",
                          length: str = "medium") -> Dict[str, Any]:
        """生成新闻简报
        
        Args:
            topic: 简报主题
            style: 写作风格
            audience: 目标受众
            length: 内容长度
            
        Returns:
            生成结果
        """
        context = {
            "task": "newsletter_generation",
            "topic": topic,
            "style": style,
            "audience": audience,
            "length": length
        }
        
        if self.prompts:
            prompt = self.prompts.get_newsletter_generation_prompt(topic, style, audience, length)
        else:
            prompt = f"请生成关于'{topic}'的新闻简报，风格：{style}，受众：{audience}，长度：{length}"
        
        return self.chat(prompt, context)
    
    def research_topic(self, topic: str, depth: str = "medium") -> Dict[str, Any]:
        """研究特定主题
        
        Args:
            topic: 研究主题
            depth: 研究深度
            
        Returns:
            研究结果
        """
        context = {
            "task": "topic_research",
            "topic": topic,
            "depth": depth
        }
        
        if self.prompts:
            prompt = self.prompts.get_research_prompt(topic, depth)
        else:
            prompt = f"请对'{topic}'进行{depth}研究"
        
        return self.chat(prompt, context)
    
    def analyze_trending_topics(self, category: str = "all") -> Dict[str, Any]:
        """分析热门话题
        
        Args:
            category: 分析分类
            
        Returns:
            分析结果
        """
        context = {
            "task": "trending_analysis",
            "category": category
        }
        
        if self.prompts:
            prompt = self.prompts.get_trending_analysis_prompt(category)
        else:
            prompt = f"请分析{category}领域的热门话题"
        
        return self.chat(prompt, context)
    
    def analyze_content(self, content: str) -> Dict[str, Any]:
        """分析内容
        
        Args:
            content: 要分析的内容
            
        Returns:
            分析结果
        """
        context = {
            "task": "content_analysis",
            "content": content[:200] + "..." if len(content) > 200 else content
        }
        
        if self.prompts:
            prompt = self.prompts.get_content_analysis_prompt(content)
        else:
            prompt = f"请分析以下内容：\n{content}"
        
        return self.chat(prompt, context)
    
    def get_agent_status(self) -> Dict[str, Any]:
        """获取代理状态"""
        return {
            "agent_name": self.agent_name,
            "session_id": self.session_id,
            "is_ready": self.is_ready,
            "llm_available": self.llm is not None,
            "tools_count": len(self.tools),
            "conversation_turns": len(self.conversation_history),
            "available_tools": [tool.name for tool in self.tools] if self.tools else [],
            "langchain_available": LANGCHAIN_AVAILABLE
        }
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history.clear()
        logger.info("对话历史已清空")
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取对话历史
        
        Args:
            limit: 返回的最大对话数量
            
        Returns:
            对话历史列表
        """
        return self.conversation_history[-limit:] if limit > 0 else self.conversation_history
    
    def _build_conversation_prompt(self, message: str, context: Optional[Dict[str, Any]]) -> str:
        """构建对话提示"""
        base_prompt = message
        
        if context:
            context_info = []
            if context.get("task"):
                context_info.append(f"任务类型: {context['task']}")
            if context.get("topic"):
                context_info.append(f"主题: {context['topic']}")
            
            if context_info:
                base_prompt = f"上下文: {', '.join(context_info)}\n\n{base_prompt}"
        
        return base_prompt
    
    def _get_recent_history(self, limit: int = 5) -> List[str]:
        """获取最近的对话历史"""
        recent = self.conversation_history[-limit*2:] if self.conversation_history else []
        
        history = []
        for item in recent:
            if item["role"] == "user":
                history.append(f"Human: {item['content']}")
            elif item["role"] == "assistant":
                history.append(f"Assistant: {item['content']}")
        
        return history
    
    def _extract_tools_used(self, intermediate_steps: List) -> List[str]:
        """提取使用的工具列表"""
        tools_used = []
        
        for step in intermediate_steps:
            if hasattr(step, 'tool') and hasattr(step.tool, 'name'):
                tools_used.append(step.tool.name)
            elif isinstance(step, tuple) and len(step) >= 2:
                # 处理 (AgentAction, observation) 格式
                action = step[0]
                if hasattr(action, 'tool'):
                    tools_used.append(action.tool)
        
        return list(set(tools_used))  # 去重


def create_newsletter_agent(api_key: Optional[str] = None, 
                          api_base: Optional[str] = None) -> NewsletterAgent:
    """创建新闻简报代理实例
    
    Args:
        api_key: OpenAI API密钥
        api_base: API基础URL
        
    Returns:
        代理实例
    """
    try:
        agent = NewsletterAgent(api_key, api_base)
        logger.info("新闻简报代理创建成功")
        return agent
    except Exception as e:
        logger.error(f"代理创建失败: {e}")
        raise


def test_agent_functionality() -> bool:
    """测试代理功能"""
    try:
        agent = create_newsletter_agent()
        
        if not agent.is_ready:
            logger.warning("代理未就绪，跳过功能测试")
            return False
        
        # 简单测试
        result = agent.chat("你好，请介绍一下你的功能")
        
        return result.get("success", False)
        
    except Exception as e:
        logger.error(f"代理功能测试失败: {e}")
        return False 