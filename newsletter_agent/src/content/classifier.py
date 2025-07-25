# -*- coding: utf-8 -*-
"""
Newsletter Agent - 内容分类器
基于关键词和机器学习的智能分类功能
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class ContentClassifier:
    """内容分类器
    
    支持多种分类方法：
    1. 基于关键词的规则分类
    2. 基于机器学习的自动分类
    3. 混合分类方法
    """
    
    def __init__(self):
        """初始化分类器"""
        # 预定义分类和关键词
        self.category_keywords = {
            "科技": {
                "primary": ["科技", "技术", "AI", "人工智能", "机器学习", "深度学习", "算法", "数据", "云计算", "大数据"],
                "secondary": ["互联网", "软件", "硬件", "编程", "开发", "创新", "数字化", "智能", "自动化", "区块链"],
                "tertiary": ["手机", "电脑", "芯片", "处理器", "网络", "5G", "物联网", "虚拟现实", "增强现实"]
            },
            "财经": {
                "primary": ["经济", "金融", "银行", "股票", "投资", "基金", "证券", "货币", "汇率", "GDP"],
                "secondary": ["市场", "企业", "公司", "商业", "贸易", "财政", "税收", "通胀", "央行", "利率"],
                "tertiary": ["上市", "IPO", "并购", "融资", "估值", "财报", "营收", "利润", "债券", "期货"]
            },
            "政治": {
                "primary": ["政府", "政策", "法律", "法规", "国际", "外交", "选举", "议会", "国会", "总统"],
                "secondary": ["官员", "部长", "省长", "市长", "改革", "治理", "监管", "合规", "立法", "司法"],
                "tertiary": ["会议", "峰会", "谈判", "协议", "条约", "制裁", "关税", "签证", "移民", "难民"]
            },
            "体育": {
                "primary": ["体育", "运动", "比赛", "赛事", "锦标赛", "世界杯", "奥运", "奥运会", "冠军", "球员"],
                "secondary": ["足球", "篮球", "网球", "羽毛球", "乒乓球", "游泳", "田径", "体操", "举重", "拳击"],
                "tertiary": ["联赛", "球队", "教练", "训练", "转会", "合同", "伤病", "退役", "复出", "纪录"]
            },
            "娱乐": {
                "primary": ["娱乐", "电影", "电视", "音乐", "综艺", "明星", "演员", "歌手", "导演", "制片"],
                "secondary": ["票房", "收视率", "专辑", "演唱会", "颁奖", "首映", "拍摄", "制作", "发行", "宣传"],
                "tertiary": ["好莱坞", "奥斯卡", "金像奖", "金曲奖", "演出", "巡演", "粉丝", "红毯", "采访", "八卦"]
            },
            "健康": {
                "primary": ["健康", "医疗", "医院", "医生", "疾病", "病毒", "疫苗", "药物", "治疗", "诊断"],
                "secondary": ["养生", "保健", "营养", "运动", "心理", "精神", "康复", "护理", "急救", "手术"],
                "tertiary": ["症状", "预防", "筛查", "体检", "免疫", "传染", "流行病", "临床", "药品", "医保"]
            },
            "教育": {
                "primary": ["教育", "学校", "大学", "学院", "学生", "老师", "教师", "课程", "学习", "考试"],
                "secondary": ["招生", "录取", "毕业", "学位", "研究", "培训", "辅导", "补习", "在线教育", "远程教育"],
                "tertiary": ["高考", "中考", "托福", "雅思", "GRE", "论文", "学术", "科研", "奖学金", "助学金"]
            },
            "社会": {
                "primary": ["社会", "民生", "生活", "社区", "公益", "慈善", "志愿", "环境", "环保", "气候"],
                "secondary": ["住房", "房价", "租房", "交通", "出行", "就业", "失业", "养老", "医保", "社保"],
                "tertiary": ["人口", "户籍", "婚姻", "生育", "教育", "文化", "传统", "节日", "习俗", "风俗"]
            },
            "国际": {
                "primary": ["国际", "全球", "世界", "国外", "海外", "跨国", "多边", "双边", "联合国", "G7"],
                "secondary": ["美国", "欧洲", "亚洲", "非洲", "大洋洲", "中东", "拉美", "北约", "欧盟", "东盟"],
                "tertiary": ["贸易战", "制裁", "关税", "汇率", "石油", "天然气", "能源", "气候", "减排", "合作"]
            },
            "军事": {
                "primary": ["军事", "国防", "军队", "武器", "装备", "战争", "冲突", "军演", "演习", "安全"],
                "secondary": ["导弹", "战机", "军舰", "坦克", "雷达", "卫星", "核武器", "网络安全", "反恐", "维和"],
                "tertiary": ["军官", "士兵", "将军", "司令", "作战", "部署", "巡逻", "警戒", "情报", "间谍"]
            }
        }
        
        # 分类权重
        self.keyword_weights = {
            "primary": 3.0,
            "secondary": 2.0,
            "tertiary": 1.0
        }
        
        # 机器学习模型
        self.ml_model = None
        self.is_model_trained = False
        
        logger.info("内容分类器初始化完成")
    
    def calculate_keyword_score(self, text: str, keywords: List[str]) -> float:
        """计算关键词匹配分数"""
        if not text or not keywords:
            return 0.0
        
        text_lower = text.lower()
        score = 0.0
        
        for keyword in keywords:
            # 精确匹配
            if keyword.lower() in text_lower:
                score += 1.0
            
            # 部分匹配（对于较长的关键词）
            if len(keyword) > 2:
                words = keyword.lower().split()
                if len(words) > 1:
                    partial_matches = sum(1 for word in words if word in text_lower)
                    if partial_matches > 0:
                        score += partial_matches / len(words) * 0.5
        
        return score
    
    def classify_by_keywords(self, title: str, content: str, 
                           existing_keywords: Optional[List[str]] = None) -> Dict[str, Any]:
        """基于关键词进行分类
        
        Args:
            title: 文章标题
            content: 文章内容
            existing_keywords: 已提取的关键词
            
        Returns:
            分类结果
        """
        full_text = f"{title} {content}"
        if existing_keywords:
            full_text += " " + " ".join(existing_keywords)
        
        category_scores = {}
        
        for category, keyword_groups in self.category_keywords.items():
            total_score = 0.0
            
            for group_type, keywords in keyword_groups.items():
                group_score = self.calculate_keyword_score(full_text, keywords)
                weight = self.keyword_weights.get(group_type, 1.0)
                total_score += group_score * weight
            
            category_scores[category] = total_score
        
        # 找出得分最高的分类
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            best_score = category_scores[best_category]
            
            # 如果最高分数太低，归类为"综合"
            if best_score < 1.0:
                best_category = "综合"
                best_score = 0.0
            
            # 计算置信度
            total_score = sum(category_scores.values())
            confidence = best_score / total_score if total_score > 0 else 0.0
            
            return {
                "category": best_category,
                "confidence": confidence,
                "scores": category_scores,
                "method": "keywords"
            }
        
        return {
            "category": "综合",
            "confidence": 0.0,
            "scores": {},
            "method": "keywords"
        }
    
    def train_ml_model(self, training_data: List[Dict[str, Any]]) -> bool:
        """训练机器学习分类模型
        
        Args:
            training_data: 训练数据，每个元素包含 'text' 和 'category' 字段
            
        Returns:
            训练是否成功
        """
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn不可用，无法训练机器学习模型")
            return False
        
        if len(training_data) < 20:
            logger.warning("训练数据不足（少于20条），无法训练可靠的模型")
            return False
        
        try:
            # 准备训练数据
            texts = [item['text'] for item in training_data]
            categories = [item['category'] for item in training_data]
            
            # 检查类别分布
            category_counts = Counter(categories)
            if len(category_counts) < 2:
                logger.warning("训练数据类别不足（少于2个类别）")
                return False
            
            # 创建机器学习管道
            self.ml_model = Pipeline([
                ('tfidf', TfidfVectorizer(
                    max_features=5000,
                    ngram_range=(1, 2),
                    min_df=2,
                    max_df=0.95,
                    stop_words=None  # 我们已经在预处理中处理了停用词
                )),
                ('classifier', MultinomialNB(alpha=0.1))
            ])
            
            # 训练模型
            self.ml_model.fit(texts, categories)
            self.is_model_trained = True
            
            logger.info(f"机器学习分类模型训练完成，使用了 {len(training_data)} 条数据")
            logger.info(f"类别分布: {dict(category_counts)}")
            
            return True
            
        except Exception as e:
            logger.error(f"机器学习模型训练失败: {e}")
            return False
    
    def classify_by_ml(self, title: str, content: str) -> Dict[str, Any]:
        """基于机器学习模型进行分类
        
        Args:
            title: 文章标题
            content: 文章内容
            
        Returns:
            分类结果
        """
        if not self.is_model_trained or not self.ml_model:
            return {
                "category": "综合",
                "confidence": 0.0,
                "probabilities": {},
                "method": "ml_not_available"
            }
        
        try:
            full_text = f"{title} {content}"
            
            # 预测分类
            predicted_category = self.ml_model.predict([full_text])[0]
            
            # 获取预测概率
            probabilities = self.ml_model.predict_proba([full_text])[0]
            classes = self.ml_model.classes_
            
            prob_dict = dict(zip(classes, probabilities))
            confidence = max(probabilities)
            
            return {
                "category": predicted_category,
                "confidence": confidence,
                "probabilities": prob_dict,
                "method": "ml"
            }
            
        except Exception as e:
            logger.error(f"机器学习分类失败: {e}")
            return {
                "category": "综合",
                "confidence": 0.0,
                "probabilities": {},
                "method": "ml_error"
            }
    
    def classify_hybrid(self, title: str, content: str, 
                       existing_keywords: Optional[List[str]] = None,
                       ml_weight: float = 0.6) -> Dict[str, Any]:
        """混合分类方法
        
        结合关键词分类和机器学习分类的结果
        
        Args:
            title: 文章标题
            content: 文章内容
            existing_keywords: 已提取的关键词
            ml_weight: 机器学习结果的权重 (0-1)
            
        Returns:
            分类结果
        """
        keyword_result = self.classify_by_keywords(title, content, existing_keywords)
        ml_result = self.classify_by_ml(title, content)
        
        keyword_weight = 1.0 - ml_weight
        
        # 如果机器学习模型不可用，使用关键词分类结果
        if not self.is_model_trained:
            return keyword_result
        
        # 合并分类结果
        if keyword_result["category"] == ml_result["category"]:
            # 两种方法结果一致，提高置信度
            combined_confidence = min(1.0, keyword_result["confidence"] + ml_result["confidence"] * 0.3)
            return {
                "category": keyword_result["category"],
                "confidence": combined_confidence,
                "keyword_result": keyword_result,
                "ml_result": ml_result,
                "method": "hybrid_consistent"
            }
        else:
            # 结果不一致，按权重选择
            if ml_result["confidence"] * ml_weight > keyword_result["confidence"] * keyword_weight:
                selected_result = ml_result
                method = "hybrid_ml_preferred"
            else:
                selected_result = keyword_result
                method = "hybrid_keyword_preferred"
            
            return {
                "category": selected_result["category"],
                "confidence": selected_result["confidence"] * 0.8,  # 降低置信度
                "keyword_result": keyword_result,
                "ml_result": ml_result,
                "method": method
            }
    
    def classify_content(self, content_item: Dict[str, Any], 
                        classification_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """对单个内容项进行分类
        
        Args:
            content_item: 内容项
            classification_options: 分类选项
            
        Returns:
            分类结果
        """
        # 默认分类选项
        default_options = {
            "method": "hybrid",  # keywords, ml, hybrid
            "ml_weight": 0.6,
            "use_existing_keywords": True,
            "fallback_category": "综合"
        }
        
        if classification_options:
            default_options.update(classification_options)
        
        title = content_item.get("title", "")
        content = content_item.get("content", "")
        keywords = content_item.get("keywords", []) if default_options["use_existing_keywords"] else None
        
        # 根据选择的方法进行分类
        if default_options["method"] == "keywords":
            result = self.classify_by_keywords(title, content, keywords)
        elif default_options["method"] == "ml":
            result = self.classify_by_ml(title, content)
        else:  # hybrid
            result = self.classify_hybrid(title, content, keywords, default_options["ml_weight"])
        
        # 如果分类失败，使用默认分类
        if not result or result["category"] == "综合" and result["confidence"] == 0.0:
            result = {
                "category": default_options["fallback_category"],
                "confidence": 0.1,
                "method": "fallback"
            }
        
        return result
    
    def batch_classify(self, content_items: List[Dict[str, Any]], 
                      classification_options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """批量分类内容
        
        Args:
            content_items: 内容项列表
            classification_options: 分类选项
            
        Returns:
            分类结果列表
        """
        results = []
        
        for item in content_items:
            try:
                result = self.classify_content(item, classification_options)
                results.append({
                    "content": item,
                    "classification": result
                })
            except Exception as e:
                logger.error(f"内容分类失败: {e}")
                results.append({
                    "content": item,
                    "classification": {
                        "category": "综合",
                        "confidence": 0.0,
                        "method": "error",
                        "error": str(e)
                    }
                })
        
        return results
    
    def get_classification_statistics(self, classified_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """获取分类统计信息
        
        Args:
            classified_results: 分类结果列表
            
        Returns:
            统计信息
        """
        if not classified_results:
            return {
                "total_items": 0,
                "category_distribution": {},
                "average_confidence": 0.0,
                "method_distribution": {}
            }
        
        categories = [result["classification"]["category"] for result in classified_results]
        confidences = [result["classification"]["confidence"] for result in classified_results]
        methods = [result["classification"]["method"] for result in classified_results]
        
        category_counts = Counter(categories)
        method_counts = Counter(methods)
        
        return {
            "total_items": len(classified_results),
            "category_distribution": dict(category_counts),
            "average_confidence": sum(confidences) / len(confidences) if confidences else 0.0,
            "method_distribution": dict(method_counts),
            "confidence_by_category": {
                category: sum(conf for result, conf in zip(classified_results, confidences) 
                            if result["classification"]["category"] == category) / count
                for category, count in category_counts.items()
            }
        }
    
    def add_custom_category(self, category_name: str, keywords: Dict[str, List[str]]):
        """添加自定义分类
        
        Args:
            category_name: 分类名称
            keywords: 关键词字典，格式同 self.category_keywords
        """
        self.category_keywords[category_name] = keywords
        logger.info(f"添加自定义分类: {category_name}")
    
    def update_category_keywords(self, category_name: str, new_keywords: Dict[str, List[str]]):
        """更新分类关键词
        
        Args:
            category_name: 分类名称
            new_keywords: 新的关键词字典
        """
        if category_name in self.category_keywords:
            for group_type, keywords in new_keywords.items():
                if group_type in self.category_keywords[category_name]:
                    # 合并关键词，去重
                    existing = set(self.category_keywords[category_name][group_type])
                    new = set(keywords)
                    self.category_keywords[category_name][group_type] = list(existing | new)
                else:
                    self.category_keywords[category_name][group_type] = keywords
            
            logger.info(f"更新分类关键词: {category_name}")
        else:
            logger.warning(f"分类不存在: {category_name}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "ml_model_trained": self.is_model_trained,
            "sklearn_available": SKLEARN_AVAILABLE,
            "available_categories": list(self.category_keywords.keys()),
            "total_keywords": sum(
                len(keywords) for category_keywords in self.category_keywords.values()
                for keywords in category_keywords.values()
            )
        } 