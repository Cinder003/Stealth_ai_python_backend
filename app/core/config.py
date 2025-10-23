"""Application configuration using Pydantic Settings"""

from functools import lru_cache
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = Field(default="Unified Codegen Platform")
    APP_VERSION: str = Field(default="1.0.0")
    DEBUG: bool = Field(default=False)
    ENVIRONMENT: str = Field(default="development")
    
    # API
    API_V1_PREFIX: str = Field(default="/api/v1")
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    WORKERS: int = Field(default=4)
    
    # Security
    SECRET_KEY: str = Field(default="change-this-secret-key-in-production")
    API_KEY_HEADER: str = Field(default="X-API-Key")
    ALLOWED_HOSTS: List[str] = Field(default=["*"])
    CORS_ORIGINS: List[str] = Field(default=["*"])
    
    
    # LiteLLM Proxy
    LITELLM_URL: str = Field(default="http://litellm:4000")
    LITELLM_API_KEY: Optional[str] = Field(default=None)
    LITELLM_MASTER_KEY: Optional[str] = Field(default=None)
    LITELLM_TIMEOUT: int = Field(default=300)
    LITELLM_MAX_RETRIES: int = Field(default=3)
    GEMINI_API_KEY: Optional[str] = Field(default=None)
    
    # Redis
    REDIS_HOST: str = Field(default="redis")
    REDIS_PORT: int = Field(default=6379)
    REDIS_DB: int = Field(default=0)
    REDIS_PASSWORD: Optional[str] = Field(default=None)
    REDIS_URL: Optional[str] = Field(default=None)
    CACHE_TTL: int = Field(default=3600)
    
    # NATS
    NATS_URL: str = Field(default="nats://nats:4222")
    NATS_MAX_RECONNECT_ATTEMPTS: int = Field(default=10)
    NATS_RECONNECT_TIME_WAIT: int = Field(default=2)
    
    # Langfuse
    LANGFUSE_PUBLIC_KEY: Optional[str] = Field(default=None)
    LANGFUSE_SECRET_KEY: Optional[str] = Field(default=None)
    LANGFUSE_HOST: str = Field(default="http://langfuse:3000")
    LANGFUSE_ENABLED: bool = Field(default=False)
    
    # Figma (Future)
    FIGMA_CLIENT_ID: Optional[str] = Field(default=None)
    FIGMA_CLIENT_SECRET: Optional[str] = Field(default=None)
    FIGMA_ACCESS_TOKEN: Optional[str] = Field(default=None)
    
    # GitHub (Future)
    GITHUB_PAT: Optional[str] = Field(default=None)
    GITHUB_OWNER: Optional[str] = Field(default=None)
    GITHUB_REPO: Optional[str] = Field(default=None)
    
    # File Storage
    STORAGE_PATH: str = Field(default="/app/storage/generated")
    TEMP_PATH: str = Field(default="/app/storage/temp")
    MAX_FILE_SIZE: int = Field(default=100 * 1024 * 1024)  # 100MB
    ALLOWED_EXTENSIONS: List[str] = Field(default=[
        "py", "js", "jsx", "ts", "tsx", "html", 
        "css", "json", "md", "txt", "yaml", "yml"
    ])
    
    # Code Generation
    MAX_GENERATION_TIME: int = Field(default=600)  # 10 minutes
    MAX_FILES_PER_PROJECT: int = Field(default=1000)
    DEFAULT_FRONTEND_FRAMEWORK: str = Field(default="react")
    DEFAULT_BACKEND_FRAMEWORK: str = Field(default="nodejs")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60)
    RATE_LIMIT_PER_HOUR: int = Field(default=1000)
    
    # Monitoring
    ENABLE_METRICS: bool = Field(default=True)
    METRICS_PORT: int = Field(default=9000)
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="json")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )
    
    @property
    def redis_connection_url(self) -> str:
        """Get Redis connection URL"""
        if self.REDIS_URL:
            return self.REDIS_URL
        
        password_part = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{password_part}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()

