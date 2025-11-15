"""stock_course_dao.py
Class dao du business object Stock.
"""

from dao.db_connection import DBConnection
from src.utils.log_decorator import log
from utils.singleton import Singleton


class StockCourseDao(metaclass=Singleton):
    """Classe contenant les méthodes agissants sur le stock d'un utilisateur."""

    @log
    @staticmethod
    def update_or_create_stock_item(
        id_utilisateur: int,
        id_ingredient: int,
        quantite: float,
        id_unite: int,
    ) -> bool:
        """Ajoute ou met à jour un ingrédient dans le stock.

        - Si l'ingrédient n'existe pas, il est créé avec la quantité donnée
        - Si l'ingrédient existe, la quantité est ajoutée (cumul) et l'unité est mise à jour

        Parameters
        ----------
        id_utilisateur : int
            ID de l'utilisateur
        id_ingredient : int
            ID de l'ingrédient
        quantite : float
            Quantité à ajouter (cumulée si l'ingrédient existe déjà)
        id_unite : int
            ID de l'unité de mesure

        Returns
        -------
        bool
            True si l'opération a réussi

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO stock (id_utilisateur, id_ingredient, quantite, id_unite)
                VALUES (%(id_utilisateur)s, %(id_ingredient)s, %(quantite)s, %(id_unite)s)
                ON CONFLICT (id_utilisateur, id_ingredient)
                DO UPDATE SET
                    quantite = stock.quantite + EXCLUDED.quantite,
                    id_unite = EXCLUDED.id_unite
                """,
                {
                    "id_utilisateur": id_utilisateur,
                    "id_ingredient": id_ingredient,
                    "quantite": quantite,
                    "id_unite": id_unite,
                },
            )
            return cursor.rowcount > 0

    @log
    @staticmethod
    def get_stock(id_utilisateur: int, only_available: bool = True) -> list[dict]:
        """Récupère le stock d'un utilisateur.

        Parameters
        ----------
        id_utilisateur : int
            ID de l'utilisateur
        only_available : bool, optional
            Si True, retourne seulement les ingrédients avec quantité > 0

        Returns
        -------
        list[dict]
            Liste des items du stock (dictionnaires bruts)

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            query = """
                SELECT
                    s.id_ingredient,
                    i.nom as nom_ingredient,
                    s.quantite,
                    s.id_unite,
                    u.abbreviation as code_unite,
                    u.nom as nom_unite_complet
                FROM stock s
                JOIN ingredient i ON s.id_ingredient = i.id_ingredient
                LEFT JOIN unite u ON s.id_unite = u.id_unite
                WHERE s.id_utilisateur = %(id_utilisateur)s
            """

            if only_available:
                query += " AND s.quantite > 0"

            query += " ORDER BY i.nom"

            cursor.execute(query, {"id_utilisateur": id_utilisateur})

            return cursor.fetchall()

    @log
    @staticmethod
    def get_stock_item(
        id_utilisateur: int,
        id_ingredient: int,
    ) -> dict | None:
        """Récupère un item spécifique du stock.

        Parameters
        ----------
        id_utilisateur : int
            ID de l'utilisateur
        id_ingredient : int
            ID de l'ingrédient

        Returns
        -------
        dict | None
            L'item s'il existe (dictionnaire brut), None sinon

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    s.id_ingredient,
                    i.nom as nom_ingredient,
                    s.quantite,
                    s.id_unite,
                    u.abbreviation as code_unite,
                    u.nom as nom_unite_complet
                FROM stock s
                JOIN ingredient i ON s.id_ingredient = i.id_ingredient
                LEFT JOIN unite u ON s.id_unite = u.id_unite
                WHERE s.id_utilisateur = %(id_utilisateur)s
                AND s.id_ingredient = %(id_ingredient)s
                """,
                {
                    "id_utilisateur": id_utilisateur,
                    "id_ingredient": id_ingredient,
                },
            )

        # Retourner le dictionnaire brut
        return cursor.fetchone()

    @log
    @staticmethod
    def decrement_stock_item(
        id_utilisateur: int,
        id_ingredient: int,
        quantite: float,
    ) -> dict:
        """Décrémente la quantité d'un ingrédient dans le stock.

        Parameters
        ----------
        id_utilisateur : int
            ID de l'utilisateur
        id_ingredient : int
            ID de l'ingrédient
        quantite : float
            Quantité à retirer (doit être > 0)

        Returns
        -------
        dict
            Informations sur l'opération :
            - nouvelle_quantite : float - La nouvelle quantité après décrémentation
            - supprime : bool - True si la quantité atteint 0 (ligne supprimée)

        Raises
        ------
        ValueError
            Si la quantité à retirer est supérieure à la quantité disponible.

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            # Récupérer la quantité actuelle
            cursor.execute(
                """
                SELECT quantite
                FROM stock
                WHERE id_utilisateur = %(id_utilisateur)s
                AND id_ingredient = %(id_ingredient)s
                """,
                {
                    "id_utilisateur": id_utilisateur,
                    "id_ingredient": id_ingredient,
                },
            )

            row = cursor.fetchone()
            if not row:
                raise ValueError("Ingrédient non trouvé dans le stock")

            # Convertir Decimal en float
            quantite_actuelle = float(row["quantite"])

            # Vérifier que la quantité à retirer n'est pas supérieure à la quantité actuelle
            if quantite > quantite_actuelle:
                raise ValueError(
                    f"Impossible de retirer {quantite} (quantité disponible : {quantite_actuelle})",
                )

            nouvelle_quantite = quantite_actuelle - quantite

            # Si la nouvelle quantité est 0 (ou très proche de 0), supprimer la ligne
            if nouvelle_quantite < 0.0001:  # Tolérance pour les arrondis flottants
                cursor.execute(
                    """
                    DELETE FROM stock
                    WHERE id_utilisateur = %(id_utilisateur)s
                    AND id_ingredient = %(id_ingredient)s
                    """,
                    {
                        "id_utilisateur": id_utilisateur,
                        "id_ingredient": id_ingredient,
                    },
                )
                return {
                    "nouvelle_quantite": 0.0,
                    "supprime": True,
                }

            # Sinon, mettre à jour la quantité
            cursor.execute(
                """
                UPDATE stock
                SET quantite = %(nouvelle_quantite)s
                WHERE id_utilisateur = %(id_utilisateur)s
                AND id_ingredient = %(id_ingredient)s
                """,
                {
                    "id_utilisateur": id_utilisateur,
                    "id_ingredient": id_ingredient,
                    "nouvelle_quantite": nouvelle_quantite,
                },
            )

            return {
                "nouvelle_quantite": nouvelle_quantite,
                "supprime": False,
            }

    @log
    @staticmethod
    def delete_stock_item(id_utilisateur: int, id_ingredient: int) -> bool:
        """Supprime complètement un ingrédient du stock (quelle que soit la quantité).

        Cette méthode supprime la ligne entière, utilisez decrement_stock_item()
        pour retirer une quantité spécifique.

        Parameters
        ----------
        id_utilisateur : int
            ID de l'utilisateur
        id_ingredient : int
            ID de l'ingrédient à supprimer

        Returns
        -------
        bool
            True si la suppression a réussi

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM stock
                WHERE id_utilisateur = %(id_utilisateur)s
                AND id_ingredient = %(id_ingredient)s
                """,
                {
                    "id_utilisateur": id_utilisateur,
                    "id_ingredient": id_ingredient,
                },
            )
            return cursor.rowcount > 0

    @log
    @staticmethod
    def get_full_stock(id_utilisateur: int) -> list[dict]:
        """Récupère tous les ingrédients avec leur quantité dans le stock.
        Les ingrédients non présents dans le stock auront quantite = 0.

        Parameters
        ----------
        id_utilisateur : int
            id de l'utilisateur

        Returns
        -------
        list[dict]
            Liste de tous les ingrédients avec leur quantité.

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    i.id_ingredient,
                    i.nom as nom_ingredient,
                    COALESCE(s.quantite, 0) as quantite,
                    s.id_unite,
                    u.abbreviation as code_unite,
                    u.nom as nom_unite_complet
                FROM ingredient i
                LEFT JOIN stock s ON s.id_ingredient = i.id_ingredient 
                                  AND s.id_utilisateur = %(id_utilisateur)s
                LEFT JOIN unite u ON s.id_unite = u.id_unite
                ORDER BY i.nom
                """,
                {"id_utilisateur": id_utilisateur},
            )
            return cursor.fetchall()

    @log
    @staticmethod
    def get_unite_info(id_unite: int) -> dict | None:
        """Récupère les informations d'une unité.

        Parameters
        ----------
        id_unite : int
            ID de l'unité

        Returns
        -------
        dict | None
            Les infos de l'unité (abbreviation, type) ou None

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT abbreviation, type
                FROM unite
                WHERE id_unite = %(id_unite)s
                """,
                {"id_unite": id_unite},
            )
            return cursor.fetchone()
