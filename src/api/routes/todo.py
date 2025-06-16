from typing import List
from fastapi import (
    APIRouter,
    Path,
    HTTPException,
    Security,
    status,
    Body,
    Depends,
    Query,
)

from src.application.use_cases.todo_use_cases import TodoUseCases
from src.application.dtos.todo_dto import TodoCreateDTO, TodoUpdateDTO, TodoResponseDTO
from src.api.dependencies import get_todo_use_cases, get_current_user
from src.infrastructure.security.jwt import TokenData

router = APIRouter(prefix="/todos", tags=["todos"])


@router.get(
    "/all",
    response_model=List[TodoResponseDTO],
    status_code=status.HTTP_200_OK,
)
async def get_all_todos(
    use_cases: TodoUseCases = Depends(get_todo_use_cases),
    current_user: TokenData = Security(get_current_user, scopes=["todos:read"]),
):
    return await use_cases.get_all_todos_by_owner(current_user.user_id)


@router.post(
    "/create",
    response_model=TodoResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
async def create_todo(
    use_cases: TodoUseCases = Depends(get_todo_use_cases),
    current_user: TokenData = Security(get_current_user, scopes=["todos:write"]),
    todo_create: TodoCreateDTO = Body(...),
):
    return await use_cases.create_todo(todo_create, current_user.user_id)


@router.get(
    "/{todo_id}",
    response_model=TodoResponseDTO,
    status_code=status.HTTP_200_OK,
)
async def get_todo(
    todo_id: int = Path(..., gt=0),
    use_cases: TodoUseCases = Depends(get_todo_use_cases),
    current_user: TokenData = Security(get_current_user, scopes=["todos:read"]),
):
    todo = await use_cases.get_todo_by_id_and_owner(todo_id, current_user.user_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found or not yours")
    return todo


@router.patch(
    "/{todo_id}",
    response_model=TodoResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Update todo partially",
    description="Update specific fields of a todo. Only provided fields will be updated."
)
async def update_todo(
    todo_id: int = Path(..., gt=0, description="ID of the todo to update"),
    use_cases: TodoUseCases = Depends(get_todo_use_cases),
    current_user: TokenData = Security(get_current_user, scopes=["todos:write"]),
    todo_update: TodoUpdateDTO = Body(..., description="Fields to update (all optional)"),
):
    todo = await use_cases.update_todo(todo_id, todo_update, current_user.user_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found or not yours")
    return todo


@router.delete(
    "/delete",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_todo(
    id: int = Query(..., gt=0),
    use_cases: TodoUseCases = Depends(get_todo_use_cases),
    current_user: TokenData = Security(get_current_user, scopes=["todos:delete"]),
):
    deleted = await use_cases.delete_todo(id, current_user.user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Todo not found or not yours")
