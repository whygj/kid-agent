# Phase 5: Docker + Systemd + 部署 + 生产配置

你是 Kid Agent（少年助手）项目的开发者。项目已完成 Phase 1-4，现在需要完成最终的部署和生产化。

## 项目路径
`~/projects/kid-agent/`

## 已有架构
- Python 3.10+ 项目，无框架依赖（纯 openai + httpx）
- FastAPI web server（src/web/app.py）
- CLI + Web 双模式（src/main.py）
- SQLite 数据库（src/memory/store.py）
- edge-tts 语音
- 微信公众号集成（src/wechat/）
- 223 个测试全通过
- requirements.txt 已有所有依赖

## Phase 5 需要完成的任务

### 5.1 Docker 化
创建以下文件：

**Dockerfile**（多阶段构建，精简镜像）:
```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .
EXPOSE 8000
CMD ["python3", "-m", "src.main", "--mode", "web", "--port", "8000", "--host", "0.0.0.0"]
```

**docker-compose.yml**:
- kid-agent 服务
- volumes: ./data（SQLite持久化）, ./config（配置）
- environment 从 config/.env 加载
- restart: unless-stopped
- healthcheck

**.dockerignore**:
- 排除 .venv, __pycache__, .git, tests, *.pyc

### 5.2 Systemd 服务
创建 `deploy/kid-agent.service`:
```ini
[Unit]
Description=Kid Agent - AI Math Tutor
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/kid-agent
ExecStart=/opt/kid-agent/.venv/bin/python3 -m src.main --mode web --port 8000 --host 0.0.0.0
Restart=always
RestartSec=5
Environment=PYTHONPATH=/opt/kid-agent
EnvironmentFile=/opt/kid-agent/config/.env

[Install]
WantedBy=multi-user.target
```

### 5.3 Nginx 反向代理配置
创建 `deploy/nginx-kid-agent.conf`:
- proxy_pass to 127.0.0.1:8000
- WebSocket upgrade support（/ws 路径）
- 静态文件直接 serve
- SSL 占位（Let's Encrypt）

### 5.4 部署脚本
创建 `scripts/deploy.sh`:
- 安装依赖
- 创建 systemd 服务
- 启动服务
- 健康检查
- 回滚功能

### 5.5 生产配置
修改 `src/config/settings.py`（如果还没有）：
- 添加 ProductionConfig vs DevelopmentConfig
- CORS 配置（生产环境限制域名）
- 日志级别可配置
- 数据库路径可配置（Docker vs 本地）

创建 `config/.env.production` 模板（不含真实密钥，只有占位说明）

### 5.6 监控和健康
创建 `src/web/health.py`:
- /health 基本健康检查
- /health/detailed 详细状态（DB连接、API可用性、磁盘空间）
- Prometheus metrics 格式输出（/metrics）

### 5.7 测试
创建/更新测试：
- `tests/test_deploy.py` — 测试 Dockerfile 能构建、docker-compose 配置正确、systemd 文件格式正确
- `tests/test_health.py` — 测试 /health 和 /health/detailed 端点
- 确保所有现有测试继续通过

### 5.8 文档
创建 `docs/DEPLOY.md`:
- Docker 部署步骤
- Systemd 部署步骤
- Nginx 配置步骤
- 环境变量说明
- 微信公众号配置步骤

更新 `README.md`:
- 项目简介
- 快速开始
- 部署方式（Docker/Systemd）
- API 文档概要

## 约束
- 不要修改 src/agent/, src/engine/, src/knowledge/ 中的核心逻辑
- 不要引入新的运行时依赖（部署工具如 Docker 除外）
- requirements.txt 只能添加 testing/deploy 相关的可选依赖
- 所有测试必须通过（223 现有 + 新增）
- main.py 需要支持 --host 参数（Docker 需要绑定 0.0.0.0）

## 完成后
1. 运行 `pytest tests/ -v` 确保全部通过
2. 输出完整的文件变更清单
3. 输出最终测试结果
