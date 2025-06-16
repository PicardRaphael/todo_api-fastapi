# 🚀 FastAPI Hybrid Architecture - Todo API

Une implémentation sophistiquée d'architecture hybride combinant **Clean Architecture** et **MVC** pour créer une API FastAPI robuste, maintenable et prête pour la production.

## 📋 Table des Matières

- [Vue d'ensemble](#-vue-densemble)
- [Architecture](#-architecture)
- [Fonctionnalités](#-fonctionnalités)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [API Documentation](#-api-documentation)
- [Tests et Démonstration](#-tests-et-démonstration)
- [Structure du Projet](#-structure-du-projet)
- [Développement](#-développement)
- [Déploiement](#-déploiement)

## 🎯 Vue d'ensemble

Cette application démontre une **architecture hybride avancée** qui résout les problèmes communs des applications FastAPI en production :

### Problèmes Résolus

- ❌ Routes surchargées avec trop de responsabilités
- ❌ Gestion d'erreurs inconsistante
- ❌ Logging fragmenté et non structuré
- ❌ Validation répétitive dans chaque route
- ❌ Difficultés de test et de maintenance
- ❌ Sécurité insuffisante pour la production

### Solution Hybride

- ✅ **Routes Ultra-Simplifiées** : Une ligne par endpoint
- ✅ **Contrôleurs Intelligents** : Coordination métier centralisée
- ✅ **Middleware Stack Avancé** : Sécurité et observabilité intégrées
- ✅ **Système d'Exceptions Structuré** : Réponses d'erreur cohérentes
- ✅ **Logging Avancé** : Performance, sécurité et debug
- ✅ **Architecture Défensive** : Validation et monitoring à tous les niveaux

## 🏗️ Architecture

### Couches Architecturales

```
┌─────────────────────────────────────────┐
│            API Layer (Routes)           │  ← Routage HTTP uniquement
├─────────────────────────────────────────┤
│         Presentation Layer              │  ← Contrôleurs + Middlewares
│  ┌─────────────────┬─────────────────┐  │
│  │   Controllers   │   Middlewares   │  │
│  │   (Business     │   (Cross-cut    │  │
│  │   Coordination) │   Concerns)     │  │
│  └─────────────────┴─────────────────┘  │
├─────────────────────────────────────────┤
│          Application Layer              │  ← Use Cases + DTOs
├─────────────────────────────────────────┤
│            Domain Layer                 │  ← Entités + Règles métier
├─────────────────────────────────────────┤
│         Infrastructure Layer            │  ← Base de données + Auth
└─────────────────────────────────────────┘
            Shared Components               ← Exceptions + Logging + Utils
```

### Principes Directeurs

1. **Single Responsibility** : Chaque couche a une responsabilité claire
2. **Dependency Inversion** : Les dépendances pointent vers l'intérieur
3. **Open/Closed** : Ouvert à l'extension, fermé à la modification
4. **Interface Segregation** : Interfaces spécifiques aux besoins
5. **Defense in Depth** : Sécurité à tous les niveaux

## 🚀 Fonctionnalités

### 🎛️ Contrôleurs Intelligents

- **Validation Automatique** : Types, contraintes métier, autorisation
- **Gestion d'Erreurs Unifiée** : Transformation d'exceptions cohérente
- **Logging Contextuel** : Traçabilité complète des opérations
- **Performance Monitoring** : Mesure automatique des temps d'exécution
- **Retry Logic** : Gestion des échecs temporaires

### 🛡️ Middleware Stack de Production

- **Security Headers** : HSTS, CSP, XSS Protection, Frame Options
- **Rate Limiting Intelligent** : Algorithmes adaptatifs avec analyse comportementale
- **Request/Response Logging** : Journalisation complète avec sanitization
- **Global Error Handler** : Gestion centralisée des erreurs non catchées
- **Auth Middleware** : JWT avec validation et refresh automatique

### 📊 Système de Logging Avancé

- **Structured Logging** : Format JSON pour analyses automatisées
- **Performance Metrics** : Temps d'exécution, seuils configurable
- **Security Events** : Détection d'activités suspectes
- **Context Propagation** : Suivi des requêtes avec IDs uniques
- **Multiple Formatters** : Adaptation selon l'environnement

### ⚠️ Gestion d'Exceptions Sophistiquée

- **Hiérarchie Structurée** : Domain, Auth, Validation exceptions
- **Codes HTTP Automatiques** : Mapping intelligent vers codes appropriés
- **Contexte Riche** : Données additionnelles pour le debugging
- **Serialization JSON** : Format uniforme pour les clients

### 🔒 Sécurité Multi-Couches

- **Rate Limiting Adaptatif** : Protection contre abuse et DoS
- **Input Validation** : Sanitization et validation stricte
- **Security Headers** : Protection contre attaques web communes
- **Audit Logging** : Traçabilité complète des actions sensibles
- **Token Management** : JWT avec rotation et invalidation

## 🛠️ Installation

### Prérequis

- Python 3.8+
- pip ou poetry

### Installation Rapide

```bash
# Cloner le repository
git clone <repository-url>
cd todo_api

# Installer les dépendances
pip install -r requirements.txt

# Ou avec poetry
poetry install

# Initialiser la base de données
python -c "from src.infrastructure.database.sqlite.models import Base; from src.infrastructure.database.sqlite.config import engine; Base.metadata.create_all(bind=engine)"
```

### Configuration

Créer un fichier `.env` :

```env
# Application
APP_NAME=Todo API Hybrid
APP_VERSION=1.0.0-hybrid
DEBUG=True
HOST=127.0.0.1
PORT=8001

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
ALLOWED_HOSTS=["localhost", "127.0.0.1"]

# Database
DATABASE_URL=sqlite:///./todo.db

# Logging
LOG_LEVEL=INFO
ENABLE_JSON_LOGGING=False
ENABLE_PERFORMANCE_LOGGING=True
ENABLE_SECURITY_LOGGING=True
```

## 🚀 Utilisation

### Démarrage du Serveur

```bash
# Version hybride (recommandée)
python src/main_hybrid.py

# Ou avec uvicorn
uvicorn src.main_hybrid:app --host 127.0.0.1 --port 8001 --reload
```

### Endpoints Disponibles

#### Routes Hybrides (Recommandées)

```
POST   /api/v1/auth/register     - Inscription utilisateur
POST   /api/v1/auth/login        - Connexion utilisateur
GET    /api/v1/auth/me           - Profil utilisateur
POST   /api/v1/auth/logout       - Déconnexion

GET    /api/v1/todos/all         - Liste des todos
GET    /api/v1/todos/{id}        - Détail d'une todo
POST   /api/v1/todos/create      - Création de todo
PATCH  /api/v1/todos/{id}        - Mise à jour partielle
DELETE /api/v1/todos/delete      - Suppression

GET    /api/v1/todos/completed   - Todos terminées
GET    /api/v1/todos/pending     - Todos en cours
GET    /api/v1/todos/priority/{level} - Todos par priorité
```

#### Routes Originales (Comparaison)

```
POST   /api/v1/original/auth/*   - Endpoints auth originaux
GET    /api/v1/original/todos/*  - Endpoints todos originaux
```

#### Endpoints Système

```
GET    /health                   - Santé de l'application
GET    /                        - Informations générales
GET    /docs                    - Documentation Swagger (dev uniquement)
```

## 📖 API Documentation

### Exemple d'Utilisation

#### 1. Inscription et Connexion

```bash
# Inscription
curl -X POST "http://localhost:8001/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "full_name": "Test User"
  }'

# Connexion
curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=SecurePassword123!"
```

#### 2. Opérations Todo

```bash
# Création d'une todo
curl -X POST "http://localhost:8001/api/v1/todos/create" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Apprendre l'\''architecture hybride",
    "description": "Étudier les patterns avancés",
    "priority": 5,
    "completed": false
  }'

# Liste des todos
curl -X GET "http://localhost:8001/api/v1/todos/all" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Mise à jour
curl -X PATCH "http://localhost:8001/api/v1/todos/1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

### Format des Réponses

#### Succès

```json
{
  "id": 1,
  "title": "Ma todo",
  "description": "Description détaillée",
  "priority": 3,
  "completed": false,
  "owner_id": 1,
  "created_at": "2024-01-10T10:30:00Z",
  "updated_at": "2024-01-10T10:30:00Z"
}
```

#### Erreur

```json
{
  "error": "TodoNotFoundError",
  "message": "Todo with ID 999 not found for user 1",
  "status_code": 404,
  "timestamp": "2024-01-10T10:30:00Z",
  "context": {
    "todo_id": 999,
    "user_id": 1,
    "operation": "get_todo_by_id"
  }
}
```

## 🧪 Tests et Démonstration

### Script de Démonstration

```bash
# Lancer le serveur hybride
python src/main_hybrid.py

# Dans un autre terminal, lancer la démo
python test_hybrid_architecture.py
```

La démonstration teste :

- ✅ Système d'exceptions structuré
- ✅ Logging avancé avec contexte
- ✅ Flux d'authentification complet
- ✅ Opérations CRUD sur les todos
- ✅ Middlewares de sécurité
- ✅ Rate limiting et headers
- ✅ Comparaison avec architecture originale

### Tests Automatisés

```bash
# Tests unitaires
pytest tests/unit/

# Tests d'intégration
pytest tests/integration/

# Tests des contrôleurs
pytest tests/controllers/

# Tests des middlewares
pytest tests/middlewares/

# Couverture complète
pytest --cov=src tests/
```

## 📁 Structure du Projet

```
todo_api/
├── src/
│   ├── shared/                    # Composants partagés
│   │   ├── exceptions/           # Système d'exceptions
│   │   │   ├── base.py          # Exception de base
│   │   │   ├── domain.py        # Exceptions métier
│   │   │   ├── auth.py          # Exceptions auth
│   │   │   └── validation.py    # Exceptions validation
│   │   └── logging/             # Système de logging
│   │       ├── config.py        # Configuration
│   │       ├── formatters.py    # Formatters logs
│   │       └── logger.py        # Logger principal
│   │
│   ├── presentation/             # Couche présentation
│   │   ├── controllers/         # Contrôleurs intelligents
│   │   │   ├── base_controller.py
│   │   │   ├── todo_controller.py
│   │   │   └── auth_controller.py
│   │   └── middlewares/         # Middlewares avancés
│   │       ├── error_handler.py
│   │       ├── logging_middleware.py
│   │       ├── rate_limiting.py
│   │       ├── security_headers.py
│   │       └── auth_middleware.py
│   │
│   ├── api/                     # Couche API
│   │   └── routes/             # Routes simplifiées
│   │       ├── todo_simplified.py
│   │       ├── auth_simplified.py
│   │       ├── todo.py         # Originales
│   │       └── auth.py         # Originales
│   │
│   ├── application/            # Couche application
│   │   ├── use_cases/         # Use cases métier
│   │   └── dtos/              # DTOs de transfert
│   │
│   ├── domain/                # Couche domaine
│   │   ├── entities/          # Entités métier
│   │   └── repositories/      # Interfaces repositories
│   │
│   ├── infrastructure/        # Couche infrastructure
│   │   ├── database/         # Base de données
│   │   ├── security/         # Sécurité et auth
│   │   └── config/           # Configuration
│   │
│   ├── main.py               # Application originale
│   └── main_hybrid.py        # Application hybride
│
├── tests/                    # Tests automatisés
│   ├── unit/
│   ├── integration/
│   ├── controllers/
│   └── middlewares/
│
├── test_hybrid_architecture.py  # Script de démonstration
├── HYBRID_ARCHITECTURE.md       # Documentation architecture
├── README_HYBRID.md             # Ce fichier
└── requirements.txt             # Dépendances
```

## 👨‍💻 Développement

### Ajout d'une Nouvelle Fonctionnalité

1. **Créer l'entité** (si nécessaire) dans `domain/entities/`
2. **Implémenter le use case** dans `application/use_cases/`
3. **Créer le DTO** dans `application/dtos/`
4. **Ajouter la méthode au contrôleur** dans `presentation/controllers/`
5. **Créer la route simplifiée** dans `api/routes/`

### Standards de Code

- **Type Hints** : Obligatoires partout
- **Docstrings** : Format Google style
- **Logging** : Structuré avec contexte
- **Validation** : Pydantic pour les DTOs
- **Tests** : Couverture > 90%

### Workflow de Développement

```bash
# 1. Créer une branche feature
git checkout -b feature/nouvelle-fonctionnalite

# 2. Développer avec tests
pytest --watch

# 3. Vérifier le code
flake8 src/
black src/
mypy src/

# 4. Tester l'intégration
python test_hybrid_architecture.py

# 5. Commit et PR
git commit -m "feat: ajouter nouvelle fonctionnalité"
git push origin feature/nouvelle-fonctionnalite
```

## 🚀 Déploiement

### Développement

```bash
python src/main_hybrid.py
```

### Production avec Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ src/
EXPOSE 8000

CMD ["uvicorn", "src.main_hybrid:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production avec Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-api-hybrid
spec:
  replicas: 3
  selector:
    matchLabels:
      app: todo-api-hybrid
  template:
    metadata:
      labels:
        app: todo-api-hybrid
    spec:
      containers:
        - name: api
          image: todo-api-hybrid:latest
          ports:
            - containerPort: 8000
          env:
            - name: DEBUG
              value: 'False'
            - name: LOG_LEVEL
              value: 'INFO'
```

### Variables d'Environnement Production

```env
# Production settings
DEBUG=False
LOG_LEVEL=INFO
ENABLE_JSON_LOGGING=True
ENABLE_PERFORMANCE_LOGGING=True
ENABLE_SECURITY_LOGGING=True

# Security
SECRET_KEY=<strong-secret-key>
ACCESS_TOKEN_EXPIRE_MINUTES=15

# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# Monitoring
SENTRY_DSN=<sentry-dsn>
```

## 📊 Monitoring et Observabilité

### Métriques Disponibles

- **Performance** : Temps de réponse par endpoint
- **Erreurs** : Taux d'erreur et types d'exceptions
- **Sécurité** : Tentatives d'accès non autorisé
- **Business** : Utilisation des fonctionnalités

### Logs Structurés

```json
{
  "timestamp": "2024-01-10T10:30:00Z",
  "level": "INFO",
  "logger": "controllers.todo",
  "operation": "create_todo",
  "user_id": 123,
  "duration": "0.045s",
  "status": "success",
  "request_id": "req_abc123"
}
```

### Alertes Recommandées

- Taux d'erreur > 5%
- Temps de réponse > 2s
- Tentatives d'authentification échouées > 10/min
- Rate limiting déclenché fréquemment

## 🎓 Conclusion

Cette architecture hybride démontre comment créer une application FastAPI **robuste**, **maintenable** et **prête pour la production** en combinant les meilleurs patterns architecturaux.

### Avantages Clés

- **90% moins de code** dans les routes
- **Cohérence parfaite** des réponses d'erreur
- **Observabilité complète** de l'application
- **Sécurité multi-couches** intégrée
- **Testabilité optimale** de tous les composants
- **Évolutivité** facilitée

### Prochaines Étapes

1. **Intégration CI/CD** avec tests automatisés
2. **Monitoring avancé** avec Prometheus/Grafana
3. **Cache Layer** avec Redis
4. **Message Queue** pour les tâches asynchrones
5. **Documentation API** interactive améliorée

---

**Made with ❤️ and Clean Architecture principles**

Pour plus d'informations, consultez [HYBRID_ARCHITECTURE.md](./HYBRID_ARCHITECTURE.md)
