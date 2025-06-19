# Plan d'amélioration de la gestion des exceptions

## 🎯 Objectif

Améliorer la gestion des erreurs dans l'application Todo API en utilisant le système d'exceptions personnalisées déjà défini dans `/shared/exceptions` pour avoir des messages d'erreur clairs et spécifiques.

## 📋 Problèmes identifiés

- Messages d'erreur génériques ("Invalid credentials") pour différents cas d'erreur
- Non-utilisation des exceptions personnalisées déjà définies
- Manque de clarté sur les formats acceptés (email OU username)
- Validation insuffisante des données d'entrée
- **Architecture des exceptions peu claire** (tout mélangé dans les mêmes fichiers)

---

## 🏗️ PHASE 0: Restructuration de l'architecture des exceptions

### ✅ Tâche 0: Réorganiser l'architecture des exceptions pour plus de clarté

**Objectif:** Restructurer les fichiers d'exceptions pour avoir une organisation claire et modulaire

**Problème actuel:**

- `auth.py` mélange authentication, authorization, rate limiting (295 lignes)
- `validation.py` mélange tous types de validation (331 lignes)
- `domain.py` mélange todo et user exceptions
- Difficile de s'y retrouver et de maintenir

**Nouvelle architecture proposée:**

```
src/shared/exceptions/
├── __init__.py (exports principaux)
├── base.py (exceptions de base - garde tel quel)
├── auth/
│   ├── __init__.py
│   ├── authentication.py (login, tokens, credentials)
│   ├── authorization.py (permissions, access control)
│   └── rate_limiting.py (rate limiting, IP blocking)
├── domain/
│   ├── __init__.py
│   ├── todo.py (exceptions spécifiques aux TODOs)
│   └── user.py (exceptions spécifiques aux users)
└── validation/
    ├── __init__.py
    ├── format.py (email, date, username format)
    ├── password.py (force mot de passe)
    ├── length.py (trop long, trop court)
    └── fields.py (champs requis, choix invalides)
```

**Actions:**

1. Créer la nouvelle structure de dossiers
2. Répartir les exceptions existantes dans les nouveaux fichiers selon leur logique
3. Mettre à jour tous les `__init__.py` pour maintenir la compatibilité
4. Vérifier que tous les imports existants continuent à fonctionner
5. Nettoyer et organiser le code dans chaque nouveau fichier

**Fichiers créés:**

- `src/shared/exceptions/auth/` (nouveau dossier)
- `src/shared/exceptions/domain/` (réorganisation)
- `src/shared/exceptions/validation/` (nouveau dossier)
- Tous les fichiers correspondants

**Fichiers modifiés:**

- `src/shared/exceptions/__init__.py` (réorganiser les exports)
- Supprimer `auth.py`, `validation.py`, `domain.py` après migration

**Test:** Vérifier que l'application démarre sans erreur et que tous les imports existants fonctionnent encore.

---

## 🏗️ PHASE 1: Correction de l'authentification (/auth/login)

### ✅ Tâche 1: Créer de nouvelles exceptions spécifiques pour l'auth

**Objectif:** Ajouter des exceptions plus précises pour distinguer les cas d'erreur d'authentification

**Actions:**

1. Ajouter `UserNotFoundError` dans `auth.py`
2. Ajouter `InvalidPasswordError` dans `auth.py`
3. Ajouter `InactiveUserError` dans `auth.py`
4. Mettre à jour `__init__.py` pour exporter ces nouvelles exceptions

**Fichiers modifiés:**

- `src/shared/exceptions/auth.py`
- `src/shared/exceptions/__init__.py`

**Test:** Vérifier que l'application démarre sans erreur et que les imports fonctionnent.

---

### ✅ Tâche 2: Modifier les use cases d'authentification

**Objectif:** Utiliser les nouvelles exceptions spécifiques dans la logique métier

**Actions:**

1. Modifier `auth_use_cases.py` pour utiliser les nouvelles exceptions:
   - `UserNotFoundError` quand l'utilisateur n'existe pas
   - `InvalidPasswordError` quand le mot de passe est incorrect
   - `InactiveUserError` quand l'utilisateur est désactivé
2. Améliorer les messages pour indiquer qu'on peut utiliser email OU username

**Fichiers modifiés:**

- `src/application/use_cases/auth_use_cases.py`

**Test:** Tester les endpoints `/auth/login` avec:

- Username qui n'existe pas
- Email qui n'existe pas
- Mot de passe incorrect
- Utilisateur désactivé (si applicable)
- Login valide

---

### ✅ Tâche 3: Mettre à jour le contrôleur d'authentification

**Objectif:** Supprimer les HTTPException génériques du contrôleur

**Actions:**

1. Modifier `auth_controller.py` pour laisser les exceptions personnalisées remonter
2. Supprimer les `HTTPException` génériques dans `authenticate_user`
3. Améliorer le logging avec les codes d'erreur spécifiques

**Fichiers modifiés:**

- `src/presentation/controllers/auth_controller.py`

**Test:** Répéter les tests de la tâche 2 et vérifier que les messages d'erreur sont plus précis.

---

### ✅ Tâche 4: Améliorer le middleware de gestion d'erreurs

**Objectif:** Optimiser l'affichage des nouvelles exceptions dans les réponses HTTP

**Actions:**

1. Améliorer `error_handler.py` pour mieux formater les nouvelles exceptions d'auth
2. S'assurer que les codes d'erreur sont inclus dans les réponses
3. Ajouter des logs spécifiques pour les tentatives de connexion échouées

**Fichiers modifiés:**

- `src/presentation/middlewares/error_handler.py`

**Test:** Tester tous les cas d'erreur d'authentification et vérifier:

- Format JSON des réponses d'erreur
- Codes d'erreur corrects
- Messages clairs
- Logs appropriés

---

## 🏗️ PHASE 2: Validation des données d'entrée

### ✅ Tâche 5: Ajouter validation email lors de l'inscription

**Objectif:** Utiliser `InvalidEmailError` pour valider les emails

**Actions:**

1. Créer une fonction de validation email dans un module utils
2. Modifier `register_user` dans `auth_use_cases.py` pour valider l'email
3. Utiliser `InvalidEmailError` en cas d'email invalide

**Fichiers modifiés:**

- `src/shared/utils/validation.py` (nouveau fichier)
- `src/application/use_cases/auth_use_cases.py`

**Test:** Tester l'inscription avec:

- Emails valides
- Emails invalides (différents formats incorrets)

**Note:** Cette tâche utilisera la nouvelle structure d'exceptions créée dans la Tâche 0.

---

### ✅ Tâche 6: Ajouter validation mot de passe

**Objectif:** Utiliser `WeakPasswordError` pour valider la force des mots de passe

**Actions:**

1. Ajouter validation de mot de passe dans utils
2. Modifier `register_user` pour valider la force du mot de passe
3. Utiliser `WeakPasswordError` avec détails des exigences manquantes

**Fichiers modifiés:**

- `src/shared/utils/validation.py`
- `src/application/use_cases/auth_use_cases.py`

**Test:** Tester l'inscription avec:

- Mots de passe faibles (trop courts, sans majuscules, etc.)
- Mots de passe forts
- Vérifier que les messages indiquent clairement les exigences manquantes

---

### ✅ Tâche 7: Ajouter validation username

**Objectif:** Utiliser `InvalidUsernameError` pour valider les noms d'utilisateur

**Actions:**

1. Ajouter validation de username dans utils
2. Modifier `register_user` pour valider le format du username
3. Utiliser `InvalidUsernameError` en cas de format invalide

**Fichiers modifiés:**

- `src/shared/utils/validation.py`
- `src/application/use_cases/auth_use_cases.py`

**Test:** Tester l'inscription avec:

- Usernames valides
- Usernames invalides (trop courts, caractères interdits, etc.)

---

## 🏗️ PHASE 3: Extension aux autres endpoints

### ✅ Tâche 8: Améliorer la gestion d'erreurs pour les TODOs

**Objectif:** Utiliser les exceptions du domaine pour les opérations TODO

**Actions:**

1. Modifier `todo_use_cases.py` pour utiliser:
   - `TodoNotFoundError` au lieu des exceptions génériques
   - `TodoAccessDeniedError` pour les problèmes d'autorisation
   - `InvalidPriorityError` pour les priorités invalides
2. Mettre à jour `todo_controller.py` en conséquence

**Fichiers modifiés:**

- `src/application/use_cases/todo_use_cases.py`
- `src/presentation/controllers/todo_controller.py`

**Test:** Tester tous les endpoints TODO:

- Créer, lire, modifier, supprimer des TODOs
- Cas d'erreur (TODO inexistant, accès non autorisé, etc.)

---

### ✅ Tâche 9: Ajouter gestion des erreurs de rate limiting

**Objectif:** Améliorer l'affichage des erreurs de limitation de débit

**Actions:**

1. Vérifier que `RateLimitExceededError` est bien utilisée dans `rate_limiting.py`
2. Améliorer les messages pour indiquer quand réessayer
3. S'assurer que les headers `Retry-After` sont inclus

**Fichiers modifiés:**

- `src/presentation/middlewares/rate_limiting.py`

**Test:** Tester la limitation de débit en faisant beaucoup de requêtes rapidement.

---

### ✅ Tâche 10: Validation complète des tokens JWT

**Objectif:** Améliorer la gestion des erreurs de tokens

**Actions:**

1. S'assurer que `InvalidTokenError` et `ExpiredTokenError` sont utilisées partout
2. Ajouter `MissingTokenError` pour les cas où le token est absent
3. Améliorer les messages d'erreur pour guider l'utilisateur

**Fichiers modifiés:**

- `src/infrastructure/auth/jwt_service.py`
- `src/api/dependencies.py`

**Test:** Tester avec:

- Tokens valides
- Tokens expirés
- Tokens malformés
- Requêtes sans token

---

## 🏗️ PHASE 4: Finalisation et optimisation

### ✅ Tâche 11: Audit complet des exceptions inutilisées

**Objectif:** Identifier et intégrer ou supprimer les exceptions non utilisées

**Actions:**

1. Faire un audit de toutes les exceptions définies dans `/shared/exceptions`
2. Identifier celles qui ne sont pas utilisées
3. Soit les intégrer dans l'application, soit les supprimer si elles ne sont pas pertinentes

**Fichiers potentiellement modifiés:**

- Tous les fichiers dans `src/shared/exceptions/`

**Test:** Test complet de l'application pour s'assurer qu'aucune régression n'a été introduite.

---

### ✅ Tâche 12: Documentation et tests finaux

**Objectif:** Documenter le système d'exceptions et faire des tests complets

**Actions:**

1. Mettre à jour la documentation des APIs avec les nouveaux codes d'erreur
2. Créer des exemples d'utilisation des exceptions
3. Test de régression complet sur toute l'application

**Fichiers modifiés:**

- Documentation API
- README si nécessaire

**Test final:** Test complet de tous les endpoints avec tous les cas d'erreur possibles.

---

## 📊 Points de contrôle par phase

### Après Phase 1

- [ ] Tous les tests d'authentification passent
- [ ] Messages d'erreur clairs pour `/auth/login`
- [ ] Distinction entre "utilisateur inexistant" et "mot de passe incorrect"
- [ ] Indication claire qu'on peut utiliser email OU username

### Après Phase 2

- [ ] Validation robuste des données d'entrée
- [ ] Messages d'erreur informatifs pour les formats invalides
- [ ] Tous les tests d'inscription passent

### Après Phase 3

- [ ] Gestion d'erreurs cohérente sur tous les endpoints
- [ ] Rate limiting fonctionnel avec messages clairs
- [ ] Gestion complète des erreurs de tokens

### Après Phase 4

- [ ] Système d'exceptions complètement intégré
- [ ] Aucune exception inutilisée
- [ ] Documentation à jour
- [ ] Application stable et robuste

---

## 🚨 Notes importantes

1. **Après chaque tâche**, faire les tests suggérés avant de passer à la suivante
2. **Sauvegarder** le code avant chaque modification importante
3. **Tester en local** avant de commiter
4. Si une tâche cause des problèmes, revenir à l'état précédent et analyser
5. **Me demander de faire les tests** si vous préférez que je les effectue

## 🔄 Processus de test recommandé

Pour chaque tâche:

1. ✅ Vérifier que l'application démarre
2. ✅ Tester les nouveaux cas d'erreur
3. ✅ Tester que les cas existants fonctionnent toujours
4. ✅ Vérifier les logs d'erreur
5. ✅ Passer à la tâche suivante uniquement si tout fonctionne
