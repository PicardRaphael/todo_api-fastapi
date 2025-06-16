"""
Routes d'Authentification - Couche API (Clean Architecture)

Ce module expose les endpoints REST pour l'authentification des utilisateurs :
- POST /register : Inscription d'un nouvel utilisateur
- POST /token : Connexion et génération de token JWT

Sécurité implémentée :
- Validation Pydantic des données entrantes
- Hachage bcrypt des mots de passe (jamais en clair)
- Tokens JWT avec expiration et scopes
- Vérification unicité email/username
- Mise à jour timestamp de dernière connexion

Principes Clean Architecture :
- Dépend uniquement de la couche Application (Use Cases)
- Convertit entre HTTP et objets métier (DTOs)
- Gère les codes de statut et erreurs HTTP
- Ne connaît pas les détails de persistance
"""

from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

# Imports Infrastructure (injectés via dépendances)
from src.infrastructure.database.sqlite.config import get_db
from src.infrastructure.database.sqlite.user_repository import SQLiteUserRepository
from src.infrastructure.security.jwt import (
    Token,
    create_access_token,
    verify_password,
)
from src.infrastructure.config import get_settings

# Imports Domain (entités métier)
from src.domain.entities.user import User

# Imports Application (DTOs et Use Cases)
from src.application.dtos.user_dto import UserCreateDTO, UserResponseDTO
from src.application.use_cases.user_use_cases import UserUseCases

# Configuration globale de l'application
settings = get_settings()

# Router FastAPI avec tag pour regrouper dans la documentation
router = APIRouter(tags=["authentication"])


# ===== INJECTION DE DÉPENDANCES =====

async def get_user_use_cases(db: Session = Depends(get_db)):
    """
    Factory pour créer une instance des Use Cases User.

    Cette fonction implémente l'injection de dépendance :
    1. Récupère une session de base de données
    2. Crée le repository SQLite avec cette session
    3. Injecte le repository dans les Use Cases

    Pattern Dependency Injection :
    - Respecte l'inversion de dépendance (DIP)
    - Facilite les tests (mock des dépendances)
    - Permet de changer d'implémentation facilement

    Args:
        db (Session): Session SQLAlchemy injectée par FastAPI

    Returns:
        UserUseCases: Instance configurée avec le repository SQLite
    """
    repo = SQLiteUserRepository(db)
    return UserUseCases(repo)


# ===== ENDPOINTS D'AUTHENTIFICATION =====

@router.post(
    "/register",
    response_model=UserResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Inscription d'un nouvel utilisateur",
    description="Crée un compte utilisateur avec email, username et mot de passe"
)
async def register_user(
    user_data: UserCreateDTO,
    use_cases: UserUseCases = Depends(get_user_use_cases)
):
    """
    Endpoint d'inscription pour créer un nouveau compte utilisateur.

    🔄 WORKFLOW D'INSCRIPTION :
    1. Validation des données avec UserCreateDTO (Pydantic)
    2. Vérification unicité email et username
    3. Hachage sécurisé du mot de passe (bcrypt)
    4. Création de l'utilisateur en base
    5. Retour des données publiques (sans mot de passe)

    🛡️ SÉCURITÉ :
    - Email et username uniques (prévient les doublons)
    - Mot de passe hashé avec bcrypt (jamais stocké en clair)
    - Validation format email avec EmailStr
    - Données sensibles filtrées dans la réponse

    Args:
        user_data (UserCreateDTO): Données d'inscription validées par Pydantic
        use_cases (UserUseCases): Use cases injectés pour la logique métier

    Returns:
        UserResponseDTO: Données publiques de l'utilisateur créé (sans mot de passe)

    Raises:
        HTTPException 400: Email déjà utilisé
        HTTPException 400: Username déjà pris
        HTTPException 400: Erreur de validation
        HTTPException 500: Erreur serveur

    Example:
        POST /register
        {
            "email": "user@example.com",
            "username": "monusername",
            "password": "motdepasse123"
        }
    """
    # Vérification unicité email - prévient les comptes multiples
    if await use_cases.get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Vérification unicité username - prévient les conflits d'identification
    if await use_cases.get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    try:
        # Création de l'utilisateur via Use Cases (logique métier)
        created_user = await use_cases.register_user(user_data)

        # Conversion entité → DTO pour la réponse (filtre les données sensibles)
        return UserResponseDTO.model_validate(created_user)

    except ValueError as e:
        # Erreurs métier remontées par les Use Cases
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/token",
    response_model=Token,
    summary="Connexion utilisateur",
    description="Authentifie un utilisateur et retourne un token JWT avec scopes"
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    use_cases: UserUseCases = Depends(get_user_use_cases),
):
    """
    Endpoint de connexion générant un token JWT pour l'authentification.

    🔄 WORKFLOW DE CONNEXION :
    1. Récupération utilisateur par username
    2. Vérification mot de passe avec bcrypt
    3. Contrôle statut actif du compte
    4. Mise à jour timestamp dernière connexion
    5. Génération token JWT avec scopes
    6. Retour du token avec type "bearer"

    🛡️ SÉCURITÉ JWT :
    - Token avec expiration configurable (défaut 30min)
    - Scopes granulaires pour les permissions
    - Signature cryptographique (HS256)
    - Format Bearer standard OAuth2

    📊 SCOPES INCLUS :
    - todos:read : Lecture des todos
    - todos:write : Création/modification des todos
    - todos:delete : Suppression des todos
    - admin : Privilèges administrateur (si superuser)

    Args:
        form_data (OAuth2PasswordRequestForm): Formulaire standard OAuth2
            (username + password via form-data)
        use_cases (UserUseCases): Use cases pour la logique d'authentification

    Returns:
        Token: Objet contenant access_token et token_type

    Raises:
        HTTPException 401: Identifiants incorrects
        HTTPException 400: Compte désactivé
        HTTPException 500: Erreur serveur

    Example:
        POST /token
        Content-Type: application/x-www-form-urlencoded

        username=monusername&password=motdepasse123

    Response:
        {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "token_type": "bearer"
        }
    """
    # Étape 1 : Récupération de l'utilisateur
    user = await use_cases.get_user_by_username(form_data.username)

    # Étape 2 : Vérification des identifiants
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},  # Standard OAuth2
        )

    # Étape 3 : Vérification statut du compte
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # Étape 4 : Mise à jour dernière connexion (audit + sécurité)
    if user.id is not None:
        await use_cases.update_last_login(user.id)

    # Étape 5 : Configuration des scopes (permissions)
    scopes = ["todos:read", "todos:write", "todos:delete"]
    if user.is_superuser:
        scopes.append("admin")  # Privilèges administrateur

    # Étape 6 : Génération du token JWT
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,  # Subject = identifiant utilisateur
            "scopes": scopes       # Permissions accordées
        },
        expires_delta=access_token_expires
    )

    # Retour du token au format OAuth2 standard
    return Token(access_token=access_token, token_type="bearer")
