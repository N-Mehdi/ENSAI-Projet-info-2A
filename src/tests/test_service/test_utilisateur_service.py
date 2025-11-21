"""Classe de test de UtilisateurService."""

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest

from src.dao.utilisateur_dao import UtilisateurDAO
from src.models.utilisateurs import (
    DateInscriptionResponse,
    User,
    UserChangePassword,
    UserDelete,
    UserRegister,
)
from src.service.utilisateur_service import UtilisateurService
from src.utils.exceptions import (
    AuthError,
    EmptyFieldError,
    InvalidBirthDateError,
    ServiceError,
    UserNotFoundError,
)
from src.utils.securite import hacher_mot_de_passe


class TestUtilisateurService:
    """Tests pour UtilisateurService."""

    # ========== Tests pour creer_compte ==========
    @staticmethod
    def test_creer_compte_succes() -> None:
        """Teste la création d'un compte avec des données valides."""
        # GIVEN
        donnees = UserRegister(
            pseudo="john_doe",
            mail="john@example.com",
            mot_de_passe="SecurePass123!",
            date_naissance="2000-05-15",
        )

        dao_mock = MagicMock(spec=UtilisateurDAO)
        dao_mock.create_compte.return_value = True

        # WHEN
        service = UtilisateurService(dao_mock)
        resultat = service.creer_compte(donnees)

        # THEN
        if resultat != "compte créé avec succès.":
            raise AssertionError(
                message=f"Le message devrait être 'compte créé avec succès.',"
                f"obtenu: {resultat}",
            )
        dao_mock.create_compte.assert_called_once()

    @staticmethod
    def test_creer_compte_pseudo_vide() -> None:
        """Teste la création d'un compte avec un pseudo vide."""
        # GIVEN
        donnees = UserRegister(
            pseudo="",
            mail="john@example.com",
            mot_de_passe="SecurePass123!",
            date_naissance="2000-05-15",
        )

        dao_mock = MagicMock(spec=UtilisateurDAO)
        service = UtilisateurService(dao_mock)

        # WHEN / THEN
        with pytest.raises(EmptyFieldError) as exc_info:
            service.creer_compte(donnees)

        error_message = str(exc_info.value)
        if "pseudo" not in error_message:
            raise AssertionError(
                message=f"'pseudo' devrait être dans le message d'erreur:"
                f"{error_message}",
            )

    @staticmethod
    def test_creer_compte_mail_vide() -> None:
        """Teste la création d'un compte avec un mail vide."""
        # GIVEN
        donnees = UserRegister(
            pseudo="john_doe",
            mail="   ",
            mot_de_passe="SecurePass123!",
            date_naissance="2000-05-15",
        )

        dao_mock = MagicMock(spec=UtilisateurDAO)
        service = UtilisateurService(dao_mock)

        # WHEN / THEN
        with pytest.raises(EmptyFieldError) as exc_info:
            service.creer_compte(donnees)

        error_message = str(exc_info.value)
        if "mail" not in error_message:
            raise AssertionError(
                message=f"'mail' devrait être dans le message d'erreur:{error_message}",
            )

    @staticmethod
    def test_creer_compte_mot_de_passe_vide() -> None:
        """Teste la création d'un compte avec un mot de passe vide."""
        # GIVEN
        donnees = UserRegister(
            pseudo="john_doe",
            mail="john@example.com",
            mot_de_passe="",
            date_naissance="2000-05-15",
        )

        dao_mock = MagicMock(spec=UtilisateurDAO)
        service = UtilisateurService(dao_mock)

        # WHEN / THEN
        with pytest.raises(EmptyFieldError) as exc_info:
            service.creer_compte(donnees)

        error_message = str(exc_info.value)
        if "mot_de_passe" not in error_message:
            raise AssertionError(
                message=f"'mot_de_passe' devrait être dans le message d'erreur:"
                f"{error_message}",
            )

    @staticmethod
    def test_creer_compte_date_naissance_future() -> None:
        """Teste la création d'un compte avec une date de naissance future."""
        # GIVEN
        date_future = (datetime.now(UTC).date() + timedelta(days=365)).isoformat()
        donnees = UserRegister(
            pseudo="john_doe",
            mail="john@example.com",
            mot_de_passe="SecurePass123!",
            date_naissance=date_future,
        )

        dao_mock = MagicMock(spec=UtilisateurDAO)
        service = UtilisateurService(dao_mock)

        # WHEN / THEN
        with pytest.raises(InvalidBirthDateError) as exc_info:
            service.creer_compte(donnees)

        error_message = str(exc_info.value)
        if "passé" not in error_message:
            raise AssertionError(
                message=f"'passé' devrait être dans le message d'erreur:"
                f"{error_message}",
            )

    @staticmethod
    def test_creer_compte_age_moins_de_18_ans() -> None:
        """Teste la création d'un compte avec un âge inférieur à 18 ans."""
        # GIVEN
        date_trop_recente = (
            datetime.now(UTC).date() - timedelta(days=365 * 10)
        ).isoformat()
        donnees = UserRegister(
            pseudo="john_doe",
            mail="john@example.com",
            mot_de_passe="SecurePass123!",
            date_naissance=date_trop_recente,
        )

        dao_mock = MagicMock(spec=UtilisateurDAO)
        service = UtilisateurService(dao_mock)

        # WHEN / THEN
        with pytest.raises(InvalidBirthDateError) as exc_info:
            service.creer_compte(donnees)

        error_message = str(exc_info.value)
        if "18 ans" not in error_message:
            raise AssertionError(
                message="'18 ans' devrait être dans le message d'erreur:"
                f"{error_message}",
            )

    @staticmethod
    def test_creer_compte_date_non_realiste() -> None:
        """Teste la création d'un compte avec une date de naissance non réaliste."""
        # GIVEN
        date_trop_ancienne = "1800-01-01"
        donnees = UserRegister(
            pseudo="john_doe",
            mail="john@example.com",
            mot_de_passe="SecurePass123!",
            date_naissance=date_trop_ancienne,
        )

        dao_mock = MagicMock(spec=UtilisateurDAO)
        service = UtilisateurService(dao_mock)

        # WHEN / THEN
        with pytest.raises(InvalidBirthDateError) as exc_info:
            service.creer_compte(donnees)

        error_message = str(exc_info.value)
        if "réaliste" not in error_message:
            raise AssertionError(
                message=f"'réaliste' devrait être dans le message d'erreur:"
                f"{error_message}",
            )

    @staticmethod
    def test_creer_compte_format_date_invalide() -> None:
        """Teste la création d'un compte avec un format de date invalide."""
        # GIVEN
        donnees = UserRegister(
            pseudo="john_doe",
            mail="john@example.com",
            mot_de_passe="SecurePass123!",
            date_naissance="15-05-2000",  # Format invalide
        )

        dao_mock = MagicMock(spec=UtilisateurDAO)
        service = UtilisateurService(dao_mock)

        # WHEN / THEN
        with pytest.raises(InvalidBirthDateError) as exc_info:
            service.creer_compte(donnees)

        error_message = str(exc_info.value)
        if "Format attendu" not in error_message:
            raise AssertionError(
                message=f"'Format attendu' devrait être dans le message d'erreur:"
                f"{error_message}",
            )

    @staticmethod
    def test_creer_compte_dao_echec() -> None:
        """Teste l'échec de création de compte au niveau du DAO."""
        # GIVEN
        donnees = UserRegister(
            pseudo="john_doe",
            mail="john@example.com",
            mot_de_passe="SecurePass123!",
            date_naissance="2000-05-15",
        )

        dao_mock = MagicMock(spec=UtilisateurDAO)
        dao_mock.create_compte.return_value = False

        # WHEN
        service = UtilisateurService(dao_mock)

        # THEN
        with pytest.raises(ServiceError) as exc_info:
            service.creer_compte(donnees)

        error_message = str(exc_info.value)
        if "créer le compte" not in error_message:
            raise AssertionError(
                message=f"'créer le compte' devrait être dans le message d'erreur:"
                f"{error_message}",
            )

    # ========== Tests pour authenticate ==========
    @staticmethod
    def test_authenticate_succes() -> None:
        """Teste l'authentification réussie d'un utilisateur."""
        # GIVEN
        pseudo = "john_doe"
        mot_de_passe = "SecurePass123!"
        mot_de_passe_hashed = hacher_mot_de_passe(mot_de_passe)

        utilisateur_attendu = User(
            id_utilisateur=1,
            pseudo="john_doe",
            mail="john@example.com",
            mot_de_passe_hashed=mot_de_passe_hashed,
            date_naissance="2000-01-01",
            date_inscription=datetime.now(UTC).date().isoformat(),
        )

        dao_mock = MagicMock(spec=UtilisateurDAO)
        dao_mock.recuperer_par_pseudo.return_value = utilisateur_attendu

        # WHEN
        service = UtilisateurService(dao_mock)
        resultat = service.authenticate(pseudo, mot_de_passe)

        # THEN
        if resultat != utilisateur_attendu:
            raise AssertionError(
                message=f"L'utilisateur retourné devrait être {utilisateur_attendu},"
                f"obtenu: {resultat}",
            )
        dao_mock.recuperer_par_pseudo.assert_called_once_with(pseudo)

    @staticmethod
    def test_authenticate_utilisateur_inexistant() -> None:
        """Teste l'authentification avec un utilisateur inexistant."""
        # GIVEN
        pseudo = "inconnu"
        mot_de_passe = "password"

        dao_mock = MagicMock(spec=UtilisateurDAO)
        dao_mock.recuperer_par_pseudo.return_value = None

        # WHEN
        service = UtilisateurService(dao_mock)

        # THEN
        with pytest.raises(UserNotFoundError):
            service.authenticate(pseudo, mot_de_passe)

    @staticmethod
    def test_authenticate_mot_de_passe_incorrect() -> None:
        """Teste l'authentification avec un mot de passe incorrect."""
        # GIVEN
        pseudo = "john_doe"
        mot_de_passe_correct = "SecurePass123!"
        mot_de_passe_incorrect = "WrongPassword"
        mot_de_passe_hashed = hacher_mot_de_passe(mot_de_passe_correct)

        utilisateur = User(
            id_utilisateur=1,
            pseudo="john_doe",
            mail="john@example.com",
            mot_de_passe_hashed=mot_de_passe_hashed,
            date_naissance="2000-01-01",
            date_inscription=datetime.now(UTC).date().isoformat(),
        )

        dao_mock = MagicMock(spec=UtilisateurDAO)
        dao_mock.recuperer_par_pseudo.return_value = utilisateur

        # WHEN
        service = UtilisateurService(dao_mock)

        # THEN
        with pytest.raises(AuthError):
            service.authenticate(pseudo, mot_de_passe_incorrect)

    # ========== Tests pour supprimer_compte ==========
    @staticmethod
    def test_supprimer_compte_succes() -> None:
        """Teste la suppression réussie d'un compte."""
        # GIVEN
        mot_de_passe = "SecurePass123!"
        mot_de_passe_hashed = hacher_mot_de_passe(mot_de_passe)

        donnees = UserDelete(
            pseudo="john_doe",
            mot_de_passe=mot_de_passe,
        )

        utilisateur = User(
            id_utilisateur=1,
            pseudo="john_doe",
            mail="john@example.com",
            mot_de_passe_hashed=mot_de_passe_hashed,
            date_naissance="2000-01-01",
            date_inscription=datetime.now(UTC).date().isoformat(),
        )

        dao_mock = MagicMock(spec=UtilisateurDAO)
        dao_mock.recuperer_par_pseudo.return_value = utilisateur
        dao_mock.delete_compte.return_value = True

        # WHEN
        service = UtilisateurService(dao_mock)
        resultat = service.supprimer_compte(donnees)

        # THEN
        if resultat != "Compte supprimé avec succès.":
            raise AssertionError(
                message=f"Le message devrait être 'Compte supprimé avec succès.',"
                f"obtenu: {resultat}",
            )
        dao_mock.delete_compte.assert_called_once_with("john_doe")

    @staticmethod
    def test_supprimer_compte_pseudo_vide() -> None:
        """Teste la suppression d'un compte avec un pseudo vide."""
        # GIVEN
        donnees = UserDelete(
            pseudo="",
            mot_de_passe="password",
        )

        # WHEN
        dao_mock = MagicMock(spec=UtilisateurDAO)
        service = UtilisateurService(dao_mock)

        # THEN
        with pytest.raises(EmptyFieldError):
            service.supprimer_compte(donnees)

    @staticmethod
    def test_supprimer_compte_utilisateur_inexistant() -> None:
        """Teste la suppression d'un compte inexistant."""
        # GIVEN
        donnees = UserDelete(
            pseudo="inconnu",
            mot_de_passe="password",
        )

        dao_mock = MagicMock(spec=UtilisateurDAO)
        dao_mock.recuperer_par_pseudo.return_value = None

        # WHEN
        service = UtilisateurService(dao_mock)

        # THEN
        with pytest.raises(UserNotFoundError):
            service.supprimer_compte(donnees)

    @staticmethod
    def test_supprimer_compte_mot_de_passe_incorrect() -> None:
        """Teste la suppression d'un compte avec un mot de passe incorrect."""
        # GIVEN
        mot_de_passe_correct = "SecurePass123!"
        mot_de_passe_hashed = hacher_mot_de_passe(mot_de_passe_correct)

        donnees = UserDelete(
            pseudo="john_doe",
            mot_de_passe="WrongPassword",
        )

        utilisateur = User(
            id_utilisateur=1,
            pseudo="john_doe",
            mail="john@example.com",
            mot_de_passe_hashed=mot_de_passe_hashed,
            date_naissance="2000-01-01",
            date_inscription=datetime.now(UTC).date().isoformat(),
        )

        dao_mock = MagicMock(spec=UtilisateurDAO)
        dao_mock.recuperer_par_pseudo.return_value = utilisateur

        # WHEN
        service = UtilisateurService(dao_mock)

        # THEN
        with pytest.raises(AuthError):
            service.supprimer_compte(donnees)

    @staticmethod
    def test_supprimer_compte_dao_echec() -> None:
        """Teste l'échec de suppression de compte au niveau du DAO."""
        # GIVEN
        mot_de_passe = "SecurePass123!"
        mot_de_passe_hashed = hacher_mot_de_passe(mot_de_passe)

        donnees = UserDelete(
            pseudo="john_doe",
            mot_de_passe=mot_de_passe,
        )

        utilisateur = User(
            id_utilisateur=1,
            pseudo="john_doe",
            mail="john@example.com",
            mot_de_passe_hashed=mot_de_passe_hashed,
            date_naissance="2000-01-01",
            date_inscription=datetime.now(UTC).date().isoformat(),
        )

        dao_mock = MagicMock(spec=UtilisateurDAO)
        dao_mock.recuperer_par_pseudo.return_value = utilisateur
        dao_mock.delete_compte.return_value = False

        # WHEN
        service = UtilisateurService(dao_mock)

        # THEN
        with pytest.raises(ServiceError) as exc_info:
            service.supprimer_compte(donnees)

        error_message = str(exc_info.value)
        if "supprimer le compte" not in error_message:
            raise AssertionError(
                message=f"'supprimer le compte' devrait être dans le message d'erreur:"
                f"{error_message}",
            )

    # ========== Tests pour changer_mot_de_passe ==========
    @staticmethod
    def test_changer_mot_de_passe_succes() -> None:
        """Teste le changement de mot de passe réussi."""
        # GIVEN
        mot_de_passe_actuel = "OldPass123!"
        mot_de_passe_nouveau = "NewPass456!"
        mot_de_passe_hashed = hacher_mot_de_passe(mot_de_passe_actuel)

        donnees = UserChangePassword(
            pseudo="john_doe",
            mot_de_passe_actuel=mot_de_passe_actuel,
            mot_de_passe_nouveau=mot_de_passe_nouveau,
        )

        utilisateur = User(
            id_utilisateur=1,
            pseudo="john_doe",
            mail="john@example.com",
            mot_de_passe_hashed=mot_de_passe_hashed,
            date_naissance="2000-01-01",
            date_inscription=datetime.now(UTC).date().isoformat(),
        )

        dao_mock = MagicMock(spec=UtilisateurDAO)
        dao_mock.recuperer_par_pseudo.return_value = utilisateur
        dao_mock.update_mot_de_passe.return_value = True

        # WHEN
        service = UtilisateurService(dao_mock)
        resultat = service.changer_mot_de_passe(donnees)

        # THEN
        if resultat != "Mot de passe modifié avec succès.":
            raise AssertionError(
                message=f"Le message devrait être 'Mot de passe modifié avec succès.',"
                f"obtenu: {resultat}",
            )
        dao_mock.update_mot_de_passe.assert_called_once()

    @staticmethod
    def test_changer_mot_de_passe_pseudo_vide() -> None:
        """Teste le changement de mot de passe avec un pseudo vide."""
        # GIVEN
        donnees = UserChangePassword(
            pseudo="",
            mot_de_passe_actuel="OldPass",
            mot_de_passe_nouveau="NewPass",
        )

        dao_mock = MagicMock(spec=UtilisateurDAO)
        service = UtilisateurService(dao_mock)

        # WHEN / THEN
        with pytest.raises(EmptyFieldError) as exc_info:
            service.changer_mot_de_passe(donnees)

        error_message = str(exc_info.value)
        if "pseudo" not in error_message:
            raise AssertionError(
                message=f"'pseudo' devrait être dans le message d'erreur:"
                f"{error_message}",
            )

    @staticmethod
    def test_changer_mot_de_passe_identique() -> None:
        """Teste le changement de mot de passe avec un nouveau mot de passe
        identique.
        """
        # GIVEN
        donnees = UserChangePassword(
            pseudo="john_doe",
            mot_de_passe_actuel="SamePass123!",
            mot_de_passe_nouveau="SamePass123!",
        )

        dao_mock = MagicMock(spec=UtilisateurDAO)
        service = UtilisateurService(dao_mock)

        # WHEN / THEN
        with pytest.raises(ServiceError) as exc_info:
            service.changer_mot_de_passe(donnees)

        error_message = str(exc_info.value)
        if "différent" not in error_message:
            raise AssertionError(
                message=f"'différent' devrait être dans le message d'erreur:"
                f"{error_message}",
            )

    @staticmethod
    def test_changer_mot_de_passe_utilisateur_inexistant() -> None:
        """Teste le changement de mot de passe pour un utilisateur inexistant."""
        # GIVEN
        donnees = UserChangePassword(
            pseudo="inconnu",
            mot_de_passe_actuel="OldPass",
            mot_de_passe_nouveau="NewPass",
        )

        dao_mock = MagicMock(spec=UtilisateurDAO)
        dao_mock.recuperer_par_pseudo.return_value = None

        # WHEN
        service = UtilisateurService(dao_mock)

        # THEN
        with pytest.raises(UserNotFoundError):
            service.changer_mot_de_passe(donnees)

    @staticmethod
    def test_changer_mot_de_passe_actuel_incorrect() -> None:
        """Teste le changement de mot de passe avec un mot de passe actuel incorrect."""
        # GIVEN
        mot_de_passe_correct = "OldPass123!"
        mot_de_passe_hashed = hacher_mot_de_passe(mot_de_passe_correct)

        donnees = UserChangePassword(
            pseudo="john_doe",
            mot_de_passe_actuel="WrongPass",
            mot_de_passe_nouveau="NewPass456!",
        )

        utilisateur = User(
            id_utilisateur=1,
            pseudo="john_doe",
            mail="john@example.com",
            mot_de_passe_hashed=mot_de_passe_hashed,
            date_naissance="2000-01-01",
            date_inscription=datetime.now(UTC).date().isoformat(),
        )

        dao_mock = MagicMock(spec=UtilisateurDAO)
        dao_mock.recuperer_par_pseudo.return_value = utilisateur

        # WHEN
        service = UtilisateurService(dao_mock)

        # THEN
        with pytest.raises(AuthError):
            service.changer_mot_de_passe(donnees)

    # ========== Tests pour read ==========
    @staticmethod
    def test_read_succes() -> None:
        """Teste la lecture réussie d'un utilisateur par ID."""
        # GIVEN
        id_utilisateur = 1
        utilisateur_attendu = User(
            id_utilisateur=1,
            pseudo="john_doe",
            mail="john@example.com",
            mot_de_passe_hashed="hashed",
            date_naissance="2000-01-01",
            date_inscription="2025-01-01",
        )

        dao_mock = MagicMock(spec=UtilisateurDAO)
        dao_mock.read.return_value = utilisateur_attendu

        # WHEN
        service = UtilisateurService(dao_mock)
        resultat = service.read(id_utilisateur)

        # THEN
        if resultat != utilisateur_attendu:
            raise AssertionError(
                message=f"L'utilisateur retourné devrait être {utilisateur_attendu},"
                f"obtenu: {resultat}",
            )
        dao_mock.read.assert_called_once_with(id_utilisateur)

    @staticmethod
    def test_read_utilisateur_inexistant() -> None:
        """Teste la lecture d'un utilisateur inexistant."""
        # GIVEN
        id_utilisateur = 999

        dao_mock = MagicMock(spec=UtilisateurDAO)
        dao_mock.read.return_value = None

        # WHEN
        service = UtilisateurService(dao_mock)

        # THEN
        with pytest.raises(UserNotFoundError):
            service.read(id_utilisateur)

    # ========== Tests pour obtenir_date_inscription ==========
    @staticmethod
    def test_obtenir_date_inscription_succes() -> None:
        """Teste l'obtention réussie de la date d'inscription."""
        # GIVEN
        pseudo = "john_doe"
        date_inscription = "2024-01-15"

        dao_mock = MagicMock(spec=UtilisateurDAO)
        dao_mock.get_date_inscription.return_value = date_inscription

        # WHEN
        service = UtilisateurService(dao_mock)
        resultat = service.obtenir_date_inscription(pseudo)

        # THEN
        if not isinstance(resultat, DateInscriptionResponse):
            raise TypeError(
                message="Le résultat devrait être de type DateInscriptionResponse,"
                "obtenu: {type(resultat)}",
            )
        if resultat.pseudo != pseudo:
            raise AssertionError(
                message=f"Le pseudo devrait être '{pseudo}', obtenu: {resultat.pseudo}",
            )
        if resultat.date_inscription != date_inscription:
            raise AssertionError(
                message=f"La date d'inscription devrait être '{date_inscription}',"
                "obtenu: {resultat.date_inscription}",
            )
        dao_mock.get_date_inscription.assert_called_once_with(pseudo)
