"""
Main logger module for the Todo API.

This module provides the main logging functionality including logger setup,
configuration, and utility functions for structured logging.
"""

import logging
import logging.handlers
import os
from typing import Optional, Dict, Any
from pathlib import Path

from .config import LoggingConfig, LogLevel, LogFormat
from .formatters import get_formatter


# Global logger registry
_loggers: Dict[str, logging.Logger] = {}
_logging_configured: bool = False


def setup_logging(config: Optional[LoggingConfig] = None) -> None:
    """
    Setup the logging system with the provided configuration.

    Args:
        config (LoggingConfig, optional): Logging configuration.
                                        If None, loads from environment.
    """
    global _logging_configured

    if config is None:
        config = LoggingConfig.from_environment()

    # Clear any existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Set root logger level
    root_logger.setLevel(config.level.value)

    # Configure console handler
    if config.log_to_console:
        console_handler = logging.StreamHandler()
        console_formatter = get_formatter(
            config.format_type.value,
            colored=config.colored_output,
            include_trace=config.include_trace,
            app_name=config.app_name
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(config.level.value)
        root_logger.addHandler(console_handler)

    # Configure file handler
    if config.log_to_file and config.log_file_path:
        # Create log directory if it doesn't exist
        log_path = Path(config.log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Use rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            filename=config.log_file_path,
            maxBytes=config.max_file_size,
            backupCount=config.backup_count,
            encoding='utf-8'
        )

        # Use JSON format for file logging in production
        file_format = LogFormat.JSON if config.environment == "production" else config.format_type
        file_formatter = get_formatter(
            file_format.value,
            colored=False,  # No colors in file logs
            include_trace=config.include_trace,
            app_name=config.app_name
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(config.level.value)
        root_logger.addHandler(file_handler)

    # Configure module-specific loggers
    _configure_module_loggers(config)

    _logging_configured = True

    # Log the configuration
    logger = get_logger("logging.setup")
    logger.info(
        "Logging system configured",
        extra={
            "config": config.to_dict(),
            "handlers_count": len(root_logger.handlers)
        }
    )


def _configure_module_loggers(config: LoggingConfig) -> None:
    """Configure loggers for specific modules."""

    # Silence noisy third-party loggers
    for module in config.exclude_modules:
        module_logger = logging.getLogger(module)
        module_logger.setLevel(logging.WARNING)
        module_logger.propagate = False

    # Configure specific modules if specified
    if config.include_modules:
        for module in config.include_modules:
            module_logger = logging.getLogger(module)
            module_logger.setLevel(config.level.value)


def get_logger(name: str, **kwargs) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name (str): Name of the logger (usually module name)
        **kwargs: Additional context to include in logs

    Returns:
        logging.Logger: Configured logger instance
    """
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)

    # Add a custom method for structured logging
    def log_structured(level: int, message: str, **extra_data):
        """Log with structured extra data."""
        combined_extra = {**kwargs, **extra_data}
        logger.log(level, message, extra=combined_extra)

    def debug_structured(message: str, **extra_data):
        """Debug log with structured data."""
        log_structured(logging.DEBUG, message, **extra_data)

    def info_structured(message: str, **extra_data):
        """Info log with structured data."""
        log_structured(logging.INFO, message, **extra_data)

    def warning_structured(message: str, **extra_data):
        """Warning log with structured data."""
        log_structured(logging.WARNING, message, **extra_data)

    def error_structured(message: str, **extra_data):
        """Error log with structured data."""
        log_structured(logging.ERROR, message, **extra_data)

    def critical_structured(message: str, **extra_data):
        """Critical log with structured data."""
        log_structured(logging.CRITICAL, message, **extra_data)

    # Add custom methods to logger
    logger.debug_structured = debug_structured
    logger.info_structured = info_structured
    logger.warning_structured = warning_structured
    logger.error_structured = error_structured
    logger.critical_structured = critical_structured
    logger.log_structured = log_structured

    _loggers[name] = logger
    return logger


def log_request(
    method: str,
    url: str,
    status_code: int,
    duration: float,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None,
    **extra_data
) -> None:
    """
    Log HTTP request information.

    Args:
        method (str): HTTP method
        url (str): Request URL
        status_code (int): HTTP status code
        duration (float): Request duration in seconds
        user_id (str, optional): User ID if authenticated
        request_id (str, optional): Unique request ID
        **extra_data: Additional request data
    """
    logger = get_logger("http.requests")

    # Determine log level based on status code
    if status_code >= 500:
        log_level = logging.ERROR
    elif status_code >= 400:
        log_level = logging.WARNING
    else:
        log_level = logging.INFO

    message = f"{method} {url} - {status_code}"

    extra_info = {
        "method": method,
        "url": url,
        "status_code": status_code,
        "duration": f"{duration:.3f}s",
        "user_id": user_id or "Anonymous",
        "request_id": request_id,
        **extra_data
    }

    logger.log(log_level, message, extra=extra_info)


def log_exception(
    logger: logging.Logger,
    message: str,
    exception: Exception,
    **extra_data
) -> None:
    """
    Log exception with full context.

    Args:
        logger (logging.Logger): Logger instance
        message (str): Error message
        exception (Exception): Exception instance
        **extra_data: Additional context data
    """
    extra_info = {
        "exception_type": type(exception).__name__,
        "exception_message": str(exception),
        **extra_data
    }

    logger.error(
        f"{message}: {exception}",
        exc_info=True,
        extra=extra_info
    )


def log_performance(
    operation: str,
    duration: float,
    threshold: float = 1.0,
    **extra_data
) -> None:
    """
    Log performance metrics for operations.

    Args:
        operation (str): Name of the operation
        duration (float): Duration in seconds
        threshold (float): Threshold for slow operation warning
        **extra_data: Additional performance data
    """
    logger = get_logger("performance")

    extra_info = {
        "operation": operation,
        "duration": f"{duration:.3f}s",
        "threshold": f"{threshold:.3f}s",
        **extra_data
    }

    if duration > threshold:
        logger.warning(
            f"Slow operation detected: {operation} took {duration:.3f}s",
            extra=extra_info
        )
    else:
        logger.debug(
            f"Operation completed: {operation} took {duration:.3f}s",
            extra=extra_info
        )


def log_security_event(
    event_type: str,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[str] = None,
    **extra_data
) -> None:
    """
    Log security-related events.

    Args:
        event_type (str): Type of security event
        user_id (str, optional): User ID involved
        ip_address (str, optional): IP address of the request
        details (str, optional): Additional details
        **extra_data: Additional security context
    """
    logger = get_logger("security")

    message = f"Security event: {event_type}"
    if details:
        message += f" - {details}"

    extra_info = {
        "event_type": event_type,
        "user_id": user_id,
        "ip_address": ip_address,
        "details": details,
        **extra_data
    }

    logger.warning(message, extra=extra_info)


def get_current_config() -> Optional[LoggingConfig]:
    """
    Get the current logging configuration.

    Returns:
        LoggingConfig: Current configuration or None if not configured
    """
    if not _logging_configured:
        return None

    # This is a simplified version - in a full implementation,
    # we'd store the actual config used during setup
    return LoggingConfig.from_environment()


def is_configured() -> bool:
    """
    Check if logging has been configured.

    Returns:
        bool: True if logging is configured
    """
    return _logging_configured


def shutdown_logging() -> None:
    """Shutdown the logging system and clean up resources."""
    global _logging_configured, _loggers

    # Flush and close all handlers
    logging.shutdown()

    # Clear logger registry
    _loggers.clear()
    _logging_configured = False