"""Classe DAO du business object Utilisateur."""

from psycopg2 import Error as DBError
from psycopg2.errors import UniqueViolation

from src.business_object.utilisateur import Utilisateur
from src.dao.db_connection import DBConnection
from src.models.utilisateurs import User, UserCreate, UserUpdatePassword
from src.utils.exceptions import (
    AccountDeletionError,
    DAOError,
    EmptyFieldError,
    MailAlreadyExistsError,
    PseudoChangingError,
    UserAlreadyExistsError,
)
from src.utils.log_decorator import log
from src.utils.singleton import Singleton


class UtilisateurDAO(metaclass=Singleton):
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
            raise EmptyFieldError(field="pseudo")
        if not utilisateur.mail or not utilisateur.mail.strip():
            raise EmptyFieldError(field="mail")
        if not utilisateur.mot_de_passe_hashed or not utilisateur.mot_de_passe_hashed.strip():
            raise EmptyFieldError(field="mot_de_passe")
        if not utilisateur.date_naissance:
            raise EmptyFieldError(field="date_naissance")
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
            # Analyser le message d'erreur pour identifier "pseudo" ou "mail"
            error_message = str(e)

            if "pseudo" in error_message.lower():
                raise UserAlreadyExistsError(utilisateur.pseudo) from None
            if "mail" in error_message.lower():
                raise MailAlreadyExistsError(utilisateur.mail) from None
            # Cas générique si on ne peut pas identifier
            raise DAOError from None

        except Exception as e:
            raise DAOError from e

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
            raise DAOError from e

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
            raise AccountDeletionError from e
        return res > 0

    def read(self, id_utilisateur: int) -> User | None:
        """Récupère un utilisateur par son identifiant.

        Parameters
        ----------
        id_utilisateur : int
            L'identifiant de l'utilisateur à récupérer

        Returns
        -------
        User | None
            L'objet User si trouvé, None sinon

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
                        id_utilisateur,
                        pseudo,
                        mail,
                        mot_de_passe,
                        date_naissance,
                        date_inscription
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
                    date_inscription=row["date_inscription"].isoformat() if row["date_inscription"] else None,  # ✅ AJOUTÉ
                )
        except DBError as exc:
            raise DAOError from exc
        return None

    def recuperer_par_pseudo(self, pseudo: str) -> User | None:
        """Récupère un utilisateur par son pseudo.

        Parameters
        ----------
        pseudo : str
            Le pseudo de l'utilisateur à récupérer

        Returns
        -------
        User | None
            L'objet User si trouvé, None sinon

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
                        id_utilisateur,
                        pseudo,
                        mail,
                        date_naissance,
                        mot_de_passe,
                        date_inscription
                    FROM utilisateur
                    WHERE pseudo = %(pseudo)s
                    """,
                    {"pseudo": pseudo},
                )
                res = cursor.fetchone()
        except Exception as e:
            raise DAOError from e

        utilisateur = None
        if res:
            utilisateur = User(
                id_utilisateur=res["id_utilisateur"],
                pseudo=res["pseudo"],
                mail=res["mail"],
                date_naissance=res["date_naissance"].isoformat() if res["date_naissance"] else None,
                mot_de_passe_hashed=res["mot_de_passe"],
                date_inscription=res["date_inscription"].isoformat() if res["date_inscription"] else None,  # ✅ AJOUTÉ
            )
        return utilisateur

    def pseudo_existe(self, pseudo: str) -> bool:
        """Vérifie si un pseudo existe déjà en base de données.

        Parameters
        ----------
        pseudo : str
            Le pseudo à vérifier

        Returns
        -------
        bool
            True si le pseudo existe, False sinon

        Raises
        ------
        DAOError
            En cas d'erreur de base de données

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

        Parameters
        ----------
        mail : str
            L'email à vérifier

        Returns
        -------
        bool
            True si l'email existe, False sinon

        Raises
        ------
        DAOError
            En cas d'erreur de base de données

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
            raise DAOError from e

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
            raise DAOError from e

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
        except DBError as e:
            raise PseudoChangingError from e

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
            raise DAOError from e
