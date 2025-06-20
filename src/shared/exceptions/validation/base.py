"""
Base validation exceptions for the Todo API.

This module contains the base ValidationError class that all
validation exceptions inherit from.
"""

from typing import Optional, Dict, Any, List
from ..base import BadRequestError, TodoAPIException


class ValidationError(BadRequestError):
    """Base class for validation-related errors."""

    def __init__(
        self, field: str, value: Any, reason: str, valid_format: Optional[str] = None
    ):
        """
        Initialize validation error.

        Args:
            field (str): Name of the field that failed validation
            value (Any): Value that failed validation
            reason (str): Reason why validation failed
            valid_format (str, optional): Description of valid format
        """
        detail = f"Validation failed for field '{field}': {reason}"
        if valid_format:
            detail += f". Valid format: {valid_format}"

        extra_data = {"field": field, "provided_value": str(value), "reason": reason}
        if valid_format:
            extra_data["valid_format"] = valid_format

        super().__init__(detail=detail, extra_data=extra_data)
        self.error_code = "VALIDATION_ERROR"


# MultipleValidationErrors removed - Pydantic already handles multiple field validation errors
