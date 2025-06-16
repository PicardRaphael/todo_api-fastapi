"""
Point d'entrée principal de l'application Todo API.
Ce fichier configure FastAPI avec tous les middlewares de sécurité,
inclut les routes API, et initialise la base de données.

Architecture utilisée : Clean Architecture
- Domain Layer : Entités et interfaces (src/domain/)
- Application Layer : Use cases et DTOs (src/application/)
- Infrastructure Layer : Implémentations concrètes (src/infrastructure/)
- API Layer : Routes et endpoints REST (src/api/)
"""

# Imports FastAPI et middlewares de sécurité
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Gestion CORS pour les appels cross-origin
from fastapi.middleware.trustedhost import TrustedHostMiddleware  # Protection contre les attaques Host header

# Imports des routes API (couche présentation)
from src.api.routes import todo, auth

# Imports infrastructure (configuration et base de données)
from src.infrastructure.config import get_settings
from src.infrastructure.database.sqlite.models import Base
from src.infrastructure.database.sqlite.config import engine
from src.infrastructure.security.timeout_middleware import TimeoutMiddleware

# ===== CONFIGURATION DE L'APPLICATION =====

# Charger les configurations depuis les variables d'environnement
# Le pattern Singleton (@lru_cache) garantit une seule instance des settings
settings = get_settings()

# Créer l'instance FastAPI avec métadonnées depuis la configuration
app = FastAPI(
    title=settings.APP_NAME,        # Nom affiché dans la doc Swagger
    version=settings.APP_VERSION,   # Version API
    debug=settings.DEBUG            # Mode debug (reload auto, logs détaillés)
)

# ===== CONFIGURATION DES MIDDLEWARES DE SÉCURITÉ =====
# Les middlewares sont appliqués dans l'ordre inverse d'ajout (LIFO)

# 1. CORS Middleware - Gestion des requêtes cross-origin
# Permet aux applications frontend (React, Vue, etc.) d'appeler l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,    # Domaines autorisés à faire des requêtes
    allow_credentials=True,                  # Autorise l'envoi de cookies/tokens
    allow_methods=["*"],                     # Toutes les méthodes HTTP autorisées
    allow_headers=["*"],                     # Tous les headers autorisés
)

# 2. TrustedHost Middleware - Protection contre les attaques Host header injection
# Vérifie que le header "Host" correspond aux domaines autorisés
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,   # Liste des hôtes de confiance
)

# 3. Timeout Middleware - Protection contre les requêtes qui traînent
# Annule automatiquement les requêtes qui dépassent 10 secondes
app.add_middleware(TimeoutMiddleware, timeout=10)

# ===== ENREGISTREMENT DES ROUTES API =====

# Routes d'authentification : /register, /token
# Gère l'inscription, la connexion et la génération de tokens JWT
app.include_router(auth.router)

# Routes de gestion des todos : /todos/*
# CRUD complet avec authentification et autorisation par scopes
app.include_router(todo.router)

# ===== INITIALISATION DE LA BASE DE DONNÉES =====

# Création automatique des tables SQLite au démarrage de l'application
# Base.metadata contient toutes les définitions de tables (User, Todo)
# Cette ligne exécute les CREATE TABLE si les tables n'existent pas
Base.metadata.create_all(bind=engine)

# ===== POINT D'ENTRÉE POUR LE DÉVELOPPEMENT =====

# Ce bloc s'exécute uniquement si le script est lancé directement (python main.py)
# En production, on utilise plutôt : uvicorn main:app --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn

    # Démarrage du serveur ASGI avec uvicorn
    uvicorn.run(
        "main:app",              # Chemin vers l'application FastAPI
        host=settings.HOST,      # Adresse d'écoute (127.0.0.1 = localhost)
        port=settings.PORT,      # Port d'écoute (défaut: 8000)
        reload=settings.DEBUG    # Auto-reload en mode debug (pratique pour le dev)
    )
