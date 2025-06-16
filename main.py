from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src.api.routes import todo, auth
from src.infrastructure.config import get_settings
from src.infrastructure.database.sqlite.models import Base
from src.infrastructure.database.sqlite.config import engine
from src.infrastructure.security.timeout_middleware import TimeoutMiddleware

# Charger les configurations
settings = get_settings()

# Créer l'application FastAPI
app = FastAPI(
    title=settings.APP_NAME, version=settings.APP_VERSION, debug=settings.DEBUG
)

# Configuration des middlewares de sécurité
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

app.add_middleware(TimeoutMiddleware, timeout=10)

# Inclure les routers
app.include_router(auth.router)
app.include_router(todo.router)

# Créer les tables de la base de données au démarrage
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG
    )
