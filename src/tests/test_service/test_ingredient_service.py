"""Tests pour IngredientService."""

from unittest.mock import MagicMock

import pytest

from src.dao.ingredient_dao import IngredientDAO
from src.service.ingredient_service import IngredientService
from src.utils.exceptions import IngredientNotFoundError


class TestIngredientService:
    """Tests pour IngredientService."""

    # ========== Tests pour check_if_alcoholic ==========
    @staticmethod
    def test_check_if_alcoholic_true() -> None:
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
        if resultat["ingredient_id"] != ingredient_id:
            raise AssertionError(
                message=f"ingredient_id devrait être {ingredient_id}, obtenu:"
                f"{resultat['ingredient_id']}",
            )
        if resultat["is_alcoholic"] is not True:
            raise AssertionError(
                message=f"is_alcoholic devrait être True, obtenu:"
                f"{resultat['is_alcoholic']}",
            )
        if "contient de l'alcool" not in resultat["message"]:
            raise AssertionError(
                message=f"'contient de l'alcool' devrait être dans le message:"
                f"{resultat['message']}",
            )
        dao_mock.is_alcoholic.assert_called_once_with(ingredient_id)

    @staticmethod
    def test_check_if_alcoholic_false() -> None:
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
        if resultat["ingredient_id"] != ingredient_id:
            raise AssertionError(
                message=f"ingredient_id devrait être {ingredient_id}, obtenu:"
                f"{resultat['ingredient_id']}",
            )
        if resultat["is_alcoholic"] is not False:
            raise AssertionError(
                message=f"is_alcoholic devrait être False, obtenu:"
                f"{resultat['is_alcoholic']}",
            )
        if "ne contient pas d'alcool" not in resultat["message"]:
            raise AssertionError(
                message=f"'ne contient pas d'alcool' devrait être dans le message:"
                f"{resultat['message']}",
            )
        dao_mock.is_alcoholic.assert_called_once_with(ingredient_id)

    @staticmethod
    def test_check_if_alcoholic_ingredient_inexistant() -> None:
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
        with pytest.raises(IngredientNotFoundError) as exc_info:
            service.check_if_alcoholic(ingredient_id)

        error_message = str(exc_info.value)
        if "introuvable" not in error_message:
            raise AssertionError(
                message=f"'introuvable' devrait être dans l'erreur: {error_message}",
            )
        if str(ingredient_id) not in error_message:
            raise AssertionError(
                message=f"'{ingredient_id}' devrait être dans l'erreur:{error_message}",
            )

    @staticmethod
    def test_check_if_alcoholic_id_negatif() -> None:
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
        with pytest.raises(IngredientNotFoundError):
            service.check_if_alcoholic(ingredient_id)

    # ========== Tests pour check_if_alcoholic_by_name ==========
    @staticmethod
    def test_check_if_alcoholic_by_name_true() -> None:
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
        if resultat["ingredient_name"] != ingredient_name:
            raise AssertionError(
                message=f"ingredient_name devrait être '{ingredient_name}', obtenu:"
                f"{resultat['ingredient_name']}",
            )
        if resultat["is_alcoholic"] is not True:
            raise AssertionError(
                message=f"is_alcoholic devrait être True, obtenu:"
                f"{resultat['is_alcoholic']}",
            )
        if "contient de l'alcool" not in resultat["message"]:
            raise AssertionError(
                message=f"'contient de l'alcool' devrait être dans le message:"
                f"{resultat['message']}",
            )
        dao_mock.is_alcoholic_by_name.assert_called_once_with(ingredient_name)

    @staticmethod
    def test_check_if_alcoholic_by_name_false() -> None:
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
        if resultat["ingredient_name"] != ingredient_name:
            raise AssertionError(
                message=f"ingredient_name devrait être '{ingredient_name}', obtenu:"
                f"{resultat['ingredient_name']}",
            )
        if resultat["is_alcoholic"] is not False:
            raise AssertionError(
                message=f"is_alcoholic devrait être False, obtenu:"
                f"{resultat['is_alcoholic']}",
            )
        if "ne contient pas d'alcool" not in resultat["message"]:
            raise AssertionError(
                message=f"'ne contient pas d'alcool' devrait être dans le message:"
                f"{resultat['message']}",
            )
        dao_mock.is_alcoholic_by_name.assert_called_once_with(ingredient_name)

    @staticmethod
    def test_check_if_alcoholic_by_name_ingredient_inexistant() -> None:
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
        with pytest.raises(IngredientNotFoundError) as exc_info:
            service.check_if_alcoholic_by_name(ingredient_name)

        error_message = str(exc_info.value)
        if "introuvable" not in error_message:
            raise AssertionError(
                message=f"'introuvable' devrait être dans l'erreur: {error_message}",
            )
        if ingredient_name not in error_message:
            raise AssertionError(
                message=f"'{ingredient_name}' devrait être dans l'erreur:"
                f"{error_message}",
            )

    @staticmethod
    def test_check_if_alcoholic_by_name_nom_vide() -> None:
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
        with pytest.raises(IngredientNotFoundError):
            service.check_if_alcoholic_by_name(ingredient_name)

    @staticmethod
    def test_check_if_alcoholic_by_name_casse_differente() -> None:
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
        if resultat["ingredient_name"] != ingredient_name:
            raise AssertionError(
                message=f"ingredient_name devrait être '{ingredient_name}', obtenu:"
                f"{resultat['ingredient_name']}",
            )
        if resultat["is_alcoholic"] is not True:
            raise AssertionError(
                message=f"is_alcoholic devrait être True, obtenu:"
                f"{resultat['is_alcoholic']}",
            )
        dao_mock.is_alcoholic_by_name.assert_called_once_with(ingredient_name)
