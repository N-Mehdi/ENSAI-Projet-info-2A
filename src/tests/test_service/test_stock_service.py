"""Tests pour StockService."""

from unittest.mock import MagicMock

import pytest

from src.service.stock_service import StockService
from src.utils.exceptions import (
    IngredientNotFoundError,
    InsufficientQuantityError,
    InvalidQuantityError,
    ServiceError,
    UniteNotFoundError,
)


@pytest.fixture
def mock_stock_dao(mocker) -> MagicMock:
    """Mock de StockDAO utilisé dans les tests."""
    return mocker.patch("src.service.stock_service.StockDAO").return_value


@pytest.fixture
def mock_ingredient_dao(mocker) -> MagicMock:
    """Mock de IngredientDAO utilisé dans les tests."""
    return mocker.patch("src.service.stock_service.IngredientDAO").return_value


# ruff: noqa: ARG001
@pytest.fixture
def service(mock_stock_dao, mock_ingredient_dao) -> StockService:
    """Instance de StockService avec des DAO mockés."""
    return StockService()


@pytest.fixture
def ingredient_sample() -> dict:
    """Dictionnaire représentant un ingrédient fictif."""
    return {"id_ingredient": 1, "nom": "citron"}


# -------------------------------------------------------------------------
# get_ingredient_by_name
# -------------------------------------------------------------------------


class TestGetIngredientByName:
    """Tests pour la méthode get_ingredient_by_name."""

    @staticmethod
    def test_success(service, mock_ingredient_dao, ingredient_sample) -> None:
        """Teste la récupération d'un ingrédient existant."""
        mock_ingredient_dao.get_by_name.return_value = ingredient_sample

        result = service.get_ingredient_by_name("Citron")

        if result != ingredient_sample:
            raise AssertionError(message=f"Résultat inattendu : {result}")

        mock_ingredient_dao.get_by_name.assert_called_once()

    @staticmethod
    def test_not_found_with_suggestions(service, mock_ingredient_dao) -> None:
        """Teste le cas où l'ingrédient n'existe pas mais des suggestions sont
        trouvées.
        """
        mock_ingredient_dao.get_by_name.return_value = None
        mock_ingredient_dao.search_by_name.return_value = [
            {"nom": "citron vert"},
            {"nom": "citron jaune"},
        ]

        with pytest.raises(IngredientNotFoundError) as exc:
            service.get_ingredient_by_name("citro")

        if (
            "citro" not in str(exc.value).lower()
            and "ingrédient" not in str(exc.value).lower()
        ):
            raise AssertionError(
                message=f"Message incorrect : {exc.value}",
            )


# -------------------------------------------------------------------------
# add_or_update_ingredient_by_name
# -------------------------------------------------------------------------


class TestAddOrUpdateIngredient:
    """Tests pour add_or_update_ingredient_by_name."""

    @staticmethod
    def test_invalid_quantity(service) -> None:
        """Teste l'erreur si la quantité est invalide."""
        with pytest.raises(InvalidQuantityError):
            service.add_or_update_ingredient_by_name(1, "citron", 0, "g")

    @staticmethod
    def test_unite_not_found(
        service,
        mock_ingredient_dao,
        mock_stock_dao,
        ingredient_sample,
    ) -> None:
        """Teste l'erreur lorsque l'unité est introuvable."""
        mock_ingredient_dao.get_by_name.return_value = ingredient_sample
        mock_stock_dao.get_unite_id_by_abbreviation.return_value = None

        with pytest.raises(UniteNotFoundError):
            service.add_or_update_ingredient_by_name(1, "citron", 10, "xxx")

    @staticmethod
    def test_success(
        service,
        mock_ingredient_dao,
        mock_stock_dao,
        ingredient_sample,
    ) -> None:
        """Teste l'ajout ou mise à jour d'un ingrédient avec succès."""
        mock_ingredient_dao.get_by_name.return_value = ingredient_sample
        mock_stock_dao.get_unite_id_by_abbreviation.return_value = 3
        mock_stock_dao.update_or_create_stock_item.return_value = True

        msg = service.add_or_update_ingredient_by_name(1, "Citron", 5, "g")

        if "ajouté/mis à jour" not in msg:
            raise AssertionError(message=f"Message inattendu : {msg}")

        mock_stock_dao.update_or_create_stock_item.assert_called_once()

    @staticmethod
    def test_update_fail(
        service,
        mock_ingredient_dao,
        mock_stock_dao,
        ingredient_sample,
    ) -> None:
        """Teste l'erreur en cas d'échec de mise à jour du stock."""
        mock_ingredient_dao.get_by_name.return_value = ingredient_sample
        mock_stock_dao.get_unite_id_by_abbreviation.return_value = 3
        mock_stock_dao.update_or_create_stock_item.return_value = False

        with pytest.raises(ServiceError):
            service.add_or_update_ingredient_by_name(1, "Citron", 5, "g")


# -------------------------------------------------------------------------
# get_user_stock
# -------------------------------------------------------------------------


class TestGetUserStock:
    """Tests pour get_user_stock."""

    @staticmethod
    def test_success(service, mock_stock_dao) -> None:
        """Teste la récupération du stock utilisateur."""
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

        if stock.id_utilisateur != 1:
            raise AssertionError(
                message=f"id_utilisateur incorrect: {stock.id_utilisateur}",
            )

        if len(stock.items) != 1:
            raise AssertionError(
                message=f"Nombre d'items incorrect : {len(stock.items)}",
            )

        if stock.items[0].nom_ingredient != "citron":
            raise AssertionError(
                message=f"Ingrédient incorrect: {stock.items[0].nom_ingredient}",
            )

    @staticmethod
    def test_failure(service, mock_stock_dao) -> None:
        """Teste l'erreur si la DAO échoue."""
        mock_stock_dao.get_stock.side_effect = Exception("DB error")

        with pytest.raises(ServiceError):
            service.get_user_stock(1)


# -------------------------------------------------------------------------
# get_ingredient_from_stock_by_name
# -------------------------------------------------------------------------


class TestGetIngredientFromStockByName:
    """Tests pour get_ingredient_from_stock_by_name."""

    @staticmethod
    def test_success(
        service,
        mock_stock_dao,
        mock_ingredient_dao,
        ingredient_sample,
    ) -> None:
        """Teste la récupération d'un ingrédient présent dans le stock."""
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

        if item.nom_ingredient != "citron":
            raise AssertionError(message=f"Nom incorrect : {item.nom_ingredient}")
        qte = 2
        if item.quantite != qte:
            raise AssertionError(message=f"Quantité incorrecte : {item.quantite}")

    @staticmethod
    def test_not_in_stock(
        service,
        mock_stock_dao,
        mock_ingredient_dao,
        ingredient_sample,
    ) -> None:
        """Teste le cas où l'ingrédient n'est pas dans le stock."""
        mock_ingredient_dao.get_by_name.return_value = ingredient_sample
        mock_stock_dao.get_stock_item.return_value = None

        result = service.get_ingredient_from_stock_by_name(1, "citron")

        if result is not None:
            raise AssertionError(message=f"Résultat attendu None, obtenu : {result}")

    @staticmethod
    def test_exception(
        service,
        mock_stock_dao,
        mock_ingredient_dao,
        ingredient_sample,
    ) -> None:
        """Teste l'erreur en cas d'exception DAO."""
        mock_ingredient_dao.get_by_name.return_value = ingredient_sample
        mock_stock_dao.get_stock_item.side_effect = Exception("DB error")

        with pytest.raises(ServiceError):
            service.get_ingredient_from_stock_by_name(1, "citron")


# -------------------------------------------------------------------------
# remove_ingredient_by_name
# -------------------------------------------------------------------------


class TestRemoveIngredient:
    """Tests pour remove_ingredient_by_name."""

    @staticmethod
    def test_invalid_quantity(service) -> None:
        """Teste l'erreur si la quantité à retirer est invalide."""
        with pytest.raises(InvalidQuantityError):
            service.remove_ingredient_by_name(1, "citron", 0)

    @staticmethod
    def test_insufficient_quantity(
        service,
        mock_stock_dao,
        mock_ingredient_dao,
        ingredient_sample,
    ) -> None:
        """Teste l'erreur si la quantité à retirer dépasse le stock disponible."""
        mock_ingredient_dao.get_by_name.return_value = ingredient_sample

        mock_stock_dao.decrement_stock_item.side_effect = ValueError(
            "Impossible de retirer 10 (quantité disponible : 2)",
        )

        with pytest.raises(InsufficientQuantityError):
            service.remove_ingredient_by_name(1, "citron", 10)

    @staticmethod
    def test_not_in_stock(
        service,
        mock_stock_dao,
        mock_ingredient_dao,
        ingredient_sample,
    ) -> None:
        """Teste l'erreur si l'ingrédient n'est pas dans le stock."""
        mock_ingredient_dao.get_by_name.return_value = ingredient_sample

        mock_stock_dao.decrement_stock_item.side_effect = ValueError(
            "Ingrédient non trouvé dans le stock",
        )

        with pytest.raises(ServiceError):
            service.remove_ingredient_by_name(1, "citron", 1)

    @staticmethod
    def test_success_partial(
        service,
        mock_stock_dao,
        mock_ingredient_dao,
        ingredient_sample,
    ) -> None:
        """Teste un retrait partiel d'un ingrédient."""
        mock_ingredient_dao.get_by_name.return_value = ingredient_sample

        mock_stock_dao.decrement_stock_item.return_value = {
            "supprime": False,
            "nouvelle_quantite": 3,
        }

        msg = service.remove_ingredient_by_name(1, "citron", 1)

        if "Nouvelle quantité" not in msg:
            raise AssertionError(message=f"Message incorrect : {msg}")

    @staticmethod
    def test_success_total(
        service,
        mock_stock_dao,
        mock_ingredient_dao,
        ingredient_sample,
    ) -> None:
        """Teste le retrait complet d'un ingrédient du stock."""
        mock_ingredient_dao.get_by_name.return_value = ingredient_sample

        mock_stock_dao.decrement_stock_item.return_value = {
            "supprime": True,
        }

        msg = service.remove_ingredient_by_name(1, "citron", 1)

        if "retiré complètement" not in msg:
            raise AssertionError(message=f"Message incorrect : {msg}")


# -------------------------------------------------------------------------
# delete_ingredient_by_name
# -------------------------------------------------------------------------


class TestDeleteIngredientByName:
    """Tests pour delete_ingredient_by_name."""

    @staticmethod
    def test_not_found(
        service,
        mock_stock_dao,
        mock_ingredient_dao,
        ingredient_sample,
    ) -> None:
        """Teste l'erreur si la suppression échoue."""
        mock_ingredient_dao.get_by_name.return_value = ingredient_sample
        mock_stock_dao.delete_stock_item.return_value = False

        with pytest.raises(ServiceError):
            service.delete_ingredient_by_name(1, "citron")

    @staticmethod
    def test_success(
        service,
        mock_stock_dao,
        mock_ingredient_dao,
        ingredient_sample,
    ) -> None:
        """Teste la suppression complète d'un ingrédient."""
        mock_ingredient_dao.get_by_name.return_value = ingredient_sample
        mock_stock_dao.delete_stock_item.return_value = True

        msg = service.delete_ingredient_by_name(1, "citron")

        if "supprimé complètement" not in msg:
            raise AssertionError(message=f"Message incorrect : {msg}")


# -------------------------------------------------------------------------
# get_full_stock_list
# -------------------------------------------------------------------------


class TestGetFullStockList:
    """Tests pour get_full_stock_list."""

    @staticmethod
    def test_success(service, mock_stock_dao) -> None:
        """Teste la récupération complète du stock."""
        mock_stock_dao.get_full_stock.return_value = [
            {"id_ingredient": 1, "quantite": 0},
        ]

        result = service.get_full_stock_list(1)

        if len(result) != 1:
            raise AssertionError(message=f"Longueur incorrecte : {len(result)}")

    @staticmethod
    def test_failure(service, mock_stock_dao) -> None:
        """Teste l'erreur en cas d'échec DAO."""
        mock_stock_dao.get_full_stock.side_effect = Exception("DB fail")

        with pytest.raises(ServiceError):
            service.get_full_stock_list(1)
