from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

from src.infrastructure.config import get_settings

settings = get_settings()

# Création du moteur SQLAlchemy avec l'URL de la base de données depuis les variables d'environnement
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # Nécessaire pour SQLite
)

# Création de la session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe de base pour les modèles SQLAlchemy
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dépendance pour obtenir une session de base de données.
    Assure que la session est fermée après utilisation.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
