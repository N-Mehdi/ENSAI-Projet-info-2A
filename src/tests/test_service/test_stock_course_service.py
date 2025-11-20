"""doc."""

import pytest

from src.service.stock_course_service import StockCourseService
from src.utils.exceptions import (
    IngredientNotFoundError,
    InsufficientQuantityError,
    InvalidQuantityError,
    ServiceError,
    UniteNotFoundError,
)

# -------------------------------------------------------------------------
# FIXTURES
# -------------------------------------------------------------------------


@pytest.fixture
def mock_stock_dao(mocker):
    return mocker.patch("src.service.stock_course_service.StockCourseDAO").return_value


@pytest.fixture
def mock_ingredient_dao(mocker):
    return mocker.patch("src.service.stock_course_service.IngredientDAO").return_value


@pytest.fixture
def service(mock_stock_dao, mock_ingredient_dao):
    return StockCourseService()


@pytest.fixture
def ingredient_sample():
    return {"id_ingredient": 1, "nom": "citron"}


# -------------------------------------------------------------------------
# get_ingredient_by_name
# -------------------------------------------------------------------------


class TestGetIngredientByName:
    def test_success(self, service, mock_ingredient_dao, ingredient_sample):
        mock_ingredient_dao.get_by_name.return_value = ingredient_sample

        result = service.get_ingredient_by_name("Citron")

        assert result == ingredient_sample
        mock_ingredient_dao.get_by_name.assert_called_once()

    def test_not_found_with_suggestions(self, service, mock_ingredient_dao):
        mock_ingredient_dao.get_by_name.return_value = None
        mock_ingredient_dao.search_by_name.return_value = [
            {"nom": "citron vert"},
            {"nom": "citron jaune"},
        ]

        with pytest.raises(IngredientNotFoundError) as exc:
            service.get_ingredient_by_name("citro")

        # Vérifier simplement que l'exception est levée avec un message approprié
        assert "citro" in str(exc.value).lower() or "Ingrédient" in str(exc.value)


# -------------------------------------------------------------------------
# add_or_update_ingredient_by_name
# -------------------------------------------------------------------------


class TestAddOrUpdateIngredient:
    def test_invalid_quantity(self, service):
        with pytest.raises(InvalidQuantityError):
            service.add_or_update_ingredient_by_name(1, "citron", 0, "g")

    def test_unite_not_found(
        self,
        service,
        mock_ingredient_dao,
        mock_stock_dao,
        ingredient_sample,
    ):
        mock_ingredient_dao.get_by_name.return_value = ingredient_sample
        mock_stock_dao.get_unite_id_by_abbreviation.return_value = None

        with pytest.raises(UniteNotFoundError):
            service.add_or_update_ingredient_by_name(1, "citron", 10, "xxx")

    def test_success(
        self,
        service,
        mock_ingredient_dao,
        mock_stock_dao,
        ingredient_sample,
    ):
        mock_ingredient_dao.get_by_name.return_value = ingredient_sample
        mock_stock_dao.get_unite_id_by_abbreviation.return_value = 3
        mock_stock_dao.update_or_create_stock_item.return_value = True

        msg = service.add_or_update_ingredient_by_name(1, "Citron", 5, "g")

        assert "ajouté/mis à jour" in msg
        mock_stock_dao.update_or_create_stock_item.assert_called_once()

    def test_update_fail(
        self,
        service,
        mock_ingredient_dao,
        mock_stock_dao,
        ingredient_sample,
    ):
        mock_ingredient_dao.get_by_name.return_value = ingredient_sample
        mock_stock_dao.get_unite_id_by_abbreviation.return_value = 3
        mock_stock_dao.update_or_create_stock_item.return_value = False

        with pytest.raises(ServiceError):
            service.add_or_update_ingredient_by_name(1, "Citron", 5, "g")


# -------------------------------------------------------------------------
# get_user_stock
# -------------------------------------------------------------------------


class TestGetUserStock:
    def test_success(self, service, mock_stock_dao):
        mock_stock_dao.get_stock.return_value = [
            {
                "id_ingredient": 1,
                "nom_ingredient": "citron",
                "quantite": 5,
                "id_unite": 2,
                "code_unite": "g",
                "nom_unite_complet": "grammes",
            },
        ]

        stock = service.get_user_stock(1)

        assert stock.id_utilisateur == 1
        assert len(stock.items) == 1
        assert stock.items[0].nom_ingredient == "citron"

    def test_failure(self, service, mock_stock_dao):
        mock_stock_dao.get_stock.side_effect = Exception("DB error")

        with pytest.raises(ServiceError):
            service.get_user_stock(1)


# -------------------------------------------------------------------------
# get_ingredient_from_stock_by_name
# -------------------------------------------------------------------------


class TestGetIngredientFromStockByName:
    def test_success(
        self,
        service,
        mock_stock_dao,
        mock_ingredient_dao,
        ingredient_sample,
    ):
        mock_ingredient_dao.get_by_name.return_value = ingredient_sample

        mock_stock_dao.get_stock_item.return_value = {
            "id_ingredient": 1,
            "nom_ingredient": "citron",
            "quantite": 2,
            "id_unite": 2,
            "code_unite": "g",
            "nom_unite_complet": "grammes",
        }

        item = service.get_ingredient_from_stock_by_name(1, "citron")

        assert item.nom_ingredient == "citron"
        assert item.quantite == 2

    def test_not_in_stock(
        self,
        service,
        mock_stock_dao,
        mock_ingredient_dao,
        ingredient_sample,
    ):
        mock_ingredient_dao.get_by_name.return_value = ingredient_sample
        mock_stock_dao.get_stock_item.return_value = None

        result = service.get_ingredient_from_stock_by_name(1, "citron")

        assert result is None

    def test_exception(
        self,
        service,
        mock_stock_dao,
        mock_ingredient_dao,
        ingredient_sample,
    ):
        mock_ingredient_dao.get_by_name.return_value = ingredient_sample
        mock_stock_dao.get_stock_item.side_effect = Exception("DB error")

        with pytest.raises(ServiceError):
            service.get_ingredient_from_stock_by_name(1, "citron")


# -------------------------------------------------------------------------
# remove_ingredient_by_name
# -------------------------------------------------------------------------


class TestRemoveIngredient:
    def test_invalid_quantity(self, service):
        with pytest.raises(InvalidQuantityError):
            service.remove_ingredient_by_name(1, "citron", 0)

    def test_insufficient_quantity(
        self,
        service,
        mock_stock_dao,
        mock_ingredient_dao,
        ingredient_sample,
    ):
        mock_ingredient_dao.get_by_name.return_value = ingredient_sample

        mock_stock_dao.decrement_stock_item.side_effect = ValueError(
            "Impossible de retirer 10 (quantité disponible : 2)",
        )

        with pytest.raises(InsufficientQuantityError):
            service.remove_ingredient_by_name(1, "citron", 10)

    def test_not_in_stock(
        self,
        service,
        mock_stock_dao,
        mock_ingredient_dao,
        ingredient_sample,
    ):
        mock_ingredient_dao.get_by_name.return_value = ingredient_sample

        mock_stock_dao.decrement_stock_item.side_effect = ValueError(
            "Ingrédient non trouvé dans le stock",
        )

        with pytest.raises(ServiceError):
            service.remove_ingredient_by_name(1, "citron", 1)

    def test_success_partial(
        self,
        service,
        mock_stock_dao,
        mock_ingredient_dao,
        ingredient_sample,
    ):
        mock_ingredient_dao.get_by_name.return_value = ingredient_sample

        mock_stock_dao.decrement_stock_item.return_value = {
            "supprime": False,
            "nouvelle_quantite": 3,
        }

        msg = service.remove_ingredient_by_name(1, "citron", 1)

        assert "Nouvelle quantité" in msg

    def test_success_total(
        self,
        service,
        mock_stock_dao,
        mock_ingredient_dao,
        ingredient_sample,
    ):
        mock_ingredient_dao.get_by_name.return_value = ingredient_sample

        mock_stock_dao.decrement_stock_item.return_value = {
            "supprime": True,
        }

        msg = service.remove_ingredient_by_name(1, "citron", 1)

        assert "retiré complètement" in msg


# -------------------------------------------------------------------------
# delete_ingredient_by_name
# -------------------------------------------------------------------------


class TestDeleteIngredientByName:
    def test_not_found(
        self,
        service,
        mock_stock_dao,
        mock_ingredient_dao,
        ingredient_sample,
    ):
        mock_ingredient_dao.get_by_name.return_value = ingredient_sample
        mock_stock_dao.delete_stock_item.return_value = False

        with pytest.raises(ServiceError):
            service.delete_ingredient_by_name(1, "citron")

    def test_success(
        self,
        service,
        mock_stock_dao,
        mock_ingredient_dao,
        ingredient_sample,
    ):
        mock_ingredient_dao.get_by_name.return_value = ingredient_sample
        mock_stock_dao.delete_stock_item.return_value = True

        msg = service.delete_ingredient_by_name(1, "citron")

        assert "supprimé complètement" in msg


# -------------------------------------------------------------------------
# get_full_stock_list
# -------------------------------------------------------------------------


class TestGetFullStockList:
    def test_success(self, service, mock_stock_dao):
        mock_stock_dao.get_full_stock.return_value = [
            {"id_ingredient": 1, "quantite": 0},
        ]

        result = service.get_full_stock_list(1)

        assert len(result) == 1

    def test_failure(self, service, mock_stock_dao):
        mock_stock_dao.get_full_stock.side_effect = Exception("DB fail")

        with pytest.raises(ServiceError):
            service.get_full_stock_list(1)
