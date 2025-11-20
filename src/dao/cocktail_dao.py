"""Ce module définit la classe CocktailDAO, responsable des opérations CRUD
sur la table cocktail dans la base de données.
"""

from psycopg2 import Error as DBError

from src.business_object.cocktail import Cocktail
from src.dao.db_connection import DBConnection
from src.utils.exceptions import DAOError
from src.utils.log_decorator import log
from src.utils.singleton import Singleton


class CocktailDAO(metaclass=Singleton):
    """Classe contenant les méthodes agissant sur les cocktails de la base
    de données.
    """

    @staticmethod
    @log
    def rechercher_cocktail_par_nom(nom) -> Cocktail:
        """Recherche un cocktail par son nom exact.

        La recherche est effectuée sur le nom formaté en title case.

        Parameters
        ----------
        nom : str
            Le nom du cocktail à rechercher

        Returns
        -------
        Cocktail | None
            L'objet Cocktail si trouvé, None sinon

        Raises
        ------
        DAOError
            En cas d'erreur de base de données

        """
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
        """Recherche des cocktails dont le nom commence par une séquence donnée.

        La recherche est insensible à la casse et retourne les résultats
        par ordre alphabétique.

        Parameters
        ----------
        sequence : str
            La séquence de caractères recherchée au début du nom
        max_resultats : int
            Le nombre maximum de résultats à retourner

        Returns
        -------
        list[Cocktail]
            Liste des cocktails correspondant à la recherche, triée par nom

        Raises
        ------
        DAOError
            En cas d'erreur de base de données

        """
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
        """Récupère un cocktail aléatoire de la base de données.

        Returns
        -------
        Cocktail
        Un cocktail sélectionné aléatoirement

        Raises
        ------
        DAOError
        En cas d'erreur de base de données

        """

    @staticmethod
    @log
    def get_cocktail_id_by_name(cocktail_name: str) -> int | None:
        """Récupère l'identifiant d'un cocktail par son nom.

        La recherche est insensible à la casse et ignore les espaces superflus.

        Parameters
        ----------
        cocktail_name : str
            Le nom du cocktail à rechercher

        Returns
        -------
        int | None
            L'identifiant du cocktail si trouvé, None sinon

        Raises
        ------
        DAOError
            En cas d'erreur de base de données

        """
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

        Pour chaque cocktail, retourne ses informations de base ainsi que
        la liste complète de ses ingrédients avec quantités et unités.

        Returns
        -------
        list[dict]
            Liste de dictionnaires contenant pour chaque ligne :
            - id_cocktail : int
            - nom : str
            - categorie : str
            - verre : str
            - alcool : bool
            - image : str
            - id_ingredient : int
            - qte : float
            - unite : str

        Raises
        ------
        DAOError
            En cas d'erreur de base de données

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

        except DBError as e:
            raise DAOError(message=None) from e

    def get_cocktails_quasi_realisables(
        self,
        id_utilisateur: int,
    ) -> list[dict]:
        """Récupère tous les cocktails avec leurs ingrédients et le stock de
        l'utilisateur.

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

        except DBError as e:
            raise DAOError(message=None) from e
