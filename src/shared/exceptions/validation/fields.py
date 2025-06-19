"""
Field validation exceptions for the Todo API.

This module contains exceptions related to field-specific validation
like required fields, invalid choices, and numeric ranges.
"""

from typing import Any, Union, List
from .base import ValidationError


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
            valid_format="Must be provided and not null",
        )
        self.error_code = "REQUIRED_FIELD_MISSING"


class InvalidChoiceError(ValidationError):
    """Exception raised when value is not in allowed choices."""

    def __init__(self, field: str, value: Any, valid_choices: List[Any]):
        """
        Initialize invalid choice error.

        Args:
            field (str): Field name
            value (Any): Invalid value provided
            valid_choices (List[Any]): List of valid choices
        """
        choices_str = ", ".join(str(choice) for choice in valid_choices)

        super().__init__(
            field=field,
            value=value,
            reason=f"Invalid choice '{value}'",
            valid_format=f"Must be one of: {choices_str}",
        )

        self.extra_data.update(
            {"valid_choices": valid_choices, "provided_choice": value}
        )
        self.error_code = "INVALID_CHOICE"


class InvalidRangeError(ValidationError):
    """Exception raised when a numeric value is outside valid range."""

    def __init__(
        self,
        field: str,
        value: Union[int, float],
        min_value: Union[int, float],
        max_value: Union[int, float],
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
            valid_format=f"Between {min_value} and {max_value} (inclusive)",
        )

        self.extra_data.update(
            {"min_value": min_value, "max_value": max_value, "provided_value": value}
        )
        self.error_code = "INVALID_RANGE"
