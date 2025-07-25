# -*- coding: utf-8 -*-
"""
Newsletter Agent - Gradio用户界面
完整的Web界面，支持所有功能
"""

from typing import Tuple, List, Dict, Any, Optional
import uuid
from datetime import datetime

try:
    import gradio as gr
    GRADIO_AVAILABLE = True
except ImportError:
    gr = None
    GRADIO_AVAILABLE = False

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


def create_app():
    """创建主要的Gradio应用"""
    if not GRADIO_AVAILABLE:
        logger.error("Gradio不可用，无法创建Web界面")
        return None
    
    logger.info("创建Gradio应用界面...")
    
    # 全局状态存储
    app_state = {
        'current_user_id': None,
        'current_subscription_id': None,
        'generated_newsletter': None
    }
    
    def generate_complete_newsletter(
        topic: str,
        style: str,
        length: str,
        audience: str,
        email: str,
        name: str,
        frequency: str,
        categories: List[str],
        send_email: bool
    ) -> Tuple[str, str, str]:
        """生成完整的新闻简报并可选择发送邮件"""
        try:
            # 导入必要的模块
            from newsletter_agent.src.agents import create_newsletter_agent
            from newsletter_agent.src.templates import NewsletterTemplateEngine, EmailTemplateEngine
            from newsletter_agent.src.user import UserPreferencesManager, SubscriptionManager
            from newsletter_agent.src.email import SendGridEmailClient
            
            # 创建代理和服务
            agent = create_newsletter_agent()
            template_engine = NewsletterTemplateEngine()
            email_engine = EmailTemplateEngine()
            user_manager = UserPreferencesManager()
            subscription_manager = SubscriptionManager()
            sendgrid_client = SendGridEmailClient()
            
            # 1. 生成简报内容
            logger.info(f"开始生成简报: {topic}")
            
            # 使用代理研究主题
            research_result = agent.research_topic(topic, depth="medium")
            logger.info("主题研究完成")
            
            # 生成最终简报
            newsletter_result = agent.generate_newsletter(
                topic=topic,
                style=style,
                audience=audience,
                length=length
            )
            logger.info("简报生成完成")
            
            # 2. 用户和订阅管理
            user_id = str(uuid.uuid4())
            status_msg = f"✅ 简报生成成功！主题：{topic}\n"
            
            if email and name:
                # 创建用户偏好
                user_prefs = user_manager.create_user_preferences(
                    user_id=user_id,
                    email=email,
                    name=name,
                    topics=[topic],
                    categories=categories or ["general"],
                    content_style=style,
                    content_length=length,
                    frequency=frequency
                )
                
                # 创建订阅
                subscription = subscription_manager.create_subscription(
                    user_id=user_id,
                    email=email,
                    name=name,
                    frequency=frequency
                )
                
                app_state['current_user_id'] = user_id
                app_state['current_subscription_id'] = subscription.subscription_id
                
                status_msg += f"✅ 用户创建成功：{name} ({email})\n"
                status_msg += f"✅ 订阅创建成功：{frequency}频率\n"
                
                # 3. 发送邮件
                if send_email:
                    try:
                        # 生成HTML简报
                        newsletter_data = template_engine.create_newsletter_data(
                            title=f"{topic} - 新闻简报",
                            subtitle=f"为您精心策划的{topic}相关内容",
                            content_sections=[{
                                'title': '主要内容',
                                'articles': [{'title': topic, 'content': newsletter_result[:500]}],
                                'category': 'general'
                            }],
                            user_preferences=user_prefs.to_dict()
                        )
                        
                        html_content = template_engine.generate_newsletter(
                            newsletter_data, 
                            template_style=style,
                            output_format="html"
                        )
                        
                        # 发送邮件
                        unsubscribe_url = f"http://localhost:7860/unsubscribe?id={subscription.subscription_id}"
                        preferences_url = f"http://localhost:7860/preferences?id={subscription.subscription_id}"
                        
                        email_result = sendgrid_client.send_newsletter(
                            to_email=email,
                            subject=f"📰 {topic} - Newsletter Agent",
                            html_content=html_content,
                            subscriber_name=name,
                            unsubscribe_url=unsubscribe_url,
                            preferences_url=preferences_url
                        )
                        
                        if email_result['success']:
                            status_msg += f"✅ 邮件发送成功到：{email}\n"
                            status_msg += f"📧 邮件ID：{email_result.get('message_id', 'N/A')}\n"
                        else:
                            status_msg += f"❌ 邮件发送失败：{email_result.get('error', '未知错误')}\n"
                            
                    except Exception as e:
                        logger.error(f"邮件发送失败: {e}")
                        status_msg += f"❌ 邮件发送失败：{str(e)}\n"
            
            # 4. 保存到全局状态
            app_state['generated_newsletter'] = {
                'topic': topic,
                'content': newsletter_result,
                'research': research_result,
                'generated_at': datetime.now().isoformat(),
                'user_id': user_id if email else None
            }
            
            # 格式化显示内容
            display_content = f"""
# 📰 {topic} - 新闻简报

**生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}
**风格**: {style} | **长度**: {length} | **受众**: {audience}

---

## 🔍 主题研究

{research_result[:800]}...

---

## 📰 完整简报

{newsletter_result}

---

**🤖 由 Newsletter Agent 智能生成**
"""
            
            return display_content, status_msg, "简报生成并处理完成！"
            
        except Exception as e:
            error_msg = f"❌ 生成失败：{str(e)}"
            logger.error(f"简报生成失败: {e}")
            return f"## ❌ 生成失败\n\n错误信息：{str(e)}", error_msg, "生成失败"
    
    def manage_subscription(email: str, action: str, new_frequency: str = "daily") -> str:
        """管理订阅"""
        try:
            from newsletter_agent.src.user import SubscriptionManager
            subscription_manager = SubscriptionManager()
            
            if action == "查看订阅":
                subscription = subscription_manager.get_subscription_by_email(email)
                if subscription:
                    return f"""
## 📧 订阅信息

**邮箱**: {subscription.email}
**姓名**: {subscription.name}
**状态**: {subscription.subscription_status}
**频率**: {subscription.frequency}
**创建时间**: {subscription.created_at.strftime('%Y-%m-%d %H:%M') if subscription.created_at else 'N/A'}
**下次发送**: {subscription.next_send_at.strftime('%Y-%m-%d %H:%M') if subscription.next_send_at else 'N/A'}
**已发送**: {subscription.total_sent} 封邮件
"""
                else:
                    return "❌ 未找到该邮箱的订阅信息"
            
            elif action == "取消订阅":
                if subscription_manager.cancel_subscription_by_email(email, "用户主动取消"):
                    return f"✅ 已成功取消 {email} 的订阅"
                else:
                    return f"❌ 取消订阅失败，邮箱 {email} 可能不存在订阅"
            
            elif action == "更新频率":
                subscription = subscription_manager.get_subscription_by_email(email)
                if subscription:
                    subscription_manager.update_subscription(
                        subscription.subscription_id,
                        {'frequency': new_frequency}
                    )
                    return f"✅ 已将 {email} 的订阅频率更新为 {new_frequency}"
                else:
                    return f"❌ 未找到邮箱 {email} 的订阅"
            
            return "❌ 未知的操作"
            
        except Exception as e:
            return f"❌ 操作失败：{str(e)}"
    
    def test_email_service() -> str:
        """测试邮件服务"""
        try:
            from newsletter_agent.src.email import SendGridEmailClient
            sendgrid_client = SendGridEmailClient()
            
            # 验证配置
            config_result = sendgrid_client.validate_configuration()
            
            result = "## 📧 SendGrid 邮件服务状态\n\n"
            
            if config_result['is_configured']:
                result += "✅ **配置状态**: 已正确配置\n"
                result += f"📮 **发送邮箱**: {config_result['from_email']}\n"
                result += f"🔑 **API密钥**: {'已配置' if config_result['api_key_present'] else '未配置'}\n"
                result += f"📚 **SendGrid库**: {'已安装' if config_result['sendgrid_available'] else '未安装'}\n"
            else:
                result += "❌ **配置状态**: 配置不完整\n"
                result += "**问题列表**:\n"
                for issue in config_result['issues']:
                    result += f"- {issue}\n"
            
            return result
            
        except Exception as e:
            return f"❌ 测试失败：{str(e)}"
    
    def get_system_status() -> str:
        """获取系统状态"""
        try:
            from newsletter_agent.src.agents import create_newsletter_agent
            from newsletter_agent.src.data_sources import data_aggregator
            from newsletter_agent.src.user import SubscriptionManager
            
            # 创建代理测试
            agent = create_newsletter_agent()
            agent_status = agent.get_agent_status()
            
            # 订阅统计
            subscription_manager = SubscriptionManager()
            sub_stats = subscription_manager.get_subscription_statistics()
            
            status = f"""
## 🏠 Newsletter Agent 系统状态

### 🤖 智能代理状态
- **名称**: {agent_status.get('agent_name', 'N/A')}
- **就绪状态**: {'✅ 就绪' if agent_status.get('is_ready') else '❌ 未就绪'}
- **LLM可用**: {'✅ 可用' if agent_status.get('llm_available') else '❌ 不可用'}
- **工具数量**: {agent_status.get('tools_count', 0)} 个
- **LangChain**: {'✅ 可用' if agent_status.get('langchain_available') else '❌ 不可用'}

### 📊 订阅统计
- **总订阅数**: {sub_stats.get('total_subscriptions', 0)}
- **活跃订阅**: {sub_stats.get('active_subscriptions', 0)}
- **已取消**: {sub_stats.get('cancelled_subscriptions', 0)}
- **待发送**: {sub_stats.get('pending_count', 0)}

### 📡 数据源状态
- **NewsAPI**: {'✅ 可用' if hasattr(data_aggregator, 'news_client') else '❌ 不可用'}
- **Reddit API**: {'✅ 可用' if hasattr(data_aggregator, 'reddit_client') else '❌ 不可用'}
- **RSS解析**: {'✅ 可用' if hasattr(data_aggregator, 'rss_parser') else '❌ 不可用'}

### 📧 邮件服务
{test_email_service()}

**最后更新**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
"""
            return status
            
        except Exception as e:
            return f"❌ 获取系统状态失败：{str(e)}"
    
    # 创建Gradio界面
    with gr.Blocks(
        title="📰 Newsletter Agent - 智能新闻简报生成系统",
        theme=gr.themes.Soft()
    ) as app:
        
        # 标题和介绍
        gr.HTML("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin-bottom: 20px;">
            <h1>📰 Newsletter Agent</h1>
            <p style="font-size: 1.2em; margin: 10px 0;">智能新闻简报生成系统</p>
            <p>🤖 AI驱动 | 📧 邮件发送 | 🎯 个性化定制 | 🔄 多源聚合</p>
        </div>
        """)
        
        with gr.Tabs():
            # Tab 1: 简报生成
            with gr.Tab("📰 生成简报"):
                gr.Markdown("## 🎯 智能简报生成")
                
                with gr.Row():
                    with gr.Column(scale=2):
                        topic_input = gr.Textbox(
                            label="📝 简报主题",
                            placeholder="例如：人工智能发展趋势、区块链技术、健康生活...",
                            value="人工智能最新发展"
                        )
                        
                        with gr.Row():
                            style_dropdown = gr.Dropdown(
                                label="🎨 写作风格",
                                choices=["professional", "casual", "academic", "creative"],
                                value="professional"
                            )
                            length_dropdown = gr.Dropdown(
                                label="📏 内容长度",
                                choices=["short", "medium", "long"],
                                value="medium"
                            )
                        
                        audience_dropdown = gr.Dropdown(
                            label="👥 目标受众",
                            choices=["general", "tech", "business", "academic"],
                            value="general"
                        )
                        
                        categories_checkboxes = gr.CheckboxGroup(
                            label="🏷️ 内容分类",
                            choices=["tech", "business", "science", "health", "world", "entertainment"],
                            value=["tech", "business"]
                        )
                
                with gr.Column(scale=1):
                    gr.Markdown("### 📧 邮件发送设置")
                    
                    email_input = gr.Textbox(
                        label="📮 邮箱地址",
                        placeholder="your@email.com"
                    )
                    name_input = gr.Textbox(
                        label="👤 姓名",
                        placeholder="您的姓名"
                    )
                    frequency_dropdown = gr.Dropdown(
                        label="⏰ 发送频率",
                        choices=["daily", "weekly", "bi-weekly", "monthly"],
                        value="daily"
                    )
                    send_email_checkbox = gr.Checkbox(
                        label="📤 立即发送邮件",
                        value=False
                    )
                
                generate_btn = gr.Button(
                    "🚀 生成智能简报",
                    variant="primary",
                    size="lg"
                )
                
                # 输出区域
                with gr.Row():
                    newsletter_output = gr.Markdown(
                        label="📄 生成的简报",
                        value="点击上方按钮开始生成简报..."
                    )
                
                with gr.Row():
                    status_output = gr.Textbox(
                        label="📊 处理状态",
                        lines=5,
                        value="等待开始..."
                    )
                    result_output = gr.Textbox(
                        label="✅ 操作结果",
                        value="未开始"
                    )
                
                # 绑定生成函数
                generate_btn.click(
                    fn=generate_complete_newsletter,
                    inputs=[
                        topic_input, style_dropdown, length_dropdown, 
                        audience_dropdown, email_input, name_input, 
                        frequency_dropdown, categories_checkboxes, send_email_checkbox
                    ],
                    outputs=[newsletter_output, status_output, result_output]
                )
            
            # Tab 2: 订阅管理
            with gr.Tab("📧 订阅管理"):
                gr.Markdown("## 📋 订阅和用户管理")
                
                with gr.Row():
                    email_manage_input = gr.Textbox(
                        label="📮 邮箱地址",
                        placeholder="要管理的邮箱地址"
                    )
                    action_dropdown = gr.Dropdown(
                        label="🔧 操作类型",
                        choices=["查看订阅", "取消订阅", "更新频率"],
                        value="查看订阅"
                    )
                    new_frequency_dropdown = gr.Dropdown(
                        label="⏰ 新频率 (仅更新时使用)",
                        choices=["daily", "weekly", "bi-weekly", "monthly"],
                        value="daily"
                    )
                
                manage_btn = gr.Button("🔧 执行操作", variant="primary")
                
                subscription_output = gr.Markdown(
                    label="📊 操作结果",
                    value="选择操作后点击执行..."
                )
                
                # 绑定管理函数
                manage_btn.click(
                    fn=manage_subscription,
                    inputs=[email_manage_input, action_dropdown, new_frequency_dropdown],
                    outputs=[subscription_output]
                )
            
            # Tab 3: 系统状态
            with gr.Tab("🏠 系统状态"):
                gr.Markdown("## 📊 系统监控和状态")
                
                status_refresh_btn = gr.Button("🔄 刷新状态", variant="secondary")
                
                system_status_output = gr.Markdown(
                    label="📈 系统状态",
                    value="点击刷新获取最新状态..."
                )
                
                # 绑定状态函数
                status_refresh_btn.click(
                    fn=get_system_status,
                    outputs=[system_status_output]
                )
                
                # 自动加载初始状态
                app.load(
                    fn=get_system_status,
                    outputs=[system_status_output]
                )
        
        # 底部信息
        gr.HTML("""
        <div style="text-align: center; margin-top: 30px; padding: 15px; background: #f8f9fa; border-radius: 5px; font-size: 0.9em; color: #666;">
            <p><strong>🤖 Newsletter Agent v1.0.0</strong></p>
            <p>数据来源: NewsAPI, Reddit, RSS Feeds | AI驱动: OpenRouter | 邮件服务: SendGrid</p>
            <p>💻 LangChain + 🎨 Gradio + 📊 多源数据聚合 + 🤖 智能内容生成</p>
        </div>
        """)
    
    return app


def create_main_interface():
    """创建主界面的包装函数"""
    if not GRADIO_AVAILABLE:
        logger.error("Gradio不可用，无法创建界面")
        return None
    
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