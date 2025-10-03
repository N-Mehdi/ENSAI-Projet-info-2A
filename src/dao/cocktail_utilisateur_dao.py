from business_object.cocktail import Cocktail
from dao.db_connection import DBConnection
from utils.log_decorator import log
from utils.singleton import Singleton


class CocktailUtilisateurDao(metaclass=Singleton):
    """Classe contenant les méthodes agissant sur les cocktails et utilisateurs de la base
    de données.
    """

    @log
    def get_prive(id_utilisateur) -> list[Cocktail]:
        """Obtenir tous les cocktails privés d'un utilisateur."""
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT c.id_cocktail,                           "
                    "       c.nom,                                   "
                    "       c.categorie,                             "
                    "       c.verre,                                 "
                    "       c.alcool                                 "
                    "FROM cocktail c                                 "
                    "INNER JOIN acces a using id_cocktail           "
                    "WHERE id_utilisateur = %(id_utilisateur)s       "
                    "AND a.is_owner = TRUE                           ",
                    {"id_utilisateur": id_utilisateur},
                )
                res = cursor.fetchall()

        # Pas fini et surement faux
