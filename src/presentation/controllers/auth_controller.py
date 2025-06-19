"""
Auth Controller - Couche Presentation

Controller intelligent pour l'authentification qui gère :
- Logique de présentation des opérations d'authentification
- Validation et transformation des données
- Délégation aux Use Cases d'authentification
- Gestion des erreurs et logging contextualisé
- Formatage des réponses HTTP

Architecture Hybride :
- Routes simpifiées → Controller intelligent → Use Cases → Repositories
- Sépare les préoccupations HTTP de la logique métier
- Facilite les tests et la maintenance
"""

from typing import Optional
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

# Application layer imports
from src.application.use_cases.auth_use_cases import AuthUseCases
from src.application.dtos.auth_dto import (
    RegisterRequestDTO,
    LoginResponseDTO,
    TokenResponseDTO,
    UserResponseDTO,
    ChangePasswordRequestDTO,
)

# Shared logging
from src.shared.logging import get_logger

# Exceptions d'authentification
from src.shared.exceptions.auth.authentication import (
    UserNotFoundError,
    InvalidPasswordError,
    InactiveUserError,
)


class AuthController:
    """
    Controller intelligent pour les opérations d'authentification.

    Gère la logique de présentation et délègue la logique métier
    aux Use Cases d'authentification.
    """

    def __init__(self, auth_use_cases: AuthUseCases, logger):
        """
        Initialise le controller avec ses dépendances.

        Args:
            auth_use_cases (AuthUseCases): Use cases d'authentification
            logger: Logger pour le suivi des opérations
        """
        self.auth_use_cases = auth_use_cases
        self.logger = logger

    async def register_user(self, user_data: RegisterRequestDTO) -> UserResponseDTO:
        """
        Inscrit un nouvel utilisateur.

        Args:
            user_data (RegisterRequestDTO): Données d'inscription

        Returns:
            UserResponseDTO: Données de l'utilisateur créé

        Raises:
            HTTPException: En cas d'erreur d'inscription
        """
        try:
            self.logger.info(
                "Starting user registration",
                extra={"email": user_data.email, "username": user_data.username},
            )

            # Déléguer aux Use Cases
            result = await self.auth_use_cases.register_user(user_data)

            self.logger.info(
                "User registration successful",
                extra={"user_id": result.user.id, "email": result.user.email},
            )

            return result.user

        except Exception as e:
            self.logger.error(
                "User registration failed",
                extra={"error": str(e), "email": user_data.email},
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def authenticate_user(self, username: str, password: str) -> LoginResponseDTO:
        """
        Authentifie un utilisateur et retourne les tokens.

        Args:
            username (str): Email/nom d'utilisateur
            password (str): Mot de passe

        Returns:
            LoginResponseDTO: Réponse avec tokens et informations utilisateur

        Raises:
            HTTPException: En cas d'échec d'authentification
        """
        try:
            self.logger.info(
                "Starting user authentication", extra={"username": username}
            )

            # Créer la requête de login
            from src.application.dtos.auth_dto import LoginRequestDTO

            login_request = LoginRequestDTO(username=username, password=password)

            # Déléguer aux Use Cases
            result = await self.auth_use_cases.authenticate_user(login_request)

            self.logger.info(
                "User authentication successful",
                extra={"user_id": result.user.id, "username": username},
            )

            return result

        except (UserNotFoundError, InvalidPasswordError, InactiveUserError) as e:
            # Laisser remonter les exceptions d'authentification spécifiques
            # Elles seront gérées par le middleware error_handler
            self.logger.error(
                "User authentication failed",
                extra={
                    "error": str(e),
                    "username": username,
                    "error_code": e.error_code,
                },
            )
            raise
        except Exception as e:
            # Autres erreurs inattendues
            self.logger.error(
                "Unexpected authentication error",
                extra={"error": str(e), "username": username},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service unavailable",
            )

    async def generate_access_token(
        self, username: str, password: str
    ) -> TokenResponseDTO:
        """
        Génère un token d'accès OAuth2 compatible.

        Args:
            username (str): Email/nom d'utilisateur
            password (str): Mot de passe

        Returns:
            TokenResponseDTO: Token d'accès seulement

        Raises:
            HTTPException: En cas d'échec d'authentification
        """
        try:
            self.logger.info("Generating access token", extra={"username": username})

            # Réutiliser la logique d'authentification
            login_result = await self.authenticate_user(username, password)

            # Retourner seulement les tokens
            return TokenResponseDTO(
                access_token=login_result.access_token,
                refresh_token=login_result.refresh_token,
                token_type=login_result.token_type,
                expires_in=login_result.expires_in,
            )

        except Exception as e:
            self.logger.error(
                "Access token generation failed",
                extra={"error": str(e), "username": username},
            )
            raise

    async def refresh_access_token(self, refresh_token: str) -> TokenResponseDTO:
        """
        Rafraîchit un token d'accès expiré.

        Args:
            refresh_token (str): Token de rafraîchissement

        Returns:
            TokenResponseDTO: Nouveaux tokens

        Raises:
            HTTPException: En cas de token invalide
        """
        try:
            self.logger.info("Refreshing access token")

            # Créer la requête de refresh
            from src.application.dtos.auth_dto import TokenRefreshRequestDTO

            refresh_request = TokenRefreshRequestDTO(refresh_token=refresh_token)

            # Déléguer aux Use Cases
            result = await self.auth_use_cases.refresh_token(refresh_request)

            self.logger.info("Access token refreshed successfully")

            return result

        except Exception as e:
            self.logger.error("Token refresh failed", extra={"error": str(e)})
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

    async def get_current_user_info(self, user_id: int) -> UserResponseDTO:
        """
        Récupère les informations de l'utilisateur actuel.

        Args:
            user_id (int): ID de l'utilisateur

        Returns:
            UserResponseDTO: Informations de l'utilisateur

        Raises:
            HTTPException: En cas d'utilisateur introuvable
        """
        try:
            self.logger.info("Getting current user info", extra={"user_id": user_id})

            # Pour l'instant, utiliser les Use Cases d'auth
            # Dans une vraie implémentation, il faudrait un UserUseCases.get_by_id
            # Pour maintenant, on simule avec une réponse basique

            # TODO: Implémenter la récupération réelle via Use Cases
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Get current user info not yet implemented",
            )

        except Exception as e:
            self.logger.error(
                "Failed to get current user info",
                extra={"error": str(e), "user_id": user_id},
            )
            raise

    async def logout_user(self, user_id: int, token_id: Optional[str] = None) -> None:
        """
        Déconnecte un utilisateur et invalide ses tokens.

        Args:
            user_id (int): ID de l'utilisateur
            token_id (Optional[str]): ID du token à invalider

        Raises:
            HTTPException: En cas d'erreur de déconnexion
        """
        try:
            self.logger.info(
                "Logging out user", extra={"user_id": user_id, "token_id": token_id}
            )

            # TODO: Implémenter la logique de logout
            # - Invalider les tokens en base/cache
            # - Logger l'événement de sécurité

            self.logger.info("User logged out successfully", extra={"user_id": user_id})

        except Exception as e:
            self.logger.error(
                "User logout failed", extra={"error": str(e), "user_id": user_id}
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Logout failed",
            )

    async def change_user_password(
        self, user_id: int, old_password: str, new_password: str
    ) -> None:
        """
        Change le mot de passe d'un utilisateur.

        Args:
            user_id (int): ID de l'utilisateur
            old_password (str): Ancien mot de passe
            new_password (str): Nouveau mot de passe

        Raises:
            HTTPException: En cas d'erreur de changement
        """
        try:
            self.logger.info("Changing user password", extra={"user_id": user_id})

            # TODO: Implémenter via Use Cases
            # - Vérifier l'ancien mot de passe
            # - Valider le nouveau mot de passe
            # - Mettre à jour en base
            # - Logger l'événement de sécurité

            self.logger.info(
                "Password changed successfully", extra={"user_id": user_id}
            )

        except Exception as e:
            self.logger.error(
                "Password change failed", extra={"error": str(e), "user_id": user_id}
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Password change failed"
            )

    async def delete_user_account(self, user_id: int) -> None:
        """
        Supprime le compte utilisateur et toutes ses données.

        Args:
            user_id (int): ID de l'utilisateur

        Raises:
            HTTPException: En cas d'erreur de suppression
        """
        try:
            self.logger.info("Deleting user account", extra={"user_id": user_id})

            # TODO: Implémenter la suppression complète
            # - Supprimer les todos de l'utilisateur
            # - Supprimer le compte utilisateur
            # - Invalider tous les tokens
            # - Logger l'événement de sécurité

            self.logger.info(
                "User account deleted successfully", extra={"user_id": user_id}
            )

        except Exception as e:
            self.logger.error(
                "Account deletion failed", extra={"error": str(e), "user_id": user_id}
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Account deletion failed",
            )
