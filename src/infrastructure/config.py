"""
Configuration Application - Couche Infrastructure (Clean Architecture)

Ce module centralise toute la configuration de l'application via des variables d'environnement.
Utilise Pydantic Settings pour une validation automatique et un typage strict.

Avantages de cette approche :
- Validation automatique des types et valeurs
- Documentation intégrée de chaque paramètre
- Pattern Singleton pour éviter les rechargements
- Séparation claire dev/test/prod via .env
- Type safety avec auto-complétion IDE

Sécurité :
- Variables sensibles (JWT_SECRET_KEY) via environnement uniquement
- Validation des URLs et formats
- Configuration différente par environnement
- Aucune valeur par défaut pour les secrets

Variables d'environnement requises dans .env :
DATABASE_URL, JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES,
APP_NAME, APP_VERSION, DEBUG, ENVIRONMENT, HOST, PORT,
CORS_ORIGINS, ALLOWED_HOSTS
"""

from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Configuration centralisée de l'application Todo API.

    Cette classe utilise Pydantic Settings pour charger et valider automatiquement
    toutes les variables d'environnement nécessaires au fonctionnement de l'application.

    Fonctionnalités :
    - Chargement automatique depuis .env
    - Validation des types et formats
    - Documentation intégrée de chaque paramètre
    - Gestion d'erreurs si variables manquantes
    - Support des listes JSON (CORS_ORIGINS, ALLOWED_HOSTS)

    Organisation par sections :
    - Database : Configuration base de données
    - JWT : Paramètres d'authentification
    - Application : Métadonnées de l'app
    - Server : Configuration serveur web
    - Security : Paramètres de sécurité
    """

    # ===== DATABASE CONFIGURATION =====

    DATABASE_URL: str
    """
    URL de connexion à la base de données.

    Formats supportés :
    - SQLite : "sqlite:///./todo.db"
    - PostgreSQL : "postgresql://user:pass@host:port/dbname"
    - MySQL : "mysql://user:pass@host:port/dbname"

    IMPORTANT : En production, utilisez une base robuste (PostgreSQL/MySQL)
    SQLite est recommandé uniquement pour le développement.

    Example .env:
        DATABASE_URL=sqlite:///./todo.db
    """

    # ===== JWT AUTHENTICATION =====

    JWT_SECRET_KEY: str
    """
    Clé secrète pour signer les tokens JWT.

    SÉCURITÉ CRITIQUE :
    - Doit être aléatoire et complexe (256 bits minimum)
    - JAMAIS dans le code source ou git
    - Différente par environnement (dev/test/prod)
    - Si compromise, tous les tokens deviennent invalides

    Génération recommandée :
        openssl rand -hex 32

    Example .env:
        JWT_SECRET_KEY=8f4e7b2a9c1d6f3b7e9a2c5d8f1b4e7a2c5d8f1b4e7a2c5d8f1b4e7a2c5d8f1b
    """

    JWT_ALGORITHM: str
    """
    Algorithme de signature JWT.

    Valeurs recommandées :
    - "HS256" : HMAC SHA-256 (symétrique, simple)
    - "RS256" : RSA SHA-256 (asymétrique, scalable)

    HS256 est suffisant pour la plupart des cas d'usage.

    Example .env:
        JWT_ALGORITHM=HS256
    """

    ACCESS_TOKEN_EXPIRE_MINUTES: int
    """
    Durée de validité des tokens JWT en minutes.

    Recommandations par contexte :
    - Développement : 60-480 minutes (1-8h)
    - Production : 15-30 minutes
    - Applications critiques : 5-15 minutes

    Plus court = plus sécurisé mais plus d'interruptions utilisateur.

    Example .env:
        ACCESS_TOKEN_EXPIRE_MINUTES=30
    """

    # ===== APPLICATION METADATA =====

    APP_NAME: str
    """
    Nom de l'application affiché dans la documentation Swagger.

    Utilisé pour :
    - Documentation API automatique
    - Logs et monitoring
    - Headers HTTP personnalisés

    Example .env:
        APP_NAME="Todo API"
    """

    APP_VERSION: str
    """
    Version de l'application (semantic versioning recommandé).

    Format recommandé : MAJOR.MINOR.PATCH
    - MAJOR : Changements incompatibles
    - MINOR : Nouvelles fonctionnalités compatibles
    - PATCH : Corrections de bugs

    Example .env:
        APP_VERSION="1.0.0"
    """

    DEBUG: bool
    """
    Mode debug pour le développement.

    En mode debug :
    - Logs détaillés et traces d'erreur
    - Auto-reload sur changement de code
    - Validation moins stricte
    - Endpoints de debug exposés

    ATTENTION : TOUJOURS False en production !

    Example .env:
        DEBUG=true  # dev
        DEBUG=false # prod
    """

    ENVIRONMENT: str
    """
    Environnement d'exécution (dev/test/staging/prod).

    Utilisé pour :
    - Logs et monitoring contextuels
    - Configuration spécifique par env
    - Sécurité adaptative
    - Debugging conditionnel

    Example .env:
        ENVIRONMENT=development
    """

    # ===== SERVER CONFIGURATION =====

    HOST: str
    """
    Adresse IP d'écoute du serveur.

    Valeurs communes :
    - "127.0.0.1" : Localhost uniquement (dev)
    - "0.0.0.0" : Toutes interfaces (prod, Docker)
    - IP spécifique : Interface réseau dédiée

    Example .env:
        HOST=127.0.0.1  # dev
        HOST=0.0.0.0    # prod
    """

    PORT: int
    """
    Port d'écoute du serveur HTTP.

    Conventions :
    - 8000 : Valeur par défaut FastAPI/uvicorn
    - 80 : HTTP standard (nécessite privilèges)
    - 443 : HTTPS standard (nécessite privilèges)
    - 5000-9999 : Ports développement

    Example .env:
        PORT=8000
    """

    # ===== SECURITY CONFIGURATION =====

    CORS_ORIGINS: List[str]
    """
    Liste des origines autorisées pour CORS (Cross-Origin Resource Sharing).

    Format JSON array en string pour compatibilité .env

    Permet aux applications frontend de différents domaines d'appeler l'API.

    Valeurs recommandées :
    - Dev : ["*"] (toutes origines, pratique mais non sécurisé)
    - Prod : ["https://monapp.com", "https://admin.monapp.com"]

    ATTENTION : "*" en production = faille de sécurité !

    Example .env:
        CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
    """

    ALLOWED_HOSTS: List[str]
    """
    Liste des hôtes autorisés à accéder à l'API (protection Host header injection).

    Protection contre les attaques par manipulation du header "Host".

    Doit inclure tous les domaines légitimes de l'application :
    - Domaine principal
    - Sous-domaines autorisés
    - Domaines de test/staging
    - Load balancer interne

    Example .env:
        ALLOWED_HOSTS=["localhost", "127.0.0.1", "api.monapp.com"]
    """

    class Config:
        """
        Configuration Pydantic Settings.

        env_file : Fichier à charger automatiquement (.env)
        case_sensitive : Respecter la casse des variables (recommandé)
        """
        env_file = ".env"           # Charge automatiquement le fichier .env
        case_sensitive = True       # Les noms de variables sont sensibles à la casse


@lru_cache()
def get_settings() -> Settings:
    """
    Factory singleton pour obtenir la configuration de l'application.

    Pattern Singleton avec @lru_cache :
    - Une seule instance créée pendant toute la durée de vie de l'app
    - Évite les rechargements coûteux du fichier .env
    - Thread-safe par design
    - Peut être mockée facilement pour les tests

    Utilisation dans l'application :
    - Injection de dépendance FastAPI
    - Import direct pour la configuration au démarrage
    - Tests unitaires avec override

    Returns:
        Settings: Instance unique de la configuration validée

    Raises:
        ValidationError: Si des variables requises sont manquantes
        ValueError: Si des valeurs ont un format invalide

    Example:
        settings = get_settings()
        print(f"App: {settings.APP_NAME} v{settings.APP_VERSION}")

    Note:
        Le cache peut être vidé pour les tests avec :
        get_settings.cache_clear()
    """
    return Settings()
