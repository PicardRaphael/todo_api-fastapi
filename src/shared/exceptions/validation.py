"""
Validation exceptions for the Todo API.

This module contains exceptions related to data validation,
input sanitization, and format checking.
"""

from typing import Optional, Dict, Any, Union, List
from .base import TodoAPIException, BadRequestError


class ValidationError(BadRequestError):
    """Base class for validation-related errors."""

    def __init__(
        self,
        field: str,
        value: Any,
        reason: str,
        valid_format: Optional[str] = None
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

        extra_data = {
            "field": field,
            "provided_value": str(value),
            "reason": reason
        }
        if valid_format:
            extra_data["valid_format"] = valid_format

        super().__init__(
            detail=detail,
            extra_data=extra_data
        )
        self.error_code = "VALIDATION_ERROR"


class InvalidEmailError(ValidationError):
    """Exception raised when email format is invalid."""

    def __init__(self, email: str):
        """
        Initialize invalid email error.

        Args:
            email (str): Invalid email address
        """
        super().__init__(
            field="email",
            value=email,
            reason="Invalid email format",
            valid_format="user@example.com"
        )
        self.error_code = "INVALID_EMAIL"


class WeakPasswordError(ValidationError):
    """Exception raised when password doesn't meet security requirements."""

    def __init__(
        self,
        password_length: int,
        requirements: List[str],
        missing_requirements: List[str]
    ):
        """
        Initialize weak password error.

        Args:
            password_length (int): Length of the provided password
            requirements (List[str]): All password requirements
            missing_requirements (List[str]): Requirements that are not met
        """
        reason = f"Password doesn't meet security requirements: {', '.join(missing_requirements)}"

        super().__init__(
            field="password",
            value="[HIDDEN]",
            reason=reason,
            valid_format="At least 8 characters with uppercase, lowercase, digit and special character"
        )

        self.extra_data.update({
            "password_length": password_length,
            "all_requirements": requirements,
            "missing_requirements": missing_requirements
        })
        self.error_code = "WEAK_PASSWORD"


class InvalidUsernameError(ValidationError):
    """Exception raised when username format is invalid."""

    def __init__(self, username: str, reason: str = "Invalid username format"):
        """
        Initialize invalid username error.

        Args:
            username (str): Invalid username
            reason (str): Specific reason why username is invalid
        """
        super().__init__(
            field="username",
            value=username,
            reason=reason,
            valid_format="3-20 characters, letters, numbers and underscores only"
        )
        self.error_code = "INVALID_USERNAME"


class InvalidDateFormatError(ValidationError):
    """Exception raised when date format is invalid."""

    def __init__(self, date_value: str, field_name: str = "date"):
        """
        Initialize invalid date format error.

        Args:
            date_value (str): Invalid date value
            field_name (str): Name of the date field
        """
        super().__init__(
            field=field_name,
            value=date_value,
            reason="Invalid date format",
            valid_format="YYYY-MM-DD or ISO 8601 format"
        )
        self.error_code = "INVALID_DATE_FORMAT"


class ValueTooLongError(ValidationError):
    """Exception raised when a string value exceeds maximum length."""

    def __init__(
        self,
        field: str,
        value: str,
        max_length: int,
        actual_length: Optional[int] = None
    ):
        """
        Initialize value too long error.

        Args:
            field (str): Field name
            value (str): Value that is too long
            max_length (int): Maximum allowed length
            actual_length (int, optional): Actual length of the value
        """
        actual_length = actual_length or len(value)

        super().__init__(
            field=field,
            value=value[:50] + "..." if len(value) > 50 else value,
            reason=f"Value too long. Maximum {max_length} characters allowed, got {actual_length}",
            valid_format=f"Maximum {max_length} characters"
        )

        self.extra_data.update({
            "max_length": max_length,
            "actual_length": actual_length
        })
        self.error_code = "VALUE_TOO_LONG"


class ValueTooShortError(ValidationError):
    """Exception raised when a string value is below minimum length."""

    def __init__(
        self,
        field: str,
        value: str,
        min_length: int,
        actual_length: Optional[int] = None
    ):
        """
        Initialize value too short error.

        Args:
            field (str): Field name
            value (str): Value that is too short
            min_length (int): Minimum required length
            actual_length (int, optional): Actual length of the value
        """
        actual_length = actual_length or len(value)

        super().__init__(
            field=field,
            value=value,
            reason=f"Value too short. Minimum {min_length} characters required, got {actual_length}",
            valid_format=f"Minimum {min_length} characters"
        )

        self.extra_data.update({
            "min_length": min_length,
            "actual_length": actual_length
        })
        self.error_code = "VALUE_TOO_SHORT"


class InvalidRangeError(ValidationError):
    """Exception raised when a numeric value is outside valid range."""

    def __init__(
        self,
        field: str,
        value: Union[int, float],
        min_value: Union[int, float],
        max_value: Union[int, float]
    ):
        """
        Initialize invalid range error.

        Args:
            field (str): Field name
            value (int|float): Value that is out of range
            min_value (int|float): Minimum allowed value
            max_value (int|float): Maximum allowed value
        """
        super().__init__(
            field=field,
            value=value,
            reason=f"Value {value} is outside valid range",
            valid_format=f"Between {min_value} and {max_value} (inclusive)"
        )

        self.extra_data.update({
            "min_value": min_value,
            "max_value": max_value,
            "provided_value": value
        })
        self.error_code = "INVALID_RANGE"


class RequiredFieldMissingError(ValidationError):
    """Exception raised when a required field is missing."""

    def __init__(self, field: str):
        """
        Initialize required field missing error.

        Args:
            field (str): Name of the missing required field
        """
        super().__init__(
            field=field,
            value="<missing>",
            reason="Required field is missing",
            valid_format="Must be provided and not null"
        )
        self.error_code = "REQUIRED_FIELD_MISSING"


class InvalidChoiceError(ValidationError):
    """Exception raised when value is not in allowed choices."""

    def __init__(
        self,
        field: str,
        value: Any,
        valid_choices: List[Any]
    ):
        """
        Initialize invalid choice error.

        Args:
            field (str): Field name
            value (Any): Invalid value provided
            valid_choices (List[Any]): List of valid choices
        """
        choices_str = ', '.join(str(choice) for choice in valid_choices)

        super().__init__(
            field=field,
            value=value,
            reason=f"Invalid choice '{value}'",
            valid_format=f"Must be one of: {choices_str}"
        )

        self.extra_data.update({
            "valid_choices": valid_choices,
            "provided_choice": value
        })
        self.error_code = "INVALID_CHOICE"


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
                "extra_data": error.extra_data
            }

        detail = f"Multiple validation errors:\n" + "\n".join(error_details)

        super().__init__(
            status_code=400,
            detail=detail,
            error_code="MULTIPLE_VALIDATION_ERRORS",
            extra_data={
                "error_count": len(errors),
                "field_errors": field_errors
            }
        )