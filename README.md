# 少年助手（Kid Agent）

> 专属孩子的AI成长伙伴 — 小学3-5年级数学教学 AI Agent

## 项目简介

Kid Agent 是一款基于大语言模型的小学数学教学助手，为3-5年级学生提供个性化学习体验：

- **自适应出题** - 根据学生水平自动调整题目难度
- **智能评分** - AI 分析错误原因并提供针对性反馈
- **学习诊断** - 识别知识薄弱点，生成个性化学习计划
- **艾宾浩斯复习** - 基于遗忘曲线智能安排复习
- **游戏化激励** - XP经验值、等级系统、连续答对奖励
- **多端支持** - 命令行、Web界面、微信公众号

## 技术栈

- **后端** - Python 3.12 + FastAPI
- **LLM** - 智谱 GLM-4 / DeepSeek
- **数据库** - SQLite
- **语音** - Edge-TTS + Web Speech API
- **前端** - 原生 HTML/JS（儿童友好界面）

## 快速开始

### 本地运行

```bash
# 克隆项目
git clone <repository-url>
cd kid-agent

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp config/.env.production config/.env
# 编辑 config/.env，填入你的 API 密钥

# 命令行模式
python src/main.py --mode cli --student <学生名>

# Web 模式
python src/main.py --mode web --port 8000
```

### Docker 部署

```bash
# 配置环境变量
cp config/.env.production config/.env
# 编辑 config/.env

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f kid-agent

# 健康检查
curl http://localhost:8000/health
```

## 部署方式

### 生产环境部署

详细的部署指南请参考 [docs/DEPLOY.md](./docs/DEPLOY.md)

**支持两种部署方式：**

1. **Docker 部署**（推荐）
   ```bash
   docker-compose up -d
   ```

2. **Systemd 部署**
   ```bash
   sudo ./scripts/deploy.sh install
   sudo systemctl start kid-agent
   ```

### Nginx 反向代理

使用提供的 Nginx 配置文件：

```bash
sudo cp deploy/nginx-kid-agent.conf /etc/nginx/sites-available/kid-agent
sudo ln -s /etc/nginx/sites-available/kid-agent /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

## API 文档

启动 Web 服务后，访问以下地址查看 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 监控和健康检查

### 健康检查端点

```bash
# 基础健康检查
curl http://localhost:8000/health

# 详细健康检查
curl http://localhost:8000/health/detailed

# Prometheus 指标
curl http://localhost:8000/metrics
```

### Prometheus 监控

可用的指标：

- `kid_agent_uptime_seconds` - 应用运行时间
- `kid_agent_health_status` - 健康状态
- `kid_agent_database_size_bytes` - 数据库大小
- `kid_agent_disk_percent_used` - 磁盘使用率

## 项目阶段

| Phase | 内容 | 状态 |
|-------|------|------|
| Phase 1 | 命令行版教学Agent | ✅ 完成 |
| Phase 2 | FastAPI Web API + WebSocket聊天 | ✅ 完成 |
| Phase 3 | 语音交互 (Web Speech API + Edge-TTS) | ✅ 完成 |
| Phase 4 | 微信公众号接入 + 家长通知系统 | ✅ 完成 |
| Phase 5 | Docker + Systemd + 部署 + 生产配置 | ✅ 完成 |

## 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_deploy.py -v
pytest tests/test_health.py -v

# 集成测试（需要API配置）
python tests/integration.py
```

## 目录结构

```
kid-agent/
├── src/
│   ├── agent/      # 核心Agent逻辑
│   ├── engine/     # 四大引擎（出题/判题/诊断/讲解）
│   ├── knowledge/  # 知识体系
│   ├── memory/     # 持久化
│   ├── web/        # Web API和前端
│   ├── config/     # 配置管理
│   └── utils/      # 工具函数
├── config/
│   └── .env.production  # 生产环境配置模板
├── deploy/
│   ├── kid-agent.service   # Systemd服务配置
│   └── nginx-kid-agent.conf  # Nginx配置
├── docs/
│   └── DEPLOY.md   # 部署文档
├── scripts/
│   └── deploy.sh   # 部署脚本
├── tests/          # 测试文件
├── Dockerfile      # Docker构建文件
├── docker-compose.yml
└── README.md
```

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `ENVIRONMENT` | 运行环境 | `development` |
| `LOG_LEVEL` | 日志级别 | `INFO` |
| `LLM_PROVIDER` | LLM提供商 | `glm` |
| `GLM_API_KEY` | 智谱GLM API密钥 | - |
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | - |
| `DB_PATH` | 数据库路径 | `./data/kid_agent.db` |
| `WECHAT_APP_ID` | 微信AppID | - |
| `WECHAT_APP_SECRET` | 微信AppSecret | - |
| `CORS_ORIGINS` | CORS允许的源 | `*` |

详细配置请参考 [config/.env.production](./config/.env.production)

## 文档

- [部署指南](./docs/DEPLOY.md)
- [设计文档](./DESIGN.md)
- [API 文档](http://localhost:8000/docs)

## License

MIT License
