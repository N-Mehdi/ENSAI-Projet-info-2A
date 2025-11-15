"""Tests pour CocktailUtilisateurService."""

from unittest.mock import MagicMock

import pytest

from src.business_object.cocktail import Cocktail
from src.dao.cocktail_utilisateur_dao import CocktailUtilisateurDao
from src.service.cocktail_utilisateur_service import CocktailUtilisateurService


class TestCocktailUtilisateurService:
    """Tests pour CocktailUtilisateurService."""

    # ========== Tests pour get_cocktails_testes ==========

    def test_get_cocktails_testes_succes(self) -> None:
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

        dao_mock = MagicMock(spec=CocktailUtilisateurDao)
        dao_mock.get_teste.return_value = cocktails_attendus

        # WHEN
        service = CocktailUtilisateurService()
        service.dao = dao_mock
        resultat = service.get_cocktails_testes(id_utilisateur)

        # THEN
        assert resultat == cocktails_attendus
        dao_mock.get_teste.assert_called_once_with(id_utilisateur)

    def test_get_cocktails_testes_liste_vide(self) -> None:
        """Teste la récupération des cocktails testés quand la liste est vide."""
        # GIVEN
        id_utilisateur = 1

        dao_mock = MagicMock(spec=CocktailUtilisateurDao)
        dao_mock.get_teste.return_value = []

        # WHEN
        service = CocktailUtilisateurService()
        service.dao = dao_mock
        resultat = service.get_cocktails_testes(id_utilisateur)

        # THEN
        assert resultat == []
        dao_mock.get_teste.assert_called_once_with(id_utilisateur)

    # ========== Tests pour ajouter_cocktail_teste ==========

    def test_ajouter_cocktail_teste_succes(self) -> None:
        """Teste l'ajout d'un cocktail testé avec succès."""
        # GIVEN
        id_utilisateur = 1
        nom_cocktail = "Margarita"
        reponse_attendue = {
            "success": True,
            "message": "Cocktail 'Margarita' ajouté aux cocktails testés",
        }

        dao_mock = MagicMock(spec=CocktailUtilisateurDao)
        dao_mock.ajouter_cocktail_teste.return_value = reponse_attendue

        # WHEN
        service = CocktailUtilisateurService()
        service.dao = dao_mock
        resultat = service.ajouter_cocktail_teste(id_utilisateur, nom_cocktail)

        # THEN
        assert resultat == reponse_attendue
        dao_mock.ajouter_cocktail_teste.assert_called_once_with(id_utilisateur, nom_cocktail)

    def test_ajouter_cocktail_teste_deja_present(self) -> None:
        """Teste l'ajout d'un cocktail déjà testé."""
        # GIVEN
        id_utilisateur = 1
        nom_cocktail = "Margarita"
        reponse_attendue = {
            "success": False,
            "message": "Cocktail 'Margarita' est déjà dans les cocktails testés",
        }

        dao_mock = MagicMock(spec=CocktailUtilisateurDao)
        dao_mock.ajouter_cocktail_teste.return_value = reponse_attendue

        # WHEN
        service = CocktailUtilisateurService()
        service.dao = dao_mock
        resultat = service.ajouter_cocktail_teste(id_utilisateur, nom_cocktail)

        # THEN
        assert resultat == reponse_attendue
        assert resultat["success"] is False

    def test_ajouter_cocktail_teste_cocktail_inexistant(self) -> None:
        """Teste l'ajout d'un cocktail inexistant.

        Raises
        ------
        Exception
            Quand le cocktail n'existe pas

        """
        # GIVEN
        id_utilisateur = 1
        nom_cocktail = "CocktailInconnu"

        dao_mock = MagicMock(spec=CocktailUtilisateurDao)
        dao_mock.ajouter_cocktail_teste.side_effect = Exception("Cocktail non trouvé")

        # WHEN
        service = CocktailUtilisateurService()
        service.dao = dao_mock

        # THEN
        with pytest.raises(Exception) as exc_info:
            service.ajouter_cocktail_teste(id_utilisateur, nom_cocktail)
        assert "Cocktail non trouvé" in str(exc_info.value)

    # ========== Tests pour retirer_cocktail_teste ==========

    def test_retirer_cocktail_teste_succes(self) -> None:
        """Teste le retrait d'un cocktail testé avec succès."""
        # GIVEN
        id_utilisateur = 1
        nom_cocktail = "Margarita"
        reponse_attendue = {
            "success": True,
            "message": "Cocktail 'Margarita' retiré des cocktails testés",
        }

        dao_mock = MagicMock(spec=CocktailUtilisateurDao)
        dao_mock.retirer_cocktail_teste.return_value = reponse_attendue

        # WHEN
        service = CocktailUtilisateurService()
        service.dao = dao_mock
        resultat = service.retirer_cocktail_teste(id_utilisateur, nom_cocktail)

        # THEN
        assert resultat == reponse_attendue
        dao_mock.retirer_cocktail_teste.assert_called_once_with(id_utilisateur, nom_cocktail)

    def test_retirer_cocktail_teste_non_present(self) -> None:
        """Teste le retrait d'un cocktail non testé."""
        # GIVEN
        id_utilisateur = 1
        nom_cocktail = "Margarita"
        reponse_attendue = {
            "success": False,
            "message": "Cocktail 'Margarita' n'est pas dans les cocktails testés",
        }

        dao_mock = MagicMock(spec=CocktailUtilisateurDao)
        dao_mock.retirer_cocktail_teste.return_value = reponse_attendue

        # WHEN
        service = CocktailUtilisateurService()
        service.dao = dao_mock
        resultat = service.retirer_cocktail_teste(id_utilisateur, nom_cocktail)

        # THEN
        assert resultat == reponse_attendue
        assert resultat["success"] is False

    def test_retirer_cocktail_teste_cocktail_inexistant(self) -> None:
        """Teste le retrait d'un cocktail inexistant.

        Raises
        ------
        Exception
            Quand le cocktail n'existe pas

        """
        # GIVEN
        id_utilisateur = 1
        nom_cocktail = "CocktailInconnu"

        dao_mock = MagicMock(spec=CocktailUtilisateurDao)
        dao_mock.retirer_cocktail_teste.side_effect = Exception("Cocktail non trouvé")

        # WHEN
        service = CocktailUtilisateurService()
        service.dao = dao_mock

        # THEN
        with pytest.raises(Exception) as exc_info:
            service.retirer_cocktail_teste(id_utilisateur, nom_cocktail)
        assert "Cocktail non trouvé" in str(exc_info.value)

    def test_retirer_cocktail_teste_utilisateur_sans_cocktails(self) -> None:
        """Teste le retrait d'un cocktail pour un utilisateur sans cocktails testés."""
        # GIVEN
        id_utilisateur = 999
        nom_cocktail = "Margarita"
        reponse_attendue = {
            "success": False,
            "message": "Aucun cocktail testé trouvé pour cet utilisateur",
        }

        dao_mock = MagicMock(spec=CocktailUtilisateurDao)
        dao_mock.retirer_cocktail_teste.return_value = reponse_attendue

        # WHEN
        service = CocktailUtilisateurService()
        service.dao = dao_mock
        resultat = service.retirer_cocktail_teste(id_utilisateur, nom_cocktail)

        # THEN
        assert resultat == reponse_attendue
        assert resultat["success"] is False
