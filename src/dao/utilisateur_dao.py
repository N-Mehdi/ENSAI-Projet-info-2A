"""utilisateur_dao.py
Classe DAO du business object Utilistauer.
"""

import logging

from psycopg2 import Error as DBError
from psycopg2.errors import UniqueViolation

from src.business_object.utilisateur import Utilisateur
from src.dao.db_connection import DBConnection
from src.models.utilisateurs import User, UserCreate, UserUpdatePassword
from src.utils.exceptions import DAOError, EmptyFieldError, MailAlreadyExistsError, UserAlreadyExistsError
from src.utils.log_decorator import log
from src.utils.singleton import Singleton


class UtilisateurDao(metaclass=Singleton):
    """Classe contenant les méthodes agissant sur les utilisateurs de la base de données."""

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
        # Validation des champs vides
        if not utilisateur.pseudo or not utilisateur.pseudo.strip():
            raise EmptyFieldError("pseudo")
        if not utilisateur.mail or not utilisateur.mail.strip():
            raise EmptyFieldError("mail")
        if not utilisateur.mot_de_passe_hashed or not utilisateur.mot_de_passe_hashed.strip():
            raise EmptyFieldError("mot_de_passe")
        if not utilisateur.date_naissance:
            raise EmptyFieldError("date_naissance")
        res = None
        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
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
        except UniqueViolation as e:
            # Analyser le message d'erreur pour identifier la colonne
            error_message = str(e)

            if "pseudo" in error_message.lower():
                raise UserAlreadyExistsError(utilisateur.pseudo) from None
            if "mail" in error_message.lower():
                raise MailAlreadyExistsError(utilisateur.mail) from None
            # Cas générique si on ne peut pas identifier la colonne
            raise DAOError("Contrainte d'unicité violée") from None

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
    def delete_compte(self, pseudo) -> bool:
        """Supprimer un utilisateur de la base de données.

        Parameters
        ----------
        pseudo : str
            pseudo de l'utilisateur à supprimer de la base de données

        Return
        ------
            True si l'utilisateur a bien été supprimé
            False sinon

        """
        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    """
                        DELETE FROM utilisateur
                        WHERE pseudo=%(pseudo)s
                        """,
                    {"pseudo": pseudo},
                )
                res = cursor.rowcount
        except Exception as e:
            logging.info("Erreur lors de la suppression du compte : %s", e)
            raise DAOError("Impossible de supprimer le compte") from e
        return res > 0

    def read(self, id_utilisateur: int) -> User | None:
        """Read a user by their ID.

        :param user_id: ID of the user to read
        :raises DAOError: Raised if DB error occurs
        :return: The User object or None if not found
        """
        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    """
                        SELECT id_utilisateur, pseudo, mail, mot_de_passe, date_naissance
                        FROM utilisateur
                        WHERE id_utilisateur = %(id_utilisateur)s
                        """,
                    {"id_utilisateur": id_utilisateur},
                )
                row = cursor.fetchone()
            if row:
                return User(
                    id_utilisateur=row["id_utilisateur"],
                    pseudo=row["pseudo"],
                    mail=row["mail"],
                    date_naissance=row["date_naissance"].isoformat(),
                    mot_de_passe_hashed=row["mot_de_passe"],
                )
            return None
        except DBError as exc:
            raise DAOError from exc

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
                date_naissance=res["date_naissance"].isoformat() if res["date_naissance"] else None,
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
    def update_mot_de_passe(self, mdps: UserUpdatePassword) -> bool:
        """Met à jour le mot de passe d'un utilisateur par son pseudo.

        Parameters
        ----------
        mdps : UserUpdatePassword
            Contient le pseudo et le nouveau mot de passe haché

        Returns
        -------
        bool
            True si le mot de passe a été mis à jour, False sinon

        Raises
        ------
        DAOError
            En cas d'erreur de base de données

        """
        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE utilisateur
                    SET mot_de_passe = %(mot_de_passe_nouveau_hashed)s
                    WHERE pseudo = %(pseudo)s
                    """,
                    {
                        "mot_de_passe_nouveau_hashed": mdps.mot_de_passe_nouveau_hashed,
                        "pseudo": mdps.pseudo,
                    },
                )
                return cursor.rowcount > 0
        except Exception as e:
            logging.exception("Erreur lors de la mise à jour du mot de passe : %s", e)
            raise DAOError("Impossible de mettre à jour le mot de passe") from e

    @log
    def update_pseudo(self, ancien_pseudo: str, nouveau_pseudo: str) -> bool:
        """Met à jour le pseudo d'un utilisateur.

        Parameters
        ----------
        ancien_pseudo : str
            Pseudo actuel de l'utilisateur
        nouveau_pseudo : str
            Nouveau pseudo souhaité

        Returns
        -------
        bool
            True si le pseudo a été mis à jour, False sinon

        Raises
        ------
        UserAlreadyExistsError
            Si le nouveau pseudo existe déjà
        DAOError
            En cas d'erreur de base de données

        """
        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE utilisateur
                    SET pseudo = %(nouveau_pseudo)s
                    WHERE pseudo = %(ancien_pseudo)s
                    """,
                    {
                        "nouveau_pseudo": nouveau_pseudo,
                        "ancien_pseudo": ancien_pseudo,
                    },
                )
                return cursor.rowcount > 0
        except UniqueViolation:
            raise UserAlreadyExistsError(nouveau_pseudo) from None
        except Exception as e:
            logging.exception("Erreur lors de la mise à jour du pseudo : %s", e)
            raise DAOError("Impossible de mettre à jour le pseudo") from e

    @log
    def get_date_inscription(self, pseudo: str) -> str | None:
        """Récupère la date d'inscription d'un utilisateur par son pseudo.

        Parameters
        ----------
        pseudo : str
            Pseudo de l'utilisateur

        Returns
        -------
        str | None
            Date d'inscription au format ISO (YYYY-MM-DD) ou None si l'utilisateur n'existe pas

        Raises
        ------
        DAOError
            En cas d'erreur de base de données

        """
        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT date_inscription
                    FROM utilisateur
                    WHERE pseudo = %(pseudo)s
                    """,
                    {"pseudo": pseudo},
                )
                res = cursor.fetchone()

                if res and res["date_inscription"]:
                    # Extraire uniquement la partie date (sans l'heure)
                    date_obj = res["date_inscription"]
                    if hasattr(date_obj, "date"):  # Si c'est un datetime
                        return date_obj.date().isoformat()
                    return date_obj.isoformat()  # Si c'est déjà une date
                return None
        except Exception as e:
            logging.exception("Erreur lors de la récupération de la date d'inscription : %s", e)
            raise DAOError("Impossible de récupérer la date d'inscription") from e
