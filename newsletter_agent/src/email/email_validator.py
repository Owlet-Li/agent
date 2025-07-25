# -*- coding: utf-8 -*-
"""
Newsletter Agent - 邮件验证器
验证邮箱地址的有效性和格式
"""

import re
from typing import Dict, Any, Optional


class EmailValidator:
    """邮件验证器"""
    
    def __init__(self):
        # 基本邮箱正则表达式
        self.email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        
        # 常见的一次性邮箱域名（示例）
        self.disposable_domains = {
            '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
            'mailinator.com', 'yopmail.com', 'temp-mail.org'
        }
    
    def validate_email(self, email: str) -> Dict[str, Any]:
        """验证邮箱地址"""
        result = {
            'email': email,
            'is_valid': False,
            'errors': [],
            'warnings': []
        }
        
        if not email:
            result['errors'].append('邮箱地址不能为空')
            return result
        
        # 基本格式验证
        if not self.email_pattern.match(email):
            result['errors'].append('邮箱格式无效')
            return result
        
        # 检查域名
        domain = email.split('@')[1].lower()
        
        # 检查是否为一次性邮箱
        if domain in self.disposable_domains:
            result['warnings'].append('检测到一次性邮箱域名')
        
        # 检查常见的拼写错误
        common_domains = {
            'gmail.com': ['gmai.com', 'gmial.com', 'gmail.co'],
            'yahoo.com': ['yaho.com', 'yahooo.com', 'yahoo.co'],
            'outlook.com': ['outlok.com', 'outlook.co'],
            'hotmail.com': ['hotmai.com', 'hotmial.com']
        }
        
        for correct_domain, typos in common_domains.items():
            if domain in typos:
                result['warnings'].append(f'可能的拼写错误，您是否想输入 {correct_domain}？')
        
        # 如果没有错误，则标记为有效
        if not result['errors']:
            result['is_valid'] = True
        
        return result
    
    def validate_batch(self, emails: list) -> Dict[str, Any]:
        """批量验证邮箱"""
        results = []
        valid_count = 0
        
        for email in emails:
            validation = self.validate_email(email)
            results.append(validation)
            if validation['is_valid']:
                valid_count += 1
        
        return {
            'total': len(emails),
            'valid': valid_count,
            'invalid': len(emails) - valid_count,
            'results': results
        }
    
    def suggest_corrections(self, email: str) -> Optional[str]:
        """建议邮箱修正"""
        if not email or '@' not in email:
            return None
        
        domain = email.split('@')[1].lower()
        
        # 常见域名建议
        suggestions = {
            'gmai.com': 'gmail.com',
            'gmial.com': 'gmail.com',
            'gmail.co': 'gmail.com',
            'yaho.com': 'yahoo.com',
            'yahooo.com': 'yahoo.com',
            'yahoo.co': 'yahoo.com',
            'outlok.com': 'outlook.com',
            'outlook.co': 'outlook.com',
            'hotmai.com': 'hotmail.com',
            'hotmial.com': 'hotmail.com'
        }
        
        if domain in suggestions:
            username = email.split('@')[0]
            return f"{username}@{suggestions[domain]}"
        
        return None 