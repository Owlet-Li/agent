# -*- coding: utf-8 -*-
"""
Newsletter Agent - 邮件调度器
管理邮件发送的时间调度和批量处理
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import time

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class EmailScheduler:
    """邮件调度器"""
    
    def __init__(self):
        self.scheduled_emails = []
        logger.info("邮件调度器初始化完成")
    
    def schedule_email(self, email_data: Dict[str, Any], send_at: datetime) -> str:
        """调度邮件发送"""
        email_id = f"email_{int(time.time())}"
        
        schedule_item = {
            'id': email_id,
            'email_data': email_data,
            'send_at': send_at,
            'status': 'scheduled',
            'created_at': datetime.now()
        }
        
        self.scheduled_emails.append(schedule_item)
        logger.info(f"邮件已调度: {email_id} - {send_at}")
        
        return email_id
    
    def get_pending_emails(self) -> List[Dict[str, Any]]:
        """获取待发送的邮件"""
        now = datetime.now()
        pending = []
        
        for email in self.scheduled_emails:
            if email['status'] == 'scheduled' and email['send_at'] <= now:
                pending.append(email)
        
        return pending
    
    def mark_as_sent(self, email_id: str) -> bool:
        """标记邮件为已发送"""
        for email in self.scheduled_emails:
            if email['id'] == email_id:
                email['status'] = 'sent'
                email['sent_at'] = datetime.now()
                return True
        return False
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """获取调度器状态"""
        total = len(self.scheduled_emails)
        scheduled = len([e for e in self.scheduled_emails if e['status'] == 'scheduled'])
        sent = len([e for e in self.scheduled_emails if e['status'] == 'sent'])
        
        return {
            'total_emails': total,
            'scheduled': scheduled,
            'sent': sent,
            'pending': len(self.get_pending_emails())
        } 