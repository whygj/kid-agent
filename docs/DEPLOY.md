# Kid Agent 部署指南

本文档介绍如何将 Kid Agent 部署到生产环境。

## 目录

- [部署方式](#部署方式)
- [Docker 部署](#docker-部署)
- [Systemd 部署](#systemd-部署)
- [Nginx 反向代理](#nginx-反向代理)
- [环境变量配置](#环境变量配置)
- [微信公众号配置](#微信公众号配置)
- [监控和健康检查](#监控和健康检查)
- [故障排查](#故障排查)

---

## 部署方式

Kid Agent 支持两种部署方式：

1. **Docker 部署** - 推荐用于容器化环境，易于管理和扩展
2. **Systemd 部署** - 适用于传统 Linux 服务器

---

## Docker 部署

### 前置要求

- Docker 20.10+
- Docker Compose 1.29+

### 快速开始

1. **克隆项目并进入目录**
   ```bash
   cd ~/projects/kid-agent
   ```

2. **创建配置文件**
   ```bash
   cp config/.env.production config/.env
   ```

3. **编辑配置文件**
   ```bash
   nano config/.env
   ```

   必须配置的变量：
   ```bash
   # GLM API 密钥（或使用 DeepSeek）
   GLM_API_KEY=your_api_key_here

   # 环境设置
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   ```

4. **启动服务**
   ```bash
   docker-compose up -d
   ```

5. **检查服务状态**
   ```bash
   docker-compose ps
   docker-compose logs -f kid-agent
   ```

6. **健康检查**
   ```bash
   curl http://localhost:8000/health
   ```

### Docker 常用命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f kid-agent

# 进入容器
docker-compose exec kid-agent bash

# 更新镜像
docker-compose pull
docker-compose up -d

# 备份数据
cp data/kid_agent.db data/kid_agent.db.backup
```

### 数据持久化

以下目录通过 volume 挂载持久化数据：

- `./data` - SQLite 数据库
- `./config` - 配置文件（包括 .env）

请定期备份数据目录。

---

## Systemd 部署

### 前置要求

- Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- Python 3.10+
- sudo 权限

### 自动部署

使用提供的部署脚本：

```bash
cd ~/projects/kid-agent
sudo ./scripts/deploy.sh install
```

脚本会自动：
1. 创建 `kidagent` 用户
2. 安装到 `/opt/kid-agent`
3. 创建 Python 虚拟环境
4. 安装依赖
5. 创建 systemd 服务
6. 创建必要的目录

### 手动部署

如果需要手动部署：

1. **创建用户**
   ```bash
   sudo useradd -r -s /bin/bash -d /opt/kid-agent kidagent
   sudo mkdir -p /opt/kid-agent
   sudo chown kidagent:kidagent /opt/kid-agent
   ```

2. **复制项目文件**
   ```bash
   sudo rsync -av \
     --exclude='.venv' \
     --exclude='.git' \
     --exclude='__pycache__' \
     --exclude='data' \
     ~/projects/kid-agent/ /opt/kid-agent/
   ```

3. **创建虚拟环境**
   ```bash
   sudo -u kidagent python3 -m venv /opt/kid-agent/.venv
   ```

4. **安装依赖**
   ```bash
   sudo -u kidagent /opt/kid-agent/.venv/bin/pip install \
     --upgrade pip
   sudo -u kidagent /opt/kid-agent/.venv/bin/pip install \
     -r /opt/kid-agent/requirements.txt
   ```

5. **配置环境变量**
   ```bash
   sudo -u kidagent cp /opt/kid-agent/config/.env.production \
     /opt/kid-agent/config/.env
   sudo -u kidagent nano /opt/kid-agent/config/.env
   ```

6. **安装 systemd 服务**
   ```bash
   sudo cp /opt/kid-agent/deploy/kid-agent.service \
     /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable kid-agent
   ```

7. **启动服务**
   ```bash
   sudo systemctl start kid-agent
   ```

### Systemd 管理命令

```bash
# 查看状态
sudo systemctl status kid-agent

# 启动服务
sudo systemctl start kid-agent

# 停止服务
sudo systemctl stop kid-agent

# 重启服务
sudo systemctl restart kid-agent

# 查看日志
sudo journalctl -u kid-agent -f

# 健康检查
./scripts/deploy.sh health

# 备份
./scripts/deploy.sh backup

# 回滚
./scripts/deploy.sh rollback
```

---

## Nginx 反向代理

使用 Nginx 作为反向代理可以提供以下好处：
- SSL/TLS 加密
- 静态文件缓存
- 负载均衡（多实例）
- 安全加固

### 安装 Nginx

```bash
sudo apt update
sudo apt install nginx -y  # Ubuntu/Debian
# 或
sudo yum install nginx -y    # CentOS/RHEL
```

### 配置

1. **复制配置文件**
   ```bash
   sudo cp /opt/kid-agent/deploy/nginx-kid-agent.conf \
     /etc/nginx/sites-available/kid-agent
   ```

2. **编辑配置文件**
   ```bash
   sudo nano /etc/nginx/sites-available/kid-agent
   ```

   修改 `server_name` 为你的域名：
   ```nginx
   server_name your-domain.com;
   ```

3. **启用站点**
   ```bash
   sudo ln -s /etc/nginx/sites-available/kid-agent \
     /etc/nginx/sites-enabled/
   ```

4. **测试配置**
   ```bash
   sudo nginx -t
   ```

5. **重启 Nginx**
   ```bash
   sudo systemctl restart nginx
   ```

### 配置 HTTPS（Let's Encrypt）

1. **安装 Certbot**
   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   ```

2. **获取证书**
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

3. **自动续期**
   ```bash
   sudo certbot renew --dry-run
   ```

Certbot 会自动配置 Nginx 使用 HTTPS。

### Nginx 配置说明

Nginx 配置包含以下部分：

- `/ws` - WebSocket 端点（实时聊天）
- `/api` - REST API 端点
- `/wechat` - 微信公众号 Webhook
- `/health` - 健康检查端点
- `/metrics` - Prometheus 监控指标
- `/static` - 静态文件

---

## 环境变量配置

### 完整配置列表

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `ENVIRONMENT` | 运行环境 | `development` | 否 |
| `LOG_LEVEL` | 日志级别 | `INFO` | 否 |
| `LLM_PROVIDER` | LLM 提供商 | `glm` | 否 |
| `GLM_API_KEY` | 智谱 GLM API 密钥 | - | 是* |
| `GLM_API_BASE` | GLM API 地址 | `https://open.bigmodel.cn/api/paas/v4` | 否 |
| `GLM_MODEL` | GLM 模型名称 | `glm-4` | 否 |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | - | 是* |
| `DEEPSEEK_API_BASE` | DeepSeek API 地址 | `https://api.deepseek.com/v1` | 否 |
| `DEEPSEEK_MODEL` | DeepSeek 模型名称 | `deepseek-chat` | 否 |
| `DB_PATH` | 数据库路径 | `./data/kid_agent.db` | 否 |
| `TTS_PROVIDER` | TTS 提供商 | `edge` | 否 |
| `TTS_VOICE` | TTS 语音 | `zh-CN-XiaoxiaoNeural` | 否 |
| `TTS_AUTO_PLAY` | 自动播放语音 | `true` | 否 |
| `WECHAT_APP_ID` | 微信 AppID | - | 否 |
| `WECHAT_APP_SECRET` | 微信 AppSecret | - | 否 |
| `WECHAT_TOKEN` | 微信 Token | `kidagent2024` | 否 |
| `WECHAT_ENCODING_AES_KEY` | 微信 AES Key | - | 否 |
| `CORS_ORIGINS` | CORS 允许的源 | `*` | 否 |

* 至少需要配置一个 LLM 提供商的 API 密钥。

### 生产环境建议

```bash
# 运行环境
ENVIRONMENT=production
LOG_LEVEL=INFO

# 使用 GLM
LLM_PROVIDER=glm
GLM_API_KEY=your_production_key
GLM_MODEL=glm-4

# 数据库路径（绝对路径）
DB_PATH=/opt/kid-agent/data/kid_agent.db

# CORS（生产环境应该限制）
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

---

## 微信公众号配置

### 1. 获取公众号信息

在微信公众平台（mp.weixin.qq.com）获取：
- AppID
- AppSecret
- 服务器配置 Token
- 服务器配置 EncodingAESKey

### 2. 配置服务器

在公众号后台设置服务器地址：
```
URL: https://your-domain.com/wechat
Token: kidagent2024 (或自定义)
EncodingAESKey: 自动生成或手动设置
```

### 3. 配置环境变量

```bash
WECHAT_APP_ID=your_app_id
WECHAT_APP_SECRET=your_app_secret
WECHAT_TOKEN=kidagent2024
WECHAT_ENCODING_AES_KEY=your_encoding_aes_key
```

### 4. 测试连接

```bash
curl -X POST https://your-domain.com/wechat \
  -H "Content-Type: application/xml" \
  -d '<xml><ToUserName><
![CDATA[test]]></ToUserName><FromUserName><![CDATA[123456]]></FromUserName><CreateTime>1234567890</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[hello]]></Content><MsgId>1234567890123456</MsgId></xml>'
```

---

## 监控和健康检查

### 健康检查端点

**基础健康检查**
```bash
curl http://localhost:8000/health
```

响应：
```json
{
  "status": "healthy",
  "timestamp": "2026-05-20T10:30:00.000000",
  "version": "2.0.0"
}
```

**详细健康检查**
```bash
curl http://localhost:8000/health/detailed
```

响应包含：
- 数据库连接状态
- LLM API 配置
- 磁盘空间
- 运行时间

**Ping 端点**
```bash
curl http://localhost:8000/ping
```

### Prometheus 监控指标

访问 `/metrics` 获取 Prometheus 格式的指标：

```bash
curl http://localhost:8000/metrics
```

可用的指标：

| 指标名 | 类型 | 说明 |
|--------|------|------|
| `kid_agent_uptime_seconds` | Gauge | 应用运行时间 |
| `kid_agent_health_status` | Gauge | 健康状态 (1=健康, 0=不健康) |
| `kid_agent_version` | Gauge | 版本信息 |
| `kid_agent_database_size_bytes` | Gauge | 数据库大小 |
| `kid_agent_disk_percent_used` | Gauge | 磁盘使用百分比 |
| `kid_agent_disk_available_bytes` | Gauge | 可用磁盘空间 |

### 使用 Prometheus

配置 Prometheus 抓取指标：

```yaml
scrape_configs:
  - job_name: 'kid-agent'
    static_configs:
      - targets: ['localhost:8000']
        labels:
          instance: 'kid-agent-production'
    scrape_interval: 30s
```

### 日志管理

**Systemd 日志**
```bash
# 查看最新日志
sudo journalctl -u kid-agent -n 100

# 实时跟踪日志
sudo journalctl -u kid-agent -f

# 按时间过滤
sudo journalctl -u kid-agent --since "1 hour ago"
```

**Docker 日志**
```bash
# 查看最新日志
docker-compose logs --tail=100 kid-agent

# 实时跟踪日志
docker-compose logs -f kid-agent
```

---

## 故障排查

### 常见问题

#### 1. 服务无法启动

**检查端口占用**
```bash
sudo netstat -tlnp | grep 8000
# 或
sudo ss -tlnp | grep 8000
```

**检查日志**
```bash
# Systemd
sudo journalctl -u kid-agent -n 50

# Docker
docker-compose logs kid-agent
```

#### 2. 数据库错误

**检查数据库文件权限**
```bash
ls -la /opt/kid-agent/data/kid_agent.db
sudo chown kidagent:kidagent /opt/kid-agent/data/kid_agent.db
```

**检查磁盘空间**
```bash
df -h /opt/kid-agent/data
```

#### 3. LLM API 调用失败

**验证 API 密钥**
```bash
curl -X POST https://open.bigmodel.cn/api/paas/v4/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"glm-4","messages":[{"role":"user","content":"test"}]}'
```

**检查网络连接**
```bash
curl -I https://open.bigmodel.cn/api/paas/v4
```

#### 4. 微信公众号无法接收消息

**检查服务器配置**
- 确保服务器地址正确
- 确保端口 80/443 可访问
- 检查 Nginx 配置

**验证 Token**
```bash
# 验证微信服务器验证接口
curl "https://your-domain.com/wechat?signature=...&timestamp=...&nonce=...&echostr=test"
```

#### 5. CORS 错误

检查 `CORS_ORIGINS` 配置：
```bash
curl -H "Origin: https://yourdomain.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS http://localhost:8000/api/chat
```

### 性能优化

#### 数据库优化

```sql
-- 分析数据库
PRAGMA analyze;

-- 优化数据库
PRAGMA optimize;

-- 检查数据库完整性
PRAGMA integrity_check;
```

#### 缓存配置

对于高流量场景，考虑：
- 使用 Redis 缓存
- 启用 Nginx 缓存
- 配置 CDN

#### 资源限制

在 `docker-compose.yml` 中添加资源限制：
```yaml
services:
  kid-agent:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

---

## 备份和恢复

### 备份

**数据库备份**
```bash
# 创建备份
cp /opt/kid-agent/data/kid_agent.db /opt/kid-agent/data/kid_agent.db.$(date +%Y%m%d)

# 或使用 sqlite3 备份
sqlite3 /opt/kid-agent/data/kid_agent.db ".backup /opt/kid-agent/data/kid_agent.db.backup"
```

**配置备份**
```bash
tar -czf kid-agent-config-$(date +%Y%m%d).tar.gz /opt/kid-agent/config/
```

### 恢复

**恢复数据库**
```bash
# 停止服务
sudo systemctl stop kid-agent

# 恢复数据库
cp /path/to/backup/kid_agent.db /opt/kid-agent/data/kid_agent.db

# 重启服务
sudo systemctl start kid-agent
```

---

## 安全建议

1. **使用 HTTPS** - 在生产环境始终使用 SSL/TLS
2. **限制 CORS** - 仅允许可信的源
3. **定期更新** - 保持依赖包和系统更新
4. **监控日志** - 定期检查异常访问
5. **最小权限原则** - 运行服务使用专用用户
6. **API 密钥管理** - 使用密钥管理服务存储敏感信息
7. **防火墙配置** - 仅开放必要的端口

---

## 支持

如有问题，请：
1. 查看本文档的故障排查部分
2. 检查日志文件
3. 访问健康检查端点确认服务状态
4. 提交 Issue 到项目仓库
