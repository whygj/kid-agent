"""FastAPI REST API endpoints"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import Response
from pydantic import ValidationError

from src.agent.tutor import get_tutor_agent
from src.memory.student import MasteryLevel
from src.knowledge.math_g3g5 import get_point_by_id
from src.voice.tts import TTSError, get_tts_service
from src.web.models import (
    ChatRequest,
    ChatResponse,
    LearningReport,
    SessionStartRequest,
    SessionStartResponse,
    StudentStatus,
    KnowledgePointMastery,
    HealthResponse,
    TTSRequest,
)

router = APIRouter(prefix="/api", tags=["api"])
wechat_router = APIRouter(prefix="/wechat", tags=["wechat"])


@router.post("/session/start", response_model=SessionStartResponse)
async def start_session(request: SessionStartRequest) -> SessionStartResponse:
    """开始学习会话"""
    try:
        agent = await get_tutor_agent()
        greeting = await agent.start_session(request.student_id)
        return SessionStartResponse(
            greeting=greeting,
            student_id=request.student_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start session: {str(e)}",
        ) from e


@router.post("/session/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """发送消息"""
    try:
        agent = await get_tutor_agent()
        response = await agent.chat(request.student_id, request.message)

        # 尝试从响应中提取意图（简化处理）
        intent = "chat"
        if "做题" in response or "题目" in response or "第" in response:
            intent = "quiz"
        elif "对" in response or "错" in response or "答案" in response:
            intent = "answer"

        return ChatResponse(
            response=response,
            intent=intent,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat: {str(e)}",
        ) from e


@router.get("/student/{student_id}/status", response_model=StudentStatus)
async def get_student_status(student_id: str) -> StudentStatus:
    """获取学生状态"""
    try:
        agent = await get_tutor_agent()
        student = await agent._store.get_student(student_id)

        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student {student_id} not found",
            )

        mastery_data = await agent._store.get_mastery(student_id)
        mastered_count = sum(1 for level in mastery_data.values() if level >= MasteryLevel.MASTERED.value)
        fuzzy_count = sum(1 for level in mastery_data.values() if level == MasteryLevel.FUZZY.value)

        return StudentStatus(
            student_id=student.id,
            name=student.name,
            grade=student.grade,
            level=1 + student.total_xp // 100,
            total_xp=student.total_xp,
            streak_days=student.streak_days,
            mastery_count=mastered_count,
            fuzzy_count=fuzzy_count,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get student status: {str(e)}",
        ) from e


@router.get("/student/{student_id}/report", response_model=LearningReport)
async def get_student_report(student_id: str) -> LearningReport:
    """获取学习报告"""
    try:
        agent = await get_tutor_agent()
        student = await agent._store.get_student(student_id)

        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student {student_id} not found",
            )

        roster = agent._student_roster
        report = await roster.get_student_report(student_id)

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Failed to generate report for {student_id}",
            )

        # 获取掌握数据
        mastery_data = await agent._store.get_mastery(student_id)

        # 转换掌握的知识点
        mastered_points = []
        for point_id, level in mastery_data.items():
            if level >= MasteryLevel.FUZZY.value:
                point = get_point_by_id(point_id)
                if point:
                    mastery_name = "已掌握" if level >= MasteryLevel.MASTERED.value else "需巩固"
                    mastered_points.append(
                        KnowledgePointMastery(
                            point_id=point_id,
                            point_name=point.name,
                            mastery_level=level,
                            mastery_name=mastery_name,
                        )
                    )

        # 薄弱点（掌握度低的）
        weak_points = [p for p in mastered_points if p.mastery_level < MasteryLevel.MASTERED.value]

        # 获取最近活动
        history = await agent._store.get_student_history(student_id, limit=5)
        recent_activity = []
        for record in history:
            point = get_point_by_id(record.point_id)
            recent_activity.append(
                {
                    "question": record.question,
                    "is_correct": record.is_correct,
                    "point_name": point.name if point else record.point_id,
                    "created_at": record.created_at.isoformat() if record.created_at else None,
                }
            )

        return LearningReport(
            student_id=student.id,
            name=student.name,
            grade=student.grade,
            level=1 + student.total_xp // 100,
            total_xp=student.total_xp,
            streak_days=student.streak_days,
            total_quizzes=report.total_quizzes,
            correct_rate=report.correct_rate,
            mastered_points=mastered_points,
            weak_points=weak_points,
            recent_activity=recent_activity,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get student report: {str(e)}",
        ) from e


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """健康检查"""
    return HealthResponse(status="ok", version="2.0.0")


@router.post("/voice/tts")
async def text_to_speech(request: TTSRequest):
    """文字转语音

    Args:
        request: TTS请求，包含要转换的文本

    Returns:
        Response: MP3音频流
    """
    try:
        tts_service = await get_tts_service()

        # 语音类型映射
        voice_map = {
            "female": "zh-CN-XiaoxiaoNeural",
            "male": "zh-CN-YunxiNeural",
            "child_female": "zh-CN-XiaoyiNeural",
            "child_male": "zh-CN-YunfengNeural",
        }

        voice = voice_map.get(request.voice, "zh-CN-XiaoxiaoNeural")

        audio_bytes = await tts_service.synthesize(request.text, voice=voice)

        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3",
                "Cache-Control": "no-cache",
            },
        )
    except TTSError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TTS合成失败: {str(e)}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理请求失败: {str(e)}",
        ) from e


# 微信公众号路由
@wechat_router.get("/verify")
async def wechat_verify(
    signature: str = Query(..., description="微信签名"),
    timestamp: str = Query(..., description="时间戳"),
    nonce: str = Query(..., description="随机数"),
    echostr: str = Query(..., description="随机字符串"),
) -> str:
    """微信服务器验证

    用于微信公众号服务器配置验证
    """
    from src.wechat.server import get_wechat_server

    server = await get_wechat_server()
    result = await server.verify(signature, timestamp, nonce, echostr)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Signature verification failed"
        )

    return result


@wechat_router.post("/message")
async def wechat_message(body: str):
    """接收微信消息

    接收微信公众号推送的消息并返回回复
    """
    from src.wechat.server import get_wechat_server

    server = await get_wechat_server()
    reply = await server.handle_message(body)

    return Response(
        content=reply,
        media_type="application/xml",
    )


@wechat_router.post("/bind")
async def wechat_bind(
    wechat_user_id: str = Query(..., description="微信用户OpenID"),
    student_id: str = Query(..., description="学生ID"),
    role: str = Query("student", description="角色: student 或 parent"),
) -> dict[str, str]:
    """手动绑定微信账号

    用于测试或管理绑定关系
    """
    from src.wechat.binding import get_user_binding

    binding = get_user_binding()
    result = await binding.bind(wechat_user_id, student_id, role)

    return {"message": result}


@wechat_router.post("/notify/{student_id}")
async def wechat_notify(
    student_id: str,
    report_type: str = Query("daily", description="报告类型: daily 或 achievement"),
) -> dict[str, Any]:
    """触发家长通知

    手动触发家长通知发送
    """
    from src.wechat.notify import get_parent_notifier

    notifier = get_parent_notifier()

    if report_type == "daily":
        success = await notifier.send_daily_report(student_id)
    else:
        success = await notifier.send_achievement(student_id, "测试通知", "这是一条测试消息")

    return {"success": success, "student_id": student_id}


@wechat_router.get("/menu")
async def get_menu() -> dict[str, Any]:
    """获取微信菜单配置"""
    import json
    from pathlib import Path

    menu_path = Path(__file__).parent.parent.parent / "src" / "wechat" / "menu.json"
    if menu_path.exists():
        with open(menu_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"button": []}


@wechat_router.post("/menu/create")
async def create_menu() -> dict[str, Any]:
    """创建微信自定义菜单"""
    from src.wechat.client import get_wechat_client

    client = await get_wechat_client()
    import json
    from pathlib import Path

    menu_path = Path(__file__).parent.parent.parent / "src" / "wechat" / "menu.json"
    if not menu_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu config not found"
        )

    with open(menu_path, "r", encoding="utf-8") as f:
        menu_data = json.load(f)

    success = await client.create_menu(menu_data)

    return {"success": success}