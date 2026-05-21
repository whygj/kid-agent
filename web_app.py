"""kid-agent Web API — FastAPI + H5前端

启动: python web_app.py
访问: http://localhost:8900
"""

import asyncio
import json
import os
import sys
import uuid
from pathlib import Path
from typing import Optional

# 确保能import kid_agent
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import uvicorn

app = FastAPI(title="kid-agent", version="0.3.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# 加载.env
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")
load_dotenv(Path(__file__).parent / "src" / ".env")

# kid-agent 配置
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_HOST = os.getenv("LLM_HOST", "https://open.bigmodel.cn/api/paas/v4")
LLM_MODEL = os.getenv("LLM_MODEL", "glm-5.1")

# ============================================================
# HTML 前端
# ============================================================
HTML_PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>kid-agent 小学数学AI家教</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f0f2f5; height: 100vh; display: flex; flex-direction: column; }
.header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 20px; display: flex; align-items: center; justify-content: space-between; }
.header h1 { font-size: 18px; font-weight: 600; }
.header .badge { background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 12px; font-size: 12px; }
.chat-area { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
.msg { max-width: 80%; padding: 12px 16px; border-radius: 16px; line-height: 1.6; font-size: 14px; word-break: break-word; white-space: pre-wrap; }
.msg.user { align-self: flex-end; background: #667eea; color: white; border-bottom-right-radius: 4px; }
.msg.bot { align-self: flex-start; background: white; color: #333; border-bottom-left-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }
.msg.system { align-self: center; background: #fff3cd; color: #856404; font-size: 12px; padding: 8px 16px; border-radius: 8px; }
.input-area { padding: 12px 16px; background: white; border-top: 1px solid #e0e0e0; display: flex; gap: 8px; }
.input-area input { flex: 1; padding: 10px 16px; border: 2px solid #e0e0e0; border-radius: 24px; font-size: 14px; outline: none; transition: border-color 0.2s; }
.input-area input:focus { border-color: #667eea; }
.input-area button { padding: 10px 24px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; border-radius: 24px; font-size: 14px; cursor: pointer; transition: opacity 0.2s; }
.input-area button:hover { opacity: 0.9; }
.input-area button:disabled { opacity: 0.5; cursor: not-allowed; }
.grade-selector { display: flex; gap: 6px; padding: 8px 16px; background: white; border-top: 1px solid #eee; flex-wrap: wrap; }
.grade-btn { padding: 4px 12px; border: 1px solid #ddd; border-radius: 16px; background: white; cursor: pointer; font-size: 12px; transition: all 0.2s; }
.grade-btn.active { background: #667eea; color: white; border-color: #667eea; }
.typing { display: flex; gap: 4px; padding: 4px 0; }
.typing span { width: 8px; height: 8px; background: #999; border-radius: 50%; animation: bounce 1.4s infinite; }
.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce { 0%, 60%, 100% { transform: translateY(0); } 30% { transform: translateY(-8px); } }
.toolbar { display: flex; gap: 6px; padding: 4px 16px 8px; background: white; }
.tool-btn { padding: 4px 10px; border: 1px solid #ddd; border-radius: 8px; background: #f8f9fa; cursor: pointer; font-size: 11px; }
.tool-btn:hover { background: #e9ecef; }
</style>
</head>
<body>
<div class="header">
  <h1>🎓 kid-agent 数学AI家教</h1>
  <span class="badge">K-12 智能辅导</span>
</div>
<div class="grade-selector" id="gradeSelector">
  <button class="grade-btn" onclick="setGrade(1)">1年级</button>
  <button class="grade-btn" onclick="setGrade(2)">2年级</button>
  <button class="grade-btn active" onclick="setGrade(3)">3年级</button>
  <button class="grade-btn" onclick="setGrade(4)">4年级</button>
  <button class="grade-btn" onclick="setGrade(5)">5年级</button>
  <button class="grade-btn" onclick="setGrade(6)">6年级</button>
  <button class="grade-btn" onclick="setGrade(7)">初中</button>
  <button class="grade-btn" onclick="setGrade(10)">高中</button>
</div>
<div class="toolbar">
  <button class="tool-btn" onclick="sendAction('quiz')">📝 出题练习</button>
  <button class="tool-btn" onclick="sendAction('explain')">📖 讲解知识</button>
  <button class="tool-btn" onclick="sendAction('diagnose')">🔍 诊断薄弱点</button>
  <button class="tool-btn" onclick="clearChat()">🗑️ 清空</button>
</div>
<div class="chat-area" id="chatArea">
  <div class="msg bot">你好！我是kid-agent数学AI家教 🎓\n\n我可以帮你：
• 📝 出题练习（选择年级后点击出题练习）
• 📖 讲解知识点（输入知识点名称，如加法交换律）
• 🔍 诊断薄弱点（点击诊断薄弱点）
• ❓ 回答数学问题（直接输入问题）\n\n试试看吧！</div>
</div>
<div class="input-area">
  <input type="text" id="msgInput" placeholder="输入数学问题或指令..." onkeypress="if(event.key==='Enter')sendMsg()">
  <button id="sendBtn" onclick="sendMsg()">发送</button>
</div>
<script>
let currentGrade = 3;
let sessionId = 'session_' + Date.now();

function setGrade(g) {
  currentGrade = g;
  document.querySelectorAll('.grade-btn').forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');
  addMsg('system', '已切换到' + (g <= 6 ? g + '年级' : g === 7 ? '初中' : '高中') + '模式');
}

function addMsg(type, text) {
  const area = document.getElementById('chatArea');
  const div = document.createElement('div');
  div.className = 'msg ' + type;
  div.textContent = text;
  area.appendChild(div);
  area.scrollTop = area.scrollHeight;
  return div;
}

function showTyping() {
  const div = document.createElement('div');
  div.className = 'msg bot';
  div.id = 'typing';
  div.innerHTML = '<div class="typing"><span></span><span></span><span></span></div>';
  document.getElementById('chatArea').appendChild(div);
  document.getElementById('chatArea').scrollTop = document.getElementById('chatArea').scrollHeight;
}

function hideTyping() {
  const el = document.getElementById('typing');
  if (el) el.remove();
}

async function sendMsg() {
  const input = document.getElementById('msgInput');
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  addMsg('user', text);
  await callAPI(text);
}

async function sendAction(action) {
  const actionMap = {
    'quiz': '请给我出一道' + currentGrade + '年级的数学练习题',
    'explain': '请讲解一下' + currentGrade + '年级的核心知识点',
    'diagnose': '请帮我诊断' + currentGrade + '年级的薄弱知识点'
  };
  const text = actionMap[action];
  addMsg('user', text);
  await callAPI(text);
}

async function callAPI(text) {
  const btn = document.getElementById('sendBtn');
  btn.disabled = true;
  showTyping();
  try {
    const resp = await fetch('/api/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: text, grade: currentGrade, session_id: sessionId})
    });
    const data = await resp.json();
    hideTyping();
    if (data.error) {
      addMsg('system', '❌ ' + data.error);
    } else {
      addMsg('bot', data.response || data.explanation || JSON.stringify(data));
    }
  } catch(e) {
    hideTyping();
    addMsg('system', '❌ 网络错误: ' + e.message);
  }
  btn.disabled = false;
}

function clearChat() {
  document.getElementById('chatArea').innerHTML = '';
  sessionId = 'session_' + Date.now();
  addMsg('bot', '对话已清空，重新开始吧！');
}
</script>
</body>
</html>"""

# ============================================================
# API 路由
# ============================================================

@app.get("/")
async def index():
    return HTMLResponse(HTML_PAGE)

@app.get("/api/health")
async def health():
    return {"status": "ok", "model": LLM_MODEL, "host": LLM_HOST[:30] + "..."}

@app.post("/api/chat")
async def chat(request: dict):
    """主聊天接口"""
    message = request.get("message", "")
    grade = request.get("grade", 3)
    session_id = request.get("session_id", str(uuid.uuid4()))
    
    if not message:
        return {"error": "消息不能为空"}
    
    try:
        response = await call_llm(message, grade)
        return {"response": response, "session_id": session_id, "grade": grade}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/quiz")
async def quiz(request: dict):
    """出题接口"""
    grade = request.get("grade", 3)
    topic = request.get("topic", "")
    count = request.get("count", 1)
    
    prompt = f"""你是一个小学数学老师。请为{grade}年级学生出一道数学题。
{'主题：' + topic if topic else ''}
要求：
1. 题目要符合{grade}年级的难度
2. 返回JSON格式：{{"question": "题目", "options": ["A. ...", "B. ...", "C. ...", "D. ..."], "answer": "B", "explanation": "解析"}}
3. 只返回JSON，不要其他文字"""
    
    try:
        resp = await call_llm_raw(prompt)
        return {"quiz": resp, "grade": grade}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/diagnose")
async def diagnose(request: dict):
    """诊断薄弱点"""
    grade = request.get("grade", 3)
    
    try:
        # 尝试用知识库
        from kid_agent.tools.kid_knowledge_tool import _get_concepts_by_grade
        topics = _get_concepts_by_grade(grade)
        if topics:
            topic_names = [t.get("name", "") for t in topics[:10]]
            prompt = f"""你是数学教育专家。以下是{grade}年级的知识点列表：
{chr(10).join(topic_names)}

请分析这些知识点，列出{grade}年级学生最容易出错的3个知识点，并给出每个的常见错误和纠正建议。用简洁的中文回答。"""
            resp = await call_llm_raw(prompt)
            return {"diagnosis": resp, "grade": grade, "topics_count": len(topics)}
        else:
            return {"diagnosis": f"未找到{grade}年级的知识点", "grade": grade}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/knowledge/{grade}")
async def get_knowledge(grade: int):
    """获取某年级知识点"""
    try:
        from kid_agent.tools.kid_knowledge_tool import _get_concepts_by_grade
        topics = _get_concepts_by_grade(grade)
        return {"grade": grade, "topics": topics, "count": len(topics)}
    except Exception as e:
        return {"error": str(e)}

# ============================================================
# LLM 调用
# ============================================================

async def call_llm(message: str, grade: int = 3) -> str:
    """带教学system prompt的LLM调用"""
    system = f"""你是一个专业的{grade}年级数学AI家教。你的任务是：
1. 用适合{grade}年级学生的语言解释数学概念
2. 出题要有趣、贴近生活
3. 批改要详细，指出错误原因和正确方法
4. 鼓励学生，培养数学思维
请用中文回答。"""
    
    async with httpx.AsyncClient(timeout=180) as client:
        resp = await client.post(
            f"{LLM_HOST}/chat/completions",
            headers={"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": LLM_MODEL,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.7,
                "max_tokens": 4096
            }
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"API错误 {resp.status_code}: {resp.text[:200]}")

async def call_llm_raw(prompt: str) -> str:
    """原始LLM调用"""
    async with httpx.AsyncClient(timeout=180) as client:
        resp = await client.post(
            f"{LLM_HOST}/chat/completions",
            headers={"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": LLM_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 4096
            }
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"API错误 {resp.status_code}: {resp.text[:200]}")

# ============================================================
# 启动
# ============================================================
if __name__ == "__main__":
    print("🎓 kid-agent Web Server starting...")
    print(f"   Model: {LLM_MODEL}")
    print(f"   Host: {LLM_HOST[:40]}...")
    print(f"   API Key: {LLM_API_KEY[:8]}...")
    uvicorn.run(app, host="0.0.0.0", port=8900)
