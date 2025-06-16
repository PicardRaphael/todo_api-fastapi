"""
Presentation Layer - Clean Architecture

Cette couche contient tous les composants de présentation :
- Controllers : Gèrent la logique de présentation et délèguent aux Use Cases
- Middlewares : Interceptent et traitent les requêtes/réponses HTTP

Cette couche dépend uniquement de la couche Application (Use Cases).
"""

from .controllers import *
from .middlewares import *

__all__ = [
    # Controllers will be imported here once created
]
