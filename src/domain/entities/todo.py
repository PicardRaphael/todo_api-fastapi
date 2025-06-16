from typing import Optional
from pydantic import BaseModel, Field


class Todo(BaseModel):
    """
    Entité représentant une tâche.
    """

    id: Optional[int] = Field(
        default=None, description="L'identifiant unique de la tâche"
    )
    title: str = Field(description="Le titre de la tâche")
    description: str = Field(default="", description="La description de la tâche")
    completed: bool = Field(
        default=False, description="Indique si la tâche est terminée"
    )
    priority: int = Field(default=1, description="Priorité de la tâche (1-5)")
    owner_id: Optional[int] = Field(
        default=None, description="L'identifiant de l'utilisateur propriétaire"
    )

    class Config:
        from_attributes = True  # Permet la conversion depuis les modèles SQLAlchemy
