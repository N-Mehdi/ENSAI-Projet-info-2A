"""cocktail_dao.py
Classe DAO du business object Cocktail.
"""

from src.business_object.cocktail import Cocktail
from src.dao.db_connection import DBConnection
from src.utils.log_decorator import log
from src.utils.singleton import Singleton


class CocktailDao(metaclass=Singleton):
    """Classe contenant les méthodes agissant sur les cocktails de la base
    de données.
    """

    @log
    def rechercher_cocktail_par_nom(self, nom) -> Cocktail:
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT *                       FROM cocktail                  WHERE nom = %(nom)s            ",
                {"nom": nom.title()},
            )
            res = cursor.fetchone()
        cocktail = None
        if res:
            cocktail = Cocktail(
                id_cocktail=res["id_cocktail"],
                nom=res["nom"],
                categorie=res["categorie"],
                verre=res["verre"],
                alcool=res["alcool"],
                image=res["image"],
            )
        return cocktail

    @log
    def rechercher_cocktail_par_sequence_debut(
        self,
        sequence,
        max_resultats,
    ) -> list[Cocktail]:
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT *                       "
                "FROM cocktail                  "
                "WHERE nom ILIKE %(sequence)s   "
                "ORDER BY nom ASC               "
                "LIMIT %(max_resultats)s        ",
                {"sequence": sequence + "%", "max_resultats": max_resultats},
            )
            res = cursor.fetchall()

        liste_cocktails = []
        if res:
            for raw_cocktail in res:
                cocktail = Cocktail(
                    id_cocktail=raw_cocktail["id_cocktail"],
                    nom=raw_cocktail["nom"],
                    categorie=raw_cocktail["categorie"],
                    verre=raw_cocktail["verre"],
                    alcool=raw_cocktail["alcool"],
                    image=raw_cocktail["image"],
                )
                liste_cocktails.append(cocktail)
        return liste_cocktails

    def rechercher_cocktail_aleatoire():
        pass

    def get_cocktail_id_by_name(self, cocktail_name: str) -> int | None:
        """Récupère l'ID d'un cocktail par son nom."""
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT id_cocktail
                    FROM cocktail
                    WHERE LOWER(TRIM(nom)) = LOWER(TRIM(%(cocktail_name)s))
                    """,
                {"cocktail_name": cocktail_name},
            )
            result = cursor.fetchone()
            return result["id_cocktail"] if result else None
