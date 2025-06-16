"""
Routes Todo - Couche API (Clean Architecture)

Ce module expose les endpoints REST pour la gestion des todos avec authentification JWT.
Tous les endpoints nécessitent une authentification valide et des scopes spécifiques.

Endpoints disponibles :
- GET /todos/all : Liste toutes les todos de l'utilisateur
- GET /todos/{id} : Récupère une todo spécifique
- POST /todos/create : Crée une nouvelle todo
- PATCH /todos/{id} : Mise à jour partielle d'une todo
- DELETE /todos/delete?id={id} : Supprime une todo

Sécurité implémentée :
- Authentification JWT obligatoire sur tous les endpoints
- Scopes granulaires (read, write, delete)
- Isolation stricte par propriétaire (owner_id)
- Validation des données avec Pydantic
- Codes d'erreur HTTP appropriés

Principes Clean Architecture :
- Dépend uniquement de la couche Application (Use Cases)
- Convertit HTTP ↔ DTOs métier
- Gère authentification et autorisation
- Ne connaît pas les détails de persistance
"""

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

# Imports Application (Use Cases et DTOs)
from src.application.use_cases.todo_use_cases import TodoUseCases
from src.application.dtos.todo_dto import TodoCreateDTO, TodoUpdateDTO, TodoResponseDTO

# Imports API (dépendances et sécurité)
from src.api.dependencies import get_todo_use_cases, get_current_user
from src.infrastructure.security.jwt import TokenData

# Router avec préfixe pour grouper tous les endpoints todos
router = APIRouter(prefix="/todos", tags=["todos"])


# ===== ENDPOINTS DE CONSULTATION =====

@router.get(
    "/all",
    response_model=List[TodoResponseDTO],
    status_code=status.HTTP_200_OK,
    summary="Liste toutes mes todos",
    description="Récupère toutes les todos appartenant à l'utilisateur connecté"
)
async def get_all_todos(
    use_cases: TodoUseCases = Depends(get_todo_use_cases),
    current_user: TokenData = Security(get_current_user, scopes=["todos:read"]),
):
    """
    Endpoint pour récupérer toutes les todos de l'utilisateur connecté.

    🛡️ SÉCURITÉ :
    - Authentification JWT obligatoire
    - Scope 'todos:read' requis
    - Isolation par owner_id (utilisateur ne voit que ses todos)

    🔄 WORKFLOW :
    1. Validation du token JWT et du scope
    2. Extraction user_id depuis le token
    3. Récupération des todos via Use Cases
    4. Conversion entités → DTOs pour la réponse

    Args:
        use_cases (TodoUseCases): Use cases injectés pour la logique métier
        current_user (TokenData): Données utilisateur extraites du JWT

    Returns:
        List[TodoResponseDTO]: Liste des todos de l'utilisateur (peut être vide)

    Raises:
        HTTPException 401: Token invalide ou expiré
        HTTPException 403: Scope insuffisant

    Example:
        GET /todos/all
        Authorization: Bearer eyJ0eXAiOiJKV1Q...

        Response: [
            {
                "id": 1,
                "title": "Ma première tâche",
                "description": "Description de la tâche",
                "priority": 2,
                "completed": false,
                "owner_id": 1
            }
        ]
    """
    return await use_cases.get_all_todos_by_owner(current_user.user_id)


@router.get(
    "/{todo_id}",
    response_model=TodoResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Récupère une todo spécifique",
    description="Récupère le détail d'une todo par son ID (seulement si elle appartient à l'utilisateur)"
)
async def get_todo(
    todo_id: int = Path(..., gt=0, description="ID de la todo à récupérer"),
    use_cases: TodoUseCases = Depends(get_todo_use_cases),
    current_user: TokenData = Security(get_current_user, scopes=["todos:read"]),
):
    """
    Endpoint pour récupérer une todo spécifique par son ID.

    🛡️ SÉCURITÉ :
    - Authentification JWT obligatoire
    - Scope 'todos:read' requis
    - Vérification double : ID + owner_id
    - Erreur 404 si todo inexistante OU appartenant à un autre utilisateur

    🔄 WORKFLOW :
    1. Validation du token JWT et du scope
    2. Validation de l'ID (doit être > 0)
    3. Récupération sécurisée via Use Cases (ID + owner_id)
    4. Retour 404 si non trouvée ou pas propriétaire

    Args:
        todo_id (int): Identifiant de la todo (validé > 0)
        use_cases (TodoUseCases): Use cases pour la logique métier
        current_user (TokenData): Données utilisateur du JWT

    Returns:
        TodoResponseDTO: Données complètes de la todo

    Raises:
        HTTPException 401: Token invalide
        HTTPException 403: Scope insuffisant
        HTTPException 404: Todo inexistante ou pas propriétaire
        HTTPException 422: ID invalide (≤ 0)

    Example:
        GET /todos/1
        Authorization: Bearer eyJ0eXAiOiJKV1Q...
    """
    todo = await use_cases.get_todo_by_id_and_owner(todo_id, current_user.user_id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found or not yours"
        )
    return todo


# ===== ENDPOINTS DE MODIFICATION =====

@router.post(
    "/create",
    response_model=TodoResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Crée une nouvelle todo",
    description="Crée une nouvelle todo avec les données fournies"
)
async def create_todo(
    use_cases: TodoUseCases = Depends(get_todo_use_cases),
    current_user: TokenData = Security(get_current_user, scopes=["todos:write"]),
    todo_create: TodoCreateDTO = Body(..., description="Données de la todo à créer"),
):
    """
    Endpoint pour créer une nouvelle todo.

    🛡️ SÉCURITÉ :
    - Authentification JWT obligatoire
    - Scope 'todos:write' requis
    - owner_id automatiquement assigné depuis le token

    📝 VALIDATION :
    - Titre : 3-50 caractères obligatoire
    - Description : 3-100 caractères obligatoire
    - Priorité : 1-5 (défaut: 1)
    - Completed : défaut false

    🔄 WORKFLOW :
    1. Validation du token JWT et du scope
    2. Validation des données avec TodoCreateDTO
    3. Création via Use Cases avec owner_id automatique
    4. Retour de la todo créée avec son ID généré

    Args:
        use_cases (TodoUseCases): Use cases pour la logique métier
        current_user (TokenData): Données utilisateur du JWT
        todo_create (TodoCreateDTO): Données validées de la todo

    Returns:
        TodoResponseDTO: Todo créée avec ID généré

    Raises:
        HTTPException 401: Token invalide
        HTTPException 403: Scope insuffisant
        HTTPException 422: Données invalides

    Example:
        POST /todos/create
        Authorization: Bearer eyJ0eXAiOiJKV1Q...

        {
            "title": "Nouvelle tâche",
            "description": "Description de la tâche",
            "priority": 3,
            "completed": false
        }
    """
    return await use_cases.create_todo(todo_create, current_user.user_id)


@router.patch(
    "/{todo_id}",
    response_model=TodoResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Mise à jour partielle d'une todo",
    description="Met à jour seulement les champs fournis. Les autres restent inchangés."
)
async def update_todo(
    todo_id: int = Path(..., gt=0, description="ID de la todo à modifier"),
    use_cases: TodoUseCases = Depends(get_todo_use_cases),
    current_user: TokenData = Security(get_current_user, scopes=["todos:write"]),
    todo_update: TodoUpdateDTO = Body(..., description="Champs à mettre à jour (tous optionnels)"),
):
    """
    Endpoint pour la mise à jour partielle d'une todo (PATCH).

    🎯 FONCTIONNALITÉ CLÉ : MISE À JOUR PARTIELLE
    - Seuls les champs fournis sont mis à jour
    - Les champs non fournis restent inchangés
    - Idéal pour les interfaces utilisateur granulaires

    🛡️ SÉCURITÉ :
    - Authentification JWT obligatoire
    - Scope 'todos:write' requis
    - Vérification propriété (ID + owner_id)
    - Erreur 404 si inexistante ou pas propriétaire

    📝 CHAMPS OPTIONNELS :
    - title : 3-50 caractères si fourni
    - description : 3-100 caractères si fourni
    - priority : 1-5 si fourni
    - completed : boolean si fourni

    🔄 WORKFLOW :
    1. Validation du token JWT et du scope
    2. Validation de l'ID (> 0)
    3. Validation des champs fournis avec TodoUpdateDTO
    4. Mise à jour partielle via Use Cases
    5. Retour de la todo mise à jour

    Args:
        todo_id (int): Identifiant de la todo (> 0)
        use_cases (TodoUseCases): Use cases pour la logique métier
        current_user (TokenData): Données utilisateur du JWT
        todo_update (TodoUpdateDTO): Champs à mettre à jour (optionnels)

    Returns:
        TodoResponseDTO: Todo mise à jour avec nouveaux champs

    Raises:
        HTTPException 401: Token invalide
        HTTPException 403: Scope insuffisant
        HTTPException 404: Todo inexistante ou pas propriétaire
        HTTPException 422: Données invalides

    Examples:
        # Changer seulement le titre
        PATCH /todos/1
        {"title": "Nouveau titre"}

        # Marquer comme terminée
        PATCH /todos/1
        {"completed": true}

        # Changer titre et priorité
        PATCH /todos/1
        {"title": "Urgent!", "priority": 5}
    """
    todo = await use_cases.update_todo(todo_id, todo_update, current_user.user_id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found or not yours"
        )
    return todo


# ===== ENDPOINTS DE SUPPRESSION =====

@router.delete(
    "/delete",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprime une todo",
    description="Supprime définitivement une todo (action irréversible)"
)
async def delete_todo(
    id: int = Query(..., gt=0, description="ID de la todo à supprimer"),
    use_cases: TodoUseCases = Depends(get_todo_use_cases),
    current_user: TokenData = Security(get_current_user, scopes=["todos:delete"]),
):
    """
    Endpoint pour supprimer définitivement une todo.

    ⚠️ SUPPRESSION DÉFINITIVE : Cette action est irréversible !

    🛡️ SÉCURITÉ :
    - Authentification JWT obligatoire
    - Scope 'todos:delete' requis (différent de write)
    - Vérification propriété avant suppression
    - Erreur 404 si inexistante ou pas propriétaire

    🔄 WORKFLOW :
    1. Validation du token JWT et du scope spécial 'delete'
    2. Validation de l'ID (> 0)
    3. Vérification propriété via Use Cases
    4. Suppression définitive si validée
    5. Retour 204 No Content (succès sans données)

    Args:
        id (int): Identifiant de la todo à supprimer (> 0)
        use_cases (TodoUseCases): Use cases pour la logique métier
        current_user (TokenData): Données utilisateur du JWT

    Returns:
        None: Statut 204 No Content (pas de body de réponse)

    Raises:
        HTTPException 401: Token invalide
        HTTPException 403: Scope insuffisant (besoin todos:delete)
        HTTPException 404: Todo inexistante ou pas propriétaire
        HTTPException 422: ID invalide (≤ 0)

    Example:
        DELETE /todos/delete?id=1
        Authorization: Bearer eyJ0eXAiOiJKV1Q...

        Response: 204 No Content (pas de body)

    Note:
        Le scope 'todos:delete' est distinct de 'todos:write' pour
        permettre un contrôle granulaire des permissions.
    """
    deleted = await use_cases.delete_todo(id, current_user.user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found or not yours"
        )
