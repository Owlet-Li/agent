# -*- coding: utf-8 -*-
"""
Newsletter Agent - 文本预处理器
智能文本清洗、分词、去噪和标准化
"""

import re
import html
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse

try:
    import jieba
    import jieba.posseg as pseg
    import jieba.analyse
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False

try:
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer, WordNetLemmatizer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

try:
    from langdetect import detect, LangDetectError
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class TextProcessor:
    """智能文本预处理器
    
    支持中英文文本处理，包括清洗、分词、去噪、标准化等功能
    """
    
    def __init__(self):
        """初始化文本处理器"""
        self.chinese_stopwords = self._load_chinese_stopwords()
        self.english_stopwords = self._load_english_stopwords()
        
        # 编译常用正则表达式以提高性能
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(\+\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}')
        self.html_tag_pattern = re.compile(r'<[^>]+>')
        self.multiple_spaces_pattern = re.compile(r'\s+')
        self.chinese_punctuation = '，。！？；：""''（）【】《》〈〉—…·'
        self.english_punctuation = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
        
        # 表情符号和特殊字符
        self.emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # 表情符号
            "\U0001F300-\U0001F5FF"  # 符号和象形文字
            "\U0001F680-\U0001F6FF"  # 运输和地图符号
            "\U0001F1E0-\U0001F1FF"  # 国旗
            "\U00002700-\U000027BF"  # 装饰符号
            "\U0001f926-\U0001f937"
            "\U00010000-\U0010ffff"
            "\u2640-\u2642"
            "\u2600-\u2B55"
            "\u200d"
            "\u23cf"
            "\u23e9"
            "\u231a"
            "\ufe0f"  # dingbats
            "\u3030"
            "]+", flags=re.UNICODE
        )
        
        logger.info("文本处理器初始化完成")
    
    def _load_chinese_stopwords(self) -> set:
        """加载中文停用词"""
        stopwords_list = [
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很',
            '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '能', '他',
            '这个', '来', '用', '第', '样', '时', '还', '把', '被', '让', '将', '做', '或者', '等', '可以',
            '什么', '怎么', '只是', '如果', '因为', '所以', '但是', '而且', '然后', '虽然', '不过', '的话',
            '比如', '例如', '包括', '根据', '由于', '关于', '对于', '至于', '除了', '另外', '此外', '而言'
        ]
        return set(stopwords_list)
    
    def _load_english_stopwords(self) -> set:
        """加载英文停用词"""
        if NLTK_AVAILABLE:
            try:
                return set(stopwords.words('english'))
            except LookupError:
                logger.warning("NLTK停用词数据未下载，使用默认停用词列表")
        
        # 默认英文停用词
        default_stopwords = [
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
            'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
            'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
            'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
            'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
            'while', 'of', 'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after',
            'above', 'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
            'further', 'then', 'once'
        ]
        return set(default_stopwords)
    
    def detect_language(self, text: str) -> str:
        """检测文本语言"""
        if not text or not text.strip():
            return "unknown"
            
        if not LANGDETECT_AVAILABLE:
            # 简单的中英文检测
            chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
            english_chars = len(re.findall(r'[a-zA-Z]', text))
            total_chars = chinese_chars + english_chars
            
            if total_chars == 0:
                return "unknown"
            
            if chinese_chars / total_chars > 0.5:
                return "zh"
            elif english_chars / total_chars > 0.5:
                return "en"
            else:
                return "mixed"
        
        try:
            return detect(text)
        except (LangDetectError, Exception):
            return "unknown"
    
    def clean_html(self, text: str) -> str:
        """清理HTML标签和实体"""
        if not text:
            return ""
        
        # 解码HTML实体
        text = html.unescape(text)
        
        # 移除HTML标签
        text = self.html_tag_pattern.sub(' ', text)
        
        return text
    
    def remove_urls(self, text: str) -> str:
        """移除URL链接"""
        if not text:
            return ""
        
        text = self.url_pattern.sub(' ', text)
        return text
    
    def remove_emails(self, text: str) -> str:
        """移除邮箱地址"""
        if not text:
            return ""
        
        text = self.email_pattern.sub(' ', text)
        return text
    
    def remove_phone_numbers(self, text: str) -> str:
        """移除电话号码"""
        if not text:
            return ""
        
        text = self.phone_pattern.sub(' ', text)
        return text
    
    def remove_emojis(self, text: str) -> str:
        """移除表情符号"""
        if not text:
            return ""
        
        text = self.emoji_pattern.sub(' ', text)
        return text
    
    def normalize_whitespace(self, text: str) -> str:
        """标准化空白字符"""
        if not text:
            return ""
        
        # 将多个空白字符替换为单个空格
        text = self.multiple_spaces_pattern.sub(' ', text)
        
        # 去除首尾空白
        text = text.strip()
        
        return text
    
    def remove_punctuation(self, text: str, keep_chinese: bool = True) -> str:
        """移除标点符号
        
        Args:
            text: 输入文本
            keep_chinese: 是否保留中文标点符号
        """
        if not text:
            return ""
        
        # 移除英文标点符号
        for char in self.english_punctuation:
            text = text.replace(char, ' ')
        
        # 根据参数决定是否移除中文标点符号
        if not keep_chinese:
            for char in self.chinese_punctuation:
                text = text.replace(char, ' ')
        
        return self.normalize_whitespace(text)
    
    def tokenize_chinese(self, text: str) -> List[str]:
        """中文分词"""
        if not text or not JIEBA_AVAILABLE:
            # 简单的字符分割作为后备方案
            return list(text.replace(' ', ''))
        
        tokens = list(jieba.cut(text, cut_all=False))
        return [token.strip() for token in tokens if token.strip()]
    
    def tokenize_english(self, text: str) -> List[str]:
        """英文分词"""
        if not text:
            return []
        
        if NLTK_AVAILABLE:
            try:
                return word_tokenize(text.lower())
            except LookupError:
                logger.warning("NLTK分词数据未下载，使用简单分词")
        
        # 简单的空格分词
        return text.lower().split()
    
    def remove_stopwords(self, tokens: List[str], language: str = "auto") -> List[str]:
        """移除停用词
        
        Args:
            tokens: 词汇列表
            language: 语言类型 ("zh", "en", "auto")
        """
        if not tokens:
            return []
        
        if language == "auto":
            # 自动检测语言
            sample_text = " ".join(tokens[:10])
            language = self.detect_language(sample_text)
        
        if language.startswith("zh") or language == "mixed":
            stopwords_set = self.chinese_stopwords
        elif language.startswith("en"):
            stopwords_set = self.english_stopwords
        else:
            # 未知语言，使用中英文停用词的并集
            stopwords_set = self.chinese_stopwords | self.english_stopwords
        
        return [token for token in tokens if token.lower() not in stopwords_set]
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """提取关键词"""
        if not text or not JIEBA_AVAILABLE:
            return []
        
        try:
            keywords = jieba.analyse.extract_tags(text, topK=top_n, withWeight=False)
            return keywords
        except Exception as e:
            logger.warning(f"关键词提取失败: {e}")
            return []
    
    def preprocess_text(self, text: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """完整的文本预处理流程
        
        Args:
            text: 输入文本
            options: 处理选项
        
        Returns:
            处理结果字典
        """
        if not text:
            return {
                "original": "",
                "cleaned": "",
                "tokens": [],
                "keywords": [],
                "language": "unknown",
                "length": 0
            }
        
        # 默认选项
        default_options = {
            "remove_html": True,
            "remove_urls": True,
            "remove_emails": True,
            "remove_phone": True,
            "remove_emojis": True,
            "remove_punctuation": False,
            "keep_chinese_punctuation": True,
            "remove_stopwords": True,
            "extract_keywords": True,
            "max_keywords": 10
        }
        
        if options:
            default_options.update(options)
        
        original_text = text
        processed_text = text
        
        # 检测语言
        language = self.detect_language(processed_text)
        
        # 应用各种清洗步骤
        if default_options["remove_html"]:
            processed_text = self.clean_html(processed_text)
        
        if default_options["remove_urls"]:
            processed_text = self.remove_urls(processed_text)
        
        if default_options["remove_emails"]:
            processed_text = self.remove_emails(processed_text)
        
        if default_options["remove_phone"]:
            processed_text = self.remove_phone_numbers(processed_text)
        
        if default_options["remove_emojis"]:
            processed_text = self.remove_emojis(processed_text)
        
        if default_options["remove_punctuation"]:
            processed_text = self.remove_punctuation(
                processed_text, 
                keep_chinese=default_options["keep_chinese_punctuation"]
            )
        
        # 标准化空白字符
        processed_text = self.normalize_whitespace(processed_text)
        
        # 分词
        if language.startswith("zh") or language == "mixed":
            tokens = self.tokenize_chinese(processed_text)
        else:
            tokens = self.tokenize_english(processed_text)
        
        # 移除停用词
        if default_options["remove_stopwords"]:
            tokens = self.remove_stopwords(tokens, language)
        
        # 提取关键词
        keywords = []
        if default_options["extract_keywords"]:
            keywords = self.extract_keywords(original_text, default_options["max_keywords"])
        
        return {
            "original": original_text,
            "cleaned": processed_text,
            "tokens": tokens,
            "keywords": keywords,
            "language": language,
            "length": len(processed_text),
            "token_count": len(tokens),
            "keyword_count": len(keywords)
        }
    
    def batch_preprocess(self, texts: List[str], options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """批量文本预处理"""
        results = []
        
        for text in texts:
            try:
                result = self.preprocess_text(text, options)
                results.append(result)
            except Exception as e:
                logger.error(f"文本预处理失败: {e}")
                results.append({
                    "original": text,
                    "cleaned": "",
                    "tokens": [],
                    "keywords": [],
                    "language": "unknown",
                    "length": 0,
                    "error": str(e)
                })
        
        return results 