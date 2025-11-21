"""Classe DAO du business object Unite."""


from src.dao.db_connection import DBConnection
from src.utils.log_decorator import log


class UniteDAO:
    """DAO pour gérer les unités de mesure."""

    @log
    def get_or_create_unit(self, nom: str) -> int:
        """Récupère l'ID d'une unité ou la crée si elle n'existe pas.

        Parameters
        ----------
        nom : str
            Nom de l'unité (ex: "ml", "g", "oz", "dash")

        Returns
        -------
        int
            ID de l'unité

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            # Vérifier si l'unité existe (insensible à la casse)
            cursor.execute(
                """
                SELECT id_unite
                FROM unite
                WHERE LOWER(nom) = LOWER(%(nom)s)
                """,
                {"nom": nom},
            )

            row = cursor.fetchone()
            if row:
                return row["id_unite"]

            # Créer l'unité si elle n'existe pas
            cursor.execute(
                """
                INSERT INTO unite (nom)
                VALUES (%(nom)s)
                RETURNING id_unite
                """,
                {"nom": nom},
            )

            return cursor.fetchone()["id_unite"]

    @log
    def get_unit_name_by_id(self, id_unite: int) -> str | None:
        """Récupère le nom d'une unité par son ID.

        Parameters
        ----------
        id_unite : int
            ID de l'unité

        Returns
        -------
        str | None
            Nom de l'unité ou None si non trouvée

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT nom FROM unite WHERE id_unite = %(id_unite)s",
                {"id_unite": id_unite},
            )

            row = cursor.fetchone()
            return row["nom"] if row else None
