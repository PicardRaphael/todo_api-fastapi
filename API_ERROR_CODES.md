# API Error Codes Documentation - Todo API

## 📖 Vue d'ensemble

Cette documentation complète liste tous les codes d'erreur disponibles dans l'API Todo, leurs conditions de déclenchement, et des exemples de réponses.

**Format des Réponses d'Erreur :**

```json
{
  "detail": "Message d'erreur lisible par l'humain",
  "status_code": 400,
  "error_code": "CODE_MACHINE_READABLE",
  "extra_data": {
    "field": "nom_du_champ",
    "context": "informations_additionnelles"
  },
  "headers": {
    "WWW-Authenticate": "Bearer"
  }
}
```

---

## 🔐 Authentication & Authorization Errors (4xx)

### **Authentication Errors (401)**

#### `AUTHENTICATION_FAILED`

- **Message** : "Authentication failed"
- **Trigger** : Erreur d'authentification générique
- **Headers** : `WWW-Authenticate: Bearer`

#### `INVALID_CREDENTIALS`

- **Message** : "Invalid username or password"
- **Trigger** : Login avec identifiants incorrects
- **Extra Data** : `attempted_username`
- **Exemple** :

```json
{
  "detail": "Invalid username or password",
  "status_code": 401,
  "error_code": "INVALID_CREDENTIALS",
  "extra_data": {
    "attempted_username": "john@example.com"
  }
}
```

#### `USER_NOT_FOUND`

- **Message** : "No user found with username or email '{identifier}'"
- **Trigger** : Utilisateur inexistant lors du login
- **Extra Data** : `identifier`, `identifier_type`, `hint`
- **Exemple** :

```json
{
  "detail": "No user found with username or email 'john@example.com'. You can login with either your username or email address.",
  "status_code": 401,
  "error_code": "USER_NOT_FOUND",
  "extra_data": {
    "identifier": "john@example.com",
    "identifier_type": "username/email",
    "hint": "You can use either username or email to login"
  }
}
```

#### `INVALID_PASSWORD`

- **Message** : "Incorrect password. Please check your password and try again."
- **Trigger** : Mot de passe incorrect
- **Extra Data** : `identifier`, `hint`

#### `USER_INACTIVE`

- **Message** : "Account is inactive: {reason}. Please contact support to reactivate your account."
- **Trigger** : Compte utilisateur désactivé
- **Extra Data** : `user_id`, `reason`, `contact_support`

#### `INVALID_TOKEN`

- **Message** : "Invalid token: {reason}"
- **Trigger** : Token JWT malformé ou signature invalide
- **Extra Data** : `reason`
- **Exemples** :

```json
{
  "detail": "Invalid token: Token signature verification failed",
  "status_code": 401,
  "error_code": "INVALID_TOKEN",
  "extra_data": {
    "reason": "Token signature verification failed"
  }
}
```

#### `EXPIRED_TOKEN`

- **Message** : "Token has expired. Please login again."
- **Trigger** : Token JWT expiré
- **Extra Data** : `expired_at` (optionnel)
- **Headers** : `WWW-Authenticate: Bearer`

#### `MISSING_TOKEN`

- **Message** : "Authentication token is required"
- **Trigger** : Aucun token fourni pour un endpoint protégé
- **Headers** : `WWW-Authenticate: Bearer`

### **Authorization Errors (403)**

#### `ACCESS_DENIED`

- **Message** : "Access denied"
- **Trigger** : Erreur d'autorisation générique

#### `TODO_ACCESS_DENIED`

- **Message** : "Access denied to todo {todo_id}. This todo belongs to another user."
- **Trigger** : Tentative d'accès à une todo d'un autre utilisateur
- **Extra Data** : `todo_id`, `owner_id`, `user_id`
- **Exemple** :

```json
{
  "detail": "Access denied to todo 123. This todo belongs to another user.",
  "status_code": 403,
  "error_code": "TODO_ACCESS_DENIED",
  "extra_data": {
    "todo_id": 123,
    "owner_id": 1,
    "user_id": 2
  }
}
```

#### `RATE_LIMIT_EXCEEDED`

- **Message** : "Rate limit exceeded. Try again in {retry_after} seconds."
- **Trigger** : Trop de requêtes en peu de temps
- **Extra Data** : `limit_type`, `retry_after`, `endpoint`, `recommended_action`
- **Headers** : `X-RateLimit-*`, `Retry-After`
- **Exemple** :

```json
{
  "detail": "Burst rate limit exceeded for /auth/login. Please slow down and try again in 30 seconds.",
  "status_code": 429,
  "error_code": "RATE_LIMIT_EXCEEDED",
  "extra_data": {
    "limit_type": "burst",
    "retry_after": 30,
    "endpoint": "/auth/login",
    "recommended_action": "Please slow down your requests"
  },
  "headers": {
    "Retry-After": "30",
    "X-RateLimit-Limit": "60",
    "X-RateLimit-Remaining": "0",
    "X-RateLimit-Reset": "1641811800"
  }
}
```

---

## 🔍 Validation Errors (400)

### **Base Validation**

#### `VALIDATION_ERROR`

- **Message** : "Validation failed for field '{field}': {reason}"
- **Trigger** : Erreur de validation générique
- **Extra Data** : `field`, `provided_value`, `reason`, `valid_format`

#### `WEAK_PASSWORD`

- **Message** : "Password does not meet security requirements"
- **Trigger** : Mot de passe trop faible lors de l'inscription
- **Extra Data** : `password_length`, `requirements`, `missing_requirements`
- **Exemple** :

```json
{
  "detail": "Password does not meet security requirements",
  "status_code": 400,
  "error_code": "WEAK_PASSWORD",
  "extra_data": {
    "password_length": 6,
    "requirements": [
      "At least 8 characters long",
      "At least one uppercase letter",
      "At least one lowercase letter",
      "At least one digit",
      "At least one special character (!@#$%^&*)"
    ],
    "missing_requirements": [
      "At least 8 characters long",
      "At least one uppercase letter",
      "At least one special character (!@#$%^&*)"
    ]
  }
}
```

### **Format Validation**

#### `INVALID_EMAIL`

- **Message** : "Invalid email format: {reason}"
- **Trigger** : Format d'email invalide
- **Extra Data** : `field`, `provided_value`, `valid_format`
- **Exemple** :

```json
{
  "detail": "Validation failed for field 'email': Email must be in valid format (user@domain.com). Valid format: user@example.com",
  "status_code": 400,
  "error_code": "INVALID_EMAIL",
  "extra_data": {
    "field": "email",
    "provided_value": "invalid-email",
    "reason": "Email must be in valid format (user@domain.com)",
    "valid_format": "user@example.com"
  }
}
```

#### `INVALID_USERNAME`

- **Message** : "Invalid username format: {reason}"
- **Trigger** : Format de nom d'utilisateur invalide
- **Extra Data** : `field`, `provided_value`, `valid_format`
- **Exemples de validation** :
  - Trop court : "Username is too short (2 characters). Minimum is 3 characters"
  - Trop long : "Username is too long (25 characters). Maximum is 20 characters"
  - Caractères interdits : "Username can only contain letters, numbers, and underscores"
  - Underscore au début/fin : "Username cannot start or end with an underscore"
  - Underscores consécutifs : "Username cannot contain consecutive underscores"

### **Length Validation**

#### `VALUE_TOO_LONG`

- **Message** : "Validation failed for field '{field}': Value too long"
- **Trigger** : Valeur dépassant la longueur maximale
- **Extra Data** : `max_length`, `actual_length`

#### `VALUE_TOO_SHORT`

- **Message** : "Validation failed for field '{field}': Value too short"
- **Trigger** : Valeur en dessous de la longueur minimale
- **Extra Data** : `min_length`, `actual_length`

---

## 🏗️ Domain Errors

### **Todo Errors**

#### `TODO_NOT_FOUND`

- **Message** : "Todo with ID {todo_id} not found for user {owner_id}"
- **Trigger** : Todo inexistante ou n'appartenant pas à l'utilisateur
- **Extra Data** : `todo_id`, `owner_id`
- **Exemple** :

```json
{
  "detail": "Todo with ID 999 not found for user 1",
  "status_code": 404,
  "error_code": "TODO_NOT_FOUND",
  "extra_data": {
    "todo_id": 999,
    "owner_id": 1
  }
}
```

#### `INVALID_PRIORITY`

- **Message** : "Invalid priority '{priority}'. Priority must be between {valid_range}."
- **Trigger** : Priorité en dehors de la plage 1-5
- **Extra Data** : `provided_priority`, `valid_range`, `valid_values`
- **Exemple** :

```json
{
  "detail": "Invalid priority '10'. Priority must be between 1-5.",
  "status_code": 400,
  "error_code": "INVALID_PRIORITY",
  "extra_data": {
    "provided_priority": 10,
    "valid_range": "1-5",
    "valid_values": [1, 2, 3, 4, 5]
  }
}
```

#### `TODO_TITLE_TOO_LONG`

- **Message** : "Todo title is too long. Maximum {max_length} characters allowed."
- **Trigger** : Titre de todo dépassant la limite
- **Extra Data** : `provided_length`, `max_length`, `title_preview`

#### `TODO_ALREADY_COMPLETED`

- **Message** : "Todo {todo_id} is already completed"
- **Trigger** : Tentative de completion d'une todo déjà completée
- **Extra Data** : `todo_id`, `completed_at`

#### `EMPTY_TODO_LIST`

- **Message** : "No todos found for user {user_id}"
- **Trigger** : Liste de todos vide
- **Extra Data** : `user_id`, `suggestion`

### **User Errors**

#### `DUPLICATE_USER`

- **Message** : "User already exists with {field}: {value}"
- **Trigger** : Tentative de création d'un utilisateur avec email existant
- **Extra Data** : `field`, `value`
- **Exemple** :

```json
{
  "detail": "User already exists with email: john@example.com",
  "status_code": 400,
  "error_code": "DUPLICATE_USER",
  "extra_data": {
    "field": "email",
    "value": "john@example.com"
  }
}
```

---

## ⚙️ System Errors (5xx)

#### `INTERNAL_SERVER_ERROR`

- **Message** : "Internal server error"
- **Trigger** : Erreur système inattendue
- **Extra Data** : `original_error_type` (en développement)

#### `BAD_REQUEST`

- **Message** : "Bad request"
- **Trigger** : Requête malformée générique

#### `NOT_FOUND`

- **Message** : "{Resource} not found" ou "{Resource} with id '{id}' not found"
- **Trigger** : Ressource générique non trouvée
- **Extra Data** : `resource_type`, `resource_id`

---

## 🔧 Utilisation des Codes d'Erreur

### **Pour les Développeurs Frontend**

```javascript
// Gestion des erreurs spécifiques
async function handleApiError(error) {
  const { error_code, detail, extra_data } = error.response.data;

  switch (error_code) {
    case 'WEAK_PASSWORD':
      showPasswordRequirements(extra_data.missing_requirements);
      break;

    case 'RATE_LIMIT_EXCEEDED':
      showRetryTimer(extra_data.retry_after);
      break;

    case 'TODO_NOT_FOUND':
      redirectToTodoList();
      break;

    case 'EXPIRED_TOKEN':
      refreshToken();
      break;

    default:
      showGenericError(detail);
  }
}
```

### **Pour les Tests Automatisés**

```python
def test_weak_password_validation():
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "weak"
    })

    assert response.status_code == 400
    assert response.json()["error_code"] == "WEAK_PASSWORD"
    assert "missing_requirements" in response.json()["extra_data"]
```

### **Pour le Monitoring**

```python
# Métriques par code d'erreur
error_counts = {
    "WEAK_PASSWORD": 45,
    "RATE_LIMIT_EXCEEDED": 23,
    "TODO_NOT_FOUND": 12,
    "INVALID_TOKEN": 8
}

# Alertes sur erreurs critiques
if error_counts["INTERNAL_SERVER_ERROR"] > threshold:
    send_alert("High server error rate detected")
```

---

## 🚀 Évolution des Codes d'Erreur

### **Bonnes Pratiques**

1. **Stabilité** : Ne jamais supprimer un code d'erreur existant
2. **Versioning** : Ajouter de nouveaux codes sans casser l'existant
3. **Clarté** : Messages compréhensibles par les utilisateurs
4. **Contexte** : `extra_data` riche pour le debugging
5. **Consistance** : Format uniforme pour tous les codes

### **Ajout de Nouveaux Codes**

1. Définir l'exception dans le module approprié
2. Spécifier le `error_code` explicitement
3. Documenter dans ce fichier
4. Ajouter des tests
5. Mettre à jour les intégrations client

---

## 📊 Statistiques des Codes d'Erreur

| Catégorie          | Nombre de Codes | Usage Principal                 |
| ------------------ | --------------- | ------------------------------- |
| **Authentication** | 7               | Login, tokens, sessions         |
| **Authorization**  | 2               | Permissions, accès              |
| **Validation**     | 6               | Formats, longueurs, contraintes |
| **Domain**         | 7               | Logique métier todos/users      |
| **System**         | 3               | Erreurs techniques              |
| **Total**          | **25**          | **Application complète**        |

---

Cette documentation est mise à jour automatiquement avec chaque nouvelle version de l'API. Pour toute question ou suggestion d'amélioration, consultez l'équipe de développement.
