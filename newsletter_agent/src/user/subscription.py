# -*- coding: utf-8 -*-
"""
Newsletter Agent - Subscription Management System
Handles user subscriptions, unsubscriptions, and email scheduling
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
    """Subscription data structure"""
    subscription_id: str
    user_id: str
    email: str
    name: str = ""
    
    # Subscription status
    is_active: bool = True
    subscription_status: str = "active"  # active, paused, cancelled, pending
    
    # Subscription settings
    frequency: str = "daily"  # daily, weekly, bi-weekly, monthly
    preferred_time: str = "09:00"
    timezone: str = "Asia/Shanghai"
    
    # Send history
    last_sent_at: Optional[datetime] = None
    next_send_at: Optional[datetime] = None
    total_sent: int = 0
    
    # Subscription source and type
    subscription_source: str = "web"  # web, api, email
    subscription_type: str = "newsletter"  # newsletter, digest, alerts
    
    # Metadata
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
        """Calculate next send time"""
        now = datetime.now()
        
        # Parse preferred_time
        try:
            hour, minute = map(int, self.preferred_time.split(':'))
        except:
            hour, minute = 9, 0  # Default 9:00
        
        # Calculate next send time
        if self.frequency == "daily":
            next_send = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_send <= now:
                next_send += timedelta(days=1)
        elif self.frequency == "weekly":
            # Send every Monday
            days_ahead = 0 - now.weekday()  # Monday = 0
            if days_ahead <= 0:
                days_ahead += 7
            next_send = (now + timedelta(days=days_ahead)).replace(hour=hour, minute=minute, second=0, microsecond=0)
        elif self.frequency == "bi-weekly":
            # Send every two weeks
            days_ahead = 0 - now.weekday()
            if days_ahead <= 0:
                days_ahead += 14
            next_send = (now + timedelta(days=days_ahead)).replace(hour=hour, minute=minute, second=0, microsecond=0)
        elif self.frequency == "monthly":
            # Send on 1st of each month
            if now.day == 1 and now.hour < hour:
                next_send = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            else:
                # 1st of next month
                if now.month == 12:
                    next_send = datetime(now.year + 1, 1, 1, hour, minute)
                else:
                    next_send = datetime(now.year, now.month + 1, 1, hour, minute)
        else:
            # Default daily
            next_send = now.replace(hour=hour, minute=minute, second=0, microsecond=0) + timedelta(days=1)
        
        return next_send
    
    def update_next_send_time(self):
        """Update next send time"""
        self.next_send_at = self._calculate_next_send_time()
        self.updated_at = datetime.now()
    
    def mark_as_sent(self):
        """Mark as sent"""
        self.last_sent_at = datetime.now()
        self.total_sent += 1
        self.update_next_send_time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        # Convert datetime to ISO string
        datetime_fields = ['created_at', 'updated_at', 'last_sent_at', 'next_send_at', 'cancelled_at']
        for field in datetime_fields:
            if data.get(field):
                data[field] = getattr(self, field).isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Subscription':
        """Create instance from dictionary"""
        # Convert ISO string to datetime
        datetime_fields = ['created_at', 'updated_at', 'last_sent_at', 'next_send_at', 'cancelled_at']
        for field in datetime_fields:
            if data.get(field):
                data[field] = datetime.fromisoformat(data[field])
        
        return cls(**data)


class SubscriptionManager:
    """Subscription manager"""
    
    def __init__(self):
        self.subscriptions: Dict[str, Subscription] = {}
        self.email_subscriptions: Dict[str, str] = {}  # email -> subscription_id mapping
        logger.info("Subscription manager initialized")
    
    def create_subscription(
        self,
        user_id: str,
        email: str,
        name: str = "",
        frequency: str = "daily",
        preferred_time: str = "09:00",
        subscription_source: str = "web"
    ) -> Subscription:
        """Create new subscription"""
        # Check if subscription already exists
        existing_subscription = self.get_subscription_by_email(email)
        if existing_subscription:
            logger.warning(f"Email already has subscription: {email}")
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
        
        logger.info(f"Created subscription: {email} ({subscription.subscription_id})")
        return subscription
    
    def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Get subscription"""
        return self.subscriptions.get(subscription_id)
    
    def get_subscription_by_email(self, email: str) -> Optional[Subscription]:
        """Get subscription by email"""
        subscription_id = self.email_subscriptions.get(email)
        if subscription_id:
            return self.subscriptions.get(subscription_id)
        return None
    
    def get_user_subscriptions(self, user_id: str) -> List[Subscription]:
        """Get all subscriptions for user"""
        return [sub for sub in self.subscriptions.values() if sub.user_id == user_id]
    
    def update_subscription(
        self,
        subscription_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Subscription]:
        """Update subscription"""
        subscription = self.get_subscription(subscription_id)
        if not subscription:
            logger.warning(f"Subscription not found: {subscription_id}")
            return None
        
        # Update fields
        for key, value in updates.items():
            if hasattr(subscription, key):
                setattr(subscription, key, value)
        
        subscription.updated_at = datetime.now()
        
        # 如果更新了频率或时间，重新计算下次发送时间
        if 'frequency' in updates or 'preferred_time' in updates:
            subscription.update_next_send_time()
        
        logger.info(f"Updated subscription: {subscription_id}")
        return subscription
    
    def cancel_subscription(
        self,
        subscription_id: str,
        reason: str = ""
    ) -> bool:
        """Cancel subscription"""
        subscription = self.get_subscription(subscription_id)
        if not subscription:
            logger.warning(f"Subscription not found: {subscription_id}")
            return False
        
        subscription.is_active = False
        subscription.subscription_status = "cancelled"
        subscription.cancelled_at = datetime.now()
        subscription.cancellation_reason = reason
        subscription.updated_at = datetime.now()
        
        logger.info(f"Cancelled subscription: {subscription_id} (Reason: {reason})")
        return True
    
    def cancel_subscription_by_email(self, email: str, reason: str = "") -> bool:
        """Cancel subscription by email"""
        subscription = self.get_subscription_by_email(email)
        if subscription:
            return self.cancel_subscription(subscription.subscription_id, reason)
        return False
    
    def reactivate_subscription(self, subscription_id: str) -> bool:
        """Reactivate subscription"""
        subscription = self.get_subscription(subscription_id)
        if not subscription:
            return False
        
        subscription.is_active = True
        subscription.subscription_status = "active"
        subscription.cancelled_at = None
        subscription.cancellation_reason = ""
        subscription.updated_at = datetime.now()
        subscription.update_next_send_time()
        
        logger.info(f"Reactivated subscription: {subscription_id}")
        return True
    
    def pause_subscription(self, subscription_id: str) -> bool:
        """Pause subscription"""
        subscription = self.get_subscription(subscription_id)
        if not subscription:
            return False
        
        subscription.subscription_status = "paused"
        subscription.updated_at = datetime.now()
        
        logger.info(f"Paused subscription: {subscription_id}")
        return True
    
    def resume_subscription(self, subscription_id: str) -> bool:
        """Resume subscription"""
        subscription = self.get_subscription(subscription_id)
        if not subscription:
            return False
        
        subscription.subscription_status = "active"
        subscription.updated_at = datetime.now()
        subscription.update_next_send_time()
        
        logger.info(f"Resumed subscription: {subscription_id}")
        return True
    
    def get_pending_subscriptions(self, limit_time: Optional[datetime] = None) -> List[Subscription]:
        """Get pending subscriptions"""
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
        """Mark subscription as sent"""
        subscription = self.get_subscription(subscription_id)
        if not subscription:
            return False
        
        subscription.mark_as_sent()
        logger.info(f"Marked subscription as sent: {subscription_id}")
        return True
    
    def get_subscription_statistics(self) -> Dict[str, Any]:
        """Get subscription statistics"""
        total = len(self.subscriptions)
        active = len([s for s in self.subscriptions.values() if s.is_active])
        cancelled = len([s for s in self.subscriptions.values() if s.subscription_status == "cancelled"])
        paused = len([s for s in self.subscriptions.values() if s.subscription_status == "paused"])
        
        # Statistics by frequency
        frequency_stats = {}
        for subscription in self.subscriptions.values():
            freq = subscription.frequency
            frequency_stats[freq] = frequency_stats.get(freq, 0) + 1
        
        # Statistics by source
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
        """Export all subscription data"""
        data = {
            'subscriptions': [sub.to_dict() for sub in self.subscriptions.values()],
            'exported_at': datetime.now().isoformat(),
            'total_count': len(self.subscriptions)
        }
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    def import_subscriptions(self, data_json: str) -> int:
        """Import subscription data"""
        try:
            data = json.loads(data_json)
            imported_count = 0
            
            for sub_data in data.get('subscriptions', []):
                subscription = Subscription.from_dict(sub_data)
                self.subscriptions[subscription.subscription_id] = subscription
                self.email_subscriptions[subscription.email] = subscription.subscription_id
                imported_count += 1
            
            logger.info(f"Imported subscription data: {imported_count} subscriptions")
            return imported_count
            
        except Exception as e:
            logger.error(f"Failed to import subscription data: {e}")
            return 0
    
    def validate_subscription_data(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate subscription data"""
        errors = {}
        
        # Validate required fields
        required_fields = ['user_id', 'email']
        for field in required_fields:
            if field not in subscription_data or not subscription_data[field]:
                errors[field] = f"{field} is required"
        
        # Validate email format
        import re
        email = subscription_data.get('email', '')
        if email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            errors['email'] = "Invalid email format"
        
        # Validate frequency
        valid_frequencies = ['daily', 'weekly', 'bi-weekly', 'monthly']
        frequency = subscription_data.get('frequency', 'daily')
        if frequency not in valid_frequencies:
            errors['frequency'] = f"Frequency must be one of: {', '.join(valid_frequencies)}"
        
        # Validate time format
        preferred_time = subscription_data.get('preferred_time', '09:00')
        if not re.match(r'^\d{2}:\d{2}$', preferred_time):
            errors['preferred_time'] = "Time format must be HH:MM"
        
        return errors
    
    def get_unsubscribe_link(self, subscription_id: str, base_url: str = "http://localhost:7860") -> str:
        """Generate unsubscribe link"""
        return f"{base_url}/unsubscribe?subscription_id={subscription_id}"
    
    def get_manage_preferences_link(self, subscription_id: str, base_url: str = "http://localhost:7860") -> str:
        """Generate preferences management link"""
        return f"{base_url}/preferences?subscription_id={subscription_id}"
