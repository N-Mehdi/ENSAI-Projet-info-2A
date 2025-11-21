"""Classe DAO agissant sur les instructions des cocktails."""

from src.dao.db_connection import DBConnection
from src.utils.exceptions import DAOError, InstructionError
from src.utils.log_decorator import log


class InstructionDAO:
    """DAO pour accéder aux instructions de cocktails."""

    @staticmethod
    def get_instruction(id_cocktail: int) -> str | None:
        """Récupération du texte d'instruction pour un cocktail.

        Parameters
        ----------
        id_cocktail : int
            Identifiant du cocktail dont on veut récupérer l'instruction.

        Returns
        -------
        texte : str or None
            Le texte de l'instruction si trouvé,
            None sinon.

        """
        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    """
                SELECT texte
                FROM instruction
                WHERE id_cocktail = %(id_cocktail)s
                LIMIT 1;
            """,
                    {"id_cocktail": id_cocktail},
                )
                row = cursor.fetchone()

        except Exception as e:
            raise InstructionError(
                message=f"Erreur lors de la récupération de l'instruction : {e}",
            ) from e
        if row:
            return row["texte"]

        return None

    @staticmethod
    @log
    def ajouter_instruction(
        id_cocktail: int,
        texte: str,
        langue: str = "en",
    ) -> bool:
        """Ajoute une instruction pour un cocktail dans la base de données.

        Parameters
        ----------
        id_cocktail : int
            L'identifiant du cocktail
        texte : str
            Le texte de l'instruction
        langue : str, optional
            La langue de l'instruction (par défaut: "en")

        Returns
        -------
        bool
            True si l'insertion a réussi

        Raises
        ------
        DAOError
            En cas d'erreur lors de l'insertion

        """
        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO instruction (id_cocktail, langue, texte)
                    VALUES (%s, %s, %s);
                    """,
                    (id_cocktail, langue, texte),
                )

        except Exception as e:
            raise DAOError(
                message=f"Erreur lors de l'ajout de l'instruction : {e}",
            ) from e

        return True
