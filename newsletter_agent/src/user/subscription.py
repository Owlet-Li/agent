# -*- coding: utf-8 -*-
"""
Newsletter Agent - 订阅管理系统
处理用户订阅、取消订阅、邮件发送调度
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import uuid
import json

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


@dataclass
class Subscription:
    """订阅数据结构"""
    subscription_id: str
    user_id: str
    email: str
    name: str = ""
    
    # 订阅状态
    is_active: bool = True
    subscription_status: str = "active"  # active, paused, cancelled, pending
    
    # 订阅设置
    frequency: str = "daily"  # daily, weekly, bi-weekly, monthly
    preferred_time: str = "09:00"
    timezone: str = "Asia/Shanghai"
    
    # 发送历史
    last_sent_at: Optional[datetime] = None
    next_send_at: Optional[datetime] = None
    total_sent: int = 0
    
    # 订阅来源和类型
    subscription_source: str = "web"  # web, api, email
    subscription_type: str = "newsletter"  # newsletter, digest, alerts
    
    # 元数据
    created_at: datetime = None
    updated_at: datetime = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: str = ""
    
    def __post_init__(self):
        if not self.subscription_id:
            self.subscription_id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.next_send_at is None:
            self.next_send_at = self._calculate_next_send_time()
    
    def _calculate_next_send_time(self) -> datetime:
        """计算下次发送时间"""
        now = datetime.now()
        
        # 解析preferred_time
        try:
            hour, minute = map(int, self.preferred_time.split(':'))
        except:
            hour, minute = 9, 0  # 默认9:00
        
        # 计算下次发送时间
        if self.frequency == "daily":
            next_send = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_send <= now:
                next_send += timedelta(days=1)
        elif self.frequency == "weekly":
            # 每周一发送
            days_ahead = 0 - now.weekday()  # Monday = 0
            if days_ahead <= 0:
                days_ahead += 7
            next_send = (now + timedelta(days=days_ahead)).replace(hour=hour, minute=minute, second=0, microsecond=0)
        elif self.frequency == "bi-weekly":
            # 每两周发送
            days_ahead = 0 - now.weekday()
            if days_ahead <= 0:
                days_ahead += 14
            next_send = (now + timedelta(days=days_ahead)).replace(hour=hour, minute=minute, second=0, microsecond=0)
        elif self.frequency == "monthly":
            # 每月1号发送
            if now.day == 1 and now.hour < hour:
                next_send = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            else:
                # 下个月1号
                if now.month == 12:
                    next_send = datetime(now.year + 1, 1, 1, hour, minute)
                else:
                    next_send = datetime(now.year, now.month + 1, 1, hour, minute)
        else:
            # 默认每日
            next_send = now.replace(hour=hour, minute=minute, second=0, microsecond=0) + timedelta(days=1)
        
        return next_send
    
    def update_next_send_time(self):
        """更新下次发送时间"""
        self.next_send_at = self._calculate_next_send_time()
        self.updated_at = datetime.now()
    
    def mark_as_sent(self):
        """标记为已发送"""
        self.last_sent_at = datetime.now()
        self.total_sent += 1
        self.update_next_send_time()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        # 转换datetime为ISO字符串
        datetime_fields = ['created_at', 'updated_at', 'last_sent_at', 'next_send_at', 'cancelled_at']
        for field in datetime_fields:
            if data.get(field):
                data[field] = getattr(self, field).isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Subscription':
        """从字典创建实例"""
        # 转换ISO字符串为datetime
        datetime_fields = ['created_at', 'updated_at', 'last_sent_at', 'next_send_at', 'cancelled_at']
        for field in datetime_fields:
            if data.get(field):
                data[field] = datetime.fromisoformat(data[field])
        
        return cls(**data)


class SubscriptionManager:
    """订阅管理器"""
    
    def __init__(self):
        self.subscriptions: Dict[str, Subscription] = {}
        self.email_subscriptions: Dict[str, str] = {}  # email -> subscription_id映射
        logger.info("订阅管理器初始化完成")
    
    def create_subscription(
        self,
        user_id: str,
        email: str,
        name: str = "",
        frequency: str = "daily",
        preferred_time: str = "09:00",
        subscription_source: str = "web"
    ) -> Subscription:
        """创建新订阅"""
        # 检查是否已存在订阅
        existing_subscription = self.get_subscription_by_email(email)
        if existing_subscription:
            logger.warning(f"邮箱已存在订阅: {email}")
            return existing_subscription
        
        subscription = Subscription(
            subscription_id=str(uuid.uuid4()),
            user_id=user_id,
            email=email,
            name=name,
            frequency=frequency,
            preferred_time=preferred_time,
            subscription_source=subscription_source
        )
        
        self.subscriptions[subscription.subscription_id] = subscription
        self.email_subscriptions[email] = subscription.subscription_id
        
        logger.info(f"创建订阅: {email} ({subscription.subscription_id})")
        return subscription
    
    def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """获取订阅"""
        return self.subscriptions.get(subscription_id)
    
    def get_subscription_by_email(self, email: str) -> Optional[Subscription]:
        """通过邮箱获取订阅"""
        subscription_id = self.email_subscriptions.get(email)
        if subscription_id:
            return self.subscriptions.get(subscription_id)
        return None
    
    def get_user_subscriptions(self, user_id: str) -> List[Subscription]:
        """获取用户的所有订阅"""
        return [sub for sub in self.subscriptions.values() if sub.user_id == user_id]
    
    def update_subscription(
        self,
        subscription_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Subscription]:
        """更新订阅"""
        subscription = self.get_subscription(subscription_id)
        if not subscription:
            logger.warning(f"订阅不存在: {subscription_id}")
            return None
        
        # 更新字段
        for key, value in updates.items():
            if hasattr(subscription, key):
                setattr(subscription, key, value)
        
        subscription.updated_at = datetime.now()
        
        # 如果更新了频率或时间，重新计算下次发送时间
        if 'frequency' in updates or 'preferred_time' in updates:
            subscription.update_next_send_time()
        
        logger.info(f"更新订阅: {subscription_id}")
        return subscription
    
    def cancel_subscription(
        self,
        subscription_id: str,
        reason: str = ""
    ) -> bool:
        """取消订阅"""
        subscription = self.get_subscription(subscription_id)
        if not subscription:
            logger.warning(f"订阅不存在: {subscription_id}")
            return False
        
        subscription.is_active = False
        subscription.subscription_status = "cancelled"
        subscription.cancelled_at = datetime.now()
        subscription.cancellation_reason = reason
        subscription.updated_at = datetime.now()
        
        logger.info(f"取消订阅: {subscription_id} (原因: {reason})")
        return True
    
    def cancel_subscription_by_email(self, email: str, reason: str = "") -> bool:
        """通过邮箱取消订阅"""
        subscription = self.get_subscription_by_email(email)
        if subscription:
            return self.cancel_subscription(subscription.subscription_id, reason)
        return False
    
    def reactivate_subscription(self, subscription_id: str) -> bool:
        """重新激活订阅"""
        subscription = self.get_subscription(subscription_id)
        if not subscription:
            return False
        
        subscription.is_active = True
        subscription.subscription_status = "active"
        subscription.cancelled_at = None
        subscription.cancellation_reason = ""
        subscription.updated_at = datetime.now()
        subscription.update_next_send_time()
        
        logger.info(f"重新激活订阅: {subscription_id}")
        return True
    
    def pause_subscription(self, subscription_id: str) -> bool:
        """暂停订阅"""
        subscription = self.get_subscription(subscription_id)
        if not subscription:
            return False
        
        subscription.subscription_status = "paused"
        subscription.updated_at = datetime.now()
        
        logger.info(f"暂停订阅: {subscription_id}")
        return True
    
    def resume_subscription(self, subscription_id: str) -> bool:
        """恢复订阅"""
        subscription = self.get_subscription(subscription_id)
        if not subscription:
            return False
        
        subscription.subscription_status = "active"
        subscription.updated_at = datetime.now()
        subscription.update_next_send_time()
        
        logger.info(f"恢复订阅: {subscription_id}")
        return True
    
    def get_pending_subscriptions(self, limit_time: Optional[datetime] = None) -> List[Subscription]:
        """获取待发送的订阅"""
        if limit_time is None:
            limit_time = datetime.now()
        
        pending = []
        for subscription in self.subscriptions.values():
            if (subscription.is_active and 
                subscription.subscription_status == "active" and
                subscription.next_send_at and
                subscription.next_send_at <= limit_time):
                pending.append(subscription)
        
        return pending
    
    def mark_subscription_as_sent(self, subscription_id: str) -> bool:
        """标记订阅为已发送"""
        subscription = self.get_subscription(subscription_id)
        if not subscription:
            return False
        
        subscription.mark_as_sent()
        logger.info(f"标记订阅已发送: {subscription_id}")
        return True
    
    def get_subscription_statistics(self) -> Dict[str, Any]:
        """获取订阅统计"""
        total = len(self.subscriptions)
        active = len([s for s in self.subscriptions.values() if s.is_active])
        cancelled = len([s for s in self.subscriptions.values() if s.subscription_status == "cancelled"])
        paused = len([s for s in self.subscriptions.values() if s.subscription_status == "paused"])
        
        # 按频率统计
        frequency_stats = {}
        for subscription in self.subscriptions.values():
            freq = subscription.frequency
            frequency_stats[freq] = frequency_stats.get(freq, 0) + 1
        
        # 按来源统计
        source_stats = {}
        for subscription in self.subscriptions.values():
            source = subscription.subscription_source
            source_stats[source] = source_stats.get(source, 0) + 1
        
        return {
            'total_subscriptions': total,
            'active_subscriptions': active,
            'cancelled_subscriptions': cancelled,
            'paused_subscriptions': paused,
            'frequency_distribution': frequency_stats,
            'source_distribution': source_stats,
            'pending_count': len(self.get_pending_subscriptions())
        }
    
    def export_subscriptions(self) -> str:
        """导出所有订阅数据"""
        data = {
            'subscriptions': [sub.to_dict() for sub in self.subscriptions.values()],
            'exported_at': datetime.now().isoformat(),
            'total_count': len(self.subscriptions)
        }
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    def import_subscriptions(self, data_json: str) -> int:
        """导入订阅数据"""
        try:
            data = json.loads(data_json)
            imported_count = 0
            
            for sub_data in data.get('subscriptions', []):
                subscription = Subscription.from_dict(sub_data)
                self.subscriptions[subscription.subscription_id] = subscription
                self.email_subscriptions[subscription.email] = subscription.subscription_id
                imported_count += 1
            
            logger.info(f"导入订阅数据: {imported_count} 个订阅")
            return imported_count
            
        except Exception as e:
            logger.error(f"导入订阅数据失败: {e}")
            return 0
    
    def validate_subscription_data(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证订阅数据"""
        errors = {}
        
        # 验证必填字段
        required_fields = ['user_id', 'email']
        for field in required_fields:
            if field not in subscription_data or not subscription_data[field]:
                errors[field] = f"{field}是必填字段"
        
        # 验证邮箱格式
        import re
        email = subscription_data.get('email', '')
        if email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            errors['email'] = "邮箱格式不正确"
        
        # 验证频率
        valid_frequencies = ['daily', 'weekly', 'bi-weekly', 'monthly']
        frequency = subscription_data.get('frequency', 'daily')
        if frequency not in valid_frequencies:
            errors['frequency'] = f"频率必须是: {', '.join(valid_frequencies)}"
        
        # 验证时间格式
        preferred_time = subscription_data.get('preferred_time', '09:00')
        if not re.match(r'^\d{2}:\d{2}$', preferred_time):
            errors['preferred_time'] = "时间格式必须是 HH:MM"
        
        return errors
    
    def get_unsubscribe_link(self, subscription_id: str, base_url: str = "http://localhost:7860") -> str:
        """生成取消订阅链接"""
        return f"{base_url}/unsubscribe?subscription_id={subscription_id}"
    
    def get_manage_preferences_link(self, subscription_id: str, base_url: str = "http://localhost:7860") -> str:
        """生成管理偏好链接"""
        return f"{base_url}/preferences?subscription_id={subscription_id}" 