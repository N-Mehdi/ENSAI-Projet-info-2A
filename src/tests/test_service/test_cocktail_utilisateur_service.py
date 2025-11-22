"""Tests pour CocktailUtilisateurService."""

from unittest.mock import MagicMock

import pytest

from src.business_object.cocktail import Cocktail
from src.dao.cocktail_utilisateur_dao import CocktailUtilisateurDAO
from src.service.cocktail_utilisateur_service import CocktailUtilisateurService
from src.utils.exceptions import CocktailNotFoundError


class TestCocktailUtilisateurService:
    """Tests pour CocktailUtilisateurService."""

    # ========== Tests pour get_cocktails_testes ==========
    @staticmethod
    def test_get_cocktails_testes_succes() -> None:
        """Teste la récupération des cocktails testés avec succès."""
        # GIVEN
        id_utilisateur = 1
        cocktails_attendus = [
            Cocktail(
                id_cocktail=1,
                nom="Margarita",
                categorie="Ordinary Drink",
                verre="Cocktail glass",
                alcool=True,
                image="https://example.com/margarita.jpg",
            ),
            Cocktail(
                id_cocktail=2,
                nom="Mojito",
                categorie="Ordinary Drink",
                verre="Highball glass",
                alcool=True,
                image="https://example.com/mojito.jpg",
            ),
        ]

        dao_mock = MagicMock(spec=CocktailUtilisateurDAO)
        dao_mock.get_teste.return_value = cocktails_attendus

        # WHEN
        service = CocktailUtilisateurService()
        service.dao = dao_mock
        resultat = service.get_cocktails_testes(id_utilisateur)

        # THEN
        if resultat != cocktails_attendus:
            raise AssertionError(
                message=f"Le résultat devrait être {cocktails_attendus},"
                f"obtenu: {resultat}",
            )
        dao_mock.get_teste.assert_called_once_with(id_utilisateur)

    @staticmethod
    def test_get_cocktails_testes_liste_vide() -> None:
        """Teste la récupération des cocktails testés avec une liste vide."""
        # GIVEN
        id_utilisateur = 1

        dao_mock = MagicMock(spec=CocktailUtilisateurDAO)
        dao_mock.get_teste.return_value = []

        # WHEN
        service = CocktailUtilisateurService()
        service.dao = dao_mock
        resultat = service.get_cocktails_testes(id_utilisateur)

        # THEN
        if resultat != []:
            raise AssertionError(
                message=f"La liste devrait être vide, obtenu: {resultat}",
            )
        dao_mock.get_teste.assert_called_once_with(id_utilisateur)

    # ========== Tests pour ajouter_cocktail_teste ==========
    @staticmethod
    def test_ajouter_cocktail_teste_succes() -> None:
        """Teste l'ajout d'un cocktail testé avec succès."""
        # GIVEN
        id_utilisateur = 1
        nom_cocktail = "Margarita"
        reponse_attendue = {
            "success": True,
            "message": "Cocktail 'Margarita' ajouté aux cocktails testés",
        }

        dao_mock = MagicMock(spec=CocktailUtilisateurDAO)
        dao_mock.ajouter_cocktail_teste.return_value = reponse_attendue

        # WHEN
        service = CocktailUtilisateurService()
        service.dao = dao_mock
        resultat = service.ajouter_cocktail_teste(id_utilisateur, nom_cocktail)

        # THEN
        if resultat != reponse_attendue:
            raise AssertionError(
                message=f"Le résultat devrait être {reponse_attendue},"
                f"obtenu: {resultat}",
            )
        dao_mock.ajouter_cocktail_teste.assert_called_once_with(
            id_utilisateur,
            nom_cocktail,
        )

    @staticmethod
    def test_ajouter_cocktail_teste_deja_present() -> None:
        """Teste l'ajout d'un cocktail déjà testé."""
        # GIVEN
        id_utilisateur = 1
        nom_cocktail = "Margarita"
        reponse_attendue = {
            "success": False,
            "message": "Cocktail 'Margarita' est déjà dans les cocktails testés",
        }

        dao_mock = MagicMock(spec=CocktailUtilisateurDAO)
        dao_mock.ajouter_cocktail_teste.return_value = reponse_attendue

        # WHEN
        service = CocktailUtilisateurService()
        service.dao = dao_mock
        resultat = service.ajouter_cocktail_teste(id_utilisateur, nom_cocktail)

        # THEN
        if resultat != reponse_attendue:
            raise AssertionError(
                message=f"Le résultat devrait être {reponse_attendue},"
                f"obtenu: {resultat}",
            )
        if resultat["success"] is not False:
            raise AssertionError(
                message=f"success devrait être False, obtenu: {resultat['success']}",
            )

    @staticmethod
    def test_ajouter_cocktail_teste_cocktail_inexistant() -> None:
        """Teste l'ajout d'un cocktail inexistant."""
        # GIVEN
        id_utilisateur = 1
        nom_cocktail = "CocktailInconnu"

        dao_mock = MagicMock(spec=CocktailUtilisateurDAO)
        dao_mock.ajouter_cocktail_teste.side_effect = CocktailNotFoundError(
            "Cocktail non trouvé",
        )

        # WHEN
        service = CocktailUtilisateurService()
        service.dao = dao_mock

        # THEN
        with pytest.raises(CocktailNotFoundError) as exc_info:
            service.ajouter_cocktail_teste(id_utilisateur, nom_cocktail)
        if "Cocktail non trouvé" not in str(exc_info.value):
            raise AssertionError(
                message=f"'Cocktail non trouvé' devrait être dans l'erreur, "
                f"obtenu: {exc_info.value}",
            )

    # ========== Tests pour retirer_cocktail_teste ==========

    @staticmethod
    def test_retirer_cocktail_teste_succes() -> None:
        """Teste le retrait d'un cocktail testé avec succès."""
        # GIVEN
        id_utilisateur = 1
        nom_cocktail = "Margarita"
        reponse_attendue = {
            "success": True,
            "message": "Cocktail 'Margarita' retiré des cocktails testés",
        }

        dao_mock = MagicMock(spec=CocktailUtilisateurDAO)
        dao_mock.retirer_cocktail_teste.return_value = reponse_attendue

        # WHEN
        service = CocktailUtilisateurService()
        service.dao = dao_mock
        resultat = service.retirer_cocktail_teste(id_utilisateur, nom_cocktail)

        # THEN
        if resultat != reponse_attendue:
            raise AssertionError(
                message=f"Le résultat devrait être {reponse_attendue},"
                f"obtenu: {resultat}",
            )
        dao_mock.retirer_cocktail_teste.assert_called_once_with(
            id_utilisateur,
            nom_cocktail,
        )

    @staticmethod
    def test_retirer_cocktail_teste_non_present() -> None:
        """Teste le retrait d'un cocktail non testé."""
        # GIVEN
        id_utilisateur = 1
        nom_cocktail = "Margarita"
        reponse_attendue = {
            "success": False,
            "message": "Cocktail 'Margarita' n'est pas dans les cocktails testés",
        }

        dao_mock = MagicMock(spec=CocktailUtilisateurDAO)
        dao_mock.retirer_cocktail_teste.return_value = reponse_attendue

        # WHEN
        service = CocktailUtilisateurService()
        service.dao = dao_mock
        resultat = service.retirer_cocktail_teste(id_utilisateur, nom_cocktail)

        # THEN
        if resultat != reponse_attendue:
            raise AssertionError(
                message=f"Le résultat devrait être {reponse_attendue},"
                f"obtenu: {resultat}",
            )
        if resultat["success"] is not False:
            raise AssertionError(
                message=f"success devrait être False, obtenu:{resultat['success']}",
            )

    @staticmethod
    def test_retirer_cocktail_teste_cocktail_inexistant() -> None:
        """Teste le retrait d'un cocktail inexistant."""
        # GIVEN
        id_utilisateur = 1
        nom_cocktail = "CocktailInconnu"

        dao_mock = MagicMock(spec=CocktailUtilisateurDAO)
        dao_mock.retirer_cocktail_teste.side_effect = CocktailNotFoundError(
            "Cocktail non trouvé",
        )

        # WHEN
        service = CocktailUtilisateurService()
        service.dao = dao_mock

        # THEN
        with pytest.raises(CocktailNotFoundError) as exc_info:
            service.retirer_cocktail_teste(id_utilisateur, nom_cocktail)
        if "Cocktail non trouvé" not in str(exc_info.value):
            raise AssertionError(
                message=f"'Cocktail non trouvé' devrait être dans l'erreur, "
                f"obtenu: {exc_info.value}",
            )

    @staticmethod
    def test_retirer_cocktail_teste_utilisateur_sans_cocktails() -> None:
        """Teste le retrait pour un utilisateur sans cocktails testés."""
        # GIVEN
        id_utilisateur = 999
        nom_cocktail = "Margarita"
        reponse_attendue = {
            "success": False,
            "message": "Aucun cocktail testé trouvé pour cet utilisateur",
        }

        dao_mock = MagicMock(spec=CocktailUtilisateurDAO)
        dao_mock.retirer_cocktail_teste.return_value = reponse_attendue

        # WHEN
        service = CocktailUtilisateurService()
        service.dao = dao_mock
        resultat = service.retirer_cocktail_teste(id_utilisateur, nom_cocktail)

        # THEN
        if resultat != reponse_attendue:
            raise AssertionError(
                message=f"Le résultat devrait être {reponse_attendue},"
                f"obtenu: {resultat}",
            )
        if resultat["success"] is not False:
            raise AssertionError(
                message=f"success devrait être False, obtenu:{resultat['success']}",
            )
