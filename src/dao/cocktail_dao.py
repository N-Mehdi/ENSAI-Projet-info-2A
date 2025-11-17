"""Ce module définit la classe CocktailDAO, responsable des opérations CRUD
sur la table cocktail dans la base de données.
"""

from src.business_object.cocktail import Cocktail
from src.dao.db_connection import DBConnection
from src.utils.exceptions import DAOError
from src.utils.log_decorator import log, logging
from src.utils.singleton import Singleton


class CocktailDAO(metaclass=Singleton):
    """Classe contenant les méthodes agissant sur les cocktails de la base
    de données.
    """

    @staticmethod
    @log
    def rechercher_cocktail_par_nom(nom) -> Cocktail:
        """Doc."""
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """SELECT *
                FROM cocktail
                WHERE nom = %(nom)s  """,
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

    @staticmethod
    @log
    def rechercher_cocktail_par_sequence_debut(
        sequence,
        max_resultats,
    ) -> list[Cocktail]:
        """Doc."""
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

    @staticmethod
    @log
    def rechercher_cocktail_aleatoire() -> Cocktail:
        """Doc."""

    @staticmethod
    @log
    def get_cocktail_id_by_name(cocktail_name: str) -> int | None:
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

    @staticmethod
    @log
    def get_tous_cocktails_avec_ingredients() -> list[dict]:
        """Récupère tous les cocktails avec leurs ingrédients requis.

        Returns
        -------
        list[dict]
            Liste de tous les cocktails avec leurs ingrédients

        """
        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        c.id_cocktail,
                        c.nom,
                        c.categorie,
                        c.verre,
                        c.alcool,
                        c.image,
                        ci.id_ingredient,
                        ci.qte,
                        ci.unite
                    FROM cocktail c
                    LEFT JOIN cocktail_ingredient ci ON c.id_cocktail = ci.id_cocktail
                    ORDER BY c.id_cocktail, ci.id_ingredient
                    """,
                )

                return cursor.fetchall()

        except Exception as e:
            logging.exception("Erreur lors de la récupération des cocktails avec ingrédients")
            raise DAOError from e

    def get_cocktails_quasi_realisables(
        self,
        id_utilisateur: int,
    ) -> list[dict]:
        """Récupère tous les cocktails avec leurs ingrédients et le stock de l'utilisateur.

        Retourne les données brutes sans calcul de conversion.

        Parameters
        ----------
        id_utilisateur : int
            ID de l'utilisateur

        Returns
        -------
        list[dict]
            Liste de dictionnaires avec les données brutes

        """
        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        c.id_cocktail,
                        c.nom,
                        c.categorie,
                        c.verre,
                        c.alcool,
                        c.image,
                        ci.id_ingredient,
                        ci.qte as quantite_requise,
                        ci.unite as unite_requise,
                        i.nom as nom_ingredient,
                        s.quantite as quantite_stock,
                        u_stock.abbreviation as unite_stock
                    FROM cocktail c
                    LEFT JOIN cocktail_ingredient ci ON c.id_cocktail = ci.id_cocktail
                    LEFT JOIN ingredient i ON ci.id_ingredient = i.id_ingredient
                    LEFT JOIN stock s ON ci.id_ingredient = s.id_ingredient
                        AND s.id_utilisateur = %(id_utilisateur)s
                    LEFT JOIN unite u_stock ON s.id_unite = u_stock.id_unite
                    ORDER BY c.id_cocktail, ci.id_ingredient
                    """,
                    {"id_utilisateur": id_utilisateur},
                )

                return cursor.fetchall()

        except Exception as e:
            logging.exception("Erreur lors de la récupération des données pour cocktails quasi-réalisables")
            raise DAOError from e
