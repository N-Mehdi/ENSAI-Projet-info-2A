"""Data Access Object pour les avis."""
from typing import Any

from business_object.utilisateur import Utilisateur  # noqa: F401  # utilisé si extension plus tard
from dao.db_connection import DBConnection
from utils.log_decorator import log
from utils.singleton import Singleton


class AvisDAO(metaclass=Singleton):
    """Classe contenant les méthodes d'appel à la base de données pour les avis."""

    @log
    def rechercher_avis(self, nom_cocktail: str) -> list[list[Any]]:
        """
        Retourne la liste des avis liés à un cocktail.

        Fait la jointure entre Avis, Cocktail et Utilisateur
        pour récupérer les informations des avis associés
        à un cocktail donné par son nom.

        Args:
            nom_cocktail (str): le nom du cocktail à rechercher

        Returns:
            list[list[Any]]: liste de listes contenant [note, commentaire, pseudo]
        """
        query = """
            SELECT
                avis.note,
                avis.commentaire,
                utilisateur.pseudo
            FROM avis
            LEFT JOIN cocktail USING (id_cocktail)
            LEFT JOIN utilisateur USING (id_utilisateur)
            WHERE cocktail.nom = %(nom)s
        """

        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, {"nom": nom_cocktail})
                results = cursor.fetchall()

        liste_avis = [
            [row["note"], row["commentaire"], row["pseudo"]] for row in results or []
        ]
        return liste_avis
