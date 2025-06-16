"""
Base controller for the Todo API presentation layer.

This module provides the foundation for all controllers with common functionality
including error handling, logging, validation, and response formatting.
"""

import time
from abc import ABC
from typing import TypeVar, Generic, Optional, Any, Dict
from logging import Logger

from src.shared.exceptions import (
    TodoAPIException,
    InternalServerError,
    ValidationError,
    BadRequestError
)
from src.shared.logging import get_logger, log_exception, log_performance

T = TypeVar('T')


class BaseController(ABC, Generic[T]):
    """
    Base controller providing common functionality for all controllers.

    This class implements cross-cutting concerns that all controllers need:
    - Structured logging with context
    - Consistent error handling and transformation
    - Performance monitoring
    - Input validation helpers
    - Response formatting

    Generic type T represents the main entity type this controller handles.
    """

    def __init__(self, controller_name: str, logger: Optional[Logger] = None):
        """
        Initialize base controller.

        Args:
            controller_name (str): Name of the controller for logging
            logger (Logger, optional): Logger instance. If None, creates one.
        """
        self.controller_name = controller_name
        self.logger = logger or get_logger(f"controllers.{controller_name}")

    def _log_operation_start(self, operation: str, **context) -> float:
        """
        Log the start of an operation and return start time.

        Args:
            operation (str): Name of the operation
            **context: Additional context for logging

        Returns:
            float: Start time for performance measurement
        """
        start_time = time.time()
        self.logger.info_structured(
            f"Starting {operation}",
            operation=operation,
            controller=self.controller_name,
            **context
        )
        return start_time

    def _log_operation_success(
        self,
        operation: str,
        start_time: float,
        result_summary: str = "Success",
        **context
    ) -> None:
        """
        Log successful completion of an operation.

        Args:
            operation (str): Name of the operation
            start_time (float): When the operation started
            result_summary (str): Summary of the result
            **context: Additional context for logging
        """
        duration = time.time() - start_time

        self.logger.info_structured(
            f"Completed {operation}: {result_summary}",
            operation=operation,
            controller=self.controller_name,
            duration=f"{duration:.3f}s",
            result=result_summary,
            **context
        )

        # Log performance if operation is slow
        log_performance(
            operation=f"{self.controller_name}.{operation}",
            duration=duration,
            threshold=1.0,  # 1 second threshold
            **context
        )

    def _log_operation_error(
        self,
        operation: str,
        start_time: float,
        error: Exception,
        **context
    ) -> None:
        """
        Log operation error with full context.

        Args:
            operation (str): Name of the operation
            start_time (float): When the operation started
            error (Exception): Exception that occurred
            **context: Additional context for logging
        """
        duration = time.time() - start_time

        log_exception(
            self.logger,
            f"Failed {operation}",
            error,
            operation=operation,
            controller=self.controller_name,
            duration=f"{duration:.3f}s",
            **context
        )

    def handle_use_case_result(
        self,
        operation: str,
        result: T,
        start_time: float,
        success_message: Optional[str] = None,
        **context
    ) -> T:
        """
        Handle successful use case result with logging and validation.

        Args:
            operation (str): Name of the operation
            result (T): Result from use case
            start_time (float): When operation started
            success_message (str, optional): Custom success message
            **context: Additional context for logging

        Returns:
            T: The validated result
        """
        if result is None:
            self._log_operation_error(
                operation,
                start_time,
                ValueError("Use case returned None result"),
                **context
            )
            raise InternalServerError("Operation completed but returned no result")

        message = success_message or f"{operation} completed successfully"
        self._log_operation_success(operation, start_time, message, **context)
        return result

    def handle_error(
        self,
        operation: str,
        error: Exception,
        start_time: float,
        **context
    ) -> None:
        """
        Handle and transform errors consistently.

        Args:
            operation (str): Name of the operation that failed
            error (Exception): Exception that occurred
            start_time (float): When operation started
            **context: Additional error context

        Raises:
            TodoAPIException: Appropriate API exception
        """
        self._log_operation_error(operation, start_time, error, **context)

        # If it's already a TodoAPIException, re-raise it
        if isinstance(error, TodoAPIException):
            raise error

        # Transform common exceptions
        if isinstance(error, ValueError):
            raise BadRequestError(
                detail=str(error),
                extra_data={"original_error": type(error).__name__, **context}
            )

        if isinstance(error, (TypeError, AttributeError)):
            raise ValidationError(
                field="unknown",
                value="unknown",
                reason=str(error)
            )

        # For unknown errors, wrap in InternalServerError
        raise InternalServerError(
            detail="An unexpected error occurred",
            original_error=error,
            extra_data={"operation": operation, **context}
        )

    def validate_positive_integer(
        self,
        value: Any,
        field_name: str,
        min_value: int = 1
    ) -> int:
        """
        Validate that a value is a positive integer.

        Args:
            value (Any): Value to validate
            field_name (str): Name of the field for error messages
            min_value (int): Minimum allowed value

        Returns:
            int: Validated integer value

        Raises:
            ValidationError: If validation fails
        """
        try:
            int_value = int(value)
            if int_value < min_value:
                raise ValidationError(
                    field=field_name,
                    value=value,
                    reason=f"Must be >= {min_value}",
                    valid_format=f"Integer >= {min_value}"
                )
            return int_value
        except (ValueError, TypeError):
            raise ValidationError(
                field=field_name,
                value=value,
                reason="Must be a valid integer",
                valid_format="Integer"
            )

    def validate_string_length(
        self,
        value: str,
        field_name: str,
        min_length: int = 0,
        max_length: Optional[int] = None
    ) -> str:
        """
        Validate string length constraints.

        Args:
            value (str): String to validate
            field_name (str): Name of the field
            min_length (int): Minimum length
            max_length (int, optional): Maximum length

        Returns:
            str: Validated string

        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(value, str):
            raise ValidationError(
                field=field_name,
                value=value,
                reason="Must be a string",
                valid_format="String"
            )

        length = len(value.strip())

        if length < min_length:
            raise ValidationError(
                field=field_name,
                value=value,
                reason=f"Too short (minimum {min_length} characters)",
                valid_format=f"String with {min_length}-{max_length or 'unlimited'} characters"
            )

        if max_length and length > max_length:
            raise ValidationError(
                field=field_name,
                value=value,
                reason=f"Too long (maximum {max_length} characters)",
                valid_format=f"String with {min_length}-{max_length} characters"
            )

        return value.strip()

    def validate_priority(self, priority: Any) -> int:
        """
        Validate todo priority value.

        Args:
            priority (Any): Priority value to validate

        Returns:
            int: Validated priority (1-5)

        Raises:
            ValidationError: If priority is invalid
        """
        try:
            priority_int = int(priority)
            if priority_int < 1 or priority_int > 5:
                raise ValidationError(
                    field="priority",
                    value=priority,
                    reason="Priority must be between 1 and 5",
                    valid_format="Integer between 1 (low) and 5 (critical)"
                )
            return priority_int
        except (ValueError, TypeError):
            raise ValidationError(
                field="priority",
                value=priority,
                reason="Priority must be a valid integer",
                valid_format="Integer between 1 and 5"
            )

    def create_context(self, **kwargs) -> Dict[str, Any]:
        """
        Create logging context with controller information.

        Args:
            **kwargs: Additional context fields

        Returns:
            Dict[str, Any]: Context dictionary for logging
        """
        return {
            "controller": self.controller_name,
            **kwargs
        }

    async def execute_operation(
        self,
        operation_name: str,
        operation_func,
        *args,
        success_message: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Execute an operation with consistent error handling and logging.

        Args:
            operation_name (str): Name of the operation
            operation_func: Function to execute
            *args: Arguments for the function
            success_message (str, optional): Custom success message
            **kwargs: Keyword arguments for the function and logging context

        Returns:
            Any: Result of the operation
        """
        # Separate logging context from function kwargs
        logging_context = kwargs.pop('_logging_context', {})
        context = self.create_context(**logging_context)

        start_time = self._log_operation_start(operation_name, **context)

        try:
            # Execute the operation
            if hasattr(operation_func, '__call__'):
                if hasattr(operation_func, '__await__'):
                    # Async function
                    result = await operation_func(*args, **kwargs)
                else:
                    # Sync function
                    result = operation_func(*args, **kwargs)
            else:
                raise ValueError(f"Invalid operation function: {operation_func}")

            # Handle successful result
            return self.handle_use_case_result(
                operation_name,
                result,
                start_time,
                success_message,
                **context
            )

        except Exception as error:
            self.handle_error(operation_name, error, start_time, **context)