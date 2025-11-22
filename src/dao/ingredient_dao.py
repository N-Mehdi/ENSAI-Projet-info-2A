"""Classe DAO du business object Ingredient."""

from src.dao.db_connection import DBConnection
from src.utils.log_decorator import log
from src.utils.singleton import Singleton
from src.utils.text_utils import normalize_ingredient_name


class IngredientDAO(metaclass=Singleton):
    """DAO pour gérer les ingrédients."""

    @staticmethod
    @log
    def get_all_ingredients() -> list[dict]:
        """Récupère tous les ingrédients.

        Returns
        -------
        list[dict]
            Liste de tous les ingrédients.

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id_ingredient, nom
                FROM ingredient
                ORDER BY nom
                """,
            )
            return cursor.fetchall()

    @staticmethod
    @log
    def get_by_name(nom: str) -> dict | None:
        """Cherche un ingrédient par son nom exact.

        Parameters
        ----------
        nom : str
            Nom de l'ingrédient (doit être normalisé au format Title Case)

        Returns
        -------
        dict | None
            L'ingrédient s'il existe, None sinon

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id_ingredient, nom
                FROM ingredient
                WHERE LOWER(nom) = LOWER(%(nom)s)
                """,
                {"nom": nom},
            )
            return cursor.fetchone()

    @staticmethod
    @log
    def search_by_name(nom: str, limit: int = 10) -> list[dict]:
        """Recherche des ingrédients dont le nom contient la chaîne donnée.
        Utile pour l'auto-complétion et les suggestions.

        Parameters
        ----------
        nom : str
            Partie du nom à rechercher (insensible à la casse)
        limit : int
            Nombre max de résultats

        Returns
        -------
        list[dict]
            Liste des ingrédients correspondants

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id_ingredient, nom
                FROM ingredient
                WHERE SIMILARITY(nom, %(nom)s) > 0.2
                ORDER BY SIMILARITY(nom, %(nom)s) DESC
                LIMIT %(limit)s
                """,
                {"nom": nom, "limit": limit},
            )
            return cursor.fetchall()

    @staticmethod
    def is_alcoholic(ingredient_id: int) -> bool:
        """Vérifie si un ingrédient contient de l'alcool."""
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                        SELECT alcool
                        FROM ingredient
                        WHERE id_ingredient = %(ingredient_id)s
                        """,
                {"ingredient_id": ingredient_id},
            )
            result = cursor.fetchone()

            if result is None:
                return None

            return result["alcool"]

    @staticmethod
    def is_alcoholic_by_name(ingredient_name: str) -> bool:
        """Vérifie si un ingrédient contient de l'alcool en utilisant son nom."""
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT alcool
                    FROM ingredient
                    WHERE LOWER(TRIM(nom)) = LOWER(TRIM(%(ingredient_name)s))
                    """,
                {"ingredient_name": ingredient_name},
            )
            result = cursor.fetchone()

            if result is None:
                return None

            return result["alcool"]

    def get_ingredient_by_name(self, nom: str) -> dict | None:
        """Récupère un ingrédient par son nom (insensible à la casse).

        Parameters
        ----------
        nom : str
            Nom de l'ingrédient

        Returns
        -------
        dict | None
            Ingrédient trouvé ou None

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT id_ingredient, nom, alcool FROM ingredient "
                "WHERE LOWER(nom) = LOWER(%s)",
                (nom,),
            )
            return cursor.fetchone()

    @log
    def create_ingredient(self, nom: str, *, alcool: bool) -> int:
        """Crée un nouvel ingrédient.

        Parameters
        ----------
        nom : str
            Nom de l'ingrédient
        alcool : bool
            Indique si l'ingrédient contient de l'alcool

        Returns
        -------
        int
            ID de l'ingrédient créé

        Raises
        ------
        DAOError
            En cas d'erreur de base de données

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO ingredient (nom, alcool) VALUES (%s, %s) "
                "RETURNING id_ingredient",
                (nom, alcool),
            )
            result = cursor.fetchone()
            return result["id_ingredient"]

    @log
    def get_or_create_ingredient(self, nom: str, *, alcool: bool) -> int:
        """Récupère ou crée un ingrédient.

        Parameters
        ----------
        nom : str
            Nom de l'ingrédient (sera normalisé)
        alcool : bool
            Indique si l'ingrédient contient de l'alcool

        Returns
        -------
        int
            ID de l'ingrédient

        """
        # Normaliser le nom
        nom_normalise = normalize_ingredient_name(nom)

        # Vérifier si l'ingrédient existe
        ingredient = self.get_ingredient_by_name(nom_normalise)
        if ingredient:
            return ingredient["id_ingredient"]

        # Créer l'ingrédient
        return self.create_ingredient(nom_normalise, alcool)
