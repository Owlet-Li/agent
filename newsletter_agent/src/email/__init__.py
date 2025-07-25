# -*- coding: utf-8 -*-
"""
Newsletter Agent - 邮件发送系统
集成SendGrid邮件服务，支持简报和通知邮件发送
"""

from .sendgrid_client import SendGridEmailClient
from .email_scheduler import EmailScheduler
from .email_validator import EmailValidator

__all__ = [
    'SendGridEmailClient',
    'EmailScheduler', 
    'EmailValidator'
]

# 全局实例
sendgrid_client = SendGridEmailClient()
email_scheduler = EmailScheduler()
email_validator = EmailValidator() 