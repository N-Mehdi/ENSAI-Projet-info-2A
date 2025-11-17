"""Tests pour IngredientService."""

from unittest.mock import MagicMock

import pytest

from src.dao.ingredient_dao import IngredientDAO
from src.service.ingredient_service import IngredientService


class TestIngredientService:
    """Tests pour IngredientService."""

    # ========== Tests pour check_if_alcoholic ==========

    def test_check_if_alcoholic_true(self) -> None:
        """Teste la vérification d'un ingrédient alcoolisé par ID."""
        # GIVEN
        ingredient_id = 1

        dao_mock = MagicMock(spec=IngredientDAO)
        dao_mock.is_alcoholic.return_value = True

        # WHEN
        service = IngredientService()
        service.dao = dao_mock
        resultat = service.check_if_alcoholic(ingredient_id)

        # THEN
        assert resultat["ingredient_id"] == ingredient_id
        assert resultat["is_alcoholic"] is True
        assert "contient de l'alcool" in resultat["message"]
        dao_mock.is_alcoholic.assert_called_once_with(ingredient_id)

    def test_check_if_alcoholic_false(self) -> None:
        """Teste la vérification d'un ingrédient non alcoolisé par ID."""
        # GIVEN
        ingredient_id = 2

        dao_mock = MagicMock(spec=IngredientDAO)
        dao_mock.is_alcoholic.return_value = False

        # WHEN
        service = IngredientService()
        service.dao = dao_mock
        resultat = service.check_if_alcoholic(ingredient_id)

        # THEN
        assert resultat["ingredient_id"] == ingredient_id
        assert resultat["is_alcoholic"] is False
        assert "ne contient pas d'alcool" in resultat["message"]
        dao_mock.is_alcoholic.assert_called_once_with(ingredient_id)

    def test_check_if_alcoholic_ingredient_inexistant(self) -> None:
        """Teste la vérification d'un ingrédient inexistant par ID.

        Raises
        ------
        ValueError
            Quand l'ingrédient n'existe pas

        """
        # GIVEN
        ingredient_id = 999

        dao_mock = MagicMock(spec=IngredientDAO)
        dao_mock.is_alcoholic.return_value = None

        # WHEN
        service = IngredientService()
        service.dao = dao_mock

        # THEN
        with pytest.raises(ValueError) as exc_info:
            service.check_if_alcoholic(ingredient_id)
        assert "introuvable" in str(exc_info.value)
        assert str(ingredient_id) in str(exc_info.value)

    def test_check_if_alcoholic_id_negatif(self) -> None:
        """Teste la vérification avec un ID négatif.

        Raises
        ------
        ValueError
            Quand l'ID est négatif (ingrédient inexistant)

        """
        # GIVEN
        ingredient_id = -1

        dao_mock = MagicMock(spec=IngredientDAO)
        dao_mock.is_alcoholic.return_value = None

        # WHEN
        service = IngredientService()
        service.dao = dao_mock

        # THEN
        with pytest.raises(ValueError):
            service.check_if_alcoholic(ingredient_id)

    # ========== Tests pour check_if_alcoholic_by_name ==========

    def test_check_if_alcoholic_by_name_true(self) -> None:
        """Teste la vérification d'un ingrédient alcoolisé par nom."""
        # GIVEN
        ingredient_name = "Vodka"

        dao_mock = MagicMock(spec=IngredientDAO)
        dao_mock.is_alcoholic_by_name.return_value = True

        # WHEN
        service = IngredientService()
        service.dao = dao_mock
        resultat = service.check_if_alcoholic_by_name(ingredient_name)

        # THEN
        assert resultat["ingredient_name"] == ingredient_name
        assert resultat["is_alcoholic"] is True
        assert "contient de l'alcool" in resultat["message"]
        dao_mock.is_alcoholic_by_name.assert_called_once_with(ingredient_name)

    def test_check_if_alcoholic_by_name_false(self) -> None:
        """Teste la vérification d'un ingrédient non alcoolisé par nom."""
        # GIVEN
        ingredient_name = "Orange Juice"

        dao_mock = MagicMock(spec=IngredientDAO)
        dao_mock.is_alcoholic_by_name.return_value = False

        # WHEN
        service = IngredientService()
        service.dao = dao_mock
        resultat = service.check_if_alcoholic_by_name(ingredient_name)

        # THEN
        assert resultat["ingredient_name"] == ingredient_name
        assert resultat["is_alcoholic"] is False
        assert "ne contient pas d'alcool" in resultat["message"]
        dao_mock.is_alcoholic_by_name.assert_called_once_with(ingredient_name)

    def test_check_if_alcoholic_by_name_ingredient_inexistant(self) -> None:
        """Teste la vérification d'un ingrédient inexistant par nom.

        Raises
        ------
        ValueError
            Quand l'ingrédient n'existe pas

        """
        # GIVEN
        ingredient_name = "IngredientInconnu"

        dao_mock = MagicMock(spec=IngredientDAO)
        dao_mock.is_alcoholic_by_name.return_value = None

        # WHEN
        service = IngredientService()
        service.dao = dao_mock

        # THEN
        with pytest.raises(ValueError) as exc_info:
            service.check_if_alcoholic_by_name(ingredient_name)
        assert "introuvable" in str(exc_info.value)
        assert ingredient_name in str(exc_info.value)

    def test_check_if_alcoholic_by_name_nom_vide(self) -> None:
        """Teste la vérification avec un nom vide.

        Raises
        ------
        ValueError
            Quand le nom est vide (ingrédient inexistant)

        """
        # GIVEN
        ingredient_name = ""

        dao_mock = MagicMock(spec=IngredientDAO)
        dao_mock.is_alcoholic_by_name.return_value = None

        # WHEN
        service = IngredientService()
        service.dao = dao_mock

        # THEN
        with pytest.raises(ValueError):
            service.check_if_alcoholic_by_name(ingredient_name)

    def test_check_if_alcoholic_by_name_casse_differente(self) -> None:
        """Teste la vérification avec une casse différente."""
        # GIVEN
        ingredient_name = "vOdKa"

        dao_mock = MagicMock(spec=IngredientDAO)
        dao_mock.is_alcoholic_by_name.return_value = True

        # WHEN
        service = IngredientService()
        service.dao = dao_mock
        resultat = service.check_if_alcoholic_by_name(ingredient_name)

        # THEN
        assert resultat["ingredient_name"] == ingredient_name
        assert resultat["is_alcoholic"] is True
        dao_mock.is_alcoholic_by_name.assert_called_once_with(ingredient_name)
