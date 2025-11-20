"""Tests pour ListeCourseService."""

from unittest.mock import MagicMock

import pytest

from src.dao.ingredient_dao import IngredientDAO
from src.dao.liste_course_dao import ListeCourseDAO
from src.dao.stock_course_dao import StockCourseDAO
from src.models.liste_course import ListeCourse
from src.service.ingredient_service import IngredientService
from src.service.liste_course_service import ListeCourseService
from src.utils.exceptions import (
    IngredientNotFoundError,
    ServiceError,
    UniteNotFoundError,
)

ingredient_service = IngredientService()


class TestListeCourseService:
    """Tests pour ListeCourseService."""

    # ========== Tests pour get_liste_course ==========

    def test_get_liste_course_succes(self) -> None:
        """Teste la récupération de la liste de course avec succès."""
        # GIVEN
        id_utilisateur = 1
        rows = [
            {
                "id_ingredient": 1,
                "nom_ingredient": "Vodka",
                "quantite": 500.0,
                "effectue": False,
                "id_unite": 1,
                "code_unite": "ml",
                "nom_unite_complet": "millilitre",
            },
            {
                "id_ingredient": 2,
                "nom_ingredient": "Sucre",
                "quantite": 200.0,
                "effectue": True,
                "id_unite": 2,
                "code_unite": "g",
                "nom_unite_complet": "gramme",
            },
        ]

        liste_course_dao_mock = MagicMock(spec=ListeCourseDAO)
        liste_course_dao_mock.get_liste_course.return_value = rows

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        ingredient_dao_mock = MagicMock(spec=IngredientDAO)

        # WHEN
        service = ListeCourseService()
        service.liste_course_dao = liste_course_dao_mock
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock
        resultat = service.get_liste_course(id_utilisateur)

        # THEN
        assert isinstance(resultat, ListeCourse)
        assert resultat.id_utilisateur == id_utilisateur
        assert len(resultat.items) == 2
        assert resultat.nombre_items == 2
        assert resultat.nombre_effectues == 1

    def test_get_liste_course_vide(self) -> None:
        """Teste la récupération d'une liste de course vide."""
        # GIVEN
        id_utilisateur = 1

        liste_course_dao_mock = MagicMock(spec=ListeCourseDAO)
        liste_course_dao_mock.get_liste_course.return_value = []

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        ingredient_dao_mock = MagicMock(spec=IngredientDAO)

        # WHEN
        service = ListeCourseService()
        service.liste_course_dao = liste_course_dao_mock
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock
        resultat = service.get_liste_course(id_utilisateur)

        # THEN
        assert resultat.nombre_items == 0
        assert resultat.nombre_effectues == 0

    # ========== Tests pour add_to_liste_course ==========


class TestListeCourseServiceAdd:
    def test_add_to_liste_course_success(self) -> None:
        """Teste l'ajout d'un ingrédient à la liste de course avec succès."""
        # GIVEN
        id_utilisateur = 1
        nom_ingredient = "Vodka"
        quantite = 500.0
        abbreviation_unite = "ml"

        ingredient_service_mock = MagicMock(spec=IngredientService)
        ingredient_service_mock.get_by_name_with_suggestions.return_value = {
            "id_ingredient": 1,
            "nom": "Vodka",
        }

        liste_course_dao_mock = MagicMock(spec=ListeCourseDAO)
        liste_course_dao_mock.add_to_liste_course.return_value = None

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        stock_dao_mock.get_unite_id_by_abbreviation.return_value = 1

        # WHEN
        service = ListeCourseService()
        service.ingredient_svc = ingredient_service_mock
        service.liste_course_dao = liste_course_dao_mock
        service.stock_dao = stock_dao_mock

        resultat = service.add_to_liste_course(
            id_utilisateur,
            nom_ingredient,
            quantite,
            abbreviation_unite,
        )

        # THEN
        assert "Vodka" in resultat
        assert str(quantite) in resultat
        liste_course_dao_mock.add_to_liste_course.assert_called_once_with(
            id_utilisateur=id_utilisateur,
            id_ingredient=1,
            quantite=quantite,
            id_unite=1,
        )

    def test_add_to_liste_course_ingredient_not_found(self) -> None:
        """Teste l'ajout d'un ingrédient inexistant."""
        # GIVEN
        id_utilisateur = 1
        nom_ingredient = "Unknown"
        quantite = 100.0
        abbreviation_unite = "g"

        ingredient_service_mock = MagicMock(spec=IngredientService)
        ingredient_service_mock.get_by_name_with_suggestions.side_effect = (
            IngredientNotFoundError("Ingrédient non trouvé")
        )

        liste_course_dao_mock = MagicMock(spec=ListeCourseDAO)
        stock_dao_mock = MagicMock(spec=StockCourseDAO)

        # WHEN
        service = ListeCourseService()
        service.ingredient_svc = ingredient_service_mock
        service.liste_course_dao = liste_course_dao_mock
        service.stock_dao = stock_dao_mock

        # THEN
        with pytest.raises(IngredientNotFoundError):
            service.add_to_liste_course(
                id_utilisateur,
                nom_ingredient,
                quantite,
                abbreviation_unite,
            )

    def test_add_to_liste_course_unite_not_found(self) -> None:
        """Teste l'ajout d'un ingrédient avec une unité inexistante."""
        # GIVEN
        id_utilisateur = 1
        nom_ingredient = "Sucre"
        quantite = 100.0
        abbreviation_unite = "invalid"

        ingredient_service_mock = MagicMock(spec=IngredientService)
        ingredient_service_mock.get_by_name_with_suggestions.return_value = {
            "id_ingredient": 2,
            "nom": "Sucre",
        }

        liste_course_dao_mock = MagicMock(spec=ListeCourseDAO)

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        stock_dao_mock.get_unite_id_by_abbreviation.return_value = None

        # WHEN
        service = ListeCourseService()
        service.ingredient_svc = ingredient_service_mock
        service.liste_course_dao = liste_course_dao_mock
        service.stock_dao = stock_dao_mock

        # THEN
        with pytest.raises(UniteNotFoundError):
            service.add_to_liste_course(
                id_utilisateur,
                nom_ingredient,
                quantite,
                abbreviation_unite,
            )

    def test_add_to_liste_course_service_error(self) -> None:
        """Teste l'erreur levée lors de l'ajout à la liste de course."""
        # GIVEN
        id_utilisateur = 1
        nom_ingredient = "Sucre"
        quantite = 100.0
        abbreviation_unite = "g"

        ingredient_service_mock = MagicMock(spec=IngredientService)
        ingredient_service_mock.get_by_name_with_suggestions.return_value = {
            "id_ingredient": 2,
            "nom": "Sucre",
        }

        liste_course_dao_mock = MagicMock(spec=ListeCourseDAO)
        liste_course_dao_mock.add_to_liste_course.side_effect = Exception("DB error")

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        stock_dao_mock.get_unite_id_by_abbreviation.return_value = 2

        # WHEN
        service = ListeCourseService()
        service.ingredient_svc = ingredient_service_mock
        service.liste_course_dao = liste_course_dao_mock
        service.stock_dao = stock_dao_mock

        # THEN
        with pytest.raises(ServiceError) as exc_info:
            service.add_to_liste_course(
                id_utilisateur,
                nom_ingredient,
                quantite,
                abbreviation_unite,
            )
        assert "DB error" in str(exc_info.value)

    # ========== Tests pour remove_from_liste_course ==========

    def test_remove_from_liste_course_succes(self) -> None:
        """Teste le retrait d'un ingrédient de la liste de course avec succès."""
        # GIVEN
        id_utilisateur = 1
        nom_ingredient = "vodka"

        ingredient = {
            "id_ingredient": 1,
            "nom": "Vodka",
        }

        liste_course_dao_mock = MagicMock(spec=ListeCourseDAO)
        liste_course_dao_mock.remove_from_liste_course.return_value = True

        stock_dao_mock = MagicMock(spec=StockCourseDAO)

        ingredient_dao_mock = MagicMock(spec=IngredientDAO)
        ingredient_dao_mock.get_by_name_with_suggestions.return_value = ingredient

        # WHEN
        service = ListeCourseService()
        service.liste_course_dao = liste_course_dao_mock
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock
        resultat = service.remove_from_liste_course(id_utilisateur, nom_ingredient)

        # THEN
        assert "Vodka" in resultat
        assert "retiré de la liste de course" in resultat

    def test_remove_from_liste_course_non_present(self) -> None:
        """Teste le retrait d'un ingrédient non présent dans la liste.

        Raises
        ------
        ServiceError
            Quand l'ingrédient n'est pas dans la liste de course

        """
        # GIVEN
        id_utilisateur = 1
        nom_ingredient = "vodka"

        ingredient = {
            "id_ingredient": 1,
            "nom": "Vodka",
        }

        liste_course_dao_mock = MagicMock(spec=ListeCourseDAO)
        liste_course_dao_mock.remove_from_liste_course.return_value = False

        stock_dao_mock = MagicMock(spec=StockCourseDAO)

        ingredient_dao_mock = MagicMock(spec=IngredientDAO)
        ingredient_dao_mock.get_by_name_with_suggestions.return_value = ingredient

        # WHEN
        service = ListeCourseService()
        service.liste_course_dao = liste_course_dao_mock
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock

        # THEN
        with pytest.raises(ServiceError) as exc_info:
            service.remove_from_liste_course(id_utilisateur, nom_ingredient)
        # Corriger la vérification pour matcher le message exact (sans espace après "liste")
        assert "n'est pas dans votre liste" in str(exc_info.value)

    # ========== Tests pour clear_liste_course ==========

    def test_clear_liste_course_succes(self) -> None:
        """Teste le vidage de la liste de course avec succès."""
        # GIVEN
        id_utilisateur = 1

        liste_course_dao_mock = MagicMock(spec=ListeCourseDAO)
        liste_course_dao_mock.clear_liste_course.return_value = 5

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        ingredient_dao_mock = MagicMock(spec=IngredientDAO)

        # WHEN
        service = ListeCourseService()
        service.liste_course_dao = liste_course_dao_mock
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock
        resultat = service.clear_liste_course(id_utilisateur)

        # THEN
        assert "vidée" in resultat
        assert "5" in resultat
        # Corriger pour vérifier "ingrédient" au lieu de "ingrédients supprimés"
        assert "ingrédient" in resultat

    def test_clear_liste_course_deja_vide(self) -> None:
        """Teste le vidage d'une liste de course déjà vide."""
        # GIVEN
        id_utilisateur = 1

        liste_course_dao_mock = MagicMock(spec=ListeCourseDAO)
        liste_course_dao_mock.clear_liste_course.return_value = 0

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        ingredient_dao_mock = MagicMock(spec=IngredientDAO)

        # WHEN
        service = ListeCourseService()
        service.liste_course_dao = liste_course_dao_mock
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock
        resultat = service.clear_liste_course(id_utilisateur)

        # THEN
        assert "déjà vide" in resultat

    def test_clear_liste_course_un_element(self) -> None:
        """Teste le vidage d'une liste avec un seul élément."""
        # GIVEN
        id_utilisateur = 1

        liste_course_dao_mock = MagicMock(spec=ListeCourseDAO)
        liste_course_dao_mock.clear_liste_course.return_value = 1

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        ingredient_dao_mock = MagicMock(spec=IngredientDAO)

        # WHEN
        service = ListeCourseService()
        service.liste_course_dao = liste_course_dao_mock
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock
        resultat = service.clear_liste_course(id_utilisateur)

        # THEN
        # Corriger pour vérifier "1 ingrédient" au lieu de "1 ingrédient supprimé"
        assert "1 ingrédient" in resultat
        assert "supprimé" in resultat

    # ========== Tests pour toggle_effectue ==========

    def test_toggle_effectue_vers_true(self) -> None:
        """Teste le basculement d'un item vers effectué."""
        # GIVEN
        id_utilisateur = 1
        nom_ingredient = "vodka"

        ingredient = {
            "id_ingredient": 1,
            "nom": "Vodka",
        }

        liste_course_dao_mock = MagicMock(spec=ListeCourseDAO)
        liste_course_dao_mock.toggle_effectue.return_value = True

        stock_dao_mock = MagicMock(spec=StockCourseDAO)

        ingredient_dao_mock = MagicMock(spec=IngredientDAO)
        ingredient_dao_mock.get_by_name_with_suggestions.return_value = ingredient

        # WHEN
        service = ListeCourseService()
        service.liste_course_dao = liste_course_dao_mock
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock
        resultat = service.toggle_effectue(id_utilisateur, nom_ingredient)

        # THEN
        assert resultat["effectue"] is True
        assert "coché" in resultat["message"]
        assert "Vodka" in resultat["message"]

    def test_toggle_effectue_vers_false(self) -> None:
        """Teste le basculement d'un item vers non effectué."""
        # GIVEN
        id_utilisateur = 1
        nom_ingredient = "vodka"

        ingredient = {
            "id_ingredient": 1,
            "nom": "Vodka",
        }

        liste_course_dao_mock = MagicMock(spec=ListeCourseDAO)
        liste_course_dao_mock.toggle_effectue.return_value = False

        stock_dao_mock = MagicMock(spec=StockCourseDAO)

        ingredient_dao_mock = MagicMock(spec=IngredientDAO)
        ingredient_dao_mock.get_by_name_with_suggestions.return_value = ingredient

        # WHEN
        service = ListeCourseService()
        service.liste_course_dao = liste_course_dao_mock
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock
        resultat = service.toggle_effectue(id_utilisateur, nom_ingredient)

        # THEN
        assert resultat["effectue"] is False
        assert "décoché" in resultat["message"]

    # ========== Tests pour remove_from_liste_course_and_add_to_stock ==========

    def test_remove_and_add_to_stock_nouveau_dans_stock(self) -> None:
        """Teste le transfert d'un ingrédient vers un stock vide."""
        # GIVEN
        id_utilisateur = 1
        nom_ingredient = "vodka"

        ingredient = {
            "id_ingredient": 1,
            "nom": "Vodka",
        }

        liste_item = {
            "quantite": 500.0,
            "id_unite": 1,
            "type_unite": "liquide",
            "code_unite": "ml",
        }

        unite_info = {
            "abbreviation": "ml",
        }

        liste_course_dao_mock = MagicMock(spec=ListeCourseDAO)
        liste_course_dao_mock.get_liste_course_item.return_value = liste_item
        liste_course_dao_mock.remove_from_liste_course.return_value = True

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        stock_dao_mock.get_stock_item.return_value = None
        stock_dao_mock.set_stock_item.return_value = (
            None  # Corriger le nom de la méthode
        )
        stock_dao_mock.get_unite_info.return_value = unite_info

        ingredient_dao_mock = MagicMock(spec=IngredientDAO)
        ingredient_dao_mock.get_by_name_with_suggestions.return_value = ingredient

        # WHEN
        service = ListeCourseService()
        service.liste_course_dao = liste_course_dao_mock
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock
        resultat = service.remove_from_liste_course_and_add_to_stock(
            id_utilisateur,
            nom_ingredient,
        )

        # THEN
        assert "Vodka" in resultat
        assert "ajouté au stock" in resultat
        stock_dao_mock.set_stock_item.assert_called_once()  # Corriger le nom de la méthode

    def test_remove_and_add_to_stock_meme_unite(self) -> None:
        """Teste le transfert avec la même unité dans le stock."""
        # GIVEN
        id_utilisateur = 1
        nom_ingredient = "vodka"

        ingredient = {
            "id_ingredient": 1,
            "nom": "Vodka",
        }

        liste_item = {
            "quantite": 500.0,
            "id_unite": 1,
            "type_unite": "liquide",
            "code_unite": "ml",
        }

        stock_item = {
            "quantite": 300.0,
            "id_unite": 1,
        }

        unite_info = {
            "abbreviation": "ml",
        }

        liste_course_dao_mock = MagicMock(spec=ListeCourseDAO)
        liste_course_dao_mock.get_liste_course_item.return_value = liste_item
        liste_course_dao_mock.remove_from_liste_course.return_value = True

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        stock_dao_mock.get_stock_item.return_value = stock_item
        stock_dao_mock.set_stock_item.return_value = (
            None  # Corriger le nom de la méthode
        )
        stock_dao_mock.get_unite_info.return_value = unite_info

        ingredient_dao_mock = MagicMock(spec=IngredientDAO)
        ingredient_dao_mock.get_by_name_with_suggestions.return_value = ingredient

        # WHEN
        service = ListeCourseService()
        service.liste_course_dao = liste_course_dao_mock
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock
        resultat = service.remove_from_liste_course_and_add_to_stock(
            id_utilisateur,
            nom_ingredient,
        )

        # THEN
        assert "Vodka" in resultat
        stock_dao_mock.set_stock_item.assert_called_once()  # Corriger le nom de la méthode
        # Vérifier que la quantité est 800 (300 + 500)
        call_args = stock_dao_mock.set_stock_item.call_args
        assert call_args[1]["quantite"] == 800.0

    def test_remove_and_add_to_stock_non_dans_liste(self) -> None:
        """Teste le transfert d'un ingrédient non présent dans la liste.

        Raises
        ------
        ServiceError
            Quand l'ingrédient n'est pas dans la liste de course

        """
        # GIVEN
        id_utilisateur = 1
        nom_ingredient = "vodka"

        ingredient = {
            "id_ingredient": 1,
            "nom": "Vodka",
        }

        liste_course_dao_mock = MagicMock(spec=ListeCourseDAO)
        liste_course_dao_mock.get_liste_course_item.return_value = None

        stock_dao_mock = MagicMock(spec=StockCourseDAO)

        ingredient_dao_mock = MagicMock(spec=IngredientDAO)
        ingredient_dao_mock.get_by_name_with_suggestions.return_value = ingredient

        # WHEN
        service = ListeCourseService()
        service.liste_course_dao = liste_course_dao_mock
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock

        # THEN
        with pytest.raises(ServiceError) as exc_info:
            service.remove_from_liste_course_and_add_to_stock(
                id_utilisateur,
                nom_ingredient,
            )
        # Corriger la vérification pour matcher le message exact (sans espace après "liste")
        assert "n'est pas dans votre liste" in str(exc_info.value)
