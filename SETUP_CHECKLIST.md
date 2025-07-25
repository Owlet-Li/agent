# Newsletter Agent 设置检查清单

## 📋 快速检查清单

### ✅ 环境准备
- [ ] Python 3.8+ 已安装 (`python --version`)
- [ ] Git 已安装 (`git --version`)
- [ ] 网络连接正常

### ✅ 项目设置
- [ ] 项目已克隆到本地
- [ ] 虚拟环境已创建并激活
- [ ] 依赖包已安装 (`pip install -r requirements.txt`)
- [ ] 项目目录结构正确

### ✅ 配置文件
- [ ] `.env` 文件已创建
- [ ] NewsAPI 密钥已配置且有效
- [ ] OpenAI API 密钥已配置且有效
- [ ] 可选服务已根据需要配置

### ✅ 启动测试
- [ ] 主程序能够启动 (`python main.py`)
- [ ] Web 界面可以访问 (http://localhost:7860)
- [ ] 系统状态检查通过
- [ ] 能够生成测试简报

---

## 🔍 详细检查步骤

### 1. 环境检查
```bash
# 检查 Python 版本
python --version
# 应该显示 Python 3.8+ 

# 检查 pip
pip --version

# 检查网络连接
ping google.com
```

### 2. 项目结构检查
确保以下文件和目录存在：
```
newsletter_agent/
├── main.py                 ✓
├── requirements.txt        ✓
├── .env                   ✓ (需要创建)
├── newsletter_agent/       ✓
│   ├── config/            ✓
│   ├── src/               ✓
│   └── tests/             ✓
├── logs/                  ✓ (自动创建)
├── cache/                 ✓ (自动创建)
└── output/                ✓ (自动创建)
```

### 3. 依赖安装检查
```bash
# 安装依赖
pip install -r requirements.txt

# 检查关键包
python -c "import gradio; print('Gradio OK')"
python -c "import requests; print('Requests OK')"
python -c "import openai; print('OpenAI OK')"
```

### 4. 配置验证
创建并检查 `.env` 文件：
```bash
# 检查文件是否存在
ls -la .env

# 检查内容格式
cat .env | grep -E "^[A-Z_]+=.+"
```

### 5. API 连接测试
```bash
# 启动项目
python main.py

# 观察启动日志，寻找：
# ✅ "环境配置检查完成"
# ✅ "可用数据源: NewsAPI"
# ✅ "AI功能密钥配置完整"
```

---

## 🚨 常见问题诊断

### 问题：ModuleNotFoundError
**症状**: `ModuleNotFoundError: No module named 'xxx'`
**解决**:
```bash
pip install -r requirements.txt
# 或者重新激活虚拟环境
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 问题：API 密钥错误
**症状**: `❌ 缺少核心数据源密钥`
**解决**:
1. 确认 `.env` 文件存在且格式正确
2. 检查 API 密钥是否有效
3. 确认没有多余的空格或引号

### 问题：端口占用
**症状**: `Port 7860 is already in use`
**解决**:
```bash
# 方法1: 找到并关闭占用进程
netstat -ano | findstr :7860  # Windows
lsof -i :7860                 # Linux/Mac

# 方法2: 使用其他端口
# 修改 main.py 中的端口号
```

### 问题：网络连接失败
**症状**: `Failed to connect to API`
**解决**:
1. 检查网络连接
2. 确认防火墙设置
3. 尝试使用代理或VPN

---

## 🧪 功能测试清单

### 基础功能测试
- [ ] 生成简报 (主题: "人工智能")
- [ ] 查看系统状态
- [ ] 切换不同格式 (HTML/Markdown)
- [ ] 测试不同风格和长度

### 高级功能测试 (如果已配置)
- [ ] Reddit 数据源连接
- [ ] 邮件发送功能
- [ ] 订阅管理功能
- [ ] 批量简报生成

### 性能测试
- [ ] 简报生成时间 < 2分钟
- [ ] Web 界面响应正常
- [ ] 日志文件正常生成
- [ ] 内存使用合理

---

## 📊 预期结果

### 成功启动标志
```
🚀 启动 Newsletter Agent v1.0.0
✅ 可用数据源: NewsAPI
✅ AI功能密钥配置完整
✅ 环境配置检查完成，应用可以启动
🎨 正在启动用户界面...
🌐 启动Web服务器 - http://localhost:7860
```

### 系统状态页面应显示
- ✅ NewsAPI: 连接正常
- ✅ OpenAI API: 服务可用
- ✅ 代理系统: 就绪
- 📊 工具数量: 8个
- 📈 可用功能: 100%

---

## 🔧 维护建议

### 定期检查
- [ ] 每周检查 API 使用量
- [ ] 每月更新依赖包
- [ ] 定期清理日志文件
- [ ] 备份配置文件

### 监控指标
- API 调用成功率 > 95%
- 简报生成时间 < 2分钟
- 系统内存使用 < 1GB
- 错误率 < 5%

---

**检查完成！如果所有项目都已勾选，您的 Newsletter Agent 就可以正常使用了。** 🎉 