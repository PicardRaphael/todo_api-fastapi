"""
Logging configuration for the Todo API.

This module provides configuration classes and enums for the logging system,
with support for different environments and output formats.
"""

import os
from enum import StrEnum
from typing import Optional, Dict, Any
from dataclasses import dataclass


class LogLevel(StrEnum):
    """Enumeration of available log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(StrEnum):
    """Enumeration of available log formats."""
    SIMPLE = "simple"
    DETAILED = "detailed"
    JSON = "json"
    STRUCTURED = "structured"


@dataclass
class LoggingConfig:
    """Configuration for the logging system."""

    # Basic configuration
    level: LogLevel = LogLevel.INFO
    format_type: LogFormat = LogFormat.STRUCTURED
    include_trace: bool = False

    # File logging
    log_to_file: bool = False
    log_file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

    # Console logging
    log_to_console: bool = True
    colored_output: bool = True

    # Structured logging
    app_name: str = "todo_api"
    environment: str = "development"
    include_request_id: bool = True

    # Performance
    async_logging: bool = False
    buffer_size: int = 1000

    # Filtering
    exclude_modules: list = None
    include_modules: list = None

    def __post_init__(self):
        """Post-initialization processing."""
        if self.exclude_modules is None:
            self.exclude_modules = [
                "uvicorn.access",
                "sqlalchemy.engine",
                "urllib3.connectionpool"
            ]

        if self.log_file_path is None and self.log_to_file:
            self.log_file_path = f"logs/{self.app_name}.log"

    @classmethod
    def from_environment(cls) -> "LoggingConfig":
        """Create logging configuration from environment variables."""
        return cls(
            level=LogLevel(os.getenv("LOG_LEVEL", LogLevel.INFO)),
            format_type=LogFormat(os.getenv("LOG_FORMAT", LogFormat.STRUCTURED)),
            include_trace=os.getenv("LOG_INCLUDE_TRACE", "false").lower() == "true",

            log_to_file=os.getenv("LOG_TO_FILE", "false").lower() == "true",
            log_file_path=os.getenv("LOG_FILE_PATH"),
            max_file_size=int(os.getenv("LOG_MAX_FILE_SIZE", 10 * 1024 * 1024)),
            backup_count=int(os.getenv("LOG_BACKUP_COUNT", 5)),

            log_to_console=os.getenv("LOG_TO_CONSOLE", "true").lower() == "true",
            colored_output=os.getenv("LOG_COLORED_OUTPUT", "true").lower() == "true",

            app_name=os.getenv("APP_NAME", "todo_api"),
            environment=os.getenv("ENVIRONMENT", "development"),
            include_request_id=os.getenv("LOG_INCLUDE_REQUEST_ID", "true").lower() == "true",

            async_logging=os.getenv("LOG_ASYNC", "false").lower() == "true",
            buffer_size=int(os.getenv("LOG_BUFFER_SIZE", 1000)),
        )

    @classmethod
    def for_development(cls) -> "LoggingConfig":
        """Create development logging configuration."""
        return cls(
            level=LogLevel.DEBUG,
            format_type=LogFormat.STRUCTURED,
            include_trace=True,
            log_to_console=True,
            colored_output=True,
            environment="development"
        )

    @classmethod
    def for_production(cls) -> "LoggingConfig":
        """Create production logging configuration."""
        return cls(
            level=LogLevel.INFO,
            format_type=LogFormat.JSON,
            include_trace=False,
            log_to_file=True,
            log_to_console=True,
            colored_output=False,
            environment="production",
            async_logging=True
        )

    @classmethod
    def for_testing(cls) -> "LoggingConfig":
        """Create testing logging configuration."""
        return cls(
            level=LogLevel.WARNING,
            format_type=LogFormat.SIMPLE,
            include_trace=False,
            log_to_console=False,
            log_to_file=False,
            environment="testing"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "level": self.level.value,
            "format_type": self.format_type.value,
            "include_trace": self.include_trace,
            "log_to_file": self.log_to_file,
            "log_file_path": self.log_file_path,
            "max_file_size": self.max_file_size,
            "backup_count": self.backup_count,
            "log_to_console": self.log_to_console,
            "colored_output": self.colored_output,
            "app_name": self.app_name,
            "environment": self.environment,
            "include_request_id": self.include_request_id,
            "async_logging": self.async_logging,
            "buffer_size": self.buffer_size,
            "exclude_modules": self.exclude_modules,
            "include_modules": self.include_modules,
        }