# -*- coding: utf-8 -*-
"""
Newsletter Agent - 邮件模板引擎
专为SendGrid邮件发送设计的模板系统
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import html

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class EmailTemplateEngine:
    """邮件模板引擎"""
    
    def __init__(self):
        self.templates = {
            'welcome': self._get_welcome_templates(),
            'newsletter': self._get_newsletter_templates(),
            'subscription': self._get_subscription_templates(),
            'notification': self._get_notification_templates()
        }
        logger.info("邮件模板引擎初始化完成")
    
    def _get_welcome_templates(self) -> Dict[str, str]:
        """欢迎邮件模板"""
        return {
            'html': '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>欢迎订阅 Newsletter Agent</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }}
        .content {{
            background: #f9f9f9;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }}
        .welcome-message {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            margin-bottom: 20px;
        }}
        .features {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .feature-item {{
            margin-bottom: 15px;
            padding: 10px;
            border-left: 3px solid #764ba2;
            background: #f8f9fa;
        }}
        .cta-button {{
            background: #667eea;
            color: white;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 25px;
            display: inline-block;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            color: #666;
            font-size: 0.9em;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎉 欢迎来到 Newsletter Agent！</h1>
        <p>感谢您订阅我们的智能新闻简报服务</p>
    </div>
    
    <div class="content">
        <div class="welcome-message">
            <h2>你好，{subscriber_name}！</h2>
            <p>我们很高兴您加入了 Newsletter Agent 大家庭！我们的AI驱动的新闻简报将为您带来：</p>
        </div>
        
        <div class="features">
            <h3>🚀 您将享受到的服务：</h3>
            <div class="feature-item">
                <strong>📰 个性化新闻</strong> - 基于您的兴趣定制的新闻内容
            </div>
            <div class="feature-item">
                <strong>🤖 AI智能筛选</strong> - 高质量内容，去除重复和低质量信息
            </div>
            <div class="feature-item">
                <strong>🔄 多源聚合</strong> - 来自NewsAPI、Reddit、RSS等多个数据源
            </div>
            <div class="feature-item">
                <strong>⏰ 定时发送</strong> - 按您设定的频率准时送达
            </div>
            <div class="feature-item">
                <strong>📱 多格式支持</strong> - HTML和纯文本格式，适配各种设备
            </div>
        </div>
        
        <div style="text-align: center;">
            <a href="{preferences_url}" class="cta-button">🔧 设置您的偏好</a>
        </div>
        
        <div class="welcome-message">
            <h3>接下来做什么？</h3>
            <ol>
                <li>点击上方按钮设置您的兴趣话题</li>
                <li>选择接收简报的频率（每日/每周）</li>
                <li>等待第一份个性化简报送达！</li>
            </ol>
        </div>
    </div>
    
    <div class="footer">
        <p>🤖 Newsletter Agent | 智能新闻简报生成系统</p>
        <p>如有任何问题，请回复此邮件或联系我们</p>
        <p><a href="{unsubscribe_url}">取消订阅</a> | <a href="{preferences_url}">管理偏好</a></p>
    </div>
</body>
</html>
            ''',
            
            'text': '''
🎉 欢迎来到 Newsletter Agent！

你好，{subscriber_name}！

感谢您订阅我们的智能新闻简报服务。我们很高兴您加入了 Newsletter Agent 大家庭！

🚀 您将享受到的服务：

📰 个性化新闻 - 基于您的兴趣定制的新闻内容
🤖 AI智能筛选 - 高质量内容，去除重复和低质量信息  
🔄 多源聚合 - 来自NewsAPI、Reddit、RSS等多个数据源
⏰ 定时发送 - 按您设定的频率准时送达
📱 多格式支持 - HTML和纯文本格式，适配各种设备

接下来做什么？

1. 访问偏好设置页面：{preferences_url}
2. 设置您的兴趣话题
3. 选择接收简报的频率（每日/每周）
4. 等待第一份个性化简报送达！

🤖 Newsletter Agent | 智能新闻简报生成系统

如有任何问题，请回复此邮件或联系我们
取消订阅：{unsubscribe_url}
管理偏好：{preferences_url}
            '''
        }
    
    def _get_newsletter_templates(self) -> Dict[str, Dict[str, str]]:
        """简报邮件模板"""
        return {
            'html': '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{newsletter_title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 0;
            background-color: #f5f5f5;
        }}
        .email-container {{
            background-color: white;
            margin: 20px;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .email-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .email-content {{
            padding: 30px;
        }}
        .newsletter-meta {{
            background: #e7f3ff;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 25px;
            text-align: center;
        }}
        .section {{
            margin-bottom: 35px;
            border-bottom: 2px solid #eee;
            padding-bottom: 25px;
        }}
        .section:last-child {{
            border-bottom: none;
        }}
        .section-title {{
            color: #667eea;
            font-size: 1.5em;
            margin-bottom: 20px;
            border-left: 4px solid #667eea;
            padding-left: 15px;
        }}
        .article {{
            margin-bottom: 20px;
            padding: 15px;
            background-color: #fafafa;
            border-radius: 8px;
            border-left: 4px solid #764ba2;
        }}
        .article-title {{
            font-size: 1.2em;
            font-weight: 600;
            margin-bottom: 8px;
        }}
        .article-title a {{
            text-decoration: none;
            color: #333;
        }}
        .article-title a:hover {{
            color: #667eea;
        }}
        .article-summary {{
            color: #666;
            margin-bottom: 10px;
        }}
        .article-meta {{
            font-size: 0.85em;
            color: #999;
            border-top: 1px solid #ddd;
            padding-top: 8px;
        }}
        .email-footer {{
            background-color: #f8f9fa;
            padding: 20px 30px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        .unsubscribe-link {{
            color: #999;
            text-decoration: none;
            font-size: 0.8em;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="email-header">
            <h1>📰 {newsletter_title}</h1>
            <p>{newsletter_subtitle}</p>
        </div>
        
        <div class="email-content">
            <div class="newsletter-meta">
                <strong>📊 本期统计:</strong> {total_articles} 篇文章 | {total_sections} 个分类 | {generated_at}
                <br><strong>👤 个性化定制</strong> 基于您的兴趣偏好
            </div>
            
            {newsletter_content}
        </div>
        
        <div class="email-footer">
            <p>🤖 由 Newsletter Agent 为您智能生成</p>
            <p>数据来源: NewsAPI, Reddit, RSS Feeds | AI驱动: OpenRouter</p>
            <p>
                <a href="{preferences_url}">⚙️ 管理偏好</a> | 
                <a href="{unsubscribe_url}" class="unsubscribe-link">取消订阅</a>
            </p>
        </div>
    </div>
</body>
</html>
            ''',
            
            'text': '''
📰 {newsletter_title}

{newsletter_subtitle}

📊 本期统计: {total_articles} 篇文章 | {total_sections} 个分类 | {generated_at}
👤 个性化定制: 基于您的兴趣偏好

{newsletter_content_text}

---

🤖 由 Newsletter Agent 为您智能生成
数据来源: NewsAPI, Reddit, RSS Feeds | AI驱动: OpenRouter

⚙️ 管理偏好: {preferences_url}
📧 取消订阅: {unsubscribe_url}
            '''
        }
    
    def _get_subscription_templates(self) -> Dict[str, Dict[str, str]]:
        """订阅管理模板"""
        return {
            'confirmation': {
                'html': '''
<div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
    <div style="background: #667eea; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
        <h1>✅ 订阅确认</h1>
    </div>
    <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
        <p>你好 {subscriber_name}，</p>
        <p>您的订阅设置已成功更新：</p>
        <ul>
            <li>订阅频率: {frequency}</li>
            <li>兴趣话题: {topics}</li>
            <li>语言偏好: {language}</li>
        </ul>
        <p>下一份简报将在 {next_delivery} 发送给您。</p>
    </div>
</div>
                ''',
                'text': '''
✅ 订阅确认

你好 {subscriber_name}，

您的订阅设置已成功更新：
- 订阅频率: {frequency}
- 兴趣话题: {topics}  
- 语言偏好: {language}

下一份简报将在 {next_delivery} 发送给您。
                '''
            },
            
            'unsubscribe': {
                'html': '''
<div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif; text-align: center;">
    <h1>😢 很遗憾看到您离开</h1>
    <p>您已成功取消订阅 Newsletter Agent。</p>
    <p>如果将来想要重新订阅，随时欢迎您回来！</p>
    <p>感谢您对我们服务的支持。</p>
</div>
                ''',
                'text': '''
😢 很遗憾看到您离开

您已成功取消订阅 Newsletter Agent。

如果将来想要重新订阅，随时欢迎您回来！

感谢您对我们服务的支持。
                '''
            }
        }
    
    def _get_notification_templates(self) -> Dict[str, Dict[str, str]]:
        """通知邮件模板"""
        return {
            'system_update': {
                'html': '''
<div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
    <h1>🔔 系统更新通知</h1>
    <p>Newsletter Agent 有新功能上线：</p>
    <div style="background: #f0f8ff; padding: 15px; border-radius: 5px;">
        {update_content}
    </div>
    <p>感谢您的支持！</p>
</div>
                ''',
                'text': '''
🔔 系统更新通知

Newsletter Agent 有新功能上线：

{update_content}

感谢您的支持！
                '''
            }
        }
    
    def generate_email(
        self,
        template_type: str,
        template_name: str,
        format_type: str,
        **kwargs
    ) -> Dict[str, Any]:
        """生成邮件内容"""
        try:
            if template_type not in self.templates:
                raise ValueError(f"未知的模板类型: {template_type}")
            
            templates = self.templates[template_type]
            
            if template_name not in templates:
                raise ValueError(f"未知的模板名称: {template_name}")
            
            template_data = templates[template_name]
            
            if format_type not in template_data:
                raise ValueError(f"不支持的格式: {format_type}")
            
            template = template_data[format_type]
            content = template.format(**kwargs)
            
            # 生成邮件元数据
            subject = self._generate_subject(template_type, template_name, **kwargs)
            
            return {
                'subject': subject,
                'content': content,
                'format': format_type,
                'template_type': template_type,
                'template_name': template_name,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"邮件生成失败: {e}")
            return self._generate_error_email(str(e))
    
    def _generate_subject(self, template_type: str, template_name: str, **kwargs) -> str:
        """生成邮件主题"""
        subject_templates = {
            'welcome': '🎉 欢迎订阅 Newsletter Agent！',
            'newsletter': {
                'default': '📰 {newsletter_title} - Newsletter Agent'
            },
            'subscription': {
                'confirmation': '✅ 订阅设置确认 - Newsletter Agent',
                'unsubscribe': '😢 取消订阅确认 - Newsletter Agent'
            },
            'notification': {
                'system_update': '🔔 Newsletter Agent 系统更新'
            }
        }
        
        if template_type == 'newsletter':
            return subject_templates[template_type]['default'].format(**kwargs)
        elif template_type in subject_templates:
            if isinstance(subject_templates[template_type], dict):
                return subject_templates[template_type].get(template_name, f'Newsletter Agent - {template_name}')
            else:
                return subject_templates[template_type]
        else:
            return 'Newsletter Agent 通知'
    
    def _generate_error_email(self, error_msg: str) -> Dict[str, Any]:
        """生成错误邮件"""
        return {
            'subject': '❌ Newsletter Agent - 邮件生成错误',
            'content': f'''
<div style="color: red; padding: 20px; border: 1px solid #ccc;">
    <h2>邮件生成失败</h2>
    <p>错误信息: {html.escape(error_msg)}</p>
    <p>请联系技术支持。</p>
</div>
            ''',
            'format': 'html',
            'template_type': 'error',
            'template_name': 'system_error',
            'generated_at': datetime.now().isoformat()
        }
    
    def format_newsletter_for_email(
        self,
        newsletter_content: str,
        newsletter_data: Dict[str, Any],
        subscriber_email: str,
        preferences_url: str = "#",
        unsubscribe_url: str = "#"
    ) -> Dict[str, Any]:
        """将简报内容格式化为邮件"""
        return self.generate_email(
            template_type='newsletter',
            template_name='default',
            format_type='html',
            newsletter_title=newsletter_data.get('title', '每日新闻简报'),
            newsletter_subtitle=newsletter_data.get('subtitle', '您的个性化新闻摘要'),
            newsletter_content=newsletter_content,
            total_articles=newsletter_data.get('total_articles', 0),
            total_sections=newsletter_data.get('total_sections', 0),
            generated_at=newsletter_data.get('generated_at', datetime.now().strftime('%Y年%m月%d日')),
            preferences_url=preferences_url,
            unsubscribe_url=unsubscribe_url
        )
    
    def get_available_templates(self) -> Dict[str, List[str]]:
        """获取可用模板列表"""
        available = {}
        for template_type, templates in self.templates.items():
            if isinstance(templates, dict):
                available[template_type] = list(templates.keys())
            else:
                available[template_type] = ['default']
        return available 