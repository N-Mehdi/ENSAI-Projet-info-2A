"""doc."""

from business_object.cocktail import Cocktail
from dao.db_connection import DBConnection
from utils.log_decorator import log
from utils.singleton import Singleton


class CocktailUtilisateurDao(metaclass=Singleton):
    """Classe contenant les méthodes agissant sur les cocktails et utilisateurs de la base
    de données.
    """

    @staticmethod
    @log
    def get_prive(id_utilisateur) -> list[Cocktail]:
        """Obtenir tous les cocktails privés d'un utilisateur."""
        with DBConnection().connection as connection, connection.cursor() as cursor:
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
            liste_cocktails_prives = [
                Cocktail(
                    id_cocktail=cocktail["id_cocktail"],
                    nom=cocktail["nom"],
                    categorie=cocktail["categorie"],
                    verre=cocktail["verre"],
                    alcool=cocktail["alcool"],
                    image=cocktail["image"],
                )
                for cocktail in res
            ]

        return liste_cocktails_prives

    @staticmethod
    @log
    def insert_cocktail_prive(id_utilisateur, cocktail: Cocktail) -> int:
        """Ajoute un nouveau cocktail privé d'un utilisateur."""
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

        with DBConnection().connection as connection, connection.cursor() as cursor:
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

    @staticmethod
    @log
    def get_cocktail_ingredient(id_cocktail) -> dict:
        """Récupère tous les ingrédients d'un cocktail donné."""
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT id_ingredient, quantite FROM cocktail_ingredient WHERE id_cocktail = %(id_cocktail)s",
                {"id_cocktail": id_cocktail},
            )
            # Retourne un dictionnaire {id_ingredient: quantite}
            return {row[0]: row[1] for row in cursor.fetchall()}

    @staticmethod
    @log
    def update_cocktail_prive_modif_ingredient(
        id_utilisateur,
        id_cocktail,
        id_ingredient,
        quantite,
    ) -> None:
        """Change la quantité d'un ingrédient dans la recette privée d'un utilisateur."""
        with DBConnection().connection as connection, connection.cursor() as cursor:
            # Vérifier si l'utilisateur est bien le propriétaire du cocktail
            cursor.execute(
                "SELECT 1 FROM acces "
                "WHERE id_utilisateur = %(id_utilisateur)s "
                "AND id_cocktail = %(id_cocktail)s "
                "AND is_owner = TRUE",
                {
                    "id_utilisateur": id_utilisateur,
                    "id_cocktail": id_cocktail,
                },
            )

            # Si l'utilisateur est le propriétaire :
            if cursor.fetchone():
                cursor.execute(
                    "UPDATE cocktail_ingredient "
                    "SET quantite = %(quantite)s "
                    "WHERE id_ingredient = %(id_ingredient)s "
                    "AND id_cocktail = %(id_cocktail)s",
                    {
                        "quantite": quantite,
                        "id_ingredient": id_ingredient,
                        "id_cocktail": id_cocktail,
                    },
                )
            else:
                # Si l'utilisateur n'est pas le propriétaire
                raise PermissionError(
                    "L'utilisateur n'es pas le propriétaire du cocktail.",
                )

    @staticmethod
    @log
    def update_cocktail_prive_ajout_ingredient(
        id_utilisateur,
        id_cocktail,
        id_ingredient,
        quantite,
    ) -> None:
        """Ajouter un ingrédient à la recette privée d'un utilisateur."""
        with DBConnection().connection as connection, connection.cursor() as cursor:
            # Vérifier si l'utilisateur est bien le propriétaire du cocktail
            cursor.execute(
                "SELECT 1 FROM acces "
                "WHERE id_utilisateur = %(id_utilisateur)s "
                "AND id_cocktail = %(id_cocktail)s "
                "AND is_owner = TRUE",
                {
                    "id_utilisateur": id_utilisateur,
                    "id_cocktail": id_cocktail,
                },
            )

            # Si l'utilisateur est le propriétaire :
            if cursor.fetchone():
                cursor.execute(
                    "INSERT INTO cocktail_ingredient (id_cocktail,  "
                    "                                 id_ingredient,"
                    "                                  quantite)    "
                    "VALUES (%(id_cocktail)s, %(id_ingredient)s,    "
                    "                                %(quantite)s)  ",
                    {
                        "id_cocktail": id_cocktail,
                        "id_ingredient": id_ingredient,
                        "quantite": quantite,
                    },
                )
            else:
                # Si l'utilisateur n'est pas le propriétaire
                raise PermissionError(
                    "L'utilisateur n'est pas le propriétaire du cocktail.",
                )

    @staticmethod
    @log
    def update_cocktail_prive_supprimer_ingredient(
        id_utilisateur,
        id_cocktail,
        id_ingredient,
        quantite,
    ) -> None:
        """Supprimer un ingrédient de la recette privée d'un utilisateur."""
        with DBConnection().connection as connection, connection.cursor() as cursor:
            # Vérifier si l'utilisateur est bien le propriétaire du cocktail
            cursor.execute(
                "SELECT 1 FROM acces "
                "WHERE id_utilisateur = %(id_utilisateur)s "
                "AND id_cocktail = %(id_cocktail)s "
                "AND is_owner = TRUE",
                {
                    "id_utilisateur": id_utilisateur,
                    "id_cocktail": id_cocktail,
                },
            )

            # Si l'utilisateur est le propriétaire :
            if cursor.fetchone():
                cursor.execute(
                    "DELETE FROM cocktail_ingredient "
                    "WHERE id_ingredient = %(id_ingredient)s "
                    "AND id_cocktail = %(id_cocktail)s",
                    {
                        "id_ingredient": id_ingredient,
                        "id_cocktail": id_cocktail,
                    },
                )
            else:
                # Si l'utilisateur n'est pas le propriétaire
                raise PermissionError(
                    "L'utilisateur n'est pas le propriétaire du cocktail.",
                )

    @staticmethod
    @log
    def delete_cocktail_prive(id_utilisateur, id_cocktail) -> None:
        """Supprime le cocktail privé d'un utilisateur."""
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

        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                cursor.execute(sql_delete_acces, params),
                cursor.execute(sql_delete_cocktail, params),
            )

    @staticmethod
    @log
    def get_favoris(id_utilisateur) -> list[Cocktail]:
        """Obtenir tous les cocktails favoris d'un utilisateur."""
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT c.id_cocktail,                           "
                "       c.nom,                                   "
                "       c.categorie,                             "
                "       c.verre,                                 "
                "       c.alcool                                 "
                "       c.image                                  "
                "FROM cocktail c                                 "
                "INNER JOIN avis a using id_cocktail             "
                "WHERE id_utilisateur = %(id_utilisateur)s       "
                "AND a.favoris = TRUE                            ",
                {"id_utilisateur": id_utilisateur},
            )
            res = cursor.fetchall()

        liste_cocktails_favoris = []

        if res:
            liste_cocktails_favoris = [
                Cocktail(
                    id_cocktail=cocktail["id_cocktail"],
                    nom=cocktail["nom"],
                    categorie=cocktail["categorie"],
                    verre=cocktail["verre"],
                    alcool=cocktail["alcool"],
                    image=cocktail["image"],
                )
                for cocktail in res
            ]

        return liste_cocktails_favoris

    @staticmethod
    @log
    def update_cocktail_favoris(id_utilisateur, id_cocktail) -> None:
        """Ajoute un cocktail dans les favoris d'un utilisateur."""
        with DBConnection().connection as connection, connection.cursor() as cursor:
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

    @staticmethod
    @log
    def delete_cocktail_favoris(id_utilisateur, id_cocktail) -> None:
        """Supprime un cocktail des favoris d'un utilisateur."""
        with DBConnection().connection as connection, connection.cursor() as cursor:
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

    @staticmethod
    @log
    def get_teste(id_utilisateur: int) -> list[Cocktail]:
        """Obtenir tous les cocktails testés par un utilisateur."""
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT c.id_cocktail,                           "
                "       c.nom,                                   "
                "       c.categorie,                             "
                "       c.verre,                                 "
                "       c.alcool,                                "
                "       c.image                                  "
                "FROM cocktail c                                 "
                "INNER JOIN avis a ON c.id_cocktail = a.id_cocktail "
                "WHERE a.id_utilisateur = %(id_utilisateur)s     "
                "AND a.teste = TRUE                              ",
                {"id_utilisateur": id_utilisateur},
            )
            res = cursor.fetchall()

        liste_cocktails_testes = []

        if res:
            liste_cocktails_testes = [
                Cocktail(
                    id_cocktail=cocktail["id_cocktail"],
                    nom=cocktail["nom"],
                    categorie=cocktail["categorie"],
                    verre=cocktail["verre"],
                    alcool=cocktail["alcool"],
                    image=cocktail["image"],
                )
                for cocktail in res
            ]

        return liste_cocktails_testes

    @staticmethod
    @log
    def get_cocktail_id_by_name(nom_cocktail: str) -> int | None:
        """Récupère l'ID d'un cocktail par son nom."""
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT id_cocktail FROM cocktail WHERE LOWER(nom) = LOWER(%(nom)s)",
                {"nom": nom_cocktail},
            )
            result = cursor.fetchone()
            return result["id_cocktail"] if result else None

    @log
    def ajouter_cocktail_teste(self, id_utilisateur: int, nom_cocktail: str) -> dict:
        """Ajoute un cocktail aux cocktails testés par son nom.
        Crée l'avis s'il n'existe pas (avec note et commentaire NULL).
        """
        # Récupérer l'ID du cocktail par son nom
        id_cocktail = self.get_cocktail_id_by_name(nom_cocktail)

        if not id_cocktail:
            raise ValueError(f"Cocktail '{nom_cocktail}' introuvable")

        with DBConnection().connection as connection, connection.cursor() as cursor:
            # Vérifier si déjà testé
            cursor.execute(
                """
                SELECT teste
                FROM avis
                WHERE id_utilisateur = %(id_utilisateur)s
                AND id_cocktail = %(id_cocktail)s
                """,
                {
                    "id_utilisateur": id_utilisateur,
                    "id_cocktail": id_cocktail,
                },
            )
            result = cursor.fetchone()

            if result and result["teste"]:
                return {
                    "nom_cocktail": nom_cocktail,
                    "id_cocktail": id_cocktail,
                    "teste": True,
                    "deja_teste": True,
                }

            # Ajouter aux testés (ou créer l'avis si inexistant)
            cursor.execute(
                """
                INSERT INTO avis (id_utilisateur, id_cocktail, note, commentaire, teste)
                VALUES (%(id_utilisateur)s, %(id_cocktail)s, NULL, NULL, TRUE)
                ON CONFLICT (id_utilisateur, id_cocktail)
                DO UPDATE SET
                    teste = TRUE,
                    date_modification = NOW()
                RETURNING teste
                """,
                {
                    "id_utilisateur": id_utilisateur,
                    "id_cocktail": id_cocktail,
                },
            )

            return {
                "nom_cocktail": nom_cocktail,
                "id_cocktail": id_cocktail,
                "teste": True,
                "deja_teste": False,
            }

    @log
    def retirer_cocktail_teste(self, id_utilisateur: int, nom_cocktail: str) -> dict:
        """Retire un cocktail des cocktails testés par son nom."""
        # Récupérer l'ID du cocktail par son nom
        id_cocktail = self.get_cocktail_id_by_name(nom_cocktail)

        if not id_cocktail:
            raise ValueError(f"Cocktail '{nom_cocktail}' introuvable")

        with DBConnection().connection as connection, connection.cursor() as cursor:
            # Vérifier si le cocktail est testé
            cursor.execute(
                """
                SELECT teste
                FROM avis
                WHERE id_utilisateur = %(id_utilisateur)s
                AND id_cocktail = %(id_cocktail)s
                """,
                {
                    "id_utilisateur": id_utilisateur,
                    "id_cocktail": id_cocktail,
                },
            )
            result = cursor.fetchone()

            if not result or not result["teste"]:
                raise ValueError(
                    f"Le cocktail '{nom_cocktail}' n'est pas dans vos cocktails testés",
                )

            # Retirer des testés
            cursor.execute(
                """
                UPDATE avis
                SET teste = FALSE,
                    date_modification = NOW()
                WHERE id_utilisateur = %(id_utilisateur)s
                AND id_cocktail = %(id_cocktail)s
                """,
                {
                    "id_utilisateur": id_utilisateur,
                    "id_cocktail": id_cocktail,
                },
            )

            return {
                "nom_cocktail": nom_cocktail,
                "id_cocktail": id_cocktail,
                "teste": False,
            }
