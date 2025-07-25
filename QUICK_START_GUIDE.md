# Newsletter Agent 快速启动指南

## ⚡ 5分钟快速启动

### 1. 环境准备
```bash
# 克隆项目
git clone <repository-url>
cd newsletter-agent

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 最小配置
创建 `.env` 文件，仅配置必需的 API 密钥：

```env
# 必需 - 获取新闻数据
NEWSAPI_KEY=your_newsapi_key_here

# 必需 - AI 功能
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. 启动运行
```bash
python main.py
```

### 4. 访问界面
打开浏览器访问：http://localhost:7860

---

## 🎯 第一次使用

1. **生成简报**：
   - 在"主题"框输入："人工智能"
   - 点击"生成完整简报"
   - 等待 30-60 秒

2. **查看结果**：
   - 在"简报内容"区域查看生成的简报
   - 切换到"Markdown格式"查看不同格式

3. **系统状态**：
   - 点击"系统状态"选项卡
   - 检查各项服务状态

---

## 🔧 常见问题快速解决

### 问题1: 找不到模块
```bash
pip install -r requirements.txt
```

### 问题2: API 密钥错误
- 检查 `.env` 文件是否存在
- 确认 API 密钥格式正确
- 访问 [NewsAPI](https://newsapi.org/) 获取免费密钥

### 问题3: 端口被占用
修改 `main.py` 第 154 行的端口号：
```python
app.launch(server_port=7861)  # 改为其他端口
```

### 问题4: 生成失败
- 检查网络连接
- 查看 `logs/newsletter_agent.log` 文件
- 确认 API 配额未用完

---

## 📊 功能演示建议

### 演示1: 基础简报生成
- 主题："科技新闻"
- 风格：专业
- 长度：中等

### 演示2: 个性化设置
- 主题："区块链"
- 风格：休闲
- 受众：技术

### 演示3: 系统功能
- 查看系统状态
- 测试数据源连接
- 查看生成统计

---

## 🚀 进阶配置

配置可选服务以获得完整体验：

```env
# Reddit 数据源
REDDIT_CLIENT_ID=your_reddit_id
REDDIT_CLIENT_SECRET=your_reddit_secret

# 邮件服务
SENDGRID_API_KEY=your_sendgrid_key
SENDGRID_FROM_EMAIL=newsletter@yourdomain.com
```

---

**完整文档请参考 [README.md](README.md)** 