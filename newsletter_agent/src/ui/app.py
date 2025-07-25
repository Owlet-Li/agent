# -*- coding: utf-8 -*-
"""
Newsletter Agent - 用户界面
Gradio-based web interface
"""

import gradio as gr
from typing import List, Tuple, Dict, Any
from datetime import datetime

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

try:
    from newsletter_agent.src.agents import get_global_agent, get_agent_status
    from newsletter_agent.src.templates.newsletter_templates import NewsletterTemplateEngine
    from newsletter_agent.src.user.preferences import UserPreferencesManager
    from newsletter_agent.src.user.subscription import SubscriptionManager
    from newsletter_agent.src.user.storage import UserDataStorage
    from newsletter_agent.config.settings import settings
except ImportError as e:
    logger.error(f"模块导入失败: {e}")
    # 创建模拟对象
    get_global_agent = None
    get_agent_status = None


def create_app():
    """创建Gradio应用"""
    logger.info("创建Gradio应用界面...")
    
    # 初始化组件
    newsletter_engine = NewsletterTemplateEngine()
    preferences_manager = UserPreferencesManager()
    subscription_manager = SubscriptionManager()
    storage = UserDataStorage()
    
    def generate_complete_newsletter(
        topic: str,
        style: str,
        length: str,
        audience: str,
        categories: List[str]
    ) -> Tuple[str, str, str]:
        """生成完整的新闻简报"""
        try:
            logger.info(f"开始生成简报: {topic}")
            
            # 获取代理
            if get_global_agent:
                agent = get_global_agent()
                
                # 执行主题研究
                research_prompt = f"请研究主题'{topic}'，收集相关信息和最新动态"
                research_result = agent.chat(research_prompt)
                logger.info("主题研究完成")
                
                # 生成简报
                newsletter_prompt = f"""
基于以下研究内容，生成一份{style}风格的{length}长度新闻简报：

主题：{topic}
目标受众：{audience}
关注分类：{', '.join(categories) if categories else '综合'}

研究内容：
{research_result.get('message', '暂无研究内容')}

请生成结构化的新闻简报，包含：
1. 标题
2. 摘要
3. 主要内容
4. 关键洞察
5. 结论
"""
                
                newsletter_result = agent.chat(newsletter_prompt)
                logger.info("简报生成完成")
                
                if newsletter_result.get('success'):
                    newsletter_content = newsletter_result['message']
                    
                    # 格式化为HTML
                    html_newsletter_content = newsletter_content.replace('\n', '<br>')
                    html_content = f"""
                    <div class="newsletter">
                        <h1>📰 智能新闻简报</h1>
                        <div class="metadata">
                            <p><strong>主题:</strong> {topic}</p>
                            <p><strong>风格:</strong> {style}</p>
                            <p><strong>生成时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                        </div>
                        <div class="content">
                            {html_newsletter_content}
                        </div>
                    </div>
                    """
                    
                    # 生成Markdown格式
                    markdown_content = f"""# 📰 智能新闻简报

**主题:** {topic}  
**风格:** {style}  
**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

{newsletter_content}

---
*本简报由Newsletter Agent自动生成*
"""
                    
                    success_msg = f"✅ 简报生成成功！主题：{topic}"
                    
                    return success_msg, html_content, markdown_content
                else:
                    error_msg = f"❌ 简报生成失败：{newsletter_result.get('error', '未知错误')}"
                    return error_msg, "", ""
            
            else:
                # 降级模式 - 生成示例简报
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                example_content = f"""
# {topic} - 智能新闻简报

## 📋 概要
本期简报聚焦于{topic}领域的最新发展和重要动态。

## 🔍 主要发现

### 技术进展
- {topic}技术不断突破创新
- 新的应用场景持续涌现
- 行业标准逐步完善

### 市场动态
- 相关市场规模快速增长
- 投资热度持续升温
- 竞争格局日趋激烈

### 政策环境
- 监管政策逐步明确
- 支持措施不断出台
- 国际合作加强

## 💡 关键洞察
{topic}作为新兴领域，正在深刻改变相关行业的发展模式。企业需要密切关注技术发展趋势，抢占市场先机。

## 🔮 未来展望
预计在未来一段时间内，{topic}将继续保持快速发展势头，相关技术应用将更加成熟。

---
*本简报由Newsletter Agent生成 | {current_time}*
"""
                
                html_example_content = example_content.replace('\n', '<br>')
                html_content = f"""
                <div class="newsletter">
                    <h1>📰 智能新闻简报</h1>
                    <div class="metadata">
                        <p><strong>主题:</strong> {topic}</p>
                        <p><strong>风格:</strong> {style}</p>
                        <p><strong>生成时间:</strong> {current_time}</p>
                    </div>
                    <div class="content">
                        {html_example_content}
                    </div>
                </div>
                """
                
                success_msg = f"✅ 简报生成成功！主题：{topic} (示例模式)"
                return success_msg, html_content, example_content
                
        except Exception as e:
            logger.error(f"简报生成失败: {e}")
            error_msg = f"❌ 简报生成失败：{str(e)}"
            return error_msg, "", ""
    
    def get_system_status() -> str:
        """获取系统状态"""
        try:
            status_info = []
            
            # 代理状态
            if get_agent_status:
                agent_status = get_agent_status()
                if agent_status.get('is_ready'):
                    status_info.append("✅ AI代理: 已就绪")
                    status_info.append(f"   - 可用工具: {agent_status.get('tools_count', 0)} 个")
                    status_info.append(f"   - 语言模型: {'可用' if agent_status.get('llm_available') else '不可用'}")
                else:
                    status_info.append("❌ AI代理: 未就绪")
            else:
                status_info.append("❌ AI代理: 未初始化")
            
            # 数据源状态
            try:
                from newsletter_agent.src.data_sources.aggregator import data_aggregator
                data_status = data_aggregator.get_data_sources_status()
                status_info.append("\n📡 数据源状态:")
                for source, info in data_status.items():
                    if info.get('available'):
                        status_info.append(f"   ✅ {source.upper()}: 可用")
                    else:
                        status_info.append(f"   ❌ {source.upper()}: 不可用")
            except Exception as e:
                status_info.append(f"❌ 数据源: 检查失败 ({e})")
            
            # 系统配置
            status_info.append("\n⚙️ 系统配置:")
            status_info.append(f"   - 应用版本: {settings.APP_VERSION}")
            status_info.append(f"   - 调试模式: {'开启' if settings.DEBUG else '关闭'}")
            status_info.append(f"   - 内容语言: {settings.CONTENT_LANGUAGE}")
            
            return "\n".join(status_info)
            
        except Exception as e:
            return f"❌ 获取系统状态失败: {str(e)}"
    
    # 创建界面
    with gr.Blocks(
        title="Newsletter Agent - 智能新闻简报生成器",
        theme=gr.themes.Soft(),
        css="""
        .newsletter {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .metadata {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            border-left: 4px solid #007bff;
        }
        .content {
            line-height: 1.6;
            color: #333;
        }
        """
    ) as app:
        
        gr.Markdown("# 📰 Newsletter Agent - 智能新闻简报生成器")
        gr.Markdown("利用AI技术，自动生成个性化新闻简报")
        
        with gr.Tabs():
            # 简报生成标签页
            with gr.TabItem("🚀 生成简报"):
                with gr.Row():
                    with gr.Column(scale=1):
                        topic_input = gr.Textbox(
                            label="📝 简报主题",
                            placeholder="例如：人工智能最新发展、新能源汽车市场动态...",
                            value="人工智能最新发展"
                        )
                        
                        style_select = gr.Dropdown(
                            label="✍️ 写作风格",
                            choices=["professional", "casual", "academic", "creative"],
                            value="professional"
                        )
                        
                        length_select = gr.Dropdown(
                            label="📄 内容长度",
                            choices=["short", "medium", "long"],
                            value="medium"
                        )
                        
                        audience_select = gr.Dropdown(
                            label="👥 目标受众",
                            choices=["general", "tech", "business", "academic"],
                            value="general"
                        )
                        
                        categories_select = gr.CheckboxGroup(
                            label="🏷️ 关注分类",
                            choices=["科技", "商业", "健康", "娱乐", "体育", "政治", "教育"],
                            value=["科技", "商业"]
                        )
                        
                        generate_btn = gr.Button("🎯 生成简报", variant="primary", size="lg")
                    
                    with gr.Column(scale=2):
                        status_output = gr.Textbox(
                            label="📊 生成状态",
                            value="等待生成...",
                            interactive=False
                        )
                        
                        with gr.Tabs():
                            with gr.TabItem("🌐 HTML预览"):
                                html_output = gr.HTML(label="HTML格式")
                            
                            with gr.TabItem("📝 Markdown"):
                                markdown_output = gr.Textbox(
                                    label="Markdown格式",
                                    lines=20,
                                    max_lines=30
                                )
                
                # 绑定事件
                generate_btn.click(
                    fn=generate_complete_newsletter,
                    inputs=[
                        topic_input,
                        style_select,
                        length_select,
                        audience_select,
                        categories_select
                    ],
                    outputs=[status_output, html_output, markdown_output]
                )
            
            # 系统状态标签页
            with gr.TabItem("⚙️ 系统状态"):
                with gr.Row():
                    with gr.Column():
                        status_btn = gr.Button("🔍 检查系统状态", variant="secondary")
                        system_status_output = gr.Textbox(
                            label="系统状态信息",
                            lines=15,
                            value="点击按钮检查系统状态..."
                        )
                
                status_btn.click(
                    fn=get_system_status,
                    outputs=system_status_output
                )
            
            # 使用指南标签页
            with gr.TabItem("📖 使用指南"):
                gr.Markdown("""
                ## 🎯 使用步骤
                
                1. **选择主题** - 在"简报主题"中输入您感兴趣的话题
                2. **设置偏好** - 选择写作风格、内容长度和目标受众
                3. **选择分类** - 勾选您关注的内容分类
                4. **生成简报** - 点击"生成简报"按钮开始创建
                5. **查看结果** - 在HTML预览或Markdown标签页中查看生成的简报
                
                ## 🔧 功能特点
                
                - ✅ **智能生成** - 基于AI技术自动生成个性化简报
                - ✅ **多种风格** - 支持专业、休闲、学术、创意等多种写作风格  
                - ✅ **内容定制** - 可调节内容长度和目标受众
                - ✅ **多格式输出** - 支持HTML和Markdown格式输出
                - ✅ **实时生成** - 快速响应，即时获得结果
                
                ## 💡 使用技巧
                
                - **主题建议**: 使用具体明确的主题描述，如"人工智能在医疗领域的应用"
                - **风格选择**: 根据阅读对象选择合适的风格
                - **分类筛选**: 选择相关分类有助于生成更精准的内容
                
                ## 🚀 开始使用
                
                现在就切换到"生成简报"标签页，开始创建您的第一份智能新闻简报吧！
                """)
        
        gr.Markdown("---")
        gr.Markdown("*Powered by Newsletter Agent | AI-Driven Newsletter Generation*")
    
    return app


def create_main_interface():
    """创建主界面 - 兼容性函数"""
    return create_app()


if __name__ == "__main__":
    app = create_app()
    if app:
        app.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            debug=True
        ) 