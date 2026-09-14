"""
应用配置管理
使用 Pydantic Settings 进行类型安全的配置管理
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    应用配置类

    从环境变量和 .env 文件加载配置
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ==================== 应用基础配置 ====================
    APP_NAME: str = "TradeBusiness API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # ==================== 服务器配置 ====================
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ==================== 数据库配置 ====================
    DATABASE_URL: str = Field(..., description="MySQL 8.0 数据库连接 URL (async)")
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # ==================== Redis 配置 ====================
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis 连接 URL")
    REDIS_CACHE_URL: str = Field(
        default="redis://localhost:6379/1", description="Redis 缓存连接 URL"
    )

    # ==================== 安全配置 ====================
    SECRET_KEY: str = Field(..., description="应用密钥，用于加密等")
    JWT_SECRET_KEY: str = Field(..., description="JWT 签名密钥")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ==================== CORS 配置 ====================
    # 支持字符串或列表格式，都转换为列表
    CORS_ORIGINS: list[str] | str = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """解析 CORS 允许的源，支持字符串或列表"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        if isinstance(v, list):
            return v
        return v

    @model_validator(mode="after")
    def validate_production_settings(self):
        """校验生产环境必须显式配置安全参数"""
        if self.ENVIRONMENT.lower() not in {"prod", "production"}:
            return self

        insecure_values = {
            "your-super-secret-key-change-this-in-production",
            "your-jwt-secret-key-change-this-in-production",
        }
        if self.DEBUG:
            raise ValueError("DEBUG must be false in production")
        if self.SECRET_KEY in insecure_values or self.JWT_SECRET_KEY in insecure_values:
            raise ValueError("SECRET_KEY and JWT_SECRET_KEY must be changed in production")
        if len(self.SECRET_KEY) < 32 or len(self.JWT_SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY and JWT_SECRET_KEY must be at least 32 characters")
        if any("localhost" in origin or "127.0.0.1" in origin for origin in self.CORS_ORIGINS):
            raise ValueError("CORS_ORIGINS must not contain localhost in production")

        return self

    # ==================== 邮件配置 ====================
    SMTP_HOST: str = Field(..., description="SMTP 服务器地址")
    SMTP_PORT: int = 587
    SMTP_USER: str = Field(..., description="SMTP 用户名")
    SMTP_PASSWORD: str = Field(..., description="SMTP 密码")
    SMTP_FROM: str = Field(..., description="发件人邮箱")
    SMTP_FROM_NAME: str = "TradeBusiness"

    # ==================== AI Provider 配置 ====================
    AI_PROVIDER: str = "rules"
    AI_API_KEY: Optional[str] = None
    AI_BASE_URL: str = "https://api.openai.com/v1"
    AI_MODEL: str = "gpt-4o-mini"
    AI_TIMEOUT_SECONDS: int = 45
    AI_MAX_RETRIES: int = 2
    AI_RETRY_BACKOFF_SECONDS: float = 0.5

    # ==================== Celery 配置 ====================
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/2", description="Celery Broker URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/3", description="Celery 结果存储 URL"
    )

    # ==================== 文件存储配置 ====================
    UPLOAD_DIR: str = "./uploads"

    # MinIO 配置（可选）
    MINIO_ENDPOINT: Optional[str] = None
    MINIO_ACCESS_KEY: Optional[str] = None
    MINIO_SECRET_KEY: Optional[str] = None
    MINIO_BUCKET: str = "tradebusiness"
    MINIO_SECURE: bool = False

    # ==================== 爬虫配置 ====================
    SCRAPER_USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    SCRAPER_TIMEOUT: int = 30
    SCRAPER_MAX_CONCURRENT: int = 10
    SCRAPER_DELAY_MIN: int = 1
    SCRAPER_DELAY_MAX: int = 3

    # ==================== 日志配置 ====================
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    # ==================== 限流配置 ====================
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 100

    # ==================== 分页配置 ====================
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # ==================== API Keys (可选) ====================
    GOOGLE_API_KEY: Optional[str] = None
    GOOGLE_SEARCH_ENGINE_ID: Optional[str] = None
    LINKEDIN_API_KEY: Optional[str] = None
    CLEARBIT_API_KEY: Optional[str] = None


@lru_cache()
def get_settings() -> Settings:
    """
    获取配置单例

    使用 lru_cache 确保配置只加载一次

    Returns:
        Settings: 应用配置实例
    """
    return Settings()


# 导出配置实例
settings = get_settings()
