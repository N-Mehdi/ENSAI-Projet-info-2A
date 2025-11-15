"""Classe de test de src/service/utilisateur_service."""

from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest

from src.dao.utilisateur_dao import UtilisateurDao
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

    def test_creer_compte_succes(self):
        # GIVEN
        donnees = UserRegister(
            pseudo="john_doe",
            mail="john@example.com",
            mot_de_passe="SecurePass123!",
            date_naissance="2000-05-15",
        )

        dao_mock = MagicMock(spec=UtilisateurDao)
        dao_mock.create_compte.return_value = True

        # WHEN
        service = UtilisateurService(dao_mock)
        resultat = service.creer_compte(donnees)

        # THEN
        assert resultat == "compte créé avec succès."
        dao_mock.create_compte.assert_called_once()

    def test_creer_compte_pseudo_vide(self):
        # GIVEN
        donnees = UserRegister(
            pseudo="",
            mail="john@example.com",
            mot_de_passe="SecurePass123!",
            date_naissance="2000-05-15",
        )

        dao_mock = MagicMock(spec=UtilisateurDao)
        service = UtilisateurService(dao_mock)

        # WHEN / THEN
        with pytest.raises(EmptyFieldError) as exc_info:
            service.creer_compte(donnees)
        assert "pseudo" in str(exc_info.value)

    def test_creer_compte_mail_vide(self):
        # GIVEN
        donnees = UserRegister(
            pseudo="john_doe",
            mail="   ",
            mot_de_passe="SecurePass123!",
            date_naissance="2000-05-15",
        )

        dao_mock = MagicMock(spec=UtilisateurDao)
        service = UtilisateurService(dao_mock)

        # WHEN / THEN
        with pytest.raises(EmptyFieldError) as exc_info:
            service.creer_compte(donnees)
        assert "mail" in str(exc_info.value)

    def test_creer_compte_mot_de_passe_vide(self):
        # GIVEN
        donnees = UserRegister(
            pseudo="john_doe",
            mail="john@example.com",
            mot_de_passe="",
            date_naissance="2000-05-15",
        )

        dao_mock = MagicMock(spec=UtilisateurDao)
        service = UtilisateurService(dao_mock)

        # WHEN / THEN
        with pytest.raises(EmptyFieldError) as exc_info:
            service.creer_compte(donnees)
        assert "mot_de_passe" in str(exc_info.value)

    def test_creer_compte_date_naissance_future(self):
        # GIVEN
        date_future = (date.today() + timedelta(days=365)).isoformat()
        donnees = UserRegister(
            pseudo="john_doe",
            mail="john@example.com",
            mot_de_passe="SecurePass123!",
            date_naissance=date_future,
        )

        dao_mock = MagicMock(spec=UtilisateurDao)
        service = UtilisateurService(dao_mock)

        # WHEN / THEN
        with pytest.raises(InvalidBirthDateError) as exc_info:
            service.creer_compte(donnees)
        assert "passé" in str(exc_info.value)

    def test_creer_compte_age_moins_de_13_ans(self):
        # GIVEN
        date_trop_recente = (date.today() - timedelta(days=365 * 10)).isoformat()
        donnees = UserRegister(
            pseudo="john_doe",
            mail="john@example.com",
            mot_de_passe="SecurePass123!",
            date_naissance=date_trop_recente,
        )

        dao_mock = MagicMock(spec=UtilisateurDao)
        service = UtilisateurService(dao_mock)

        # WHEN / THEN
        with pytest.raises(InvalidBirthDateError) as exc_info:
            service.creer_compte(donnees)
        assert "13 ans" in str(exc_info.value)

    def test_creer_compte_date_non_realiste(self):
        # GIVEN
        date_trop_ancienne = "1800-01-01"
        donnees = UserRegister(
            pseudo="john_doe",
            mail="john@example.com",
            mot_de_passe="SecurePass123!",
            date_naissance=date_trop_ancienne,
        )

        dao_mock = MagicMock(spec=UtilisateurDao)
        service = UtilisateurService(dao_mock)

        # WHEN / THEN
        with pytest.raises(InvalidBirthDateError) as exc_info:
            service.creer_compte(donnees)
        assert "réaliste" in str(exc_info.value)

    def test_creer_compte_format_date_invalide(self):
        # GIVEN
        donnees = UserRegister(
            pseudo="john_doe",
            mail="john@example.com",
            mot_de_passe="SecurePass123!",
            date_naissance="15-05-2000",  # Format invalide
        )

        dao_mock = MagicMock(spec=UtilisateurDao)
        service = UtilisateurService(dao_mock)

        # WHEN / THEN
        with pytest.raises(InvalidBirthDateError) as exc_info:
            service.creer_compte(donnees)
        assert "Format attendu" in str(exc_info.value)

    def test_creer_compte_dao_echec(self):
        # GIVEN
        donnees = UserRegister(
            pseudo="john_doe",
            mail="john@example.com",
            mot_de_passe="SecurePass123!",
            date_naissance="2000-05-15",
        )

        dao_mock = MagicMock(spec=UtilisateurDao)
        dao_mock.create_compte.return_value = False

        # WHEN
        service = UtilisateurService(dao_mock)

        # THEN
        with pytest.raises(ServiceError) as exc_info:
            service.creer_compte(donnees)
        assert "créer le compte" in str(exc_info.value)

    # ========== Tests pour authenticate ==========

    def test_authenticate_succes(self):
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
            date_inscription=date.today().isoformat(),
        )

        dao_mock = MagicMock(spec=UtilisateurDao)
        dao_mock.recuperer_par_pseudo.return_value = utilisateur_attendu

        # WHEN
        service = UtilisateurService(dao_mock)
        resultat = service.authenticate(pseudo, mot_de_passe)

        # THEN
        assert resultat == utilisateur_attendu
        dao_mock.recuperer_par_pseudo.assert_called_once_with(pseudo)

    def test_authenticate_utilisateur_inexistant(self):
        # GIVEN
        pseudo = "inconnu"
        mot_de_passe = "password"

        dao_mock = MagicMock(spec=UtilisateurDao)
        dao_mock.recuperer_par_pseudo.return_value = None

        # WHEN
        service = UtilisateurService(dao_mock)

        # THEN
        with pytest.raises(UserNotFoundError):
            service.authenticate(pseudo, mot_de_passe)

    def test_authenticate_mot_de_passe_incorrect(self):
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
            date_inscription=date.today().isoformat(),
        )

        dao_mock = MagicMock(spec=UtilisateurDao)
        dao_mock.recuperer_par_pseudo.return_value = utilisateur

        # WHEN
        service = UtilisateurService(dao_mock)

        # THEN
        with pytest.raises(AuthError):
            service.authenticate(pseudo, mot_de_passe_incorrect)

    # ========== Tests pour supprimer_compte ==========

    def test_supprimer_compte_succes(self):
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
            date_inscription=date.today().isoformat(),
        )

        dao_mock = MagicMock(spec=UtilisateurDao)
        dao_mock.recuperer_par_pseudo.return_value = utilisateur
        dao_mock.delete_compte.return_value = True

        # WHEN
        service = UtilisateurService(dao_mock)
        resultat = service.supprimer_compte(donnees)

        # THEN
        assert resultat == "Compte supprimé avec succès."
        dao_mock.delete_compte.assert_called_once_with("john_doe")

    def test_supprimer_compte_pseudo_vide(self) -> None:
        # GIVEN
        donnees = UserDelete(
            pseudo="",
            mot_de_passe="password",
        )

        # WHEN
        dao_mock = MagicMock(spec=UtilisateurDao)
        service = UtilisateurService(dao_mock)

        # THEN
        with pytest.raises(EmptyFieldError):
            service.supprimer_compte(donnees)

    def test_supprimer_compte_utilisateur_inexistant(self):
        # GIVEN
        donnees = UserDelete(
            pseudo="inconnu",
            mot_de_passe="password",
        )

        dao_mock = MagicMock(spec=UtilisateurDao)
        dao_mock.recuperer_par_pseudo.return_value = None

        # WHEN
        service = UtilisateurService(dao_mock)

        # THEN
        with pytest.raises(UserNotFoundError):
            service.supprimer_compte(donnees)

    def test_supprimer_compte_mot_de_passe_incorrect(self):
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
            date_inscription=date.today().isoformat(),
        )

        dao_mock = MagicMock(spec=UtilisateurDao)
        dao_mock.recuperer_par_pseudo.return_value = utilisateur

        # WHEN
        service = UtilisateurService(dao_mock)

        # THEN
        with pytest.raises(AuthError):
            service.supprimer_compte(donnees)

    def test_supprimer_compte_dao_echec(self):
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
            date_inscription=date.today().isoformat(),
        )

        dao_mock = MagicMock(spec=UtilisateurDao)
        dao_mock.recuperer_par_pseudo.return_value = utilisateur
        dao_mock.delete_compte.return_value = False

        # WHEN
        service = UtilisateurService(dao_mock)

        # THEN
        with pytest.raises(ServiceError) as exc_info:
            service.supprimer_compte(donnees)
        assert "supprimer le compte" in str(exc_info.value)

    # ========== Tests pour changer_mot_de_passe ==========

    def test_changer_mot_de_passe_succes(self):
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
            date_inscription=date.today().isoformat(),
        )

        dao_mock = MagicMock(spec=UtilisateurDao)
        dao_mock.recuperer_par_pseudo.return_value = utilisateur
        dao_mock.update_mot_de_passe.return_value = True

        # WHEN
        service = UtilisateurService(dao_mock)
        resultat = service.changer_mot_de_passe(donnees)

        # THEN
        assert resultat == "Mot de passe modifié avec succès."
        dao_mock.update_mot_de_passe.assert_called_once()

    def test_changer_mot_de_passe_pseudo_vide(self):
        # GIVEN
        donnees = UserChangePassword(
            pseudo="",
            mot_de_passe_actuel="OldPass",
            mot_de_passe_nouveau="NewPass",
        )

        dao_mock = MagicMock(spec=UtilisateurDao)
        service = UtilisateurService(dao_mock)

        # WHEN / THEN
        with pytest.raises(EmptyFieldError) as exc_info:
            service.changer_mot_de_passe(donnees)
        assert "pseudo" in str(exc_info.value)

    def test_changer_mot_de_passe_identique(self):
        # GIVEN
        donnees = UserChangePassword(
            pseudo="john_doe",
            mot_de_passe_actuel="SamePass123!",
            mot_de_passe_nouveau="SamePass123!",
        )

        dao_mock = MagicMock(spec=UtilisateurDao)
        service = UtilisateurService(dao_mock)

        # WHEN / THEN
        with pytest.raises(ServiceError) as exc_info:
            service.changer_mot_de_passe(donnees)
        assert "différent" in str(exc_info.value)

    def test_changer_mot_de_passe_utilisateur_inexistant(self):
        # GIVEN
        donnees = UserChangePassword(
            pseudo="inconnu",
            mot_de_passe_actuel="OldPass",
            mot_de_passe_nouveau="NewPass",
        )

        dao_mock = MagicMock(spec=UtilisateurDao)
        dao_mock.recuperer_par_pseudo.return_value = None

        # WHEN
        service = UtilisateurService(dao_mock)

        # THEN
        with pytest.raises(UserNotFoundError):
            service.changer_mot_de_passe(donnees)

    def test_changer_mot_de_passe_actuel_incorrect(self):
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
            date_inscription=date.today().isoformat(),
        )

        dao_mock = MagicMock(spec=UtilisateurDao)
        dao_mock.recuperer_par_pseudo.return_value = utilisateur

        # WHEN
        service = UtilisateurService(dao_mock)

        # THEN
        with pytest.raises(AuthError):
            service.changer_mot_de_passe(donnees)

    # ========== Tests pour read ==========

    def test_read_succes(self):
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

        dao_mock = MagicMock(spec=UtilisateurDao)
        dao_mock.read.return_value = utilisateur_attendu

        # WHEN
        service = UtilisateurService(dao_mock)
        resultat = service.read(id_utilisateur)

        # THEN
        assert resultat == utilisateur_attendu
        dao_mock.read.assert_called_once_with(id_utilisateur)

    def test_read_utilisateur_inexistant(self):
        # GIVEN
        id_utilisateur = 999

        dao_mock = MagicMock(spec=UtilisateurDao)
        dao_mock.read.return_value = None

        # WHEN
        service = UtilisateurService(dao_mock)

        # THEN
        with pytest.raises(UserNotFoundError):
            service.read(id_utilisateur)

    # ========== Tests pour obtenir_date_inscription ==========

    def test_obtenir_date_inscription_succes(self):
        # GIVEN
        pseudo = "john_doe"
        date_inscription = "2024-01-15"

        dao_mock = MagicMock(spec=UtilisateurDao)
        dao_mock.get_date_inscription.return_value = date_inscription

        # WHEN
        service = UtilisateurService(dao_mock)
        resultat = service.obtenir_date_inscription(pseudo)

        # THEN
        assert isinstance(resultat, DateInscriptionResponse)
        assert resultat.pseudo == pseudo
        assert resultat.date_inscription == date_inscription
        dao_mock.get_date_inscription.assert_called_once_with(pseudo)

    def test_obtenir_date_inscription_pseudo_vide(self):
        # GIVEN
        pseudo = "   "

        dao_mock = MagicMock(spec=UtilisateurDao)
        service = UtilisateurService(dao_mock)

        # WHEN / THEN
        with pytest.raises(EmptyFieldError) as exc_info:
            service.obtenir_date_inscription(pseudo)
        assert "pseudo" in str(exc_info.value)
