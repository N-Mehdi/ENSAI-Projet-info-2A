"""Ce module définit la classe CocktailUtilisateurDAO, responsable des opérations CRUD
sur la table prive dans la base de données.
"""

from src.business_object.cocktail import Cocktail
from src.dao.db_connection import DBConnection
from src.utils.exceptions import (
    CocktailNotFoundError,
    CocktailNotTestedError,
    PermissionDeniedError,
)
from src.utils.log_decorator import log
from src.utils.singleton import Singleton


class CocktailUtilisateurDAO(metaclass=Singleton):
    """Classe contenant les méthodes agissant sur les cocktails et utilisateurs de
    la base de données.
    """

    @staticmethod
    @log
    def get_prive(id_utilisateur) -> list[Cocktail]:
        """Récupère tous les cocktails privés d'un utilisateur.

        Parameters
        ----------
        id_utilisateur : int
            L'identifiant de l'utilisateur

        Returns
        -------
        list[Cocktail]
            Liste des cocktails dont l'utilisateur est propriétaire

        Raises
        ------
        DAOError
            En cas d'erreur de base de données

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT c.id_cocktail,                           "
                "       c.nom,                                   "
                "       c.categorie,                             "
                "       c.verre,                                 "
                "       c.alcool,                                "
                "       c.image                                  "
                "FROM cocktail c                                 "
                "INNER JOIN acces a using (id_cocktail)            "
                "WHERE a.id_utilisateur = %(id_utilisateur)s       "
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
        """Ajoute un nouveau cocktail privé pour un utilisateur.

        Crée le cocktail dans la base de données et établit la relation
        de propriété dans la table acces.

        Parameters
        ----------
        id_utilisateur : int
            L'identifiant de l'utilisateur propriétaire
        cocktail : Cocktail
            L'objet Cocktail contenant les informations du cocktail à créer

        Returns
        -------
        int
            L'identifiant du cocktail créé

        Raises
        ------
        DAOError
            En cas d'erreur de base de données

        """
        sql_insert_cocktail = """
        INSERT INTO cocktail (nom, categorie, verre, alcool, image)
        VALUES (%(nom)s, %(categorie)s, %(verre)s, %(alcool)s, %(image)s)
        RETURNING id_cocktail;
        """

        sql_insert_acces = """
        INSERT INTO acces (id_cocktail, id_utilisateur, is_owner, has_access)
        VALUES (%(id_cocktail)s, %(id_utilisateur)s, TRUE, TRUE);
        """

        cocktail_params = {
            "nom": cocktail.nom,
            "categorie": cocktail.categorie,
            "verre": cocktail.verre,
            "alcool": cocktail.alcool,
            "image": cocktail.image,
        }

        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(sql_insert_cocktail, cocktail_params)
            res = cursor.fetchone()
            new_cocktail_id = res["id_cocktail"]
            acces_params = {
                "id_cocktail": new_cocktail_id,
                "id_utilisateur": id_utilisateur,
            }
            cursor.execute(sql_insert_acces, acces_params)
        return new_cocktail_id

    @staticmethod
    @log
    def get_cocktail_ingredient(id_cocktail) -> dict:
        """Récupère tous les ingrédients d'un cocktail donné.

        Parameters
        ----------
        id_cocktail : int
            L'identifiant du cocktail

        Returns
        -------
        dict
            Dictionnaire avec les id_ingredient comme clés et les quantités comme
            valeurs

        Raises
        ------
        DAOError
            En cas d'erreur de base de données

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT id_ingredient, qte FROM cocktail_ingredient WHERE "
                "id_cocktail = %(id_cocktail)s",
                {"id_cocktail": id_cocktail},
            )
            return {row["id_ingredient"]: row["qte"] for row in cursor.fetchall()}

    @staticmethod
    @log
    def update_cocktail_prive_modif_ingredient(
        id_utilisateur,
        id_cocktail,
        id_ingredient,
        quantite,
    ) -> None:
        """Change la quantité d'un ingrédient dans un cocktail privé.

        Parameters
        ----------
        id_utilisateur : int
            L'identifiant de l'utilisateur
        id_cocktail : int
            L'identifiant du cocktail
        id_ingredient : int
            L'identifiant de l'ingrédient à modifier
        quantite : float
            La nouvelle quantité de l'ingrédient

        Raises
        ------
        PermissionDeniedError
            Si l'utilisateur n'est pas le propriétaire du cocktail
        DAOError
            En cas d'erreur de base de données

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
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

            if cursor.fetchone():
                cursor.execute(
                    "UPDATE cocktail_ingredient "
                    "SET qte = %(quantite)s "
                    "WHERE id_ingredient = %(id_ingredient)s "
                    "AND id_cocktail = %(id_cocktail)s",
                    {
                        "quantite": quantite,
                        "id_ingredient": id_ingredient,
                        "id_cocktail": id_cocktail,
                    },
                )
            else:
                raise PermissionDeniedError

    @staticmethod
    @log
    def update_cocktail_prive_ajout_ingredient(
        id_utilisateur,
        id_cocktail,
        id_ingredient,
        quantite,
    ) -> None:
        """Ajoute un ingrédient à un cocktail privé.

        Parameters
        ----------
        id_utilisateur : int
            L'identifiant de l'utilisateur
        id_cocktail : int
            L'identifiant du cocktail
        id_ingredient : int
            L'identifiant de l'ingrédient à ajouter
        quantite : float
            La quantité de l'ingrédient

        Raises
        ------
        PermissionDeniedError
            Si l'utilisateur n'est pas le propriétaire du cocktail
        DAOError
            En cas d'erreur de base de données

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
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

            if cursor.fetchone():
                cursor.execute(
                    "INSERT INTO cocktail_ingredient (id_cocktail,  "
                    "                                 id_ingredient,"
                    "                                  qte)    "
                    "VALUES (%(id_cocktail)s, %(id_ingredient)s,    "
                    "                                %(quantite)s)  ",
                    {
                        "id_cocktail": id_cocktail,
                        "id_ingredient": id_ingredient,
                        "quantite": quantite,
                    },
                )
            else:
                raise PermissionDeniedError

    @staticmethod
    @log
    def update_cocktail_prive_supprimer_ingredient(
        id_utilisateur,
        id_cocktail,
        id_ingredient,
    ) -> None:
        """Supprime un ingrédient d'un cocktail privé.

        Parameters
        ----------
        id_utilisateur : int
            L'identifiant de l'utilisateur
        id_cocktail : int
            L'identifiant du cocktail
        id_ingredient : int
            L'identifiant de l'ingrédient à supprimer

        Raises
        ------
        PermissionDeniedError
            Si l'utilisateur n'est pas le propriétaire du cocktail
        DAOError
            En cas d'erreur de base de données

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
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
                raise PermissionDeniedError

    @staticmethod
    @log
    def delete_cocktail_prive(id_utilisateur, id_cocktail) -> None:
        """Supprime un cocktail privé d'un utilisateur.

        Supprime la relation d'accès et le cocktail de la base de données.

        Parameters
        ----------
        id_utilisateur : int
            L'identifiant de l'utilisateur propriétaire
        id_cocktail : int
            L'identifiant du cocktail à supprimer

        Raises
        ------
        DAOError
            En cas d'erreur de base de données

        """
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
        """Récupère tous les cocktails favoris d'un utilisateur.

        Parameters
        ----------
        id_utilisateur : int
            L'identifiant de l'utilisateur

        Returns
        -------
        list[Cocktail]
            Liste des cocktails marqués comme favoris par l'utilisateur

        Raises
        ------
        DAOError
            En cas d'erreur de base de données

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT c.id_cocktail,                           "
                "       c.nom,                                   "
                "       c.categorie,                             "
                "       c.verre,                                 "
                "       c.alcool,                                "
                "       c.image                                  "
                "FROM cocktail c                                 "
                "INNER JOIN avis a using (id_cocktail)           "
                "WHERE a.id_utilisateur = %(id_utilisateur)s       "
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
        """Ajoute un cocktail dans les favoris d'un utilisateur.

        Parameters
        ----------
        id_utilisateur : int
            L'identifiant de l'utilisateur
        id_cocktail : int
            L'identifiant du cocktail à ajouter aux favoris

        Raises
        ------
        DAOError
            En cas d'erreur de base de données

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                "UPDATE avis                                "
                "SET favoris = TRUE                         "
                "WHERE id_utilisateur = %(id_utilisateur)s  "
                "AND id_cocktail = %(id_cocktail)s           ",
                {
                    "id_cocktail": id_cocktail,
                    "id_utilisateur": id_utilisateur,
                },
            )

    @staticmethod
    @log
    def delete_cocktail_favoris(id_utilisateur, id_cocktail) -> None:
        """Retire un cocktail des favoris d'un utilisateur.

        Parameters
        ----------
        id_utilisateur : int
            L'identifiant de l'utilisateur
        id_cocktail : int
            L'identifiant du cocktail à retirer des favoris

        Raises
        ------
        DAOError
            En cas d'erreur de base de données

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                "UPDATE avis                                "
                "SET favoris = FALSE                        "
                "WHERE id_utilisateur = %(id_utilisateur)s  "
                "AND id_cocktail = %(id_cocktail)s           ",
                {
                    "id_cocktail": id_cocktail,
                    "id_utilisateur": id_utilisateur,
                },
            )

    @staticmethod
    @log
    def get_teste(id_utilisateur: int) -> list[Cocktail]:
        """Récupère tous les cocktails testés par un utilisateur.

        Parameters
        ----------
        id_utilisateur : int
            L'identifiant de l'utilisateur

        Returns
        -------
        list[Cocktail]
            Liste des cocktails marqués comme testés par l'utilisateur

        Raises
        ------
        DAOError
            En cas d'erreur de base de données

        """
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
        """Récupère l'identifiant d'un cocktail par son nom.

        La recherche est insensible à la casse.

        Parameters
        ----------
        nom_cocktail : str
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
                "SELECT id_cocktail FROM cocktail WHERE LOWER(nom) = LOWER(%(nom)s)",
                {"nom": nom_cocktail},
            )
            result = cursor.fetchone()
            return result["id_cocktail"] if result else None

    @log
    def ajouter_cocktail_teste(self, id_utilisateur: int, nom_cocktail: str) -> dict:
        """Ajoute un cocktail aux cocktails testés par un utilisateur.

        Crée un avis avec teste=TRUE si l'avis n'existe pas encore.
        Si l'avis existe déjà, met à jour le champ teste.

        Parameters
        ----------
        id_utilisateur : int
            L'identifiant de l'utilisateur
        nom_cocktail : str
            Le nom du cocktail à marquer comme testé

        Returns
        -------
        dict
            Dictionnaire contenant :
            - nom_cocktail : str
            - id_cocktail : int
            - teste : bool (True)
            - deja_teste : bool (True si déjà testé avant, False sinon)

        Raises
        ------
        CocktailNotFoundError
            Si le cocktail n'existe pas
        DAOError
            En cas d'erreur de base de données

        """
        id_cocktail = self.get_cocktail_id_by_name(nom_cocktail)

        if not id_cocktail:
            raise CocktailNotFoundError(nom_cocktail)

        with DBConnection().connection as connection, connection.cursor() as cursor:
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
        """Retire un cocktail des cocktails testés par un utilisateur.

        Parameters
        ----------
        id_utilisateur : int
            L'identifiant de l'utilisateur
        nom_cocktail : str
            Le nom du cocktail à retirer des testés

        Returns
        -------
        dict
            Dictionnaire contenant :
            - nom_cocktail : str
            - id_cocktail : int
            - teste : bool (False)

        Raises
        ------
        CocktailNotFoundError
            Si le cocktail n'existe pas
        CocktailNotTestedError
            Si le cocktail n'était pas marqué comme testé
        DAOError
            En cas d'erreur de base de données

        """
        id_cocktail = self.get_cocktail_id_by_name(nom_cocktail)

        if not id_cocktail:
            raise CocktailNotFoundError(nom_cocktail)

        with DBConnection().connection as connection, connection.cursor() as cursor:
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
                raise CocktailNotTestedError(nom_cocktail=nom_cocktail)

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
