"""Tests d'intégration pour UtilisateurDAO."""

from datetime import datetime

import pytest

from src.business_object.utilisateur import Utilisateur
from src.dao.utilisateur_dao import UtilisateurDAO
from src.models.utilisateurs import User, UserCreate, UserUpdatePassword
from src.utils.exceptions import (
    UserAlreadyExistsError,
)


class TestUtilisateurDAOIntegration:
    """Tests d'intégration pour UtilisateurDAO."""

    # ========== Tests pour create_compte ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_create_compte_success() -> None:
        """Teste la création d'un compte utilisateur avec succès."""
        # GIVEN
        dao = UtilisateurDAO()
        utilisateur = UserCreate(
            pseudo="alice",
            mail="alice@example.com",
            mot_de_passe_hashed="hashed_password_123",
            date_naissance="2000-01-15",
        )

        # WHEN
        result = dao.create_compte(utilisateur)

        # THEN
        if result is not True:
            raise AssertionError(
                message=f"La création devrait réussir, obtenu: {result}",
            )

        # Vérifier que l'utilisateur existe en base
        user = dao.recuperer_par_pseudo("alice")
        if user is None:
            raise AssertionError(
                message="L'utilisateur devrait être trouvé en base",
            )
        if user.pseudo != "alice":
            raise AssertionError(
                message=f"Pseudo devrait être 'alice', obtenu: {user.pseudo}",
            )
        if user.mail != "alice@example.com":
            raise AssertionError(
                message=f"Mail devrait être 'alice@example.com', obtenu: {user.mail}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_se_connecter_success(db_connection) -> None:
        """Teste la connexion avec des identifiants valides."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('charlie', 'charlie@example.com', 'correct_password',
                '1995-05-20')
            """)
            db_connection.commit()

        dao = UtilisateurDAO()

        # WHEN
        utilisateur = dao.se_connecter("charlie", "correct_password")

        # THEN
        if utilisateur is None:
            raise AssertionError(
                message="L'utilisateur devrait être trouvé",
            )
        if not isinstance(utilisateur, Utilisateur):
            raise TypeError(
                message=f"Le résultat devrait être un Utilisateur, obtenu:"
                f"{type(utilisateur)}",
            )
        if utilisateur.pseudo != "charlie":
            raise AssertionError(
                message=f"Pseudo devrait être 'charlie', obtenu: {utilisateur.pseudo}",
            )
        if utilisateur.mail != "charlie@example.com":
            raise AssertionError(
                message=f"Mail devrait être 'charlie@example.com', obtenu:"
                f"{utilisateur.mail}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_se_connecter_mauvais_mot_de_passe(
        db_connection,
    ) -> None:
        """Teste la connexion avec un mauvais mot de passe."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('dave', 'dave@example.com', 'correct_password', '1990-03-10')
            """)
            db_connection.commit()

        dao = UtilisateurDAO()

        # WHEN
        utilisateur = dao.se_connecter("dave", "wrong_password")

        # THEN
        if utilisateur is not None:
            raise AssertionError(
                message=f"L'utilisateur ne devrait pas être trouvé, obtenu:"
                f"{utilisateur}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_se_connecter_utilisateur_inexistant() -> None:
        """Teste la connexion avec un utilisateur inexistant."""
        # GIVEN
        dao = UtilisateurDAO()

        # WHEN
        utilisateur = dao.se_connecter("inexistant", "password")

        # THEN
        if utilisateur is not None:
            raise AssertionError(
                message=f"L'utilisateur ne devrait pas être trouvé, obtenu:"
                f"{utilisateur}",
            )

    # ========== Tests pour recuperer_par_pseudo ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_recuperer_par_pseudo_existant(db_connection) -> None:
        """Teste la récupération d'un utilisateur existant par pseudo."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('eve', 'eve@example.com', 'hashed_pass', '1988-07-25')
            """)
            db_connection.commit()

        dao = UtilisateurDAO()

        # WHEN
        user = dao.recuperer_par_pseudo("eve")

        # THEN
        if user is None:
            raise AssertionError(
                message="L'utilisateur devrait être trouvé",
            )
        if not isinstance(user, User):
            raise TypeError(
                message=f"Le résultat devrait être un User, obtenu: {type(user)}",
            )
        if user.pseudo != "eve":
            raise AssertionError(
                message=f"Pseudo devrait être 'eve', obtenu: {user.pseudo}",
            )
        if user.mail != "eve@example.com":
            raise AssertionError(
                message=f"Mail devrait être 'eve@example.com', obtenu: {user.mail}",
            )
        if user.date_inscription is None:
            raise AssertionError(
                message="La date d'inscription ne devrait pas être None",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_recuperer_par_pseudo_inexistant() -> None:
        """Teste la récupération d'un utilisateur inexistant."""
        # GIVEN
        dao = UtilisateurDAO()

        # WHEN
        user = dao.recuperer_par_pseudo("utilisateur_inexistant")

        # THEN
        if user is not None:
            raise AssertionError(
                message=f"Le résultat devrait être None, obtenu: {user}",
            )

    # ========== Tests pour read (par ID) ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_read_utilisateur_existant(db_connection) -> None:
        """Teste la récupération d'un utilisateur par son ID."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('frank', 'frank@example.com', 'hashed_pass', '1992-11-05')
                RETURNING id_utilisateur
            """)
            user_id = cursor.fetchone()["id_utilisateur"]
            db_connection.commit()

        dao = UtilisateurDAO()

        # WHEN
        user = dao.read(user_id)

        # THEN
        if user is None:
            raise AssertionError(
                message="L'utilisateur devrait être trouvé",
            )
        if user.id_utilisateur != user_id:
            raise AssertionError(
                message=f"ID devrait être {user_id}, obtenu: {user.id_utilisateur}",
            )
        if user.pseudo != "frank":
            raise AssertionError(
                message=f"Pseudo devrait être 'frank', obtenu: {user.pseudo}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_read_utilisateur_inexistant() -> None:
        """Teste la récupération d'un utilisateur inexistant par ID."""
        # GIVEN
        dao = UtilisateurDAO()

        # WHEN
        user = dao.read(99999)

        # THEN
        if user is not None:
            raise AssertionError(
                message=f"Le résultat devrait être None, obtenu: {user}",
            )

    # ========== Tests pour pseudo_existe ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_pseudo_existe_true(db_connection) -> None:
        """Teste la vérification d'existence d'un pseudo existant."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('grace', 'grace@example.com', 'hashed_pass', '1985-02-14')
            """)
            db_connection.commit()

        dao = UtilisateurDAO()

        # WHEN
        existe = dao.pseudo_existe("grace")

        # THEN
        if existe is not True:
            raise AssertionError(
                message=f"Le pseudo devrait exister, obtenu: {existe}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_pseudo_existe_false() -> None:
        """Teste la vérification d'existence d'un pseudo inexistant."""
        # GIVEN
        dao = UtilisateurDAO()

        # WHEN
        existe = dao.pseudo_existe("pseudo_inexistant")

        # THEN
        if existe is not False:
            raise AssertionError(
                message=f"Le pseudo ne devrait pas exister, obtenu: {existe}",
            )

    # ========== Tests pour mail_existe ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_mail_existe_true(db_connection) -> None:
        """Teste la vérification d'existence d'un mail existant."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('henry', 'henry@example.com', 'hashed_pass', '1987-09-30')
            """)
            db_connection.commit()

        dao = UtilisateurDAO()

        # WHEN
        existe = dao.mail_existe("henry@example.com")

        # THEN
        if existe is not True:
            raise AssertionError(
                message=f"Le mail devrait exister, obtenu: {existe}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_mail_existe_false() -> None:
        """Teste la vérification d'existence d'un mail inexistant."""
        # GIVEN
        dao = UtilisateurDAO()

        # WHEN
        existe = dao.mail_existe("inexistant@example.com")

        # THEN
        if existe is not False:
            raise AssertionError(
                message=f"Le mail ne devrait pas exister, obtenu: {existe}",
            )

    # ========== Tests pour delete_compte ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_delete_compte_success(db_connection) -> None:
        """Teste la suppression d'un compte existant."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('iris', 'iris@example.com', 'hashed_pass', '1993-12-18')
            """)
            db_connection.commit()

        dao = UtilisateurDAO()

        # WHEN
        result = dao.delete_compte("iris")

        # THEN
        if result is not True:
            raise AssertionError(
                message=f"La suppression devrait réussir, obtenu: {result}",
            )

        # Vérifier que l'utilisateur n'existe plus
        user = dao.recuperer_par_pseudo("iris")
        if user is not None:
            raise AssertionError(
                message=f"L'utilisateur ne devrait plus exister, obtenu: {user}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_delete_compte_inexistant() -> None:
        """Teste la suppression d'un compte inexistant."""
        # GIVEN
        dao = UtilisateurDAO()

        # WHEN
        result = dao.delete_compte("utilisateur_inexistant")

        # THEN
        if result is not False:
            raise AssertionError(
                message=f"La suppression devrait retourner False, obtenu: {result}",
            )

    # ========== Tests pour update_mot_de_passe ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_update_mot_de_passe_success(db_connection) -> None:
        """Teste la mise à jour du mot de passe."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('jack', 'jack@example.com', 'old_hashed_pass', '1989-04-22')
            """)
            db_connection.commit()

        dao = UtilisateurDAO()
        mdps = UserUpdatePassword(
            pseudo="jack",
            mot_de_passe_nouveau_hashed="new_hashed_pass",
        )

        # WHEN
        result = dao.update_mot_de_passe(mdps)

        # THEN
        if result is not True:
            raise AssertionError(
                message=f"La mise à jour devrait réussir, obtenu: {result}",
            )

        # Vérifier que le mot de passe a été modifié
        with db_connection.cursor() as cursor:
            cursor.execute(
                "SELECT mot_de_passe FROM utilisateur WHERE pseudo = 'jack'",
            )
            row = cursor.fetchone()
            if row["mot_de_passe"] != "new_hashed_pass":
                raise AssertionError(
                    message=f"Le mot de passe devrait être 'new_hashed_pass', "
                    f"obtenu: {row['mot_de_passe']}",
                )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_update_mot_de_passe_utilisateur_inexistant() -> None:
        """Teste la mise à jour du mot de passe pour un utilisateur inexistant."""
        # GIVEN
        dao = UtilisateurDAO()
        mdps = UserUpdatePassword(
            pseudo="inexistant",
            mot_de_passe_nouveau_hashed="new_hashed_pass",
        )

        # WHEN
        result = dao.update_mot_de_passe(mdps)

        # THEN
        if result is not False:
            raise AssertionError(
                message=f"La mise à jour devrait retourner False, obtenu: {result}",
            )

    # ========== Tests pour update_pseudo ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_update_pseudo_success(db_connection) -> None:
        """Teste la mise à jour du pseudo."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('old_pseudo', 'user@example.com', 'hashed_pass', '1991-06-08')
            """)
            db_connection.commit()

        dao = UtilisateurDAO()

        # WHEN
        result = dao.update_pseudo("old_pseudo", "new_pseudo")

        # THEN
        if result is not True:
            raise AssertionError(
                message=f"La mise à jour devrait réussir, obtenu: {result}",
            )

        # Vérifier que le pseudo a été modifié
        user = dao.recuperer_par_pseudo("new_pseudo")
        if user is None:
            raise AssertionError(
                message="L'utilisateur devrait être trouvé avec le nouveau pseudo",
            )
        if user.pseudo != "new_pseudo":
            raise AssertionError(
                message=f"Le pseudo devrait être 'new_pseudo', obtenu: {user.pseudo}",
            )

        # Vérifier que l'ancien pseudo n'existe plus
        old_user = dao.recuperer_par_pseudo("old_pseudo")
        if old_user is not None:
            raise AssertionError(
                message="L'ancien pseudo ne devrait plus exister",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_update_pseudo_deja_existant(db_connection) -> None:
        """Teste la mise à jour avec un pseudo déjà pris."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES
                    ('user1', 'user1@example.com', 'hashed_pass', '1990-01-01'),
                    ('user2', 'user2@example.com', 'hashed_pass', '1990-01-01')
            """)
            db_connection.commit()

        dao = UtilisateurDAO()

        # WHEN / THEN
        with pytest.raises(UserAlreadyExistsError) as exc_info:
            dao.update_pseudo("user1", "user2")

        error_message = str(exc_info.value)
        if "user2" not in error_message:
            raise AssertionError(
                message=f"L'erreur devrait mentionner 'user2': {error_message}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_update_pseudo_utilisateur_inexistant() -> None:
        """Teste la mise à jour du pseudo d'un utilisateur inexistant."""
        # GIVEN
        dao = UtilisateurDAO()

        # WHEN
        result = dao.update_pseudo("inexistant", "nouveau_pseudo")

        # THEN
        if result is not False:
            raise AssertionError(
                message=f"La mise à jour devrait retourner False, obtenu: {result}",
            )

    # ========== Tests pour get_date_inscription ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_date_inscription_success(db_connection) -> None:
        """Teste la récupération de la date d'inscription."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('kate', 'kate@example.com', 'hashed_pass', '1994-08-16')
            """)
            db_connection.commit()

        dao = UtilisateurDAO()

        # WHEN
        date_inscription = dao.get_date_inscription("kate")

        # THEN
        if date_inscription is None:
            raise AssertionError(
                message="La date d'inscription ne devrait pas être None",
            )

        # Vérifier que c'est une date ISO valide
        try:
            datetime.fromisoformat(date_inscription)
        except ValueError as e:
            raise AssertionError(
                message=f"La date devrait être au format ISO: {date_inscription}",
            ) from e

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_date_inscription_utilisateur_inexistant() -> None:
        """Teste la récupération de la date d'inscription d'un utilisateur
        inexistant.
        """
        # GIVEN
        dao = UtilisateurDAO()

        # WHEN
        date_inscription = dao.get_date_inscription("inexistant")

        # THEN
        if date_inscription is not None:
            raise AssertionError(
                message=f"La date devrait être None, obtenu: {date_inscription}",
            )
