# 📝 Todo API - Clean Architecture avec FastAPI

> API REST moderne de gestion de tâches construite avec FastAPI, SQLAlchemy et Clean Architecture. Système multi-utilisateurs avec authentification JWT et permissions granulaires.

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg?style=for-the-badge&logo=python)](https://www.python.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-323232?style=for-the-badge&logo=sqlalchemy)](https://www.sqlalchemy.org/)
[![JWT](https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens)](https://jwt.io/)

## 🚀 Démarrage Rapide

### Prérequis

- Python 3.8+
- Git

### Installation

1. **Cloner le projet**

```bash
git clone <votre-repo>
cd todo_api
```

2. **Créer l'environnement virtuel**

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. **Installer les dépendances**

```bash
pip install -r requirements.txt
```

4. **Configuration**
   Créez un fichier `.env` à la racine du projet :

```env
# Database
DATABASE_URL=sqlite:///./todo.db

# JWT
JWT_SECRET_KEY=votre_clé_secrète_très_longue_et_sécurisée
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
APP_NAME=Todo API
APP_VERSION=1.0.0
DEBUG=true
ENVIRONMENT=development

# Server
HOST=127.0.0.1
PORT=8000

# Security
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
ALLOWED_HOSTS=["localhost","127.0.0.1"]
```

5. **Lancer l'application**

```bash
python main.py
```

6. **Accéder à l'API**

- 📊 Documentation Swagger : http://127.0.0.1:8000/docs
- 📖 Documentation ReDoc : http://127.0.0.1:8000/redoc

## 🏗️ Architecture

Ce projet implémente la **Clean Architecture** d'Uncle Bob avec 4 couches distinctes :

```
TodoAp/
├── src/
│   ├── 🎯 domain/                    # 🔵 COUCHE DOMAINE (Cœur)
│   │   ├── entities/                 # Entités métier (Todo, User)
│   │   │   ├── todo.py
│   │   │   └── user.py
│   │   └── repositories/             # Interfaces abstraites
│   │       ├── todo_repository.py
│   │       └── user_repository.py
│   │
│   ├── 💼 application/               # 🟢 COUCHE APPLICATION
│   │   ├── use_cases/                # Logique métier
│   │   │   ├── todo_use_cases.py
│   │   │   └── user_use_cases.py
│   │   └── dtos/                     # Data Transfer Objects
│   │       ├── todo_dto.py
│   │       └── user_dto.py
│   │
│   ├── 🔧 infrastructure/            # 🟡 COUCHE INFRASTRUCTURE
│   │   ├── database/
│   │   │   └── sqlite/               # Implémentation SQLite
│   │   │       ├── config.py
│   │   │       ├── models.py
│   │   │       ├── repository.py
│   │   │       └── user_repository.py
│   │   ├── security/                 # JWT & Sécurité
│   │   │   ├── jwt.py
│   │   │   └── timeout_middleware.py
│   │   └── config.py                 # Configuration globale
│   │
│   └── 🌐 api/                       # 🔴 COUCHE PRÉSENTATION
│       ├── routes/                   # Endpoints REST
│       │   ├── auth.py
│       │   └── todo.py
│       └── dependencies.py           # Injection de dépendances
├── main.py                           # Point d'entrée
├── requirements.txt
└── .env                             # Variables d'environnement
```

### 📋 Principes Respectés

- **🎯 Séparation des responsabilités** : Chaque couche a un rôle précis
- **🔄 Inversion de dépendance** : Les couches internes ne dépendent pas des externes
- **🧪 Testabilité** : Architecture facilitant les tests unitaires
- **🔌 Extensibilité** : Facile d'ajouter PostgreSQL, MongoDB, etc.
- **🛡️ Type Safety** : Pydantic et annotations de type partout

## 📚 Fonctionnalités

### 👤 Authentification

- ✅ Inscription utilisateur (`/register`)
- ✅ Connexion JWT (`/token`)
- ✅ Permissions granulaires (scopes)
- ✅ Sécurité bcrypt pour mots de passe
- ✅ Tokens avec expiration

### 📝 Gestion des Todos

- ✅ CRUD complet avec ownership
- ✅ Mise à jour partielle (PATCH)
- ✅ Priorités (1-5) et statuts
- ✅ Isolation par utilisateur
- ✅ Validation robuste

### 🛡️ Sécurité

- ✅ Middleware de timeout
- ✅ CORS configuré
- ✅ Headers de sécurité
- ✅ Validation des hôtes autorisés

## 🔐 Authentification & Utilisation

### 1. Créer un compte

```bash
curl -X POST "http://127.0.0.1:8000/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "username": "monusername",
       "password": "motdepasse123"
     }'
```

### 2. Se connecter

```bash
curl -X POST "http://127.0.0.1:8000/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=monusername&password=motdepasse123"
```

**Réponse :**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Utiliser l'API avec le token

**Important** : Ajoutez `Authorization: Bearer <votre_token>` à chaque requête !

## 📋 Endpoints API

### 🔑 Authentification

| Méthode | Endpoint    | Description     | Auth Required |
| ------- | ----------- | --------------- | ------------- |
| `POST`  | `/register` | Créer un compte | ❌            |
| `POST`  | `/token`    | Se connecter    | ❌            |

### 📝 Todos

| Méthode  | Endpoint                | Description            | Scopes Required |
| -------- | ----------------------- | ---------------------- | --------------- |
| `GET`    | `/todos/all`            | Lister mes todos       | `todos:read`    |
| `GET`    | `/todos/{id}`           | Récupérer une todo     | `todos:read`    |
| `POST`   | `/todos/create`         | Créer une todo         | `todos:write`   |
| `PATCH`  | `/todos/{id}`           | Modifier partiellement | `todos:write`   |
| `DELETE` | `/todos/delete?id={id}` | Supprimer une todo     | `todos:delete`  |

## 🧪 Exemples d'Utilisation

### Créer une todo

```bash
curl -X POST "http://127.0.0.1:8000/todos/create" \
     -H "Authorization: Bearer <TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Apprendre FastAPI",
       "description": "Étudier la documentation et faire des tests",
       "priority": 3,
       "completed": false
     }'
```

### Lister mes todos

```bash
curl -X GET "http://127.0.0.1:8000/todos/all" \
     -H "Authorization: Bearer <TOKEN>"
```

### Mise à jour partielle (seulement le titre)

```bash
curl -X PATCH "http://127.0.0.1:8000/todos/1" \
     -H "Authorization: Bearer <TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"title": "Nouveau titre"}'
```

### Marquer comme terminée

```bash
curl -X PATCH "http://127.0.0.1:8000/todos/1" \
     -H "Authorization: Bearer <TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"completed": true}'
```

## 🎯 Utilisation avec Swagger UI

1. **Allez sur** : http://127.0.0.1:8000/docs
2. **Testez `/token`** pour récupérer votre token
3. **Cliquez "Authorize"** (🔓 en haut à droite)
4. **Remplissez** username/password OU collez directement le token
5. **Testez les endpoints** protégés !

## 📊 Modèles de Données

### Todo

```json
{
  "id": 1,
  "title": "Titre de la tâche",
  "description": "Description détaillée",
  "priority": 3,
  "completed": false,
  "owner_id": 1
}
```

### User

```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "monusername",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-01T12:00:00",
  "last_login": "2024-01-01T13:00:00"
}
```

## ⚙️ Configuration Avancée

### Variables d'Environnement

| Variable                      | Description               | Défaut                |
| ----------------------------- | ------------------------- | --------------------- |
| `DATABASE_URL`                | URL de la base de données | `sqlite:///./todo.db` |
| `JWT_SECRET_KEY`              | Clé secrète JWT           | ⚠️ **Obligatoire**    |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Durée de vie du token     | `30`                  |
| `HOST`                        | Adresse d'écoute          | `127.0.0.1`           |
| `PORT`                        | Port d'écoute             | `8000`                |
| `DEBUG`                       | Mode debug                | `false`               |

### Sécurité Production

Pour la production, assurez-vous de :

- ✅ Changer `JWT_SECRET_KEY` (minimum 256 bits)
- ✅ Mettre `DEBUG=false`
- ✅ Configurer `CORS_ORIGINS` correctement
- ✅ Utiliser HTTPS
- ✅ Configurer un reverse proxy (nginx)

## 🔧 Développement

### Ajout d'une Nouvelle Base de Données

1. **Créer** `src/infrastructure/database/postgresql/`
2. **Implémenter** les interfaces `TodoRepository` et `UserRepository`
3. **Ajouter** la configuration dans `config.py`
4. **Modifier** `main.py` pour utiliser le nouveau repository

### Ajout d'un Nouvel Endpoint

1. **Définir** le DTO dans `application/dtos/`
2. **Implémenter** la logique dans `application/use_cases/`
3. **Créer** la route dans `api/routes/`
4. **Ajouter** les tests appropriés

## 🐛 Dépannage

### Erreurs Communes

**401 Unauthorized**

- ✅ Vérifiez que le token est valide
- ✅ Ajoutez `Authorization: Bearer <token>`
- ✅ Le token a peut-être expiré

**403 Forbidden**

- ✅ Vérifiez les scopes requis
- ✅ L'utilisateur a-t-il les bonnes permissions ?

**404 Todo not found**

- ✅ La todo appartient-elle à l'utilisateur connecté ?
- ✅ L'ID existe-t-il vraiment ?

### Logs

```bash
# Mode debug pour plus de logs
DEBUG=true python main.py
```

## 🚀 Technologies Utilisées

- **[FastAPI](https://fastapi.tiangolo.com/)** - Framework web moderne et rapide
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - ORM Python puissant
- **[Pydantic](https://pydantic-docs.helpmanual.io/)** - Validation et sérialisation
- **[JWT](https://jwt.io/)** - Authentification sans état
- **[bcrypt](https://github.com/pyca/bcrypt/)** - Hachage sécurisé des mots de passe
- **[SQLite](https://www.sqlite.org/)** - Base de données embarquée

## 📈 Performances

- **Async/Await** : Support natif FastAPI
- **Connection Pooling** : SQLAlchemy
- **JWT Stateless** : Pas de session serveur
- **Validation** : Pydantic ultra-rapide
- **Timeout Middleware** : Protection contre les requêtes lentes

⭐ **N'hésitez pas à mettre une étoile si ce projet vous a aidé !**
