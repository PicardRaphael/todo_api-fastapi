from typing import Generator, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes, HTTPBearer
from sqlalchemy.orm import Session

from src.infrastructure.database.sqlite.config import get_db
from src.infrastructure.database.sqlite.repository import SQLiteTodoRepository
from src.infrastructure.database.sqlite.user_repository import SQLiteUserRepository
from src.application.use_cases.todo_use_cases import TodoUseCases
from src.infrastructure.security.jwt import verify_token, TokenData

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/token",  # URL absolue
    scopes={
        "todos:read": "Read todos",
        "todos:write": "Create and update todos",
        "todos:delete": "Delete todos",
        "admin": "Admin access",
    },
)

# Alternative schema for easier testing in Swagger UI
bearer_scheme = HTTPBearer()


async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
) -> TokenData:
    """
    Dépendance pour obtenir l'utilisateur actuel à partir du token JWT.
    Vérifie également les scopes d'autorisation.
    """
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    token_data = verify_token(token)

    # Récupérer l'utilisateur pour obtenir son ID
    user_repo = SQLiteUserRepository(db)
    user = await user_repo.get_user_by_username(token_data.username)
    if not user:
        raise credentials_exception

    # Ajouter l'user_id au token_data
    token_data.user_id = user.id

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return token_data


def get_todo_use_cases(
    db: Annotated[Session, Depends(get_db)],
) -> TodoUseCases:
    """
    Dépendance pour obtenir les cas d'utilisation des todos.
    Requiert une authentification valide.
    """
    todo_repository = SQLiteTodoRepository(db)
    return TodoUseCases(todo_repository)
