"""
FastAPI 应用主入口
配置路由、中间件、异常处理等
"""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.core.exceptions import AppException
from app.core.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    应用生命周期管理

    在应用启动和关闭时执行操作
    """
    # 导入数据库引擎
    from app.db.session import engine

    # 启动时
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    yield

    # 关闭时 - 正确清理数据库连接
    logger.info("Shutting down application...")

    # 关闭数据库连接池
    try:
        await engine.dispose()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.warning(f"Error closing database connections: {e}")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="货运代理业务管理系统 API",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)


app.mount(
    "/uploads",
    StaticFiles(directory=settings.UPLOAD_DIR, check_dir=False),
    name="uploads",
)


# ==================== 中间件配置 ====================

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 异常处理 ====================


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    处理应用自定义异常

    Args:
        request: 请求对象
        exc: 异常对象

    Returns:
        JSON 响应
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    处理请求验证异常

    Args:
        request: 请求对象
        exc: 验证异常对象

    Returns:
        JSON 响应
    """
    errors = [
        {"field": " -> ".join(str(loc) for loc in error["loc"]), "message": error["msg"]}
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "errors": errors,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    处理所有未捕获的异常

    Args:
        request: 请求对象
        exc: 异常对象

    Returns:
        JSON 响应
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred" if not settings.DEBUG else str(exc),
        },
    )


# ==================== 路由 ====================


# 健康检查
@app.get("/", tags=["Health"])
async def root() -> dict[str, str]:
    """
    根路径 - 健康检查

    Returns:
        欢迎消息
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "healthy",
    }


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, Any]:
    """
    健康检查端点

    Returns:
        健康状态信息
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


# ==================== 注册路由 ====================

from app.api import export as export_api
from app.api import files
from app.api.v1 import (
    auth,
    billing,
    customers,
    emails,
    lead_generation,
    notifications,
    sales_agents,
    scraped_leads,
    scraping,
    tasks,
    users,
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(billing.router, prefix="/api/v1/billing", tags=["Billing"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(customers.router, prefix="/api/v1/customers", tags=["Customers"])
app.include_router(emails.router, prefix="/api/v1/emails", tags=["Emails"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(scraping.router, prefix="/api/v1/scraping", tags=["Data Scraping"])
app.include_router(scraped_leads.router, prefix="/api/v1/leads", tags=["Scraped Leads"])
app.include_router(
    lead_generation.router, prefix="/api/v1/lead-generation", tags=["AI Lead Generation"]
)
app.include_router(sales_agents.router, prefix="/api/v1/sales-agents", tags=["Sales Agents"])
app.include_router(files.router, prefix="/api/v1/files", tags=["Files"])
app.include_router(export_api.router, prefix="/api/v1", tags=["Export"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
