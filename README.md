# Newsletter Agent - 智能新闻简报生成系统

Newsletter Agent 是一个基于 AI 驱动的智能新闻简报生成系统，能够自动收集、分析和生成个性化的新闻简报。

## 🚀 项目特性

- **多数据源聚合**: 支持 NewsAPI、Reddit、RSS 等多种数据源
- **AI 智能分析**: 使用 OpenAI API 进行内容分析和生成
- **个性化定制**: 根据用户偏好生成定制化简报
- **邮件发送**: 通过 SendGrid 自动发送邮件简报
- **Web 界面**: 基于 Gradio 的友好用户界面
- **内容处理**: 智能去重、分类、摘要等功能

## 📋 系统要求

- Python 3.8 或更高版本
- 稳定的网络连接（用于 API 调用）
- 至少 2GB 可用内存

## 🔧 安装与配置

### 1. 克隆项目

```bash
git clone <repository-url>
cd newsletter-agent
```

### 2. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 环境配置

在项目根目录创建 `.env` 文件，配置以下环境变量：

```env
# 必需配置
NEWSAPI_KEY=your_newsapi_key_here
OPENAI_API_KEY=your_openai_api_key_here

# 可选配置
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
SENDGRID_API_KEY=your_sendgrid_api_key
SENDGRID_FROM_EMAIL=your_sender_email@example.com

# 应用配置
DEBUG=false
APP_NAME=Newsletter Agent
APP_VERSION=1.0.0
CONTENT_LANGUAGE=zh
MAX_ARTICLES_PER_SOURCE=10
```

## 🔑 API 密钥获取指南

### NewsAPI (必需)
1. 访问 [NewsAPI.org](https://newsapi.org/)
2. 注册免费账户
3. 获取 API 密钥并添加到 `.env` 文件

### OpenAI API (必需用于 AI 功能)
1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 创建 API 密钥
3. 添加到 `.env` 文件

### Reddit API (可选)
1. 访问 [Reddit Apps](https://www.reddit.com/prefs/apps)
2. 创建新应用程序
3. 获取 client ID 和 client secret

### SendGrid (可选，用于邮件发送)
1. 访问 [SendGrid](https://sendgrid.com/)
2. 创建账户并验证
3. 生成 API 密钥

## 🏃‍♂️ 运行项目

### 启动主程序

```bash
python main.py
```

启动成功后，您将看到类似以下输出：

```
🚀 启动 Newsletter Agent v1.0.0
✅ 环境配置检查完成，应用可以启动
🎨 正在启动用户界面...
🌐 启动Web服务器 - http://localhost:7860
```

### 访问 Web 界面

打开浏览器访问：http://localhost:7860

## 🎯 使用指南

### 1. 生成新闻简报

在 Web 界面中：

1. **输入主题**: 在"主题或关键词"框中输入您感兴趣的话题
2. **选择风格**: 选择写作风格（专业、休闲、学术、创意）
3. **设置长度**: 选择内容长度（短、中、长）
4. **定义受众**: 选择目标受众（通用、技术、商业、学术）
5. **点击生成**: 点击"生成完整简报"按钮

### 2. 订阅管理

如果配置了邮件服务：

1. 输入邮箱地址和姓名
2. 选择接收频率（每日、每周）
3. 选择感兴趣的分类
4. 勾选"发送邮件"选项

### 3. 系统状态检查

使用"系统状态"选项卡查看：
- 数据源连接状态
- AI 服务可用性
- 邮件服务配置
- 系统统计信息

## 🧪 测试运行

运行集成测试确保系统正常工作：

```bash
# 测试第四阶段功能（AI 代理）
python test_stage_4.py

# 完整集成测试
python test_final_integration.py
```

## 🛠️ 故障排除

### 常见问题

1. **导入错误**
   ```
   ModuleNotFoundError: No module named 'xxx'
   ```
   解决方案：确保已安装所有依赖 `pip install -r requirements.txt`

2. **API 密钥错误**
   ```
   ❌ 缺少核心数据源密钥: NEWSAPI_KEY
   ```
   解决方案：检查 `.env` 文件配置，确保 API 密钥正确

3. **网络连接问题**
   ```
   Failed to connect to API
   ```
   解决方案：检查网络连接和防火墙设置

4. **端口占用**
   ```
   Port 7860 is already in use
   ```
   解决方案：修改 `main.py` 中的端口号或关闭占用进程

### 日志文件

查看日志获取详细错误信息：
- 日志位置：`logs/newsletter_agent.log`
- 包含详细的错误堆栈和调试信息

### 降级模式

如果某些 API 不可用，系统会自动进入降级模式：
- 没有 OpenAI API：AI 功能将不可用，但数据收集仍可正常工作
- 没有 Reddit API：只使用 NewsAPI 和 RSS 源
- 没有 SendGrid：简报生成正常，但无法发送邮件

## 📁 项目结构

```
newsletter_agent/
├── main.py                 # 主入口文件
├── requirements.txt        # 依赖列表
├── .env                   # 环境配置（需要创建）
├── newsletter_agent/
│   ├── config/            # 配置模块
│   ├── src/
│   │   ├── agents/        # AI 代理
│   │   ├── data_sources/  # 数据源
│   │   ├── content/       # 内容处理
│   │   ├── tools/         # AI 工具
│   │   ├── templates/     # 模板系统
│   │   ├── email/         # 邮件服务
│   │   ├── user/          # 用户管理
│   │   └── ui/            # 用户界面
│   └── tests/             # 测试文件
├── logs/                  # 日志文件
├── cache/                 # 缓存文件
└── output/                # 输出文件
```

## 🔄 更新项目

```bash
# 拉取最新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt --upgrade

# 重启应用
python main.py
```

## 📝 配置说明

### 高级配置选项

在 `.env` 文件中可配置的其他选项：

```env
# OpenAI 配置
OPENAI_API_BASE=https://api.openai.com/v1  # 可替换为其他兼容服务

# Reddit 配置
REDDIT_USER_AGENT=newsletter_agent/1.0.0

# 内容配置
DEFAULT_TOPICS=科技,商业,健康
MAX_ARTICLES_PER_SOURCE=10
CONTENT_LANGUAGE=zh

# 邮件配置
EMAIL_FROM=newsletter@yourdomain.com
EMAIL_SUBJECT=您的个性化新闻简报
```

## 🤝 支持

如果遇到问题：

1. 检查日志文件获取详细错误信息
2. 确认所有 API 密钥配置正确
3. 验证网络连接正常
4. 运行测试脚本诊断问题

## 📄 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

---

**祝您使用愉快！如有问题，请查看日志文件或联系技术支持。** 