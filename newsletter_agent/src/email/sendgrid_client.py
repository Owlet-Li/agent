# -*- coding: utf-8 -*-
"""
Newsletter Agent - SendGrid邮件客户端
使用SendGrid API发送新闻简报和通知邮件
"""

from typing import Dict, List, Any, Optional
import os
from datetime import datetime
import json

try:
    import sendgrid
    from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    sendgrid = None
    Mail = Email = To = Content = None

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class SendGridEmailClient:
    """SendGrid邮件发送客户端"""
    
    def __init__(self):
        self.api_key = self._get_api_key()
        self.client = None
        self.from_email = self._get_from_email()
        self.from_name = "Newsletter Agent"
        
        if SENDGRID_AVAILABLE and self.api_key:
            try:
                self.client = sendgrid.SendGridAPIClient(api_key=self.api_key)
                logger.info("SendGrid客户端初始化成功")
            except Exception as e:
                logger.error(f"SendGrid客户端初始化失败: {e}")
                self.client = None
        else:
            logger.warning("SendGrid不可用 - 缺少依赖或API密钥")
    
    def _get_api_key(self) -> Optional[str]:
        """获取SendGrid API密钥"""
        # 从环境变量获取
        api_key = os.getenv('SENDGRID_API_KEY')
        if api_key:
            return api_key
        
        # 从配置文件获取
        try:
            from newsletter_agent.config.settings import settings
            return getattr(settings, 'SENDGRID_API_KEY', None)
        except:
            return None
    
    def _get_from_email(self) -> str:
        """获取发送方邮箱"""
        from_email = os.getenv('SENDGRID_FROM_EMAIL', 'newsletter@example.com')
        
        try:
            from newsletter_agent.config.settings import settings
            return getattr(settings, 'SENDGRID_FROM_EMAIL', from_email)
        except:
            return from_email
    
    def is_available(self) -> bool:
        """检查SendGrid是否可用"""
        return SENDGRID_AVAILABLE and self.client is not None
    
    def send_newsletter(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        subscriber_name: str = "",
        unsubscribe_url: str = "",
        preferences_url: str = ""
    ) -> Dict[str, Any]:
        """发送新闻简报邮件"""
        if not self.is_available():
            return {
                'success': False,
                'error': 'SendGrid服务不可用',
                'message_id': None
            }
        
        try:
            # 创建邮件对象
            from_email_obj = Email(self.from_email, self.from_name)
            to_email_obj = To(to_email, subscriber_name if subscriber_name else to_email.split('@')[0])
            
            # 创建HTML内容
            html_content_obj = Content("text/html", html_content)
            
            # 创建邮件
            mail = Mail(
                from_email=from_email_obj,
                to_emails=to_email_obj,
                subject=subject,
                html_content=html_content_obj
            )
            
            # 添加纯文本内容（如果提供）
            if text_content:
                mail.content = [
                    Content("text/plain", text_content),
                    html_content_obj
                ]
            
            # 添加取消订阅链接
            if unsubscribe_url:
                mail.asm = {
                    "group_id": 1,  # 取消订阅组ID
                    "groups_to_display": [1]
                }
                
                # 在HTML内容中添加取消订阅链接
                if "<body>" in html_content:
                    unsubscribe_footer = f'''
                    <div style="text-align: center; font-size: 12px; color: #666; margin-top: 20px;">
                        <p>不想再收到这些邮件？<a href="{unsubscribe_url}">取消订阅</a></p>
                        <p>或者<a href="{preferences_url}">管理您的偏好设置</a></p>
                    </div>
                    '''
                    html_content = html_content.replace("</body>", unsubscribe_footer + "</body>")
                    mail.content[1] = Content("text/html", html_content)
            
            # 发送邮件
            response = self.client.send(mail)
            
            # 检查响应
            success = 200 <= response.status_code < 300
            
            result = {
                'success': success,
                'status_code': response.status_code,
                'message_id': response.headers.get('X-Message-Id'),
                'to_email': to_email,
                'subject': subject,
                'sent_at': datetime.now().isoformat()
            }
            
            if success:
                logger.info(f"邮件发送成功: {to_email} - {subject}")
            else:
                logger.error(f"邮件发送失败: {response.status_code} - {response.body}")
                result['error'] = f"SendGrid错误: {response.status_code}"
                result['error_details'] = response.body
            
            return result
            
        except Exception as e:
            logger.error(f"SendGrid邮件发送异常: {e}")
            return {
                'success': False,
                'error': str(e),
                'message_id': None,
                'to_email': to_email
            }
    
    def send_welcome_email(
        self,
        to_email: str,
        subscriber_name: str = "",
        preferences_url: str = "",
        unsubscribe_url: str = ""
    ) -> Dict[str, Any]:
        """发送欢迎邮件"""
        try:
            from newsletter_agent.src.templates import email_template_engine
            
            # 生成欢迎邮件
            email_data = email_template_engine.generate_email(
                template_type='welcome',
                template_name='welcome',
                format_type='html',
                subscriber_name=subscriber_name if subscriber_name else to_email.split('@')[0],
                preferences_url=preferences_url,
                unsubscribe_url=unsubscribe_url
            )
            
            return self.send_newsletter(
                to_email=to_email,
                subject=email_data['subject'],
                html_content=email_data['content'],
                subscriber_name=subscriber_name,
                unsubscribe_url=unsubscribe_url,
                preferences_url=preferences_url
            )
            
        except Exception as e:
            logger.error(f"发送欢迎邮件失败: {e}")
            return {
                'success': False,
                'error': f"生成欢迎邮件失败: {str(e)}",
                'message_id': None
            }
    
    def send_subscription_confirmation(
        self,
        to_email: str,
        subscriber_name: str = "",
        frequency: str = "daily",
        topics: List[str] = None,
        language: str = "zh",
        next_delivery: str = ""
    ) -> Dict[str, Any]:
        """发送订阅确认邮件"""
        try:
            from newsletter_agent.src.templates import email_template_engine
            
            topics_str = ", ".join(topics) if topics else "通用"
            
            email_data = email_template_engine.generate_email(
                template_type='subscription',
                template_name='confirmation',
                format_type='html',
                subscriber_name=subscriber_name,
                frequency=frequency,
                topics=topics_str,
                language=language,
                next_delivery=next_delivery
            )
            
            return self.send_newsletter(
                to_email=to_email,
                subject=email_data['subject'],
                html_content=email_data['content'],
                subscriber_name=subscriber_name
            )
            
        except Exception as e:
            logger.error(f"发送订阅确认邮件失败: {e}")
            return {
                'success': False,
                'error': f"生成确认邮件失败: {str(e)}",
                'message_id': None
            }
    
    def send_unsubscribe_confirmation(
        self,
        to_email: str,
        subscriber_name: str = ""
    ) -> Dict[str, Any]:
        """发送取消订阅确认邮件"""
        try:
            from newsletter_agent.src.templates import email_template_engine
            
            email_data = email_template_engine.generate_email(
                template_type='subscription',
                template_name='unsubscribe',
                format_type='html',
                subscriber_name=subscriber_name
            )
            
            return self.send_newsletter(
                to_email=to_email,
                subject=email_data['subject'],
                html_content=email_data['content'],
                subscriber_name=subscriber_name
            )
            
        except Exception as e:
            logger.error(f"发送取消订阅确认邮件失败: {e}")
            return {
                'success': False,
                'error': f"生成取消订阅邮件失败: {str(e)}",
                'message_id': None
            }
    
    def send_bulk_newsletters(
        self,
        recipients: List[Dict[str, Any]],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """批量发送简报"""
        if not self.is_available():
            return {
                'success': False,
                'total_recipients': len(recipients),
                'sent_count': 0,
                'failed_count': len(recipients),
                'error': 'SendGrid服务不可用'
            }
        
        sent_count = 0
        failed_count = 0
        results = []
        
        for recipient in recipients:
            to_email = recipient.get('email')
            subscriber_name = recipient.get('name', '')
            unsubscribe_url = recipient.get('unsubscribe_url', '')
            preferences_url = recipient.get('preferences_url', '')
            
            if not to_email:
                failed_count += 1
                continue
            
            result = self.send_newsletter(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                subscriber_name=subscriber_name,
                unsubscribe_url=unsubscribe_url,
                preferences_url=preferences_url
            )
            
            results.append(result)
            
            if result['success']:
                sent_count += 1
            else:
                failed_count += 1
        
        summary = {
            'success': failed_count == 0,
            'total_recipients': len(recipients),
            'sent_count': sent_count,
            'failed_count': failed_count,
            'results': results,
            'sent_at': datetime.now().isoformat()
        }
        
        logger.info(f"批量邮件发送完成: {sent_count}/{len(recipients)} 成功")
        return summary
    
    def get_sendgrid_statistics(self, days: int = 7) -> Dict[str, Any]:
        """获取SendGrid统计信息"""
        if not self.is_available():
            return {'error': 'SendGrid服务不可用'}
        
        try:
            # 这里可以调用SendGrid的统计API
            # 由于需要复杂的日期处理，暂时返回基本信息
            return {
                'service_status': 'available',
                'api_key_configured': bool(self.api_key),
                'from_email': self.from_email,
                'note': f'统计数据需要调用SendGrid Stats API (过去{days}天)'
            }
            
        except Exception as e:
            logger.error(f"获取SendGrid统计失败: {e}")
            return {'error': str(e)}
    
    def validate_configuration(self) -> Dict[str, Any]:
        """验证SendGrid配置"""
        issues = []
        
        if not SENDGRID_AVAILABLE:
            issues.append("SendGrid库未安装")
        
        if not self.api_key:
            issues.append("SENDGRID_API_KEY未配置")
        
        if not self.from_email or '@' not in self.from_email:
            issues.append("发送方邮箱配置无效")
        
        if not self.client:
            issues.append("SendGrid客户端初始化失败")
        
        return {
            'is_configured': len(issues) == 0,
            'issues': issues,
            'from_email': self.from_email,
            'api_key_present': bool(self.api_key),
            'sendgrid_available': SENDGRID_AVAILABLE
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """测试SendGrid连接"""
        if not self.is_available():
            return {
                'success': False,
                'error': 'SendGrid服务不可用'
            }
        
        try:
            # 发送测试邮件到自己
            test_result = self.send_newsletter(
                to_email=self.from_email,
                subject="Newsletter Agent - 连接测试",
                html_content="""
                <h2>SendGrid连接测试</h2>
                <p>如果您收到此邮件，说明SendGrid配置正确！</p>
                <p>发送时间: {}</p>
                """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                text_content="SendGrid连接测试成功！"
            )
            
            return {
                'success': test_result['success'],
                'message': "测试邮件已发送" if test_result['success'] else "测试邮件发送失败",
                'details': test_result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"连接测试失败: {str(e)}"
            } 