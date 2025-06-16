"""
Controllers - Couche Presentation

Les controllers gèrent la logique de présentation dans l'architecture hybride :
- Reçoivent les requêtes HTTP des routes
- Valident et transforment les données
- Délèguent la logique métier aux Use Cases
- Gèrent les erreurs et logging
- Formatent les réponses HTTP

Avantages de cette approche :
- Routes simplifiées et focalisées sur HTTP
- Logique de présentation centralisée
- Facilite les tests et la maintenance
- Respect de la Clean Architecture
"""

from .auth_controller import AuthController

__all__ = ["AuthController"]
