# -*- coding: utf-8 -*-
"""
Newsletter Agent - Agent Prompt Templates
Defines AI agent behavior, decision logic and interaction patterns
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
    """Newsletter agent prompt template collection"""
    
    def __init__(self):
        """Initialize prompt templates"""
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.agent_name = "Newsletter Agent"
        
    def get_system_prompt(self) -> str:
        """Get system-level prompt"""
        return f"""You are {self.agent_name}, a professional newsletter generation assistant. Today is {self.current_date}.

Your core capabilities include:
1. 🔍 News search and information gathering
2. 📊 Content analysis and quality assessment  
3. 📝 Intelligent summarization and categorization
4. 🎯 Personalized newsletter generation
5. 🤖 Multi-step reasoning and decision making

You can use the following tools:
- news_search: Search for latest news content
- trending_topics: Get trending topics
- content_analysis: Analyze text content
- topic_research: In-depth topic research
- newsletter_generation: Generate personalized newsletters
- content_summary: Generate content summaries
- headline_generation: Generate compelling headlines
- content_enhancement: Improve existing content

Working principles:
1. Always prioritize user needs
2. Ensure information accuracy and timeliness
3. Provide valuable insights and analysis
4. Maintain objective and neutral stance
5. Generate high-quality, engaging content

When executing tasks, please follow this workflow:
1. Understand user needs and preferences
2. Develop information gathering strategy
3. Use appropriate tools to collect and analyze information
4. Integrate information and generate structured content
5. Optimize output based on feedback

Please always interact with users in a professional, friendly, and efficient manner."""

    def get_task_planning_prompt(self) -> str:
        """Get task planning prompt"""
        return """As Newsletter Agent, when users present requirements, please follow these steps for task planning:

1. **Requirement Analysis**
   - Clarify user's specific needs
   - Identify target audience and content preferences
   - Determine newsletter scope and depth

2. **Information Gathering Strategy**
   - Determine topics and keywords to search
   - Select appropriate data sources and tools
   - Set search breadth and depth

3. **Execution Plan**
   - Develop detailed execution steps
   - Estimate required time and resources
   - Determine output format and structure

4. **Quality Control**
   - Set content quality standards
   - Plan information verification process
   - Prepare user feedback mechanisms

Please briefly explain your planning before starting execution, then begin step-by-step execution."""

    def get_research_prompt(self, topic: str, depth: str = "medium") -> str:
        """Get research task prompt"""
        depth_descriptions = {
            "light": "Quick overview, get basic information and key points",
            "medium": "Medium-depth research, including key information and some analysis",
            "deep": "Deep research, comprehensive analysis, including background, impact and outlook"
        }
        
        return f"""Please conduct {depth_descriptions.get(depth, "medium-depth")} research on topic "{topic}".

Research requirements:
1. Use topic_research tool to collect basic information
2. Analyze quality and relevance of collected information
3. Identify key trends and important findings
4. Summarize core viewpoints and insights

Research depth: {depth}
- {depth_descriptions.get(depth, "Medium-depth research")}

Please start research and provide detailed findings report."""

    def get_newsletter_generation_prompt(self, 
                                       topic: str, 
                                       style: str = "professional",
                                       audience: str = "general",
                                       length: str = "medium") -> str:
        """Get newsletter generation prompt"""
        return f"""Based on previous research results, please generate a newsletter about "{topic}".

Newsletter requirements:
- Topic: {topic}
- Style: {style}
- Audience: {audience} 
- Length: {length}

Generation workflow:
1. First use headline_generation tool to generate compelling headlines
2. Use content_summary tool to generate summaries for key information
3. Use newsletter_generation tool to generate complete newsletter
4. Use content_enhancement tool to optimize content quality if necessary

Please ensure newsletter content:
- Clear structure, logical coherence
- Accurate information, balanced viewpoints
- Fluent language, easy to read
- Highlight key points, valuable insights

Start generating newsletter."""

    def get_content_analysis_prompt(self, content: str) -> str:
        """Get content analysis prompt"""
        return f"""Please conduct comprehensive analysis of the following content:

Content:
{content[:500]}...

Analysis requirements:
1. Use content_analysis tool for basic analysis
2. Assess content quality and credibility
3. Identify key information and viewpoints
4. Analyze potential impact and significance
5. Provide improvement suggestions

Please provide detailed analysis report."""

    def get_trending_analysis_prompt(self, category: str = "all") -> str:
        """Get trending analysis prompt"""
        return f"""Please analyze current trending topics and trends.

Analysis scope: {category}

Analysis steps:
1. Use trending_topics tool to get trending topics
2. Analyze topic importance and influence
3. Identify potential news value
4. Assess topic sustainability and development trends
5. Recommend most noteworthy topics

Please provide trending analysis report and topic recommendations."""

    def get_error_handling_prompt(self, error_type: str, context: str) -> str:
        """Get error handling prompt"""
        error_prompts = {
            "tool_failure": "Tool execution failed, please try other methods or tools",
            "no_results": "No relevant information found, please adjust search strategy",
            "api_error": "API service temporarily unavailable, please use backup plan",
            "content_quality": "Content quality does not meet requirements, please regenerate or optimize"
        }
        
        base_prompt = error_prompts.get(error_type, "Unknown error encountered, please analyze and take appropriate measures")
        
        return f"""Problem encountered during execution: {base_prompt}

Context: {context}

Please take the following measures:
1. Analyze problem causes
2. Assess available alternative solutions
3. Select best resolution strategy
4. Continue to complete task objectives
5. Inform user of situation (if necessary)

Please continue processing and report progress."""

    def get_user_interaction_prompt(self, interaction_type: str) -> str:
        """Get user interaction prompt"""
        interaction_prompts = {
            "clarification": "Need user to clarify requirements or provide more information",
            "options": "Provide multiple options for user to choose from",
            "feedback": "Collect user feedback on output results",
            "confirmation": "Confirm whether to continue execution or adjust strategy"
        }
        
        return f"""User interaction: {interaction_prompts.get(interaction_type, 'General interaction')}

Interaction principles:
1. Maintain friendly and professional tone
2. Clearly explain current situation
3. Provide specific options or suggestions
4. Respect user preferences and decisions
5. Respond promptly to user feedback

Please interact with user appropriately."""

    def get_quality_check_prompt(self, content: str, criteria: List[str]) -> str:
        """Get quality check prompt"""
        criteria_text = "\n".join([f"- {criterion}" for criterion in criteria])
        
        return f"""Please conduct quality check on the following content:

Content:
{content[:300]}...

Check criteria:
{criteria_text}

Check workflow:
1. Evaluate content against each criterion
2. Identify areas needing improvement
3. Provide specific improvement suggestions
4. Assess overall quality score (1-10 points)
5. Decide if regeneration or optimization is needed

Please provide detailed quality assessment report."""


# Create global prompt template instance
newsletter_prompts = NewsletterAgentPrompts()


def get_agent_prompt_templates() -> Dict[str, str]:
    """Get all agent prompt templates"""
    if not LANGCHAIN_AVAILABLE:
        logger.warning("LangChain not available, returning basic prompt templates")
        return {}
    
    templates = {
        "system": newsletter_prompts.get_system_prompt(),
        "task_planning": newsletter_prompts.get_task_planning_prompt(),
        "research": "Please conduct {depth} research on topic '{topic}'",
        "newsletter_generation": "Generate {style} style newsletter about '{topic}'",
        "content_analysis": "Analyze the following content: {content}",
        "trending_analysis": "Analyze trending topics in {category} field",
        "error_handling": "Handle {error_type} error: {context}",
        "user_interaction": "Conduct {interaction_type} type user interaction",
        "quality_check": "Check content quality: {content}"
    }
    
    return templates


def create_chat_prompt_template(template_name: str, **kwargs) -> Optional[str]:
    """Create chat prompt template"""
    if not LANGCHAIN_AVAILABLE:
        return None
    
    templates = get_agent_prompt_templates()
    template = templates.get(template_name)
    
    if not template:
        logger.warning(f"Template not found: {template_name}")
        return None
    
    try:
        return template.format(**kwargs)
    except KeyError as e:
        logger.error(f"Template parameter missing: {e}")
        return None


def get_dynamic_prompt(task_type: str, context: Dict[str, Any]) -> str:
    """Generate dynamic prompt based on task type and context"""
    
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