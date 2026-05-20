# Kid Agent Phase 4: 微信公众号接入 + 家长通知

你现在在 ~/projects/kid-agent/ 项目中。Phase 1-3 已完成（CLI+Web+语音）。

## 任务
为 Kid Agent 添加微信公众号接入，让小孩可以通过微信使用，家长收到学习通知。

## 技术方案
- 微信公众号（测试号模式）—— 接收消息/被动回复
- 家长通知 —— 每日学习报告推送
- 微信OAuth —— 用户绑定学生账号

## 代码规范
- 新代码放在 src/wechat/ 目录
- 不依赖 itchat、wechatpy 等第三方微信库，纯手写（用 httpx/curl 调用微信API）
- 微信消息加解密用手写实现

## 需要实现的功能

### 1. 微信公众号服务器 (src/wechat/server.py)
```python
class WeChatServer:
    """微信公众号消息服务器"""
    
    async def verify(self, signature: str, timestamp: str, nonce: str, echostr: str) -> str:
        """验证微信服务器签名（GET请求）"""
        
    async def handle_message(self, xml_data: str) -> str:
        """处理微信消息（POST请求），返回XML回复"""
```

实现：
- 微信签名验证（SHA1(sort(token, timestamp, nonce))）
- XML消息解析（提取 FromUserName, ToUserName, MsgType, Content）
- XML回复生成（文本消息格式）
- 消息路由：文本→TutorAgent.chat，事件→事件处理

### 2. 消息处理器 (src/wechat/handler.py)
```python
class WeChatHandler:
    """微信消息处理器"""
    
    async def handle_text(self, user_id: str, content: str) -> str:
        """处理文本消息"""
        # 1. 查找 user_id 绑定的 student_id（从数据库）
        # 2. 如果未绑定，返回绑定提示
        # 3. 如果已绑定，调用 TutorAgent.chat(student_id, content)
        # 4. 返回回复文本
        
    async def handle_event(self, user_id: str, event: str, event_key: str) -> str:
        """处理事件消息（关注/取消关注/菜单点击）"""
        # subscribe: 欢迎消息 + 绑定引导
        # CLICK_report: 生成学习报告
        # CLICK_today: 今日学习进度
```

### 3. 用户绑定 (src/wechat/binding.py)
```python
class UserBinding:
    """微信用户与学生账号绑定"""
    
    async def bind(self, wechat_user_id: str, student_name: str) -> str:
        """绑定微信用户到学生"""
        
    async def get_student_id(self, wechat_user_id: str) -> str | None:
        """根据微信user_id查找student_id"""
        
    async def get_parent_binding(self, student_id: str) -> str | None:
        """根据student_id查找绑定的家长微信user_id"""
```

存储用SQLite，在 store.py 的数据库中添加 wechat_bindings 表：
- wechat_user_id (TEXT, PK)
- student_id (TEXT, FK)
- role (TEXT): "student" | "parent"
- created_at (TEXT)

### 4. 家长通知 (src/wechat/notify.py)
```python
class ParentNotifier:
    """家长学习通知"""
    
    async def send_daily_report(self, student_id: str) -> bool:
        """发送每日学习报告给家长"""
        # 1. 获取学生学习数据
        # 2. 生成报告文本
        # 3. 通过微信客服消息接口发送
        
    async def send_achievement(self, student_id: str, achievement: str) -> bool:
        """发送成就通知（升级/连续答对等）"""
```

### 5. 微信API客户端 (src/wechat/client.py)
```python
class WeChatClient:
    """微信API客户端"""
    
    async def get_access_token(self) -> str:
        """获取access_token（带缓存）"""
        
    async def send_customer_message(self, user_id: str, content: str) -> bool:
        """发送客服消息（用于主动推送）"""
        
    async def create_menu(self, menu_data: dict) -> bool:
        """创建自定义菜单"""
```

实现：
- access_token 缓存（有效期7200秒，提前5分钟刷新）
- HTTP请求用 httpx
- 配置从 config/.env 读取：WECHAT_APP_ID, WECHAT_APP_SECRET, WECHAT_TOKEN

### 6. API路由 (修改 src/web/api.py)
添加微信相关路由：
- `GET /api/wechat/verify` — 微信服务器验证
- `POST /api/wechat/message` — 接收微信消息
- `POST /api/wechat/bind` — 手动绑定接口（测试用）
- `POST /api/wechat/notify/{student_id}` — 触发家长通知

### 7. 配置 (修改 src/config/settings.py)
添加 wechat 配置段：
```python
wechat:
  app_id: str = ""
  app_secret: str = ""
  token: str = "kidagent2024"
  encoding_aes_key: str = ""  # 留空=明文模式
```

### 8. 测试
写 tests/test_wechat.py：
- 测试签名验证
- 测试XML消息解析和回复生成
- 测试用户绑定/查询
- 测试消息路由
- Mock所有外部API调用

### 9. 自定义菜单
创建微信菜单配置 (src/wechat/menu.json)：
```json
{
  "button": [
    {"type": "click", "name": "开始学习", "key": "start_learn"},
    {"type": "click", "name": "今日报告", "key": "today_report"},
    {"type": "click", "name": "学习周报", "key": "weekly_report"}
  ]
}
```

## 文件清单
新建：
- src/wechat/__init__.py
- src/wechat/server.py
- src/wechat/handler.py
- src/wechat/binding.py
- src/wechat/notify.py
- src/wechat/client.py
- src/wechat/menu.json
- tests/test_wechat.py

修改：
- src/web/api.py（添加微信路由）
- src/config/settings.py（wechat配置）
- src/memory/store.py（添加 wechat_bindings 表）
- config/.env（添加 WECHAT_APP_ID 等配置占位）
- requirements.txt（不需要新依赖，已有 httpx）

## 注意事项
- 微信测试号申请：https://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=sandbox/login
- 测试号限制：只能100个关注者，但功能完整
- 消息必须在5秒内回复，否则微信会重试（TutorAgent调用可能超时，考虑async处理）
- 客服消息接口可以48小时内主动发送
- 不要改动 src/agent/ 和 src/engine/ 下的核心代码
- store.py 可以添加新方法但不要修改现有方法签名

开始写代码，不要询问。
