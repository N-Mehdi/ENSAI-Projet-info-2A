"""Configuration des tests d'intégration."""

import os
import subprocess

import pytest
from dotenv import load_dotenv

from src.dao.db_connection import DBConnection
from src.utils.singleton import Singleton


@pytest.fixture(scope="session", autouse=True)
def load_test_env() -> None:
    """Charge les variables d'environnement de test."""
    load_dotenv(".env.test", override=True)

    db_name = os.getenv("POSTGRES_DATABASE")

    if not db_name or db_name != "bdd_test":
        raise RuntimeError(
            message=f"DANGER: Vous n'utilisez pas la base de test!\n"
            f"POSTGRES_DATABASE actuel: {db_name}\n"
            f"Attendu: 'bdd_test'\n"
            f"Vérifiez votre fichier .env.test",
        )


@pytest.fixture(scope="session", autouse=True)
def populate_test_database(load_test_env) -> None:
    """Peuple la base de test avec les données de référence au début de la session."""
    db_name = os.getenv("POSTGRES_DATABASE")
    db_user = os.getenv("POSTGRES_USER")
    db_host = os.getenv("POSTGRES_HOST")
    db_port = os.getenv("POSTGRES_PORT")
    db_password = os.getenv("POSTGRES_PASSWORD")
    try:
        env = os.environ.copy()
        env["PGPASSWORD"] = db_password

        result = subprocess.run(
            [
                "psql",
                "-h",
                db_host,
                "-p",
                db_port,
                "-U",
                db_user,
                "-d",
                db_name,
                "-f",
                "data/pop_db_test.sql",
            ],
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )

        if "Données insérées avec succès" in result.stdout:
            print(f"Sortie du script:\n{result.stdout}")

    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            message="Impossible de peupler la base de test. "
            "Vérifiez que PostgreSQL est accessible et que le fichier "
            "'scripts/pop_db_test.sql' existe.",
        ) from e
    except FileNotFoundError as e:
        raise RuntimeError(
            message="La commande 'psql' n'a pas été trouvée.\n"
            "Assurez-vous que PostgreSQL est installé et que 'psql' est dans votre"
            "PATH.",
        ) from e


@pytest.fixture
def db_connection() -> None:
    """Fournit une connexion à la base de données de test pour chaque test."""
    connection = DBConnection().connection
    yield connection
    connection.rollback()
    connection.close()


@pytest.fixture(autouse=True)
def reset_singletons() -> None:
    """Réinitialise tous les singletons après chaque test.

    Cette fixture est CRITIQUE pour les tests d'intégration car elle évite
    que les DAOs (qui sont des Singletons) réutilisent des connexions fermées
    entre les tests.

    Sans cette fixture, vous obtiendrez des erreurs "connection already closed".
    """
    yield
    # Après chaque test, nettoyer toutes les instances singleton

    Singleton._instances = {}


@pytest.fixture
def clean_database(db_connection) -> None:
    """Nettoie la base de données avant chaque test."""
    with db_connection.cursor() as cursor:
        cursor.execute("""
            TRUNCATE TABLE
                avis,
                liste_course,
                stock,
                acces,
                instruction,
                cocktail_ingredient,
                cocktail,
                ingredient,
                unite,
                utilisateur
            RESTART IDENTITY CASCADE;
        """)

        db_connection.commit()

    yield

    db_connection.rollback()
