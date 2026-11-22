import os
from pathlib import Path
from dotenv import load_dotenv

import sys
import site

basedir = Path(__file__).resolve().parent
load_dotenv(basedir / ".env")

# Auto-add local .venv site-packages to sys.path so the app runs smoothly with any python executable
for venv_site in (basedir / ".venv" / "lib").glob("python*/site-packages"):
    if venv_site.exists():
        site.addsitedir(str(venv_site))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "jobhelper_default_secret_key_982348239478")
    
    # Ensure SQLite URI always resolves to an absolute path in the project root
    db_env = os.getenv("DATABASE_URL", "").strip()
    if not db_env or db_env == "sqlite:///jobhelper.db":
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'jobhelper.db'}"
    else:
        SQLALCHEMY_DATABASE_URI = db_env

    # Normalize postgres:// to postgresql:// for modern SQLAlchemy
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads & Security
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 5 * 1024 * 1024))  # 5MB
    ALLOWED_EXTENSIONS = {"pdf", "docx"}
    UPLOAD_FOLDER = basedir / "app" / "static" / "uploads"
    PORTFOLIO_OUTPUT_FOLDER = basedir / "generated_portfolios"

    # Session & Cookie Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False").lower() in ("true", "1")
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours

    # SMTP Email Configuration
    SMTP_HOST = os.getenv("SMTP_HOST", "").strip()
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "True").lower() in ("true", "1", "yes")
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "").strip()
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").strip()
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "JobHelper AI <noreply@jobhelper.local>").strip()

    # OTP Security Parameters
    OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", 5))
    OTP_RESEND_COOLDOWN_SECONDS = int(os.getenv("OTP_RESEND_COOLDOWN_SECONDS", 60))
    OTP_MAX_ATTEMPTS = int(os.getenv("OTP_MAX_ATTEMPTS", 5))

    # Matching Weights (Configurable)
    MATCH_WEIGHT_SKILLS = 0.50
    MATCH_WEIGHT_TFIDF = 0.25
    MATCH_WEIGHT_EXPERIENCE = 0.15
    MATCH_WEIGHT_EDUCATION = 0.10

    # Optional AI integration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    SERVER_NAME = "localhost"


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
