# 📰 Newsletter Agent - 智能新闻简报生成系统

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-Latest-green.svg)
![Gradio](https://img.shields.io/badge/Gradio-UI-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

*基于AI技术的自动化新闻简报生成系统*

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [使用指南](#-使用指南) • [代码结构](#-代码结构) • [API文档](#-api-文档)

</div>

---

## 🌟 项目概述

Newsletter Agent 是一个基于人工智能的智能新闻简报生成系统，能够自动从多个数据源收集信息，使用大语言模型进行内容分析和生成，最终产出个性化的新闻简报。

### 💡 核心亮点

- 🤖 **智能AI代理** - 基于LangChain构建的多步骤推理代理
- 🔍 **多源数据集成** - 整合NewsAPI、Reddit、RSS等多个信息源  
- ✍️ **个性化生成** - 支持多种写作风格和目标受众定制
- 🎨 **现代化界面** - 基于Gradio的直观Web界面
- 📱 **多格式输出** - 支持HTML和Markdown格式导出
- 🔧 **模块化设计** - 高度可扩展的架构设计

### 🎯 适用场景

- 📊 **企业资讯监控** - 自动生成行业动态简报
- 🎓 **学术研究辅助** - 快速了解领域最新发展
- 📈 **投资决策支持** - 获取市场趋势和商业洞察
- 📱 **个人信息订阅** - 定制化的新闻摘要服务

---

## 🚀 功能特性

### 🧠 AI智能代理
- **多步骤推理** - 自动规划研究和生成流程
- **工具集成** - 内置8+专业工具（新闻搜索、内容分析、摘要生成等）
- **对话交互** - 支持自然语言交互和指令执行
- **上下文记忆** - 维护完整的对话历史和上下文

### 📡 数据源集成
- **NewsAPI** - 来自80,000+新闻源的实时新闻
- **Reddit API** - 社区讨论和热门话题
- **RSS解析** - 支持各种RSS源的内容获取
- **内容去重** - 智能去除重复和相似内容

### 📝 内容处理
- **智能分类** - 自动识别新闻类别（科技、商业、健康等）
- **关键词提取** - 基于TF-IDF和NLP技术
- **质量评估** - 自动评估内容质量和相关性
- **格式化** - 统一的内容结构和格式

### 🎨 用户界面
- **直观操作** - 简洁易用的Web界面
- **实时预览** - HTML和Markdown双格式预览
- **参数定制** - 丰富的个性化选项
- **状态监控** - 实时显示系统状态和处理进度

---

## 🛠️ 技术栈

### 🔧 核心框架
- **Python 3.8+** - 主要编程语言
- **LangChain** - AI代理框架和工具集成
- **Gradio** - Web界面框架
- **Pydantic** - 数据验证和设置管理

### 🤖 AI & NLP
- **OpenAI API** - 大语言模型服务
- **LangChain OpenAI** - OpenAI集成
- **jieba** - 中文分词和关键词提取
- **scikit-learn** - 机器学习算法

### 📊 数据处理
- **requests** - HTTP请求库
- **feedparser** - RSS解析
- **BeautifulSoup4** - HTML解析
- **PRAW** - Reddit API客户端

### 📝 内容生成
- **Jinja2** - 模板引擎
- **Markdown** - 标记语言支持
- **python-dotenv** - 环境变量管理

---

## ⚡ 快速开始

### 📋 环境要求

- Python 3.8 或更高版本
- 稳定的网络连接
- NewsAPI密钥（免费）
- OpenAI API密钥

### 🔧 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/your-username/newsletter-agent.git
cd newsletter-agent
```

2. **创建虚拟环境**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux  
source .venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **快速配置**
```bash
python quick_start.py
```

或手动创建 `.env` 文件：
```env
# 必需配置
NEWSAPI_KEY=your_newsapi_key_here
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1

# 可选配置
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
```

5. **启动应用**
```bash
python main.py
```

6. **访问界面**
   
   打开浏览器访问：http://localhost:7860

### 🔑 获取API密钥

#### NewsAPI (必需)
1. 访问 [NewsAPI.org](https://newsapi.org/)
2. 注册免费账户
3. 获取API密钥（每日1000次免费请求）

#### OpenAI API (必需)
1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 创建账户并获取API密钥
3. 确保账户有足够余额

#### Reddit API (可选)
1. 访问 [Reddit App Preferences](https://www.reddit.com/prefs/apps)
2. 创建新应用程序
3. 获取Client ID和Client Secret

---

## 📖 使用指南

### 🎯 基本使用流程

1. **选择主题** - 在简报主题输入框中输入感兴趣的话题
   ```
   示例：人工智能最新发展、新能源汽车市场动态、区块链技术应用
   ```

2. **设置偏好**
   - **写作风格**：专业(professional)、休闲(casual)、学术(academic)、创意(creative)
   - **内容长度**：短(short)、中(medium)、长(long)
   - **目标受众**：通用(general)、技术(tech)、商业(business)、学术(academic)

3. **选择分类** - 勾选关注的内容分类
   ```
   科技、商业、健康、娱乐、体育、政治、教育
   ```

4. **生成简报** - 点击"生成简报"按钮开始创建

5. **查看结果** - 在HTML预览或Markdown标签页中查看生成的简报

### 🔧 高级功能

#### 🤖 命令行交互
```python
from newsletter_agent.src.agents import create_newsletter_agent

# 创建代理
agent = create_newsletter_agent()

# 生成简报
result = agent.generate_newsletter(
    topic="人工智能",
    style="professional", 
    audience="tech",
    length="medium"
)

print(result['message'])
```

#### 📊 批量处理
```python
from newsletter_agent.src.tools.data_source_tools import get_all_tools

# 获取数据源工具
tools = get_all_tools()

# 批量搜索新闻
news_tool = tools[0]  # NewsSearchTool
result = news_tool._run("机器学习")
```

#### 🎨 自定义模板
```python
from newsletter_agent.src.templates.newsletter_templates import NewsletterTemplateEngine

# 创建模板引擎
engine = NewsletterTemplateEngine()

# 生成自定义格式简报
newsletter = engine.generate_newsletter(
    data=newsletter_data,
    template_style="creative",
    output_format="html"
)
```

### 💡 最佳实践

#### 📝 主题选择建议
- ✅ **具体明确**：`人工智能在医疗领域的应用` 
- ❌ **过于宽泛**：`技术`
- ✅ **时效性强**：`2024年新能源汽车政策变化`
- ❌ **过于陈旧**：`互联网发展史`

#### 🎯 风格选择指南
- **专业风格**：适合企业内部报告、行业分析
- **休闲风格**：适合个人阅读、社交分享  
- **学术风格**：适合研究报告、论文参考
- **创意风格**：适合营销内容、创意写作

#### 📊 分类筛选技巧
- 选择2-3个相关分类效果最佳
- 过多分类可能导致内容分散
- 根据目标受众选择合适分类

---

## 📁 代码结构

```
newsletter-agent/
├── 📄 main.py                    # 🚀 主入口文件
├── 📄 quick_start.py             # ⚡ 快速启动脚本  
├── 📄 test_fixes.py              # 🧪 测试验证脚本
├── 📄 requirements.txt           # 📦 依赖配置文件
├── 📄 .env                       # 🔑 环境变量配置
├── 📄 .gitignore                 # 🚫 Git忽略文件
└── 📁 newsletter_agent/          # 📦 主要代码目录
    ├── 📁 config/                # ⚙️ 配置模块
    │   └── 📄 settings.py        # 🔧 应用设置
    ├── 📁 src/                   # 💻 源代码目录
    │   ├── 📁 agents/            # 🤖 AI代理模块
    │   │   ├── 📄 __init__.py
    │   │   ├── 📄 newsletter_agent.py    # 核心代理类
    │   │   └── 📄 prompts.py             # 提示模板
    │   ├── 📁 tools/             # 🔧 工具集合
    │   │   ├── 📄 __init__.py
    │   │   ├── 📄 ai_generation_tools.py    # AI生成工具
    │   │   └── 📄 data_source_tools.py      # 数据源工具
    │   ├── 📁 data_sources/      # 📡 数据源模块
    │   │   ├── 📄 __init__.py
    │   │   ├── 📄 aggregator.py          # 数据聚合器
    │   │   ├── 📄 news_api.py            # NewsAPI客户端
    │   │   ├── 📄 reddit_api.py          # Reddit API客户端
    │   │   └── 📄 rss_parser.py          # RSS解析器
    │   ├── 📁 content/           # 📝 内容处理模块
    │   │   ├── 📄 __init__.py
    │   │   ├── 📄 text_processor.py      # 文本处理器
    │   │   ├── 📄 content_formatter.py   # 内容格式化器
    │   │   ├── 📄 deduplicator.py        # 去重器
    │   │   └── 📄 classifier.py          # 分类器
    │   ├── 📁 templates/         # 🎨 模板系统
    │   │   ├── 📄 __init__.py
    │   │   ├── 📄 newsletter_templates.py   # 简报模板
    │   │   ├── 📄 email_templates.py        # 邮件模板
    │   │   └── 📄 formatting_utils.py       # 格式化工具
    │   ├── 📁 ui/                # 🎨 用户界面
    │   │   ├── 📄 __init__.py
    │   │   └── 📄 app.py                # Gradio应用
    │   ├── 📁 user/              # 👥 用户管理
    │   │   ├── 📄 __init__.py
    │   │   ├── 📄 preferences.py        # 用户偏好
    │   │   ├── 📄 subscription.py       # 订阅管理
    │   │   └── 📄 storage.py            # 数据存储
    │   └── 📁 email/             # 📧 邮件系统 (已移除)
    │       ├── 📄 __init__.py
    │       ├── 📄 sendgrid_client.py    # SendGrid客户端
    │       ├── 📄 email_scheduler.py    # 邮件调度器
    │       └── 📄 email_validator.py    # 邮件验证器
    └── 📁 tests/                 # 🧪 测试模块
        ├── 📄 __init__.py
        └── 📄 test_config.py
```

### 🏗️ 架构说明

#### 🤖 Agent Layer (代理层)
```
NewsletterAgent
├── LLM Integration (语言模型集成)
├── Tool Management (工具管理)
├── Conversation History (对话历史)
└── Decision Making (决策逻辑)
```

#### 🔧 Tools Layer (工具层)
```
AI Generation Tools          Data Source Tools
├── NewsletterGenerationTool ├── NewsSearchTool
├── ContentSummaryTool       ├── TrendingTopicsTool  
├── HeadlineGenerationTool   ├── ContentAnalysisTool
└── ContentEnhancementTool   └── TopicResearchTool
```

#### 📊 Data Layer (数据层)
```
Data Sources                 Content Processing
├── NewsAPI Client          ├── Text Processor
├── Reddit API Client       ├── Content Formatter
├── RSS Parser              ├── Deduplicator
└── Data Aggregator         └── Classifier
```

#### 🎨 Presentation Layer (展示层)
```
User Interface              Templates
├── Gradio Web App          ├── Newsletter Templates
├── Status Dashboard        ├── Email Templates
├── Configuration Panel     └── Formatting Utils
└── Real-time Preview
```

---

## 🔧 配置说明

### 📋 环境变量

| 变量名 | 必需 | 说明 | 默认值 |
|--------|------|------|--------|
| `NEWSAPI_KEY` | ✅ | NewsAPI密钥 | - |
| `OPENAI_API_KEY` | ✅ | OpenAI API密钥 | - |
| `OPENAI_API_BASE` | ❌ | OpenAI API基础URL | `https://api.openai.com/v1` |
| `REDDIT_CLIENT_ID` | ❌ | Reddit客户端ID | - |
| `REDDIT_CLIENT_SECRET` | ❌ | Reddit客户端密钥 | - |
| `REDDIT_USER_AGENT` | ❌ | Reddit用户代理 | `newsletter_agent/1.0.0` |
| `DEBUG` | ❌ | 调试模式 | `false` |
| `CONTENT_LANGUAGE` | ❌ | 内容语言 | `zh` |
| `MAX_ARTICLES_PER_SOURCE` | ❌ | 每个源的最大文章数 | `10` |

### ⚙️ 应用配置

```python
# newsletter_agent/config/settings.py
class Settings:
    APP_NAME: str = "Newsletter Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API配置
    NEWSAPI_KEY: str = ""
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    
    # 内容配置
    MAX_ARTICLES_PER_SOURCE: int = 10
    CONTENT_LANGUAGE: str = "zh"
    DEFAULT_TOPICS: list = ["科技", "商业", "健康"]
```

---

## 🔍 API文档

### 🤖 核心代理API

#### 创建代理
```python
from newsletter_agent.src.agents import create_newsletter_agent

agent = create_newsletter_agent(
    api_key="your_openai_key",           # 可选
    api_base="https://api.openai.com/v1" # 可选
)
```

#### 生成简报
```python
result = agent.generate_newsletter(
    topic="人工智能最新发展",        # 简报主题
    style="professional",           # 写作风格
    audience="tech",               # 目标受众  
    length="medium"                # 内容长度
)

print(result['message'])  # 生成的简报内容
```

#### 主题研究
```python
research = agent.research_topic(
    topic="量子计算",              # 研究主题
    depth="deep"                  # 研究深度: light/medium/deep
)
```

#### 内容分析
```python
analysis = agent.analyze_content(
    content="要分析的文本内容..."   # 待分析内容
)
```

### 🔧 工具API

#### 数据源工具
```python
from newsletter_agent.src.tools.data_source_tools import get_all_tools

tools = get_all_tools()

# 新闻搜索
news_tool = tools[0]  # NewsSearchTool
result = news_tool._run("机器学习")

# 热门话题
trending_tool = tools[1]  # TrendingTopicsTool  
topics = trending_tool._run("tech")
```

#### AI生成工具
```python
from newsletter_agent.src.tools.ai_generation_tools import get_ai_tools

ai_tools = get_ai_tools()

# 内容摘要
summary_tool = ai_tools[1]  # ContentSummaryTool
summary = summary_tool._run("长文本内容...")

# 标题生成
headline_tool = ai_tools[2]  # HeadlineGenerationTool
headlines = headline_tool._run("文章内容...")
```

### 📊 数据源API

#### 新闻数据
```python
from newsletter_agent.src.data_sources.news_api import news_client

# 搜索新闻
articles = news_client.search_everything(
    query="人工智能",
    language="en",
    page_size=10
)

# 获取头条
headlines = news_client.get_top_headlines(
    category="technology",
    country="us"
)
```

#### Reddit数据
```python
from newsletter_agent.src.data_sources.reddit_api import reddit_client

# 获取热门帖子
posts = reddit_client.get_hot_posts(
    subreddit_name="technology",
    limit=10
)

# 搜索帖子
search_results = reddit_client.search_posts(
    query="machine learning",
    subreddit_name="MachineLearning"
)
```

---

## 🐛 故障排除

### 常见问题

#### ❌ API密钥错误
```
Error: 401 Unauthorized
```
**解决方案**：
- 检查 `.env` 文件中的API密钥是否正确
- 确认OpenAI账户余额充足
- 验证NewsAPI密钥有效性

#### ❌ 模块导入失败
```
ImportError: No module named 'langchain'
```
**解决方案**：
```bash
pip install -r requirements.txt
```

#### ❌ 404错误
```
Error code: 404 - {'error': {'message': 'Not Found'}}
```
**解决方案**：
- 检查 `OPENAI_API_BASE` 配置
- 确认模型名称正确
- 验证网络连接

#### ❌ 端口占用
```
OSError: [Errno 48] Address already in use
```
**解决方案**：
```bash
# 查找占用进程
lsof -i :7860
# 或更改端口
python main.py --port 7861
```

### 🔧 调试模式

启用调试模式获取更多信息：
```bash
# 设置环境变量
export DEBUG=true
# 或在.env文件中设置
DEBUG=true

# 运行应用
python main.py
```

### 📝 日志查看

查看详细日志：
```bash
# 日志文件位置
tail -f logs/newsletter_agent.log

# 或实时查看
python main.py 2>&1 | tee debug.log
```

---

## 🤝 贡献指南

我们欢迎各种形式的贡献！

### 📋 贡献方式

- 🐛 **报告Bug** - 通过Issues报告问题
- 💡 **提出建议** - 分享您的想法和建议  
- 📝 **改进文档** - 帮助完善文档
- 💻 **提交代码** - 修复bug或添加新功能
- 🌐 **翻译** - 帮助翻译界面和文档

### 🔄 开发流程

1. **Fork仓库**
```bash
git clone https://github.com/your-username/newsletter-agent.git
cd newsletter-agent
```

2. **创建分支**
```bash
git checkout -b feature/your-feature-name
```

3. **开发环境设置**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 如果存在
```

4. **提交更改**
```bash
git add .
git commit -m "feat: add your feature description"
git push origin feature/your-feature-name
```

5. **创建Pull Request**

### 📏 代码规范

- 遵循PEP 8代码风格
- 添加适当的注释和文档字符串
- 编写单元测试
- 确保所有测试通过

### 🧪 测试

运行测试确保代码质量：
```bash
# 运行修复验证测试
python test_fixes.py

# 运行单元测试（如果存在）
python -m pytest tests/
```

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain) - 强大的AI应用开发框架
- [Gradio](https://github.com/gradio-app/gradio) - 易用的ML界面构建工具  
- [OpenAI](https://openai.com/) - 提供强大的语言模型服务
- [NewsAPI](https://newsapi.org/) - 全球新闻数据服务
- [Reddit](https://www.reddit.com/dev/api/) - 社区数据平台

---

## 📞 联系我们

- 📧 **邮箱**: [your-email@example.com](mailto:your-email@example.com)
- 🐛 **问题反馈**: [GitHub Issues](https://github.com/your-username/newsletter-agent/issues)
- 💬 **讨论交流**: [GitHub Discussions](https://github.com/your-username/newsletter-agent/discussions)

---

## 🔮 未来规划

- [ ] 📱 移动端适配
- [ ] 🌍 多语言支持
- [ ] 📊 高级分析仪表板
- [ ] 🔄 定时任务调度
- [ ] 📧 邮件订阅恢复
- [ ] 🎨 更多模板主题
- [ ] 🤖 更多AI模型支持
- [ ] 📈 性能优化

---

<div align="center">

**🎉 开始使用Newsletter Agent，体验AI驱动的智能新闻简报生成！**

⭐ 如果觉得有用，请给我们一个Star！ ⭐

</div> 