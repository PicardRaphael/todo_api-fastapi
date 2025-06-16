from typing import Optional
from pydantic import BaseModel, Field, validator


class TodoBaseDTO(BaseModel):
    title: str = Field(
        min_length=3, max_length=50, description="The title of the todo item"
    )
    description: str = Field(
        min_length=3,
        max_length=100,
        description="Detailed description of the todo item",
    )
    priority: int = Field(gt=0, lt=6, default=1, description="Priority level (1-5)")
    completed: bool = Field(default=False, description="Whether the todo is completed")


class TodoCreateDTO(TodoBaseDTO):
    pass


class TodoUpdateDTO(BaseModel):
    """DTO pour la mise à jour partielle d'une todo. Tous les champs sont optionnels."""
    title: Optional[str] = Field(
        None, min_length=3, max_length=50, description="The title of the todo item"
    )
    description: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        description="Detailed description of the todo item",
    )
    priority: Optional[int] = Field(None, gt=0, lt=6, description="Priority level (1-5)")
    completed: Optional[bool] = Field(None, description="Whether the todo is completed")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Updated title",
                "priority": 3
            }
        }


class TodoResponseDTO(TodoBaseDTO):
    id: int = Field(description="The unique identifier of the todo item")
    owner_id: Optional[int] = Field(
        default=None, description="The owner of the todo item"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Complete project",
                "description": "Finish the FastAPI project implementation",
                "priority": 3,
                "completed": False,
                "owner_id": 1,
            }
        }
