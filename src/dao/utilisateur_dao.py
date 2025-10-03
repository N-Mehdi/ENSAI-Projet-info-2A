"""utilisateur_dao.py
Classe DAO du business object Utilistauer.
"""

import logging

from business_object.utilisateur import Utilisateur
from dao.db_connection import DBConnection
from utils.log_decorator import log
from utils.singleton import Singleton


class UtilisateurDao(metaclass=Singleton):
    """Classe contenant les méthodes agissant sur les utilisateurs de la base
    de données.
    """

    @log
    def create_compte(self, utilisateur) -> bool:
        """Création d'un compte utilisateur.

        Parameters
        ----------
        utilisateur : Utilisateur

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
                    INSERT INTO utilisateur(pseudo, mail, mdp, date_naissance)
                    VALUES (%(pseudo)s, %(mail)s, %(mdp)s, %(date_naissance)s)
                    RETURNING id_utilisateur;
                    """,
                        {
                            "pseudo": utilisateur.pseudo,
                            "mail": utilisateur.mail,
                            "mdp": utilisateur.mdp,
                            "date_naissance": utilisateur.date_naissance,
                        },
                    )
                res = cursor.fetchone()
        except Exception as e:
            logging.info(e)
        created = False
        if res:
            utilisateur.id_utilisateur = res["id_utilisateur"]
            created = True

        return created

    @log
    def se_connecter(self, pseudo, mdp) -> Utilisateur:
        """Se connecter grâce à son pseudo et son mot de passe.

        Parameters
        ----------
        pseudo : str
            pseudo de l'utilisateur
        mdp : str
            mot de passe de l'utilisateur

        Returns
        -------
        utilisateur : Utilisateur
            renvoie l'utilisateur

        """
        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT *
                        FROM utilisateur
                        WHERE pseudo = %(pseudo)s
                        AND mdp = %(mdp)s;
                        """,
                        {"pseudo": pseudo, "mdp": mdp},
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
                mdp=res["mdp"],
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
            with DBConnection().connection as connection:
                with connection.cursor as cursor:
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
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
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
                mdp=res["mdp"],
                id_utilisateur=res["id_utilisateur"],
            )
        return utilisateur
