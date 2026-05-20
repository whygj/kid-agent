# Kid Agent Phase 2: Web API + 聊天前端

你现在在 ~/projects/kid-agent/ 项目中。Phase 1 已完成（CLI模式的完整数学教学Agent）。

## 任务
为 Kid Agent 添加 Web API 和浏览器聊天界面。

## 代码规范
- Python 3.12，不引入LangChain等框架
- 代码风格与现有 src/ 保持一致
- 所有新代码放在 src/web/ 目录下
- 依赖加到 requirements.txt

## 需要实现的功能

### 1. FastAPI Web API (src/web/api.py)
- `POST /api/session/start` — 开始会话，参数: student_id (str)
- `POST /api/session/chat` — 发送消息，参数: student_id (str), message (str)
- `GET /api/student/{student_id}/report` — 获取学习报告
- `GET /api/student/{student_id}/status` — 获取学生状态（掌握度、XP、等级）
- `GET /api/health` — 健康检查
- 全部使用 async/await，调用 TutorAgent 的异步接口
- CORS 支持（允许所有来源，方便前端调用）
- 请求/响应用 Pydantic model

### 2. WebSocket 实时聊天 (src/web/ws.py)
- `WS /ws/{student_id}` — WebSocket 长连接
- 前端发文本消息，后端返回AI回复（JSON格式）
- 消息格式: {"type": "message"|"status"|"report", "content": "...", "data": {...}}
- 连接管理：断开重连友好
- 心跳保活

### 3. Web 聊天前端 (src/web/static/)
用纯HTML+CSS+JS写一个单页面聊天界面（不引入任何前端框架），放在 src/web/static/ 目录：

#### index.html
- 聊天气泡界面（用户消息靠右，AI消息靠左）
- 顶部显示学生名称、等级、XP
- 底部输入框 + 发送按钮
- WebSocket 连接状态指示（已连接/断开/重连中）
- 移动端适配（响应式，手机上能用）
- 中文界面，适合小学生使用
- 配色温暖友好，按钮大，字体大（适合儿童）
- 加载时弹窗让学生输入名字（简单的 prompt 即可）

#### style.css
- 聊天气泡样式
- 响应式布局
- 打字动画（AI正在思考时显示"..."动画）
- 数学公式简单展示（数字和符号大而清晰）

#### app.js
- WebSocket 连接管理（自动重连）
- 消息发送/接收
- 状态栏更新
- 聊天历史展示

### 4. 应用入口 (src/web/app.py)
- 创建 FastAPI app
- 挂载 API 路由和 WebSocket
- 静态文件服务
- 启动时初始化 TutorAgent
- 生命周期管理

### 5. 启动脚本更新
更新 scripts/start.sh，添加 web 模式：
```bash
PYTHONPATH=. python3 -m src.main --mode web --port 8000
```
同时更新 src/main.py 支持 --mode web 和 --port 参数。

### 6. 依赖
在 requirements.txt 添加：
- fastapi
- uvicorn[standard]
- websockets
- python-multipart

### 7. 测试
写 tests/test_web_api.py：
- 用 httpx + pytest-asyncio 测试所有 API endpoint
- 测试 WebSocket 连接和消息收发
- Mock LLM 调用（避免测试时消耗API）

## 文件清单（需要创建/修改）
新建：
- src/web/__init__.py
- src/web/app.py
- src/web/api.py
- src/web/ws.py
- src/web/models.py (Pydantic models)
- src/web/static/index.html
- src/web/static/style.css
- src/web/static/app.js
- tests/test_web_api.py

修改：
- requirements.txt (添加 fastapi, uvicorn, websockets, python-multipart)
- scripts/start.sh (添加 web 模式)
- src/main.py (添加 --mode web 和 --port)

## 注意事项
- TutorAgent 是异步的，直接 await 调用
- TutorAgent() 构造函数无参数
- start_session(student_id) 和 chat(student_id, message) 都是 async
- config/.env 已有 API 密钥配置
- 不要改动任何现有 src/agent/, src/engine/, src/memory/ 下的代码
- 确保所有新文件 python -c "import ..." 能通过语法检查

开始写代码，不要询问。
