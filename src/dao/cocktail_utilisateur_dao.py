from business_object.cocktail import Cocktail
from dao.db_connection import DBConnection
from utils.log_decorator import log
from utils.singleton import Singleton

# rien n'est testé et pas fini


class CocktailUtilisateurDao(metaclass=Singleton):
    """Classe contenant les méthodes agissant sur les cocktails et utilisateurs de la base
    de données.
    """

    @log
    def get_prive(self, id_utilisateur) -> list[Cocktail]:
        """Obtenir tous les cocktails privés d'un utilisateur."""
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT c.id_cocktail,                           "
                    "       c.nom,                                   "
                    "       c.categorie,                             "
                    "       c.verre,                                 "
                    "       c.alcool                                 "
                    "       c.image                                  "
                    "FROM cocktail c                                 "
                    "INNER JOIN acces a using id_cocktail            "
                    "WHERE id_utilisateur = %(id_utilisateur)s       "
                    "AND a.is_owner = TRUE                           ",
                    {"id_utilisateur": id_utilisateur},
                )
                res = cursor.fetchall()

        liste_cocktails_prives = []
        
        if res:
            for cocktail in res:
                liste_cocktails_prives.append(
                    Cocktail(
                        id_cocktail=cocktail["id_cocktail"],
                        nom=cocktail["nom"],
                        categorie=cocktail["categorie"],
                        verre=cocktail["verre"],
                        alcool=cocktail["alcool"],
                        image=cocktail["image"]
                    )
                )
    
        return liste_cocktails_prives

    def update_cocktail_prive(self, id_utilisateur, id_cocktail) -> Cocktail:
        pass

    @log
    def delete_cocktail_prive(id_utilisateur, id_cocktail) -> None:
        """Supprime le cocktail privé d'un utilisateur"""

        sql_delete_acces = """
        DELETE FROM acces
        WHERE id_cocktail = %(id_cocktail)s
          AND id_utilisateur = %(id_utilisateur)s
          AND is_owner = TRUE;
        """

        sql_delete_cocktail = """
        DELETE FROM cocktail
        WHERE id_cocktail = %(id_cocktail)s;
        """

        params = {
            "id_cocktail": id_cocktail,
            "id_utilisateur": id_utilisateur,
        }

        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    cursor.execute(sql_delete_acces, params),
                    cursor.execute(sql_delete_cocktail, params)
                )

        @log
        def get_favoris(self, id_utilisateur) -> list[Cocktail]:
            """Obtenir tous les cocktails favoris d'un utilisateur."""
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT c.id_cocktail,                           "
                    "       c.nom,                                   "
                    "       c.categorie,                             "
                    "       c.verre,                                 "
                    "       c.alcool                                 "
                    "       c.image                                  "
                    "FROM cocktail c                                 "
                    "INNER JOIN avis a using id_cocktail            "
                    "WHERE id_utilisateur = %(id_utilisateur)s       "
                    "AND a.favoris = TRUE                           ",
                    {"id_utilisateur": id_utilisateur},
                )
                res = cursor.fetchall()

        liste_cocktails_favoris = []
        
        if res:
            for cocktail in res:
                liste_cocktails_favoris.append(
                    Cocktail(
                        id_cocktail=cocktail["id_cocktail"],
                        nom=cocktail["nom"],
                        categorie=cocktail["categorie"],
                        verre=cocktail["verre"],
                        alcool=cocktail["alcool"],
                        image=cocktail["image"]
                    )
                )
    
        return liste_cocktails_favoris

    @log
    def update_cocktail_favoris(self, id_utilisateur, id_cocktail) -> None:
        """Ajoute un cocktail dans les favoris d'un utilisateur"""

        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE avis                                "
                    "SET favoris = TRUE                         "
                    "WHERE id_utilisateur = %(id_utilisateur)s  "
                    "AND id_coktail = %(id_cocktail)s           ",
                    {
                        "id_cocktail": id_cocktail,
                        "id_utilisateur": id_utilisateur,
                    },
                )

    @log
    def delete_cocktail_favoris(self, id_utilisateur, id_cocktail) -> None:
        """Supprime un cocktail des favoris d'un utilisateur"""

        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE avis                                "
                    "SET favoris = FALSE                        "
                    "WHERE id_utilisateur = %(id_utilisateur)s  "
                    "AND id_coktail = %(id_cocktail)s           ",
                    {
                        "id_cocktail": id_cocktail,
                        "id_utilisateur": id_utilisateur,
                    },
                )


        


