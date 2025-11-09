"""
Application configuration settings.
Loads environment variables and provides typed configuration access.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator
import secrets


class Settings(BaseSettings):
    """Application settings with environment variable loading."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    APP_NAME: str = "Literattus"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_PREFIX: str = "/api"

    # Database - AWS RDS configuration
    # IMPORTANT: DB_HOST, DB_USER, and DB_PASSWORD must be set in .env file
    # No defaults provided for security - will fail if not configured
    DB_HOST: str  # AWS RDS endpoint - REQUIRED in .env
    DB_PORT: int = 3306
    DB_NAME: str = "literattus"
    DB_USER: str  # Database user - REQUIRED in .env
    DB_PASSWORD: str  # Database REDACTED - REQUIRED in .env
    
    # Constructed from above or explicitly set
    DATABASE_URL: Optional[str] = None

    # Security
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # Google Books API
    GOOGLE_BOOKS_API_KEY: Optional[str] = None

    # AWS
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@literattus.com"

    # File Upload
    MAX_FILE_SIZE: int = 5242880  # 5MB
    UPLOAD_DIR: str = "../public/uploads"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("DATABASE_URL", always=True)
    def construct_database_url(cls, v, values):
        """Construct DATABASE_URL from individual components."""
        # Always construct from components to ensure correct REDACTED encoding
        from urllib.parse import quote_plus
        
        db_host = values.get("DB_HOST", "localhost")
        db_port = values.get("DB_PORT", 3306)
        db_user = values.get("DB_USER", "root")
        db_REDACTED = values.get("DB_PASSWORD", "")
        db_name = values.get("DB_NAME", "literattus")
        
        # URL-encode REDACTED to handle special characters
        REDACTED_encoded = quote_plus(db_REDACTED) if db_REDACTED else ""
        
        return f"mysql+pymysql://{db_user}:{REDACTED_encoded}@{db_host}:{db_port}/{db_name}"

    @property
    def database_url_async(self) -> str:
        """Get async database URL."""
        return self.DATABASE_URL.replace("mysql+pymysql", "mysql+aiomysql")

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.APP_ENV == "development"


# Global settings instance
settings = Settings()

