"""
Custom formatters for the Todo API logging system.

This module provides various log formatters including JSON, structured,
and colored formatters for different environments and use cases.
"""

import json
import logging
import traceback
from datetime import datetime, timezone
from typing import Dict, Any, Optional


class BaseFormatter(logging.Formatter):
    """Base formatter with common functionality."""

    def __init__(self, include_trace: bool = False, app_name: str = "todo_api"):
        super().__init__()
        self.include_trace = include_trace
        self.app_name = app_name

    def get_base_record_data(self, record: logging.LogRecord) -> Dict[str, Any]:
        """Extract base data from log record."""
        data = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "app_name": self.app_name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception information if present
        if record.exc_info:
            data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info) if self.include_trace else None
            }

        # Add extra fields from record
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in {
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                'thread', 'threadName', 'processName', 'process', 'message'
            }:
                extra_fields[key] = value

        if extra_fields:
            data["extra"] = extra_fields

        return data


class JSONFormatter(BaseFormatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        data = self.get_base_record_data(record)

        try:
            return json.dumps(data, default=str, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            # Fallback to string representation if JSON serialization fails
            fallback_data = {
                "timestamp": data["timestamp"],
                "level": data["level"],
                "logger": data["logger"],
                "message": str(record.getMessage()),
                "error": f"JSON serialization failed: {e}"
            }
            return json.dumps(fallback_data, ensure_ascii=False)


class StructuredFormatter(BaseFormatter):
    """Structured formatter for human-readable logs."""

    def __init__(self, colored: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.colored = colored
        self.colors = {
            'DEBUG': '\033[36m',     # Cyan
            'INFO': '\033[32m',      # Green
            'WARNING': '\033[33m',   # Yellow
            'ERROR': '\033[31m',     # Red
            'CRITICAL': '\033[35m',  # Magenta
            'RESET': '\033[0m'       # Reset
        } if colored else {}

    def format(self, record: logging.LogRecord) -> str:
        """Format log record in structured human-readable format."""
        data = self.get_base_record_data(record)

        # Build the main log line
        timestamp = data["timestamp"]
        level = data["level"]
        logger = data["logger"]
        message = data["message"]
        location = f"{data['module']}.{data['function']}:{data['line']}"

        # Apply colors if enabled
        if self.colored and level in self.colors:
            level_colored = f"{self.colors[level]}{level}{self.colors['RESET']}"
            logger_colored = f"\033[90m{logger}\033[0m"  # Gray
            location_colored = f"\033[90m{location}\033[0m"  # Gray
        else:
            level_colored = level
            logger_colored = logger
            location_colored = location

        # Main log line
        log_line = f"[{timestamp}] {level_colored:>8} {logger_colored:<20} | {message}"

        # Add location information
        if self.include_trace or level in ['ERROR', 'CRITICAL']:
            log_line += f" ({location_colored})"

        # Add exception information if present
        if "exception" in data and data["exception"]["message"]:
            log_line += f"\n  Exception: {data['exception']['type']}: {data['exception']['message']}"
            if self.include_trace and data["exception"]["traceback"]:
                traceback_lines = data["exception"]["traceback"]
                for line in traceback_lines:
                    log_line += f"\n    {line.rstrip()}"

        # Add extra fields if present
        if "extra" in data:
            for key, value in data["extra"].items():
                log_line += f"\n  {key}: {value}"

        return log_line


class SimpleFormatter(BaseFormatter):
    """Simple formatter for minimal logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record in simple format."""
        timestamp = datetime.fromtimestamp(record.created, tz=timezone.utc).strftime("%H:%M:%S")
        return f"[{timestamp}] {record.levelname}: {record.getMessage()}"


class DetailedFormatter(BaseFormatter):
    """Detailed formatter with full context."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with full details."""
        data = self.get_base_record_data(record)

        lines = []
        lines.append(f"Timestamp: {data['timestamp']}")
        lines.append(f"Level: {data['level']}")
        lines.append(f"Logger: {data['logger']}")
        lines.append(f"Module: {data['module']}")
        lines.append(f"Function: {data['function']}")
        lines.append(f"Line: {data['line']}")
        lines.append(f"Message: {data['message']}")

        if "exception" in data:
            lines.append(f"Exception Type: {data['exception']['type']}")
            lines.append(f"Exception Message: {data['exception']['message']}")
            if self.include_trace and data["exception"]["traceback"]:
                lines.append("Traceback:")
                for line in data["exception"]["traceback"]:
                    lines.append(f"  {line.rstrip()}")

        if "extra" in data:
            lines.append("Extra Fields:")
            for key, value in data["extra"].items():
                lines.append(f"  {key}: {value}")

        return "\n".join(lines)


class RequestFormatter(BaseFormatter):
    """Formatter specialized for HTTP request logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record for HTTP requests."""
        data = self.get_base_record_data(record)

        # Extract request information from extra fields
        extra = data.get("extra", {})
        method = extra.get("method", "UNKNOWN")
        url = extra.get("url", "UNKNOWN")
        status_code = extra.get("status_code", "UNKNOWN")
        duration = extra.get("duration", "UNKNOWN")
        user_id = extra.get("user_id", "Anonymous")
        request_id = extra.get("request_id", "UNKNOWN")

        # Format request log
        timestamp = data["timestamp"]
        message = data["message"]

        log_line = (
            f"[{timestamp}] REQUEST | "
            f"{method:>6} {url:<30} | "
            f"Status: {status_code:>3} | "
            f"Duration: {duration:>8} | "
            f"User: {user_id:>10} | "
            f"ID: {request_id} | "
            f"{message}"
        )

        return log_line


def get_formatter(format_type: str, **kwargs) -> logging.Formatter:
    """
    Factory function to get formatter by type.

    Args:
        format_type (str): Type of formatter to create
        **kwargs: Additional arguments for formatter

    Returns:
        logging.Formatter: Configured formatter instance
    """
    formatters = {
        "simple": SimpleFormatter,
        "detailed": DetailedFormatter,
        "json": JSONFormatter,
        "structured": StructuredFormatter,
        "request": RequestFormatter,
    }

    formatter_class = formatters.get(format_type, StructuredFormatter)
    return formatter_class(**kwargs)