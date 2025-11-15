"""doc."""

from src.dao.db_connection import DBConnection
from src.utils.exceptions import IngredientNotFoundError
from src.utils.log_decorator import log
from src.utils.singleton import Singleton
from src.utils.text_utils import normalize_ingredient_name


class IngredientDao(metaclass=Singleton):
    """DAO pour gérer les ingrédients."""

    @log
    def get_all_ingredients(self) -> list[dict]:
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

    @log
    def get_by_name_with_suggestions(self, nom: str) -> dict:
        """Cherche un ingrédient par son nom exact.
        Si non trouvé, lève une exception avec des suggestions.

        Parameters
        ----------
        nom : str
            Nom de l'ingrédient (doit être normalisé au format Title Case)

        Returns
        -------
        dict
            L'ingrédient trouvé

        Raises
        ------
        IngredientNotFoundError
            Si l'ingrédient n'existe pas (avec suggestions)

        """
        # Normaliser le nom
        nom_normalized = normalize_ingredient_name(nom)

        # Chercher l'ingrédient
        ingredient = self.get_by_name(nom_normalized)

        if not ingredient:
            # Chercher des suggestions
            suggestions_data = self.rechercher_ingredient_par_sequence_debut(
                sequence=nom_normalized[:3] if len(nom_normalized) >= 3 else nom_normalized,
                max_resultats=5,
            )
            suggestions = [ing.nom for ing in suggestions_data]
            raise IngredientNotFoundError(nom_normalized, suggestions)

        return ingredient

    @log
    def get_by_name(self, nom: str) -> dict | None:
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
                WHERE nom = %(nom)s
                """,
                {"nom": nom},
            )
            return cursor.fetchone()

    @log
    def search_by_name(self, nom: str, limit: int = 10) -> list[dict]:
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
                WHERE nom ILIKE %(nom)s
                ORDER BY nom
                LIMIT %(limit)s
                """,
                {"nom": f"%{nom}%", "limit": limit},
            )
            return cursor.fetchall()

    def is_alcoholic(self, ingredient_id: int) -> bool:
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

    def is_alcoholic_by_name(self, ingredient_name: str) -> bool:
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
