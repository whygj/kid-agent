"""FastAPI application entry point"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.agent.tutor import get_tutor_agent
from src.config.settings import get_config
from src.web.api import router as api_router, wechat_router
from src.web.health import router as health_router
from src.web.ws import router as ws_router

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("Starting Kid Agent Web API...")

    # 初始化TutorAgent
    await get_tutor_agent()
    logger.info("TutorAgent initialized")

    yield

    logger.info("Shutting down Kid Agent Web API...")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    config = get_config()

    app = FastAPI(
        title="Kid Agent API",
        description="小学数学教学助手 Web API",
        version="2.0.0",
        lifespan=lifespan,
    )

    # CORS配置 - 使用环境变量配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors.allow_origins,
        allow_credentials=config.cors.allow_credentials,
        allow_methods=config.cors.allow_methods,
        allow_headers=config.cors.allow_headers,
    )

    # 注册路由
    app.include_router(health_router)
    app.include_router(api_router)
    app.include_router(ws_router)
    app.include_router(wechat_router)

    # 静态文件服务
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    return app


app = create_app()