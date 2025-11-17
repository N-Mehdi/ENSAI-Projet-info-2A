"""Classe de test de src/service/stock_course_service.py."""

from unittest.mock import MagicMock

import pytest

from src.dao.ingredient_dao import IngredientDAO
from src.dao.stock_course_dao import StockCourseDAO
from src.models.stock import Stock, StockItem
from src.service.stock_course_service import StockCourseService
from src.utils.exceptions import (
    IngredientNotFoundError,
    InsufficientQuantityError,
    InvalidQuantityError,
    ServiceError,
)


class TestStockCourseService:
    """Tests pour StockCourseService."""

    # ========== Tests pour _get_ingredient_by_name ==========

    def test_get_ingredient_by_name_succes(self):
        # GIVEN
        nom_ingredient = "vodka"
        ingredient_attendu = {
            "id_ingredient": 1,
            "nom": "Vodka",
        }

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        ingredient_dao_mock = MagicMock(spec=IngredientDAO)
        ingredient_dao_mock.get_by_name.return_value = ingredient_attendu

        # WHEN
        service = StockCourseService()
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock
        resultat = service._get_ingredient_by_name(nom_ingredient)

        # THEN
        assert resultat == ingredient_attendu
        ingredient_dao_mock.get_by_name.assert_called_once_with("Vodka")

    def test_get_ingredient_by_name_non_trouve_avec_suggestions(self):
        # GIVEN
        nom_ingredient = "vodkaa"
        suggestions_data = [
            {"nom": "Vodka"},
            {"nom": "Vodka Citron"},
        ]

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        ingredient_dao_mock = MagicMock(spec=IngredientDAO)
        ingredient_dao_mock.get_by_name.return_value = None
        ingredient_dao_mock.search_by_name.return_value = suggestions_data

        # WHEN
        service = StockCourseService()
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock

        # THEN
        with pytest.raises(IngredientNotFoundError) as exc_info:
            service._get_ingredient_by_name(nom_ingredient)

        assert exc_info.value.nom_ingredient == "Vodkaa"
        assert exc_info.value.suggestions == ["Vodka", "Vodka Citron"]

    # ========== Tests pour add_or_update_ingredient_by_name ==========

    def test_add_or_update_ingredient_by_name_succes(self):
        # GIVEN
        id_utilisateur = 1
        nom_ingredient = "vodka"
        quantite = 500.0
        id_unite = 1

        ingredient = {
            "id_ingredient": 1,
            "nom": "Vodka",
        }

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        stock_dao_mock.update_or_create_stock_item.return_value = True

        ingredient_dao_mock = MagicMock(spec=IngredientDAO)
        ingredient_dao_mock.get_by_name.return_value = ingredient

        # WHEN
        service = StockCourseService()
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock
        resultat = service.add_or_update_ingredient_by_name(
            id_utilisateur,
            nom_ingredient,
            quantite,
            id_unite,
        )

        # THEN
        assert "Vodka" in resultat
        assert "ajouté/mis à jour avec succès" in resultat
        stock_dao_mock.update_or_create_stock_item.assert_called_once_with(
            id_utilisateur=id_utilisateur,
            id_ingredient=1,
            quantite=quantite,
            id_unite=id_unite,
        )

    def test_add_or_update_ingredient_by_name_quantite_invalide(self):
        # GIVEN
        id_utilisateur = 1
        nom_ingredient = "vodka"
        quantite = -5.0
        id_unite = 1

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        ingredient_dao_mock = MagicMock(spec=IngredientDAO)

        # WHEN
        service = StockCourseService()
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock

        # THEN
        with pytest.raises(InvalidQuantityError):
            service.add_or_update_ingredient_by_name(
                id_utilisateur,
                nom_ingredient,
                quantite,
                id_unite,
            )

    def test_add_or_update_ingredient_by_name_quantite_zero(self):
        # GIVEN
        id_utilisateur = 1
        nom_ingredient = "vodka"
        quantite = 0.0
        id_unite = 1

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        ingredient_dao_mock = MagicMock(spec=IngredientDAO)

        # WHEN
        service = StockCourseService()
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock

        # THEN
        with pytest.raises(InvalidQuantityError):
            service.add_or_update_ingredient_by_name(
                id_utilisateur,
                nom_ingredient,
                quantite,
                id_unite,
            )

    def test_add_or_update_ingredient_by_name_ingredient_non_trouve(self):
        # GIVEN
        id_utilisateur = 1
        nom_ingredient = "ingredient_inexistant"
        quantite = 100.0
        id_unite = 1

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        ingredient_dao_mock = MagicMock(spec=IngredientDAO)
        ingredient_dao_mock.get_by_name.return_value = None
        ingredient_dao_mock.search_by_name.return_value = []

        # WHEN
        service = StockCourseService()
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock

        # THEN
        with pytest.raises(IngredientNotFoundError):
            service.add_or_update_ingredient_by_name(
                id_utilisateur,
                nom_ingredient,
                quantite,
                id_unite,
            )

    def test_add_or_update_ingredient_by_name_dao_echec(self):
        # GIVEN
        id_utilisateur = 1
        nom_ingredient = "vodka"
        quantite = 500.0
        id_unite = 1

        ingredient = {
            "id_ingredient": 1,
            "nom": "Vodka",
        }

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        stock_dao_mock.update_or_create_stock_item.return_value = False

        ingredient_dao_mock = MagicMock(spec=IngredientDAO)
        ingredient_dao_mock.get_by_name.return_value = ingredient

        # WHEN
        service = StockCourseService()
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock

        # THEN
        with pytest.raises(ServiceError) as exc_info:
            service.add_or_update_ingredient_by_name(
                id_utilisateur,
                nom_ingredient,
                quantite,
                id_unite,
            )
        assert "Impossible d'ajouter" in str(exc_info.value)

    # ========== Tests pour get_user_stock ==========

    def test_get_user_stock_succes(self):
        # GIVEN
        id_utilisateur = 1
        rows = [
            {
                "id_ingredient": 1,
                "nom_ingredient": "Vodka",
                "quantite": 500.0,
                "id_unite": 1,
                "code_unite": "ml",
                "nom_unite_complet": "millilitre",
            },
            {
                "id_ingredient": 2,
                "nom_ingredient": "Gin",
                "quantite": 700.0,
                "id_unite": 1,
                "code_unite": "ml",
                "nom_unite_complet": "millilitre",
            },
        ]

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        stock_dao_mock.get_stock.return_value = rows

        ingredient_dao_mock = MagicMock(spec=IngredientDAO)

        # WHEN
        service = StockCourseService()
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock
        resultat = service.get_user_stock(id_utilisateur)

        # THEN
        assert isinstance(resultat, Stock)
        assert resultat.id_utilisateur == id_utilisateur
        assert len(resultat.items) == 2
        assert resultat.items[0].nom_ingredient == "Vodka"
        assert resultat.items[0].quantite == 500.0
        stock_dao_mock.get_stock.assert_called_once_with(
            id_utilisateur=id_utilisateur,
            only_available=True,
        )

    def test_get_user_stock_vide(self):
        # GIVEN
        id_utilisateur = 1

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        stock_dao_mock.get_stock.return_value = []

        ingredient_dao_mock = MagicMock(spec=IngredientDAO)

        # WHEN
        service = StockCourseService()
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock
        resultat = service.get_user_stock(id_utilisateur)

        # THEN
        assert isinstance(resultat, Stock)
        assert resultat.id_utilisateur == id_utilisateur
        assert len(resultat.items) == 0

    def test_get_user_stock_only_available_false(self):
        # GIVEN
        id_utilisateur = 1
        rows = [
            {
                "id_ingredient": 1,
                "nom_ingredient": "Vodka",
                "quantite": 0.0,
                "id_unite": 1,
                "code_unite": "ml",
                "nom_unite_complet": "millilitre",
            },
        ]

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        stock_dao_mock.get_stock.return_value = rows

        ingredient_dao_mock = MagicMock(spec=IngredientDAO)

        # WHEN
        service = StockCourseService()
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock
        resultat = service.get_user_stock(id_utilisateur, only_available=False)

        # THEN
        assert len(resultat.items) == 1
        stock_dao_mock.get_stock.assert_called_once_with(
            id_utilisateur=id_utilisateur,
            only_available=False,
        )

    # ========== Tests pour get_ingredient_from_stock_by_name ==========

    def test_get_ingredient_from_stock_by_name_succes(self):
        # GIVEN
        id_utilisateur = 1
        nom_ingredient = "vodka"

        ingredient = {
            "id_ingredient": 1,
            "nom": "Vodka",
        }

        stock_item_data = {
            "id_ingredient": 1,
            "nom_ingredient": "Vodka",
            "quantite": 500.0,
            "id_unite": 1,
            "code_unite": "ml",
            "nom_unite_complet": "millilitre",
        }

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        stock_dao_mock.get_stock_item.return_value = stock_item_data

        ingredient_dao_mock = MagicMock(spec=IngredientDAO)
        ingredient_dao_mock.get_by_name.return_value = ingredient

        # WHEN
        service = StockCourseService()
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock
        resultat = service.get_ingredient_from_stock_by_name(id_utilisateur, nom_ingredient)

        # THEN
        assert isinstance(resultat, StockItem)
        assert resultat.nom_ingredient == "Vodka"
        assert resultat.quantite == 500.0

    def test_get_ingredient_from_stock_by_name_non_dans_stock(self):
        # GIVEN
        id_utilisateur = 1
        nom_ingredient = "vodka"

        ingredient = {
            "id_ingredient": 1,
            "nom": "Vodka",
        }

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        stock_dao_mock.get_stock_item.return_value = None

        ingredient_dao_mock = MagicMock(spec=IngredientDAO)
        ingredient_dao_mock.get_by_name.return_value = ingredient

        # WHEN
        service = StockCourseService()
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock
        resultat = service.get_ingredient_from_stock_by_name(id_utilisateur, nom_ingredient)

        # THEN
        assert resultat is None

    def test_get_ingredient_from_stock_by_name_ingredient_non_trouve(self):
        # GIVEN
        id_utilisateur = 1
        nom_ingredient = "ingredient_inexistant"

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        ingredient_dao_mock = MagicMock(spec=IngredientDAO)
        ingredient_dao_mock.get_by_name.return_value = None
        ingredient_dao_mock.search_by_name.return_value = []

        # WHEN
        service = StockCourseService()
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock

        # THEN
        with pytest.raises(IngredientNotFoundError):
            service.get_ingredient_from_stock_by_name(id_utilisateur, nom_ingredient)

    # ========== Tests pour remove_ingredient_by_name ==========

    def test_remove_ingredient_by_name_succes_partiel(self):
        # GIVEN
        id_utilisateur = 1
        nom_ingredient = "vodka"
        quantite = 100.0

        ingredient = {
            "id_ingredient": 1,
            "nom": "Vodka",
        }

        result = {
            "supprime": False,
            "nouvelle_quantite": 400.0,
        }

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        stock_dao_mock.decrement_stock_item.return_value = result

        ingredient_dao_mock = MagicMock(spec=IngredientDAO)
        ingredient_dao_mock.get_by_name.return_value = ingredient

        # WHEN
        service = StockCourseService()
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock
        resultat = service.remove_ingredient_by_name(id_utilisateur, nom_ingredient, quantite)

        # THEN
        assert "100.0 retiré(s)" in resultat
        assert "Nouvelle quantité : 400.0" in resultat

    def test_remove_ingredient_by_name_succes_complet(self):
        # GIVEN
        id_utilisateur = 1
        nom_ingredient = "vodka"
        quantite = 500.0

        ingredient = {
            "id_ingredient": 1,
            "nom": "Vodka",
        }

        result = {
            "supprime": True,
            "nouvelle_quantite": 0.0,
        }

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        stock_dao_mock.decrement_stock_item.return_value = result

        ingredient_dao_mock = MagicMock(spec=IngredientDAO)
        ingredient_dao_mock.get_by_name.return_value = ingredient

        # WHEN
        service = StockCourseService()
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock
        resultat = service.remove_ingredient_by_name(id_utilisateur, nom_ingredient, quantite)

        # THEN
        assert "retiré complètement du stock" in resultat

    def test_remove_ingredient_by_name_quantite_invalide(self):
        # GIVEN
        id_utilisateur = 1
        nom_ingredient = "vodka"
        quantite = -10.0

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        ingredient_dao_mock = MagicMock(spec=IngredientDAO)

        # WHEN
        service = StockCourseService()
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock

        # THEN
        with pytest.raises(InvalidQuantityError):
            service.remove_ingredient_by_name(id_utilisateur, nom_ingredient, quantite)

    def test_remove_ingredient_by_name_quantite_insuffisante(self):
        # GIVEN
        id_utilisateur = 1
        nom_ingredient = "vodka"
        quantite = 600.0

        ingredient = {
            "id_ingredient": 1,
            "nom": "Vodka",
        }

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        stock_dao_mock.decrement_stock_item.side_effect = ValueError(
            "Impossible de retirer 600.0 (quantité disponible : 500.0)",
        )

        ingredient_dao_mock = MagicMock(spec=IngredientDAO)
        ingredient_dao_mock.get_by_name.return_value = ingredient

        # WHEN
        service = StockCourseService()
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock

        # THEN
        with pytest.raises(InsufficientQuantityError) as exc_info:
            service.remove_ingredient_by_name(id_utilisateur, nom_ingredient, quantite)

        assert exc_info.value.quantite_demandee == 600.0
        assert exc_info.value.quantite_disponible == 500.0

    def test_remove_ingredient_by_name_non_dans_stock(self):
        # GIVEN
        id_utilisateur = 1
        nom_ingredient = "vodka"
        quantite = 100.0

        ingredient = {
            "id_ingredient": 1,
            "nom": "Vodka",
        }

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        stock_dao_mock.decrement_stock_item.side_effect = ValueError(
            "Ingrédient non trouvé dans le stock",
        )

        ingredient_dao_mock = MagicMock(spec=IngredientDAO)
        ingredient_dao_mock.get_by_name.return_value = ingredient

        # WHEN
        service = StockCourseService()
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock

        # THEN
        with pytest.raises(ServiceError) as exc_info:
            service.remove_ingredient_by_name(id_utilisateur, nom_ingredient, quantite)
        assert "n'est pas dans votre stock" in str(exc_info.value)

    # ========== Tests pour delete_ingredient_by_name ==========

    def test_delete_ingredient_by_name_succes(self):
        # GIVEN
        id_utilisateur = 1
        nom_ingredient = "vodka"

        ingredient = {
            "id_ingredient": 1,
            "nom": "Vodka",
        }

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        stock_dao_mock.delete_stock_item.return_value = True

        ingredient_dao_mock = MagicMock(spec=IngredientDAO)
        ingredient_dao_mock.get_by_name.return_value = ingredient

        # WHEN
        service = StockCourseService()
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock
        resultat = service.delete_ingredient_by_name(id_utilisateur, nom_ingredient)

        # THEN
        assert "supprimé complètement du stock" in resultat
        stock_dao_mock.delete_stock_item.assert_called_once_with(
            id_utilisateur=id_utilisateur,
            id_ingredient=1,
        )

    def test_delete_ingredient_by_name_non_dans_stock(self):
        # GIVEN
        id_utilisateur = 1
        nom_ingredient = "vodka"

        ingredient = {
            "id_ingredient": 1,
            "nom": "Vodka",
        }

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        stock_dao_mock.delete_stock_item.return_value = False

        ingredient_dao_mock = MagicMock(spec=IngredientDAO)
        ingredient_dao_mock.get_by_name.return_value = ingredient

        # WHEN
        service = StockCourseService()
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock

        # THEN
        with pytest.raises(ServiceError) as exc_info:
            service.delete_ingredient_by_name(id_utilisateur, nom_ingredient)
        assert "n'est pas dans votre stock" in str(exc_info.value)

    def test_delete_ingredient_by_name_ingredient_non_trouve(self):
        # GIVEN
        id_utilisateur = 1
        nom_ingredient = "ingredient_inexistant"

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        ingredient_dao_mock = MagicMock(spec=IngredientDAO)
        ingredient_dao_mock.get_by_name.return_value = None
        ingredient_dao_mock.search_by_name.return_value = []

        # WHEN
        service = StockCourseService()
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock

        # THEN
        with pytest.raises(IngredientNotFoundError):
            service.delete_ingredient_by_name(id_utilisateur, nom_ingredient)

    # ========== Tests pour get_full_stock_list ==========

    def test_get_full_stock_list_succes(self):
        # GIVEN
        id_utilisateur = 1
        full_stock = [
            {"id_ingredient": 1, "nom": "Vodka", "quantite": 500.0},
            {"id_ingredient": 2, "nom": "Gin", "quantite": 0.0},
        ]

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        stock_dao_mock.get_full_stock.return_value = full_stock

        ingredient_dao_mock = MagicMock(spec=IngredientDAO)

        # WHEN
        service = StockCourseService()
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock
        resultat = service.get_full_stock_list(id_utilisateur)

        # THEN
        assert resultat == full_stock
        assert len(resultat) == 2
        stock_dao_mock.get_full_stock.assert_called_once_with(id_utilisateur)

    def test_get_full_stock_list_erreur(self):
        # GIVEN
        id_utilisateur = 1

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        stock_dao_mock.get_full_stock.side_effect = Exception("Erreur DB")

        ingredient_dao_mock = MagicMock(spec=IngredientDAO)

        # WHEN
        service = StockCourseService()
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock

        # THEN
        with pytest.raises(ServiceError) as exc_info:
            service.get_full_stock_list(id_utilisateur)
        assert "stock complet" in str(exc_info.value)
