# -*- coding: utf-8 -*-
"""
Newsletter Agent - 用户数据存储
用户偏好和订阅数据的持久化存储
"""

from typing import Dict, List, Any, Optional
import json
import os
from pathlib import Path
from datetime import datetime

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class UserDataStorage:
    """用户数据存储管理器"""
    
    def __init__(self, data_dir: Optional[str] = None):
        # 设置数据目录
        if data_dir is None:
            # 使用项目根目录下的user_data文件夹
            project_root = Path(__file__).parent.parent.parent.parent
            self.data_dir = project_root / "user_data"
        else:
            self.data_dir = Path(data_dir)
        
        # 创建必要的目录
        self.preferences_dir = self.data_dir / "preferences"
        self.subscriptions_dir = self.data_dir / "subscriptions"
        self.backups_dir = self.data_dir / "backups"
        
        self._ensure_directories()
        logger.info(f"用户数据存储初始化: {self.data_dir}")
    
    def _ensure_directories(self):
        """确保所有必要目录存在"""
        for directory in [self.data_dir, self.preferences_dir, self.subscriptions_dir, self.backups_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def save_user_preferences(self, user_id: str, preferences_data: Dict[str, Any]) -> bool:
        """保存用户偏好"""
        try:
            file_path = self.preferences_dir / f"{user_id}.json"
            
            # 添加保存时间戳
            preferences_data['saved_at'] = datetime.now().isoformat()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(preferences_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"保存用户偏好: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"保存用户偏好失败 {user_id}: {e}")
            return False
    
    def load_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """加载用户偏好"""
        try:
            file_path = self.preferences_dir / f"{user_id}.json"
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                preferences_data = json.load(f)
            
            logger.info(f"加载用户偏好: {user_id}")
            return preferences_data
            
        except Exception as e:
            logger.error(f"加载用户偏好失败 {user_id}: {e}")
            return None
    
    def delete_user_preferences(self, user_id: str) -> bool:
        """删除用户偏好"""
        try:
            file_path = self.preferences_dir / f"{user_id}.json"
            
            if file_path.exists():
                file_path.unlink()
                logger.info(f"删除用户偏好: {user_id}")
                return True
            else:
                logger.warning(f"用户偏好文件不存在: {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"删除用户偏好失败 {user_id}: {e}")
            return False
    
    def save_subscription(self, subscription_id: str, subscription_data: Dict[str, Any]) -> bool:
        """保存订阅数据"""
        try:
            file_path = self.subscriptions_dir / f"{subscription_id}.json"
            
            # 添加保存时间戳
            subscription_data['saved_at'] = datetime.now().isoformat()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(subscription_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"保存订阅数据: {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"保存订阅数据失败 {subscription_id}: {e}")
            return False
    
    def load_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """加载订阅数据"""
        try:
            file_path = self.subscriptions_dir / f"{subscription_id}.json"
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                subscription_data = json.load(f)
            
            logger.info(f"加载订阅数据: {subscription_id}")
            return subscription_data
            
        except Exception as e:
            logger.error(f"加载订阅数据失败 {subscription_id}: {e}")
            return None
    
    def delete_subscription(self, subscription_id: str) -> bool:
        """删除订阅数据"""
        try:
            file_path = self.subscriptions_dir / f"{subscription_id}.json"
            
            if file_path.exists():
                file_path.unlink()
                logger.info(f"删除订阅数据: {subscription_id}")
                return True
            else:
                logger.warning(f"订阅数据文件不存在: {subscription_id}")
                return False
                
        except Exception as e:
            logger.error(f"删除订阅数据失败 {subscription_id}: {e}")
            return False
    
    def list_all_users(self) -> List[str]:
        """列出所有用户ID"""
        try:
            user_ids = []
            for file_path in self.preferences_dir.glob("*.json"):
                user_id = file_path.stem  # 文件名（不含扩展名）
                user_ids.append(user_id)
            
            return user_ids
            
        except Exception as e:
            logger.error(f"列出用户失败: {e}")
            return []
    
    def list_all_subscriptions(self) -> List[str]:
        """列出所有订阅ID"""
        try:
            subscription_ids = []
            for file_path in self.subscriptions_dir.glob("*.json"):
                subscription_id = file_path.stem
                subscription_ids.append(subscription_id)
            
            return subscription_ids
            
        except Exception as e:
            logger.error(f"列出订阅失败: {e}")
            return []
    
    def create_backup(self, backup_name: Optional[str] = None) -> bool:
        """创建数据备份"""
        try:
            if backup_name is None:
                backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            backup_path = self.backups_dir / f"{backup_name}.json"
            
            # 收集所有数据
            backup_data = {
                'created_at': datetime.now().isoformat(),
                'preferences': {},
                'subscriptions': {}
            }
            
            # 备份用户偏好
            for user_id in self.list_all_users():
                preferences = self.load_user_preferences(user_id)
                if preferences:
                    backup_data['preferences'][user_id] = preferences
            
            # 备份订阅数据
            for subscription_id in self.list_all_subscriptions():
                subscription = self.load_subscription(subscription_id)
                if subscription:
                    backup_data['subscriptions'][subscription_id] = subscription
            
            # 保存备份文件
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"创建数据备份: {backup_name}")
            return True
            
        except Exception as e:
            logger.error(f"创建备份失败: {e}")
            return False
    
    def restore_backup(self, backup_name: str) -> bool:
        """恢复数据备份"""
        try:
            backup_path = self.backups_dir / f"{backup_name}.json"
            
            if not backup_path.exists():
                logger.error(f"备份文件不存在: {backup_name}")
                return False
            
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # 恢复用户偏好
            restored_preferences = 0
            for user_id, preferences in backup_data.get('preferences', {}).items():
                if self.save_user_preferences(user_id, preferences):
                    restored_preferences += 1
            
            # 恢复订阅数据
            restored_subscriptions = 0
            for subscription_id, subscription in backup_data.get('subscriptions', {}).items():
                if self.save_subscription(subscription_id, subscription):
                    restored_subscriptions += 1
            
            logger.info(f"恢复备份成功: {backup_name} (偏好: {restored_preferences}, 订阅: {restored_subscriptions})")
            return True
            
        except Exception as e:
            logger.error(f"恢复备份失败: {e}")
            return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """列出所有备份"""
        try:
            backups = []
            for file_path in self.backups_dir.glob("*.json"):
                backup_info = {
                    'name': file_path.stem,
                    'file_path': str(file_path),
                    'size': file_path.stat().st_size,
                    'created_at': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                }
                
                # 尝试读取备份的创建时间
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        backup_data = json.load(f)
                        if 'created_at' in backup_data:
                            backup_info['created_at'] = backup_data['created_at']
                        
                        # 添加统计信息
                        backup_info['preferences_count'] = len(backup_data.get('preferences', {}))
                        backup_info['subscriptions_count'] = len(backup_data.get('subscriptions', {}))
                except:
                    pass  # 忽略读取错误
                
                backups.append(backup_info)
            
            # 按创建时间倒序排列
            backups.sort(key=lambda x: x['created_at'], reverse=True)
            return backups
            
        except Exception as e:
            logger.error(f"列出备份失败: {e}")
            return []
    
    def get_storage_statistics(self) -> Dict[str, Any]:
        """获取存储统计信息"""
        try:
            users_count = len(self.list_all_users())
            subscriptions_count = len(self.list_all_subscriptions())
            backups_count = len(self.list_backups())
            
            # 计算目录大小
            def get_dir_size(path: Path) -> int:
                total_size = 0
                for file_path in path.rglob('*'):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
                return total_size
            
            preferences_size = get_dir_size(self.preferences_dir)
            subscriptions_size = get_dir_size(self.subscriptions_dir)
            backups_size = get_dir_size(self.backups_dir)
            total_size = preferences_size + subscriptions_size + backups_size
            
            return {
                'users_count': users_count,
                'subscriptions_count': subscriptions_count,
                'backups_count': backups_count,
                'storage_sizes': {
                    'preferences': preferences_size,
                    'subscriptions': subscriptions_size,
                    'backups': backups_size,
                    'total': total_size
                },
                'data_directory': str(self.data_dir),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取存储统计失败: {e}")
            return {}
    
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """清理旧备份文件"""
        try:
            backups = self.list_backups()
            
            if len(backups) <= keep_count:
                return 0
            
            # 删除多余的备份
            deleted_count = 0
            for backup in backups[keep_count:]:
                backup_path = Path(backup['file_path'])
                if backup_path.exists():
                    backup_path.unlink()
                    deleted_count += 1
            
            logger.info(f"清理旧备份: 删除 {deleted_count} 个文件")
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理备份失败: {e}")
            return 0
    
    def find_subscriptions_by_email(self, email: str) -> List[str]:
        """根据邮箱查找订阅ID"""
        try:
            subscription_ids = []
            
            for subscription_id in self.list_all_subscriptions():
                subscription_data = self.load_subscription(subscription_id)
                if subscription_data and subscription_data.get('email') == email:
                    subscription_ids.append(subscription_id)
            
            return subscription_ids
            
        except Exception as e:
            logger.error(f"查找订阅失败: {e}")
            return []
    
    def validate_data_integrity(self) -> Dict[str, Any]:
        """验证数据完整性"""
        try:
            results = {
                'preferences': {'valid': 0, 'invalid': 0, 'errors': []},
                'subscriptions': {'valid': 0, 'invalid': 0, 'errors': []},
                'checked_at': datetime.now().isoformat()
            }
            
            # 检查用户偏好文件
            for user_id in self.list_all_users():
                try:
                    preferences = self.load_user_preferences(user_id)
                    if preferences and isinstance(preferences, dict):
                        results['preferences']['valid'] += 1
                    else:
                        results['preferences']['invalid'] += 1
                        results['preferences']['errors'].append(f"无效的偏好数据: {user_id}")
                except Exception as e:
                    results['preferences']['invalid'] += 1
                    results['preferences']['errors'].append(f"读取失败 {user_id}: {str(e)}")
            
            # 检查订阅文件
            for subscription_id in self.list_all_subscriptions():
                try:
                    subscription = self.load_subscription(subscription_id)
                    if subscription and isinstance(subscription, dict):
                        results['subscriptions']['valid'] += 1
                    else:
                        results['subscriptions']['invalid'] += 1
                        results['subscriptions']['errors'].append(f"无效的订阅数据: {subscription_id}")
                except Exception as e:
                    results['subscriptions']['invalid'] += 1
                    results['subscriptions']['errors'].append(f"读取失败 {subscription_id}: {str(e)}")
            
            return results
            
        except Exception as e:
            logger.error(f"数据完整性验证失败: {e}")
            return {'error': str(e)} 