"""doc."""

from src.dao.db_connection import DBConnection
from src.utils.log_decorator import log


class UniteDAO:
    """DAO pour gérer les unités de mesure."""

    @log
    def get_or_create_unit(self, nom_unite: str) -> int:
        """Récupère l'ID d'une unité ou la crée si elle n'existe pas.

        Parameters
        ----------
        nom_unite : str
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
                WHERE LOWER(nom_unite) = LOWER(%(nom_unite)s)
                """,
                {"nom_unite": nom_unite},
            )

            row = cursor.fetchone()
            if row:
                return row["id_unite"]

            # Créer l'unité si elle n'existe pas
            cursor.execute(
                """
                INSERT INTO unite (nom_unite)
                VALUES (%(nom_unite)s)
                RETURNING id_unite
                """,
                {"nom_unite": nom_unite},
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
                "SELECT nom_unite FROM unite WHERE id_unite = %(id_unite)s",
                {"id_unite": id_unite},
            )

            row = cursor.fetchone()
            return row["nom_unite"] if row else None
