"""Configuration settings for the application."""

import os
from functools import lru_cache


class Config:
    """Database and app configuration."""
    
    # Database settings
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "factory")
    
    # Server settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"


class LoggingConfig:
    """Logging configuration."""
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


@lru_cache()
def get_config():
    """Get application configuration."""
    return Config()


@lru_cache()
def get_logging_config():
    """Get logging configuration."""
    return LoggingConfig()
