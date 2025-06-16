#!/usr/bin/env python3
"""
Script de démonstration de l'Architecture Hybride

Ce script démontre les fonctionnalités de l'architecture hybride en comparant
les approches traditionnelles et hybrides, et en testant toutes les nouvelles fonctionnalités.
"""

import asyncio
import json
import time
from typing import Dict, Any
import requests
import sys
import os

# Ajouter le chemin src pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.shared.logging import get_logger, setup_logging, LoggingConfig
from src.shared.exceptions import *
from src.shared.exceptions.auth import InvalidCredentialsError

# Configuration
BASE_URL = "http://localhost:8001"  # Port hybride
ORIGINAL_URL = "http://localhost:8000"  # Port original

logger = get_logger("hybrid_demo")


class HybridArchitectureDemo:
    """
    Classe de démonstration pour l'architecture hybride.

    Cette classe teste et compare les différentes approches
    architecturales implémentées.
    """

    def __init__(self):
        """Initialiser la démonstration."""
        self.session = requests.Session()
        self.auth_token = None
        self.test_user = {
            "email": "demo@hybrid.test",
            "password": "SecurePassword123!",
            "full_name": "Demo User",
        }

    def print_section(self, title: str):
        """Afficher une section avec formatage."""
        print("\n" + "=" * 60)
        print(f"  {title}")
        print("=" * 60)

    def print_subsection(self, title: str):
        """Afficher une sous-section avec formatage."""
        print(f"\n--- {title} ---")

    def check_server_health(self) -> bool:
        """Vérifier que le serveur hybride est en cours d'exécution."""
        try:
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Serveur hybride en marche : {health_data['status']}")
                print(f"   Version : {health_data['version']}")
                print(f"   Architecture : {health_data['architecture']}")
                return True
            else:
                print(f"❌ Problème serveur : {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Impossible de se connecter au serveur hybride")
            print(
                "   Assurez-vous que 'python main_hybrid.py' est en cours d'exécution"
            )
            return False

    def demonstrate_exception_system(self):
        """Démontrer le système d'exceptions avancé."""
        self.print_section("SYSTÈME D'EXCEPTIONS AVANCÉ")

        print("Testant la hiérarchie d'exceptions...")

        # Test TodoNotFoundError
        try:
            raise TodoNotFoundError(999, 1)
        except TodoAPIException as e:
            print(f"✅ TodoNotFoundError : {e}")
            print(f"   Code HTTP : {e.status_code}")
            print(f"   Données : {e.to_dict()}")

        # Test InvalidCredentialsError
        try:
            raise InvalidCredentialsError("demo@test.com")
        except TodoAPIException as e:
            print(f"✅ InvalidCredentialsError : {e}")
            print(f"   Code HTTP : {e.status_code}")

        # Test ValidationError
        try:
            raise WeakPasswordError(
                password_length=3,
                requirements=["Au moins 8 caractères", "Majuscules et minuscules"],
                missing_requirements=[
                    "Au moins 8 caractères",
                    "Majuscules et minuscules",
                ],
            )
        except TodoAPIException as e:
            print(f"✅ WeakPasswordError : {e}")
            print(f"   Détails : {e.extra_data}")

    def demonstrate_logging_system(self):
        """Démontrer le système de logging avancé."""
        self.print_section("SYSTÈME DE LOGGING AVANCÉ")

        # Configuration du logging pour la démo
        logging_config = LoggingConfig.from_environment()
        setup_logging(logging_config)

        demo_logger = get_logger("demo")

        print("Testant les différents types de logs...")

        # Log structuré normal
        demo_logger.info_structured(
            "Démarrage de la démonstration",
            operation="demo_start",
            user_id=123,
            features=["logging", "exceptions", "controllers"],
        )

        # Log de performance
        start_time = time.time()
        time.sleep(0.1)  # Simulation d'opération
        duration = time.time() - start_time

        demo_logger.info_structured(
            "Opération terminée",
            operation="demo_operation",
            duration=f"{duration:.3f}s",
            status="success",
        )

        # Log de sécurité
        demo_logger.warning_structured(
            "Tentative d'accès suspect détectée",
            operation="security_event",
            ip_address="192.168.1.100",
            user_agent="SuspiciousBot/1.0",
            event_type="suspicious_access",
        )

        print("✅ Logs structurés générés avec succès")

    def test_authentication_flow(self) -> bool:
        """Tester le flux d'authentification hybride."""
        self.print_section("FLUX D'AUTHENTIFICATION HYBRIDE")

        # Test d'inscription
        self.print_subsection("1. Inscription d'utilisateur")
        try:
            register_response = self.session.post(
                f"{BASE_URL}/api/v1/auth/register", json=self.test_user
            )

            if register_response.status_code == 201:
                user_data = register_response.json()
                print(f"✅ Utilisateur créé : {user_data['email']}")
            elif register_response.status_code == 400:
                print("ℹ️ Utilisateur existe déjà, continuons...")
            else:
                print(f"❌ Erreur inscription : {register_response.status_code}")
                print(f"   Réponse : {register_response.text}")

        except Exception as e:
            print(f"❌ Erreur lors de l'inscription : {e}")

        # Test de connexion
        self.print_subsection("2. Connexion utilisateur")
        try:
            login_response = self.session.post(
                f"{BASE_URL}/api/v1/auth/login",
                data={
                    "username": self.test_user["email"],
                    "password": self.test_user["password"],
                },
            )

            if login_response.status_code == 200:
                login_data = login_response.json()
                self.auth_token = login_data["access_token"]
                print(f"✅ Connexion réussie")
                print(f"   Token type : {login_data['token_type']}")
                print(f"   User ID : {login_data['user']['id']}")
                return True
            else:
                print(f"❌ Erreur connexion : {login_response.status_code}")
                print(f"   Réponse : {login_response.text}")
                return False

        except Exception as e:
            print(f"❌ Erreur lors de la connexion : {e}")
            return False

    def test_todo_operations(self):
        """Tester les opérations TODO avec l'architecture hybride."""
        if not self.auth_token:
            print("❌ Pas de token d'authentification, connexion requise")
            return

        self.print_section("OPÉRATIONS TODO HYBRIDES")

        # Headers d'authentification
        headers = {"Authorization": f"Bearer {self.auth_token}"}

        # Test de création
        self.print_subsection("1. Création de TODO")
        todo_data = {
            "title": "Tester l'architecture hybride",
            "description": "Vérifier toutes les fonctionnalités avancées",
            "priority": 5,
            "completed": False,
        }

        try:
            create_response = self.session.post(
                f"{BASE_URL}/api/v1/todos/create", json=todo_data, headers=headers
            )

            if create_response.status_code == 201:
                created_todo = create_response.json()
                todo_id = created_todo["id"]
                print(f"✅ TODO créé avec l'ID : {todo_id}")
                print(f"   Titre : {created_todo['title']}")
                print(f"   Priorité : {created_todo['priority']}")

                # Test de récupération
                self.print_subsection("2. Récupération de TODO")
                get_response = self.session.get(
                    f"{BASE_URL}/api/v1/todos/{todo_id}", headers=headers
                )

                if get_response.status_code == 200:
                    retrieved_todo = get_response.json()
                    print(f"✅ TODO récupéré : {retrieved_todo['title']}")
                else:
                    print(f"❌ Erreur récupération : {get_response.status_code}")

                # Test de mise à jour
                self.print_subsection("3. Mise à jour de TODO")
                update_data = {
                    "title": "Tester l'architecture hybride - TERMINÉ",
                    "completed": True,
                }

                update_response = self.session.patch(
                    f"{BASE_URL}/api/v1/todos/{todo_id}",
                    json=update_data,
                    headers=headers,
                )

                if update_response.status_code == 200:
                    updated_todo = update_response.json()
                    print(f"✅ TODO mis à jour : {updated_todo['title']}")
                    print(f"   Terminé : {updated_todo['completed']}")
                else:
                    print(f"❌ Erreur mise à jour : {update_response.status_code}")

                # Test de suppression
                self.print_subsection("4. Suppression de TODO")
                delete_response = self.session.delete(
                    f"{BASE_URL}/api/v1/todos/delete?id={todo_id}", headers=headers
                )

                if delete_response.status_code == 204:
                    print(f"✅ TODO supprimé avec succès")
                else:
                    print(f"❌ Erreur suppression : {delete_response.status_code}")

            else:
                print(f"❌ Erreur création : {create_response.status_code}")
                print(f"   Réponse : {create_response.text}")

        except Exception as e:
            print(f"❌ Erreur lors des opérations TODO : {e}")

    def test_middleware_features(self):
        """Tester les fonctionnalités des middlewares."""
        self.print_section("FONCTIONNALITÉS DES MIDDLEWARES")

        # Test des headers de sécurité
        self.print_subsection("1. Headers de sécurité")
        try:
            response = self.session.get(f"{BASE_URL}/health")
            security_headers = [
                "X-Content-Type-Options",
                "X-Frame-Options",
                "X-XSS-Protection",
                "Referrer-Policy",
            ]

            print("Headers de sécurité détectés :")
            for header in security_headers:
                if header in response.headers:
                    print(f"✅ {header}: {response.headers[header]}")
                else:
                    print(f"❌ {header}: Non présent")

        except Exception as e:
            print(f"❌ Erreur test headers : {e}")

        # Test du rate limiting
        self.print_subsection("2. Rate Limiting")
        print("Testant les limites de taux...")

        try:
            # Faire plusieurs requêtes rapides
            for i in range(5):
                response = self.session.get(f"{BASE_URL}/health")
                if "X-RateLimit-Remaining" in response.headers:
                    remaining = response.headers["X-RateLimit-Remaining"]
                    print(f"   Requête {i+1}: {remaining} requêtes restantes")
                else:
                    print(f"   Requête {i+1}: Headers rate limit non trouvés")
                time.sleep(0.1)

        except Exception as e:
            print(f"❌ Erreur test rate limiting : {e}")

    def compare_architectures(self):
        """Comparer les architectures originale et hybride."""
        self.print_section("COMPARAISON DES ARCHITECTURES")

        if not self.auth_token:
            print("❌ Authentification requise pour la comparaison")
            return

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        print("Comparaison des temps de réponse...")

        # Test route hybride
        self.print_subsection("Route Hybride")
        start_time = time.time()
        try:
            hybrid_response = self.session.get(
                f"{BASE_URL}/api/v1/todos/all", headers=headers
            )
            hybrid_time = time.time() - start_time
            print(f"✅ Temps de réponse hybride : {hybrid_time:.3f}s")
            print(f"   Status : {hybrid_response.status_code}")

        except Exception as e:
            print(f"❌ Erreur route hybride : {e}")

        # Test route originale (si serveur original disponible)
        self.print_subsection("Route Originale")
        try:
            start_time = time.time()
            original_response = self.session.get(
                f"{BASE_URL}/api/v1/original/todos/all", headers=headers
            )
            original_time = time.time() - start_time
            print(f"✅ Temps de réponse original : {original_time:.3f}s")
            print(f"   Status : {original_response.status_code}")

        except Exception as e:
            print(f"❌ Route originale non disponible : {e}")

    def display_architecture_summary(self):
        """Afficher un résumé de l'architecture hybride."""
        self.print_section("RÉSUMÉ DE L'ARCHITECTURE HYBRIDE")

        try:
            response = self.session.get(f"{BASE_URL}/")
            if response.status_code == 200:
                summary = response.json()

                print("🏗️ Architecture hybride FastAPI")
                print(f"   Description : {summary['description']}")

                print("\n📋 Endpoints disponibles :")
                for category, endpoints in summary["endpoints"].items():
                    print(f"   {category.replace('_', ' ').title()} :")
                    for name, url in endpoints.items():
                        print(f"     - {name} : {url}")

                print("\n🎯 Avantages de l'architecture :")
                for benefit in summary["architecture_benefits"]:
                    print(f"   ✅ {benefit}")

        except Exception as e:
            print(f"❌ Erreur récupération résumé : {e}")

    def run_full_demo(self):
        """Exécuter la démonstration complète."""
        print("🚀 DÉMONSTRATION DE L'ARCHITECTURE HYBRIDE FASTAPI")
        print("=" * 60)

        # Vérification du serveur
        if not self.check_server_health():
            print("\n❌ Impossible de continuer sans serveur en marche")
            print("💡 Exécutez : python main_hybrid.py")
            return

        # Démonstrations des composants
        self.demonstrate_exception_system()
        self.demonstrate_logging_system()

        # Tests fonctionnels
        if self.test_authentication_flow():
            self.test_todo_operations()

        # Tests des middlewares
        self.test_middleware_features()

        # Comparaison
        self.compare_architectures()

        # Résumé final
        self.display_architecture_summary()

        print("\n🎉 DÉMONSTRATION TERMINÉE")
        print("=" * 60)
        print("L'architecture hybride combine avec succès :")
        print("✅ Clean Architecture pour la structure")
        print("✅ MVC pour la simplicité")
        print("✅ Middlewares avancés pour la production")
        print("✅ Contrôleurs intelligents pour la robustesse")
        print("✅ Routes simplifiées pour la maintenabilité")


def main():
    """Point d'entrée principal."""
    demo = HybridArchitectureDemo()
    demo.run_full_demo()


if __name__ == "__main__":
    main()
