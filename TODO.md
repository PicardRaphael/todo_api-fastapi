Pour /auth/login:

- Si mot de passe faux :
  {
  "detail": "Invalid credentials"
  }
  alors qu'il faudrait mauvais mot de passe quelque chose comme ça.
- Si username ou email n'existe pas faudrait dire actuellement j'ai mis un username qui n'existe pas et j'ai encore eu :
  {
  "detail": "Invalid credentials"
  }
- Dans request body dire qu'on peut utilise soir username soit email là on dirait qu'on peut utiliser que username
