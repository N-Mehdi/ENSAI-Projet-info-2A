"""utilisateur_dao.py
Classe DAO du business object Utilistauer.
"""

import logging

from src.business_object.utilisateur import Utilisateur
from src.dao.db_connection import DBConnection
from src.models.utilisateurs import User, UserCreate
from src.utils.exceptions import DAOError
from src.utils.log_decorator import log
from src.utils.singleton import Singleton


class UtilisateurDao(metaclass=Singleton):
    """Classe contenant les méthodes agissant sur les utilisateurs de la base
    de données.
    """

    @log
    def create_compte(self, utilisateur: UserCreate) -> bool:
        """Création d'un compte utilisateur.

        Parameters
        ----------
        utilisateur : UserCreate

        Returns
        -------
        created : bool
            True si la création est un succès
            False sinon

        """
        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                    INSERT INTO utilisateur(pseudo, mail, date_naissance, mot_de_passe)
                    VALUES (%(pseudo)s, %(mail)s, %(date_naissance)s, %(mot_de_passe_hashed)s)
                    RETURNING *
                    """,
                        {
                            "pseudo": utilisateur.pseudo,
                            "mail": utilisateur.mail,
                            "date_naissance": utilisateur.date_naissance,
                            "mot_de_passe_hashed": utilisateur.mot_de_passe_hashed,
                        },
                    )
                    res = cursor.fetchone()
                connection.commit()
        except Exception as e:
            logging.info(e)
            raise DAOError("Impossible de créer le compte") from e
        created = False
        if res:
            created = True

        return created

    @log
    def se_connecter(self, pseudo, mot_de_passe) -> Utilisateur:
        """Se connecter grâce à son pseudo et son mot de passe.

        Parameters
        ----------
        pseudo : str
            pseudo de l'utilisateur
        mot_de_passe : str
            mot de passe de l'utilisateur

        Returns
        -------
        utilisateur : Utilisateur
            renvoie l'utilisateur

        """
        res = None
        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    """
                        SELECT *
                        FROM utilisateur
                        WHERE pseudo = %(pseudo)s
                        AND mot_de_passe = %(mot_de_passe)s;
                        """,
                    {"pseudo": pseudo, "mot_de_passe": mot_de_passe},
                )
                res = cursor.fetchone()
        except Exception as e:
            logging.info(e)

        utilisateur = None

        if res:
            utilisateur = Utilisateur(
                pseudo=res["pseudo"],
                mail=res["mail"],
                date_naissance=res["date_naissance"],
                mot_de_passe=res["mot_de_passe"],
                id_utilisateur=res["id_utilisateur"],
            )
        return utilisateur

    @log
    def delete_compte(self, utilisateur) -> bool:
        """Supprimer un utilisateur de la base de données.

        Parameters
        ----------
        utilisateur : Utilisateur
            utilisateur à supprimer de la base de données

        Return
        ------
            True si l'utilisateur a bien été supprimé
            False sinon

        """
        try:
            with DBConnection().connection as connection, connection.cursor as cursor:
                cursor.execute(
                    """
                        DELETE FROM utilisateur
                        WHERE id_utilisateur=%(id_utilisateur)s
                        """,
                    {"id_utilisateur": utilisateur.id_utilisateur},
                )
                res = cursor.rowcount
        except Exception as e:
            logging.info(e)
            raise
        return res > 0

    @log
    def trouver_par_id(self, id_utilisateur) -> Utilisateur:
        """Trouver un utilisateur grâce à son identifiant.

        Parameters
        ----------
        id_utilisateur : int
            identifiant de l'utilisateur à trouver

        Returns
        -------
        utilisateur : Utilisateur
            renvoie l'utilisateur cherché par id

        """
        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    """
                    "SELECT *
                    FROM utilisateur
                    WHERE id_utilisateur = %(id_utilisateur)s;
                    """,
                    {"id_utilisateur": id_utilisateur},
                )
                res = cursor.fetchone()
        except Exception as e:
            logging.info(e)
            raise

        utilisateur = None
        if res:
            utilisateur = Utilisateur(
                pseudo=res["pseudo"],
                mail=res["mail"],
                date_naissace=res["date_naissance"],
                mot_de_passe=res["mot_de_passe"],
                id_utilisateur=res["id_utilisateur"],
            )
        return utilisateur

    def recuperer_mot_de_passe_hashe_par_mail(self, mail: str) -> dict | None:
        """Récupérer le mot de passe hashé et le pseudo d'un utilisateur par son email.

        Parameters
        ----------
            mail: L'email de l'utilisateur.

        Returns
        -------
            dict avec {mail : mot_de_passe} si trouvé, None sinon.

        """
        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    "SELECT mot_de_passe FROM utilisateur WHERE mail = %(mail)s",
                    {"mail": mail},
                )
                res = cursor.fetchone()
        except Exception as e:
            logging.info(e)
            raise
        return res


def recuperer_par_pseudo(self, pseudo: str) -> User | None:
    """Récupérer le mot de passe hashé et le pseudo d'un utilisateur par son email.

    Parameters
    ----------
        mail: L'email de l'utilisateur.

    Returns
    -------
        dict avec {mail : mot_de_passe} si trouvé, None sinon.

    """
    try:
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM utilisateur WHERE pseudo = %(pseudo)s",
                {"pseudo": pseudo},
            )
            res = cursor.fetchone()
    except Exception as e:
        logging.info(e)
        raise

    utilisateur = None
    if res:
        utilisateur = User(
            id_utilisateur=res["id_utilisateur"],
            pseudo=res["pseudo"],
            mail=res["mail"],
            date_naissance=res["date_naissance"],
            mot_de_passe_hashed=res["mot_de_passe"],
        )
    return utilisateur


def pseudo_existe(self, pseudo: str) -> bool:
    """Vérifie si un pseudo existe déjà en base de données.

    Args:
        pseudo: Le pseudo à vérifier

    Returns:
        bool: True si le pseudo existe, False sinon

    """
    try:
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT EXISTS(SELECT 1 FROM utilisateur WHERE pseudo = %(pseudo)s)",
                    {"pseudo": pseudo},
                )
                result = cursor.fetchone()
            if result:
                return result["exists"]
            return False
    except Exception as e:
        raise DAOError from e


def mail_existe(self, mail: str) -> bool:
    """Vérifie si un email existe déjà en base de données.

    Args:
        mail: L'email à vérifier

    Returns:
        bool: True si l'email existe, False sinon

    """
    try:
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT EXISTS(SELECT 1 FROM utilisateur WHERE mail = %(mail)s)",
                    {"mail": mail},
                )
                result = cursor.fetchone()
            if result:
                return result["exists"]
            return False
    except Exception as e:
        logging.exception("Erreur lors de la vérification de l'email")
        raise DAOError("Erreur lors de la vérification de l'email") from e


@log
def update_mot_de_passe(self, utilisateur_id: int, nouveau_mot_de_passe_hashed: str) -> bool:
    """Met à jour le mot de passe d'un utilisateur.

    Parameters
    ----------
    utilisateur_id : int
        L'identifiant de l'utilisateur
    nouveau_mot_de_passe_hashed : str
        Le nouveau mot de passe déjà hashé

    Returns
    -------
    bool
        True si le mot de passe a été mis à jour, False sinon.

    """
    try:
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE utilisateur
                SET mot_de_passe = %(mot_de_passe)s
                WHERE id_utilisateur = %(id_utilisateur)s
                """,
                {"mot_de_passe": nouveau_mot_de_passe_hashed, "id_utilisateur": utilisateur_id},
            )
            connection.commit()
            return cursor.rowcount > 0
    except Exception as e:
        raise DAOError("Impossible de mettre à jour le mot de passe") from e


@log
def update_pseudo(self, utilisateur_id: int, nouveau_pseudo: str) -> bool:
    """Met à jour le pseudo d'un utilisateur.

    Parameters
    ----------
    utilisateur_id : int
        L'identifiant de l'utilisateur
    nouveau_pseudo : str
        Le nouveau pseudo

    Returns
    -------
    bool
        True si le pseudo a été mis à jour, False sinon.

    """
    try:
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE utilisateur
                SET pseudo = %(pseudo)s
                WHERE id_utilisateur = %(id_utilisateur)s
                """,
                {"pseudo": nouveau_pseudo, "id_utilisateur": utilisateur_id},
            )
            connection.commit()
            return cursor.rowcount > 0
    except Exception as e:
        raise DAOError("Impossible de mettre à jour le pseudo") from e
