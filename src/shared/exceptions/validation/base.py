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


class MultipleValidationErrors(TodoAPIException):
    """Exception raised when multiple validation errors occur."""

    def __init__(self, errors: List[ValidationError]):
        """
        Initialize multiple validation errors.

        Args:
            errors (List[ValidationError]): List of validation errors
        """
        error_details = []
        field_errors = {}

        for error in errors:
            error_details.append(f"- {error.detail}")
            field_name = error.extra_data.get("field", "unknown")
            field_errors[field_name] = {
                "message": error.detail,
                "error_code": error.error_code,
                "extra_data": error.extra_data,
            }

        detail = f"Multiple validation errors:\n" + "\n".join(error_details)

        super().__init__(
            status_code=400,
            detail=detail,
            error_code="MULTIPLE_VALIDATION_ERRORS",
            extra_data={"error_count": len(errors), "field_errors": field_errors},
        )
