# 环境配置示例

## 创建 .env 文件

在项目根目录创建 `.env` 文件，参考以下配置：

```env
# Newsletter Agent 环境配置文件
# 必需配置 - 这些配置是系统运行的最低要求

# NewsAPI 配置 (必需)
# 获取地址: https://newsapi.org/
NEWSAPI_KEY=your_newsapi_key_here

# OpenAI API 配置 (必需，用于AI功能)
# 获取地址: https://platform.openai.com/
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1

# 可选配置 - 增强系统功能

# Reddit API 配置 (可选)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=newsletter_agent/1.0.0

# SendGrid 邮件服务配置 (可选)
SENDGRID_API_KEY=your_sendgrid_api_key
SENDGRID_FROM_EMAIL=newsletter@yourdomain.com

# 应用配置
APP_NAME=Newsletter Agent
APP_VERSION=1.0.0
DEBUG=false
CONTENT_LANGUAGE=zh
MAX_ARTICLES_PER_SOURCE=10
DEFAULT_TOPICS=科技,商业,健康
EMAIL_FROM=newsletter@yourdomain.com
EMAIL_SUBJECT=您的个性化新闻简报
```

## API 密钥获取步骤

### 1. NewsAPI (必需)
1. 访问 https://newsapi.org/
2. 点击 "Get API Key" 注册
3. 验证邮箱后获得免费API密钥
4. 免费版每日1000次请求

### 2. OpenAI API (必需)
1. 访问 https://platform.openai.com/
2. 注册并登录账户
3. 进入 API Keys 页面
4. 创建新的API密钥
5. 复制密钥到配置文件

### 3. Reddit API (可选)
1. 访问 https://www.reddit.com/prefs/apps
2. 点击 "Create App" 或 "Create Another App"
3. 选择 "script" 类型
4. 获取 client ID 和 client secret

### 4. SendGrid (可选)
1. 访问 https://sendgrid.com/
2. 注册免费账户
3. 验证邮箱和发件人身份
4. 创建API密钥
5. 设置发件人邮箱

## 最小配置示例

如果只想快速测试，最少只需要配置这两个：

```env
NEWSAPI_KEY=your_actual_newsapi_key
OPENAI_API_KEY=your_actual_openai_key
```

## 配置验证

启动应用后检查配置是否正确：

1. 查看启动日志是否有错误
2. 访问 Web 界面的"系统状态"页面
3. 检查各项服务的连接状态

## 常见配置问题

### 问题1: API密钥格式错误
- NewsAPI密钥通常是32位字符串
- OpenAI密钥以 "sk-" 开头

### 问题2: 网络访问限制
- 确保能访问相关API服务
- 检查防火墙和代理设置

### 问题3: 配额限制
- NewsAPI免费版有请求限制
- OpenAI API按使用量计费

### 问题4: 邮箱验证
- SendGrid需要验证发件人邮箱
- 检查垃圾邮件文件夹 