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
                        image=cocktail["image"],
                    ),
                )

        return liste_cocktails_prives

    @log
    def insert_cocktail_prive(self, id_utilisateur, cocktail: Cocktail) -> int:
        """Ajoute un nouveau cocktail privé d'un utilisateur"""
        # Ajout du cocktail dans la base de données et récupération de son id
        sql_insert_cocktail = """
        INSERT INTO cocktail (nom, categorie, verre, alcool, image)
        VALUES (%(nom)s, %(categorie)s, %(verre)s, %(alcool)s, %(image)s)
        RETURNING id_cocktail;
        """

        # Insertion du cocktail dans la table acces pour établir le lien de propriété
        sql_insert_acces = """
        INSERT INTO acces (id_cocktail, id_utilisateur, is_owner, can_edit)
        VALUES (%(id_cocktail)s, %(id_utilisateur)s, TRUE, TRUE);
        """

        # Paramètres pour l'insertion du cocktail
        cocktail_params = {
            "nom": cocktail.nom,
            "categorie": cocktail.categorie,
            "verre": cocktail.verre,
            "alcool": cocktail.alcool,
            "image": cocktail.image,
        }

        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                # Ajout du cocktail et récupération de l'id
                cursor.execute(sql_insert_cocktail, cocktail_params)
                # Récupération de l'id généré par la bdd
                res = cursor.fetchone()
                new_cocktail_id = res["id_cocktail"]
                # Ajout de la relation d'accès
                acces_params = {
                    "id_cocktail": new_cocktail_id,
                    "id_utilisateur": id_utilisateur,
                }
                cursor.execute(sql_insert_acces, acces_params)
        return new_cocktail_id

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
                    cursor.execute(sql_delete_cocktail, params),
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
                        image=cocktail["image"],
                    ),
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

    @log
    def get_teste(self, id_utilisateur) -> list[Cocktail]:
        """Obtenir tous les cocktails testés par un utilisateur."""
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
                    "AND a.teste = TRUE                           ",
                    {"id_utilisateur": id_utilisateur},
                )
                res = cursor.fetchall()

        liste_cocktails_testes = []

        if res:
            for cocktail in res:
                liste_cocktails_testes.append(
                    Cocktail(
                        id_cocktail=cocktail["id_cocktail"],
                        nom=cocktail["nom"],
                        categorie=cocktail["categorie"],
                        verre=cocktail["verre"],
                        alcool=cocktail["alcool"],
                        image=cocktail["image"],
                    ),
                )

        return liste_cocktails_testes

    @log
    def update_cocktail_teste(self, id_utilisateur, id_cocktail) -> None:
        """Ajoute un cocktail dans les cocktails testés d'un utilisateur"""
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE avis                                "
                    "SET teste = TRUE                         "
                    "WHERE id_utilisateur = %(id_utilisateur)s  "
                    "AND id_coktail = %(id_cocktail)s           ",
                    {
                        "id_cocktail": id_cocktail,
                        "id_utilisateur": id_utilisateur,
                    },
                )

    @log
    def delete_cocktail_teste(self, id_utilisateur, id_cocktail) -> None:
        """Supprime un cocktail des cocktails testés d'un utilisateur"""
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE avis                                "
                    "SET teste = FALSE                        "
                    "WHERE id_utilisateur = %(id_utilisateur)s  "
                    "AND id_coktail = %(id_cocktail)s           ",
                    {
                        "id_cocktail": id_cocktail,
                        "id_utilisateur": id_utilisateur,
                    },
                )
