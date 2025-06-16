"""
Simplified Todo Routes - Hybrid Architecture Implementation

This module demonstrates the simplified route approach where routes are thin
and delegate all business logic, validation, and error handling to intelligent controllers.

Key principles:
- Routes only handle HTTP routing and dependency injection
- Controllers handle all business coordination
- Middleware handles cross-cutting concerns
- Clean separation of HTTP concerns from business logic

Architecture benefits:
- Easier testing (test controllers independently)
- Better error handling consistency
- Cleaner code organization
- Improved maintainability
"""

from typing import List
from fastapi import (
    APIRouter,
    Path,
    Body,
    Depends,
    Security,
    Query,
    status,
    HTTPException,
)

# Application layer dependencies
from src.application.use_cases.todo_use_cases import TodoUseCases
from src.application.dtos.todo_dto import TodoCreateDTO, TodoUpdateDTO, TodoResponseDTO

# Presentation layer - intelligent controllers
from src.presentation.controllers.todo_controller import TodoController

# API dependencies
from src.api.dependencies import get_todo_use_cases, get_current_user
from src.infrastructure.auth.jwt_service import TokenData

# Shared logging for route-level monitoring
from src.shared.logging import get_logger

# Router configuration
router = APIRouter(prefix="/todos", tags=["todos-simplified"])
logger = get_logger("routes.todo_simplified")


# ===== DEPENDENCY INJECTION =====


async def get_todo_controller(
    use_cases: TodoUseCases = Depends(get_todo_use_cases),
) -> TodoController:
    """
    Dependency injection for TodoController.

    This creates a controller instance with all necessary dependencies
    injected, following the dependency inversion principle.
    """
    return TodoController(use_cases, logger)


# ===== SIMPLIFIED ROUTES =====


@router.get(
    "/all",
    response_model=List[TodoResponseDTO],
    status_code=status.HTTP_200_OK,
    summary="Get all todos (Simplified)",
    description="Retrieve all todos for the authenticated user - Delegates to controller",
)
async def get_all_todos(
    controller: TodoController = Depends(get_todo_controller),
    current_user: TokenData = Security(get_current_user, scopes=["todos:read"]),
):
    """
    Simplified route for retrieving all todos.

    This route demonstrates the hybrid architecture approach:
    - Minimal HTTP handling (just routing and auth)
    - Complete delegation to intelligent controller
    - Controller handles validation, error handling, logging
    - Middleware handles cross-cutting concerns

    The route is now purely focused on HTTP concerns.
    """
    # Validate user_id is not None for type safety
    if current_user.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user session"
        )
    user_id: int = current_user.user_id

    return await controller.get_all_todos(user_id)


@router.get(
    "/{todo_id}",
    response_model=TodoResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Get todo by ID (Simplified)",
    description="Retrieve a specific todo by ID - Delegates to controller",
)
async def get_todo(
    todo_id: int = Path(..., gt=0, description="ID of the todo to retrieve"),
    controller: TodoController = Depends(get_todo_controller),
    current_user: TokenData = Security(get_current_user, scopes=["todos:read"]),
):
    """
    Simplified route for retrieving a specific todo.

    Notice how clean this becomes:
    - No business logic in the route
    - No manual error handling (controller handles it)
    - No manual validation (controller handles it)
    - No manual logging (controller handles it)
    """
    # Validate user_id is not None for type safety
    if current_user.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user session"
        )
    user_id: int = current_user.user_id

    return await controller.get_todo_by_id(todo_id, user_id)


@router.post(
    "/create",
    response_model=TodoResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create todo (Simplified)",
    description="Create a new todo - Delegates to controller",
)
async def create_todo(
    todo_data: TodoCreateDTO = Body(..., description="Todo creation data"),
    controller: TodoController = Depends(get_todo_controller),
    current_user: TokenData = Security(get_current_user, scopes=["todos:write"]),
):
    """
    Simplified route for creating a todo.

    The controller handles:
    - Input validation
    - Business rule enforcement
    - Error handling and transformation
    - Success/failure logging
    - Performance monitoring
    """
    # Validate user_id is not None for type safety
    if current_user.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user session"
        )
    user_id: int = current_user.user_id

    return await controller.create_todo(todo_data, user_id)


@router.patch(
    "/{todo_id}",
    response_model=TodoResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Update todo (Simplified)",
    description="Update an existing todo - Delegates to controller",
)
async def update_todo(
    todo_id: int = Path(..., gt=0, description="ID of the todo to update"),
    todo_update: TodoUpdateDTO = Body(..., description="Update data"),
    controller: TodoController = Depends(get_todo_controller),
    current_user: TokenData = Security(get_current_user, scopes=["todos:write"]),
):
    """
    Simplified route for updating a todo.

    This demonstrates how simple routes become when using intelligent controllers.
    All the complexity is moved to the appropriate layer.
    """
    # Validate user_id is not None for type safety
    if current_user.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user session"
        )
    user_id: int = current_user.user_id

    return await controller.update_todo(todo_id, todo_update, user_id)


@router.delete(
    "/delete",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete todo (Simplified)",
    description="Delete a todo - Delegates to controller",
)
async def delete_todo(
    todo_id: int = Query(..., gt=0, alias="id", description="ID of the todo to delete"),
    controller: TodoController = Depends(get_todo_controller),
    current_user: TokenData = Security(get_current_user, scopes=["todos:delete"]),
):
    """
    Simplified route for deleting a todo.

    Notice the clean separation:
    - Route handles HTTP routing only
    - Controller handles business logic and validation
    - Middleware handles security and logging
    - Use cases handle domain logic
    """
    # Validate user_id is not None for type safety
    if current_user.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user session"
        )
    user_id: int = current_user.user_id

    await controller.delete_todo(todo_id, user_id)
    # No return needed for 204 status


# ===== ADDITIONAL SIMPLIFIED ROUTES =====


@router.patch(
    "/{todo_id}/complete",
    response_model=TodoResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Mark todo as complete (Simplified)",
    description="Mark a todo as completed - Delegates to controller",
)
async def complete_todo(
    todo_id: int = Path(..., gt=0, description="ID of the todo to complete"),
    controller: TodoController = Depends(get_todo_controller),
    current_user: TokenData = Security(get_current_user, scopes=["todos:write"]),
):
    """
    Simplified route for completing a todo.

    This shows how additional business operations become simple routes
    when using intelligent controllers.
    """
    # Validate user_id is not None for type safety
    if current_user.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user session"
        )
    user_id: int = current_user.user_id

    return await controller.complete_todo(todo_id, user_id)


@router.patch(
    "/{todo_id}/uncomplete",
    response_model=TodoResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Mark todo as incomplete (Simplified)",
    description="Mark a todo as incomplete - Delegates to controller",
)
async def uncomplete_todo(
    todo_id: int = Path(..., gt=0, description="ID of the todo to uncomplete"),
    controller: TodoController = Depends(get_todo_controller),
    current_user: TokenData = Security(get_current_user, scopes=["todos:write"]),
):
    """
    Simplified route for un-completing a todo.
    """
    # Validate user_id is not None for type safety
    if current_user.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user session"
        )
    user_id: int = current_user.user_id

    return await controller.uncomplete_todo(todo_id, user_id)


@router.get(
    "/priority/{priority}",
    response_model=List[TodoResponseDTO],
    status_code=status.HTTP_200_OK,
    summary="Get todos by priority (Simplified)",
    description="Retrieve todos by priority level - Delegates to controller",
)
async def get_todos_by_priority(
    priority: int = Path(..., ge=1, le=5, description="Priority level (1-5)"),
    controller: TodoController = Depends(get_todo_controller),
    current_user: TokenData = Security(get_current_user, scopes=["todos:read"]),
):
    """
    Simplified route for getting todos by priority.

    Even complex filtering becomes simple with intelligent controllers.
    """
    # Validate user_id is not None for type safety
    if current_user.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user session"
        )
    user_id: int = current_user.user_id

    return await controller.get_todos_by_priority(user_id, priority)


@router.get(
    "/completed",
    response_model=List[TodoResponseDTO],
    status_code=status.HTTP_200_OK,
    summary="Get completed todos (Simplified)",
    description="Retrieve all completed todos - Delegates to controller",
)
async def get_completed_todos(
    controller: TodoController = Depends(get_todo_controller),
    current_user: TokenData = Security(get_current_user, scopes=["todos:read"]),
):
    """
    Simplified route for getting completed todos.
    """
    # Validate user_id is not None for type safety
    if current_user.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user session"
        )
    user_id: int = current_user.user_id

    return await controller.get_completed_todos(user_id)


@router.get(
    "/pending",
    response_model=List[TodoResponseDTO],
    status_code=status.HTTP_200_OK,
    summary="Get pending todos (Simplified)",
    description="Retrieve all pending (incomplete) todos - Delegates to controller",
)
async def get_pending_todos(
    controller: TodoController = Depends(get_todo_controller),
    current_user: TokenData = Security(get_current_user, scopes=["todos:read"]),
):
    """
    Simplified route for getting pending todos.
    """
    # Validate user_id is not None for type safety
    if current_user.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user session"
        )
    user_id: int = current_user.user_id

    return await controller.get_pending_todos(user_id)
