# 🧹 PLAN DE NETTOYAGE - TODO API

## 🎯 OBJECTIF FINAL

Consolider l'architecture en supprimant les duplications et optimiser le code pour une maintenance simplifiée. L'application doit utiliser uniquement l'architecture hybride moderne et être débarrassée de tout code obsolète.

## 📊 ÉTAT ACTUEL

- ✅ Architecture hybride fonctionnelle
- ❌ Duplication routes traditionnelles/simplifiées
- ❌ Fichiers potentiellement obsolètes
- ❌ Imports morts possibles
- ❌ Configuration sous-optimale

---

## 📋 TÂCHES SÉQUENTIELLES

### TÂCHE 1 : Audit complet des duplications

- **🎯 Objectif** : Identifier toutes les duplications et dépendances
- **⚡ Priorité** : CRITIQUE - Base pour toutes les autres tâches
- **📁 Fichiers concernés** : Tous les fichiers du projet
- **🔧 Réalisation** :
  ```bash
  # Analyser les imports entre routes
  grep -r "from src.api.routes" src/
  # Identifier les routes dupliquées
  diff src/api/routes/auth.py src/api/routes/auth_simplified.py
  diff src/api/routes/todo.py src/api/routes/todo_simplified.py
  # Vérifier les dépendances dans main.py vs main_hybrid.py
  grep "include_router" main.py main_hybrid.py
  ```
- **📊 Dépendances** : Aucune
- **✅ Validation** :
  - [x] Liste complète des fichiers dupliqués créée
  - [x] Carte des dépendances établie
  - [x] Analyse des différences documentée
  - [x] Plan de migration défini

---

### TÂCHE 2 : Backup et tests de régression

- **🎯 Objectif** : Sécuriser l'état actuel avant modifications
- **⚡ Priorité** : CRITIQUE - Sécurité avant nettoyage
- **📁 Fichiers concernés** : Tous les fichiers fonctionnels
- **🔧 Réalisation** :

  ```bash
  # Créer une branche de backup
  git checkout -b backup-pre-nettoyage
  git add -A && git commit -m "Backup avant nettoyage"

  # Tester que l'application fonctionne
  python main.py & sleep 3 && curl http://localhost:5000/health
  python main_hybrid.py & sleep 3 && curl http://localhost:5001/health
  ```

- **📊 Dépendances** : TÂCHE 1 terminée
- **✅ Validation** :
  - [x] Backup Git créé avec succès
  - [x] `main.py` démarre sans erreur
  - [x] `main_hybrid.py` démarre sans erreur
  - [x] Endpoints de base accessibles
  - [x] Base de données fonctionnelle

---

### TÂCHE 3 : Consolidation des routes d'authentification

- **🎯 Objectif** : Supprimer `auth.py` et garder uniquement `auth_simplified.py`
- **⚡ Priorité** : HAUTE - Éliminer duplication critique
- **📁 Fichiers concernés** :
  - `src/api/routes/auth.py` (à supprimer)
  - `src/api/routes/auth_simplified.py` (à renommer)
  - `main.py` (à mettre à jour)
- **🔧 Réalisation** :

  ```bash
  # 1. Vérifier les dépendances de auth.py
  grep -r "from.*auth import" src/ main.py

  # 2. Renommer auth_simplified.py → auth.py
  mv src/api/routes/auth_simplified.py src/api/routes/auth.py

  # 3. Mettre à jour les imports dans main.py
  # Remplacer: from src.api.routes import todo, auth
  # Par: from src.api.routes import todo, auth

  # 4. Supprimer les références obsolètes
  ```

- **📊 Dépendances** : TÂCHE 2 terminée
- **✅ Validation** :
  - [x] `auth.py` traditionnel supprimé
  - [x] `auth_simplified.py` renommé en `auth.py`
  - [x] Imports mis à jour dans `main.py`
  - [x] Application démarre sans erreur
  - [x] Endpoints auth fonctionnels : `/auth/register`, `/auth/login`

---

### TÂCHE 4 : Consolidation des routes todo

- **🎯 Objectif** : Supprimer `todo.py` et garder uniquement `todo_simplified.py`
- **⚡ Priorité** : HAUTE - Éliminer duplication critique
- **📁 Fichiers concernés** :
  - `src/api/routes/todo.py` (à supprimer)
  - `src/api/routes/todo_simplified.py` (à renommer)
  - `main.py` (à mettre à jour)
- **🔧 Réalisation** :

  ```bash
  # 1. Vérifier les dépendances de todo.py
  grep -r "from.*todo import" src/ main.py

  # 2. Renommer todo_simplified.py → todo.py
  mv src/api/routes/todo_simplified.py src/api/routes/todo.py

  # 3. Mettre à jour les imports dans main.py
  # Vérifier que les imports pointent vers les bons fichiers

  # 4. Supprimer les références obsolètes
  ```

- **📊 Dépendances** : TÂCHE 3 terminée
- **✅ Validation** :
  - [x] `todo.py` traditionnel supprimé
  - [x] `todo_simplified.py` renommé en `todo.py`
  - [x] Imports mis à jour dans `main.py`
  - [x] Application démarre sans erreur
  - [x] Endpoints todo fonctionnels : `/todos/all`, `/todos/create`

---

### TÂCHE 5 : Consolidation des points d'entrée

- **🎯 Objectif** : Supprimer `main_hybrid.py` et enrichir `main.py`
- **⚡ Priorité** : MOYENNE - Simplifier le démarrage
- **📁 Fichiers concernés** :
  - `main_hybrid.py` (à analyser puis supprimer)
  - `main.py` (à enrichir)
- **🔧 Réalisation** :

  ```python
  # 1. Extraire les fonctionnalités avancées de main_hybrid.py
  # - Middleware stack avancé
  # - Logging structuré
  # - Health checks
  # - Configuration hybride

  # 2. Intégrer dans main.py
  # - Ajouter les middlewares manquants
  # - Intégrer le logging avancé
  # - Ajouter les endpoints système

  # 3. Supprimer main_hybrid.py
  ```

- **📊 Dépendances** : TÂCHE 4 terminée
- **✅ Validation** :
  - [x] Fonctionnalités de `main_hybrid.py` intégrées dans `main.py`
  - [x] `main_hybrid.py` supprimé
  - [x] `main.py` démarre avec toutes les fonctionnalités
  - [x] Middleware stack complet actif
  - [x] Endpoints système disponibles : `/health`, `/`

---

### TÂCHE 6 : Nettoyage des imports morts

- **🎯 Objectif** : Supprimer tous les imports inutilisés
- **⚡ Priorité** : MOYENNE - Optimisation code
- **📁 Fichiers concernés** : Tous les fichiers Python
- **🔧 Réalisation** :

  ```bash
  # 1. Installer outil de détection
  pip install unimport

  # 2. Scanner les imports morts
  unimport --check src/

  # 3. Supprimer automatiquement
  unimport --remove-all src/

  # 4. Vérification manuelle des imports critiques
  ```

- **📊 Dépendances** : TÂCHE 5 terminée
- **✅ Validation** :
  - [x] Outil `unimport` installé
  - [x] Scan des imports morts effectué
  - [x] Imports inutilisés supprimés
  - [x] Application démarre sans erreur
  - [x] Tous les tests passent

---

### TÂCHE 7 : Optimisation configuration

- **🎯 Objectif** : Nettoyer et optimiser `requirements.txt` et configuration
- **⚡ Priorité** : BASSE - Optimisation finale
- **📁 Fichiers concernés** :
  - `requirements.txt`
  - `src/infrastructure/config.py`
  - `.env.example`
- **🔧 Réalisation** :

  ```bash
  # 1. Analyser les dépendances réellement utilisées
  pip-autoremove -y --show

  # 2. Générer requirements.txt optimisé
  pip freeze > requirements_new.txt

  # 3. Nettoyer la configuration
  # Supprimer variables obsolètes
  # Optimiser valeurs par défaut

  # 4. Créer .env.example à jour
  ```

- **📊 Dépendances** : TÂCHE 6 terminée
- **✅ Validation** :
  - [x] `requirements.txt` optimisé
  - [x] Configuration nettoyée
  - [x] `.env.example` créé/mis à jour
  - [x] Application démarre avec config minimale
  - [x] Aucune dépendance inutile

---

### TÂCHE 8 : Documentation

- **🎯 Objectif** : Documenter les changements et finaliser
- **⚡ Priorité** : BASSE - Finalisation
- **📁 Fichiers concernés** :
  - `README.md`
  - `CHANGELOG.md` (nouveau)
  - Documentation inline
- **🔧 Réalisation** :

  ```markdown
  # 1. Mettre à jour README.md

  - Architecture finale
  - Instructions de démarrage unifiées
  - Endpoints disponibles

  # 2. Créer CHANGELOG.md

  - Changements apportés
  - Breaking changes
  - Migration guide
  ```

- **📊 Dépendances** : TÂCHE 7 terminée
- **✅ Validation** :
  - [x] `README.md` mis à jour
  - [x] `CHANGELOG.md` créé
  - [x] Documentation cohérente
  - [x] Architecture consolidée fonctionnelle

---

## 🎯 RÉSULTATS ATTENDUS

**Après toutes les tâches :**

- ✅ **Architecture unifiée** : Uniquement hybride moderne
- ✅ **Aucune duplication** : Code base épuré
- ✅ **Point d'entrée unique** : `main.py` avec toutes les fonctionnalités
- ✅ **Configuration optimisée** : Dependencies minimales
- ✅ **Documentation à jour** : README et CHANGELOG cohérents

## 🏗️ ARCHITECTURE FINALE ATTENDUE

```
src/
├── infrastructure/     # ✅ Configs et services
├── application/       # ✅ Use cases et DTOs
├── domain/           # ✅ Entités pures
├── presentation/     # ✅ Controllers et middlewares
└── api/
    ├── dependencies.py
    └── routes/
        ├── auth.py    # ✅ Hybride consolidé
        └── todo.py    # ✅ Hybride consolidé

main.py               # ✅ Point d'entrée unique enrichi
requirements.txt      # ✅ Optimisé
README.md            # ✅ Documentation unifiée
```

---

## 🚀 DÉMARRAGE

**Commencer par la TÂCHE 1** - elle analyse tout le reste !

```bash
# Validation après chaque tâche
python main.py
curl http://localhost:5000/health
```

**Prêt pour le nettoyage ?** 🧹
