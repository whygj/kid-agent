"""WebSocket chat endpoints"""

import json
import asyncio
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from src.agent.tutor import get_tutor_agent
from src.web.models import WSMessage

router = APIRouter()


class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, student_id: str, websocket: WebSocket) -> None:
        """接受连接"""
        await websocket.accept()
        self.active_connections[student_id] = websocket

    def disconnect(self, student_id: str) -> None:
        """断开连接"""
        if student_id in self.active_connections:
            del self.active_connections[student_id]

    async def send_message(self, student_id: str, message: WSMessage) -> bool:
        """发送消息给指定学生"""
        if student_id not in self.active_connections:
            return False
        try:
            await self.active_connections[student_id].send_text(message.model_dump_json())
            return True
        except Exception:
            self.disconnect(student_id)
            return False

    async def broadcast(self, message: WSMessage) -> None:
        """广播消息给所有连接"""
        for student_id in list(self.active_connections.keys()):
            await self.send_message(student_id, message)

    def get_status(self, student_id: str) -> str:
        """获取连接状态"""
        return "connected" if student_id in self.active_connections else "disconnected"


manager = ConnectionManager()


@router.websocket("/ws/{student_id}")
async def websocket_chat(student_id: str, websocket: WebSocket) -> None:
    """WebSocket聊天端点"""
    await manager.connect(student_id, websocket)

    # 发送连接成功消息
    await manager.send_message(
        student_id,
        WSMessage(type="status", content="已连接到服务器", data={"status": "connected"}),
    )

    agent = None
    try:
        # 初始化Agent
        agent = await get_tutor_agent()

        # 开始会话（如果还没有会话）
        greeting = await agent.start_session(student_id)
        await manager.send_message(
            student_id,
            WSMessage(type="message", content=greeting),
        )

        # 心跳保活
        heartbeat_task = asyncio.create_task(heartbeat_loop(student_id, websocket))

        # 消息循环
        while True:
            data = await websocket.receive_text()
            try:
                msg_data = json.loads(data)
                message_type = msg_data.get("type", "message")
                content = msg_data.get("content", "")

                if message_type == "ping":
                    await manager.send_message(
                        student_id,
                        WSMessage(type="pong", content="pong"),
                    )
                elif message_type == "message":
                    # 处理聊天消息
                    response = await agent.chat(student_id, content)
                    await manager.send_message(
                        student_id,
                        WSMessage(type="message", content=response),
                    )
                elif message_type == "status":
                    # 发送状态
                    student = await agent._store.get_student(student_id)
                    if student:
                        await manager.send_message(
                            student_id,
                            WSMessage(
                                type="status",
                                content="状态更新",
                                data={
                                    "level": 1 + student.total_xp // 100,
                                    "xp": student.total_xp,
                                    "streak_days": student.streak_days,
                                },
                            ),
                        )
                elif message_type == "report":
                    # 发送学习报告
                    report = await agent._student_roster.get_student_report(student_id)
                    if report:
                        await manager.send_message(
                            student_id,
                            WSMessage(
                                type="report",
                                content=report.summary,
                                data={
                                    "total_quizzes": report.total_quizzes,
                                    "correct_rate": report.correct_rate,
                                    "mastered_count": len(report.mastered_points),
                                },
                            ),
                        )
            except json.JSONDecodeError:
                await manager.send_message(
                    student_id,
                    WSMessage(type="error", content="消息格式错误"),
                )
            except Exception as e:
                await manager.send_message(
                    student_id,
                    WSMessage(type="error", content=f"处理消息出错: {str(e)}"),
                )

    except WebSocketDisconnect:
        manager.disconnect(student_id)
        if heartbeat_task:
            heartbeat_task.cancel()
    except Exception as e:
        await manager.send_message(
            student_id,
            WSMessage(type="error", content=f"连接出错: {str(e)}"),
        )
        manager.disconnect(student_id)


async def heartbeat_loop(student_id: str, websocket: WebSocket) -> None:
    """心跳保活循环"""
    try:
        while True:
            await asyncio.sleep(30)
            try:
                await websocket.send_json({"type": "ping"})
            except Exception:
                break
    except asyncio.CancelledError:
        pass