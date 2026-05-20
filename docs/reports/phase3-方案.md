# Kid Agent Phase 3: 语音交互

你现在在 ~/projects/kid-agent/ 项目中。Phase 1-2 已完成（CLI+Web API+前端）。

## 任务
为 Kid Agent 添加语音交互能力——小孩可以说话（语音识别）和听AI回复（语音合成）。

## 技术方案
- **STT（语音识别）**：前端用浏览器 Web Speech API（SpeechRecognition），零成本，无需后端API
- **TTS（语音合成）**：后端用智谱GLM语音合成API（或edge-tts作为fallback）
- **音频传输**：前端录音→识别为文字→发送给后端；后端返回文字→前端用浏览器SpeechSynthesis朗读

## 代码规范
- 新代码放在 src/voice/ 目录
- 前端修改 src/web/static/ 的文件
- 依赖加到 requirements.txt

## 需要实现的功能

### 1. 语音合成服务 (src/voice/tts.py)
```python
class TTSService:
    async def synthesize(self, text: str, voice: str = "female") -> bytes:
        """文字转语音，返回mp3音频bytes"""
        # 方案1: 智谱GLM TTS API (POST https://open.bigmodel.cn/api/paas/v4/audio/speech)
        #   - model: "tts-1"
        #   - input: text
        #   - voice: "alloy" | "echo" | "fable" | "onyx" | "nova" | "shimmer"
        #   - 返回 mp3 audio
        # 方案2 (fallback): edge-tts (免费，不需要API key)
        #   - 使用 edge_tts.Communicate(text, voice="zh-CN-XiaoxiaoNeural")
        #   - 保存到临时文件，返回bytes
```

### 2. 语音API路由 (修改 src/web/api.py)
添加：
- `POST /api/voice/tts` — 文字转语音
  - 请求: {"text": "你好", "voice": "female"}
  - 响应: audio/mpeg 直接返回mp3
- 在WebSocket消息中支持 type="audio" 消息

### 3. 前端语音功能 (修改 src/web/static/app.js)
添加：
- **麦克风按钮**：输入框旁边加一个麦克风图标按钮
- **录音功能**：点击麦克风开始录音，再点停止
- **语音识别**：用 Web Speech API 的 SpeechRecognition
  - 设置 lang = "zh-CN"
  - continuous = false, interimResults = true
  - 识别结果实时显示在输入框
  - 最终结果自动发送
- **语音播放**：AI回复自动朗读
  - 用 Web Speech API 的 SpeechSynthesis
  - 设置中文语音（SpeechSynthesisVoice 找 zh-CN 的）
  - 设置语速偏慢（rate=0.9），适合小学生
  - 朗读时AI气泡显示播放动画
  - 提供"停止朗读"按钮

### 4. 前端UI更新 (修改 src/web/static/index.html 和 style.css)
- 输入框区域：文本输入框 | 麦克风按钮 | 发送按钮 | 🔊朗读开关
- 麦克风按钮状态：待机（灰色）→ 录音中（红色闪烁动画）
- 🔊朗读开关：控制AI回复是否自动朗读
- 移动端：麦克风按钮足够大，方便小孩按

### 5. 配置 (修改 src/config/settings.py)
添加 voice 配置段：
```python
voice:
  tts_provider: "glm" | "edge"  # 默认 edge（免费稳定）
  tts_voice: "zh-CN-XiaoxiaoNeural"  # edge-tts voice
  auto_play: true  # 默认自动朗读
```

### 6. 测试
写 tests/test_voice.py：
- 测试 TTSService 初始化
- Mock API调用测试synthesize
- 测试API endpoint
- 测试Pydantic模型

## 文件清单
新建：
- src/voice/__init__.py
- src/voice/tts.py
- tests/test_voice.py

修改：
- src/web/api.py（添加TTS endpoint）
- src/web/static/app.js（语音识别+播放）
- src/web/static/index.html（麦克风按钮+朗读开关）
- src/web/static/style.css（录音动画+播放动画）
- src/config/settings.py（voice配置）
- requirements.txt（添加 edge-tts）

## 注意事项
- edge-tts 是免费方案，用 async 的 edge_tts.Communicate
- Web Speech API 只在 Chrome/Edge 等浏览器支持，Safari部分支持
- 语音识别结果直接作为聊天消息发送给 TutorAgent
- 不要改动 src/agent/ 和 src/engine/ 下的代码
- 确保所有新 .py 文件语法正确

开始写代码，不要询问。
