"""Tests pour ListeCourseService."""

from unittest.mock import MagicMock

import pytest

from src.dao.ingredient_dao import IngredientDAO
from src.dao.liste_course_dao import ListeCourseDAO
from src.dao.stock_course_dao import StockCourseDAO
from src.models.utilisateurs import User
from src.service.ingredient_service import IngredientService
from src.service.liste_course_service import ListeCourseService
from src.service.utilisateur_service import UtilisateurService
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

        utilisateur = User(
            id_utilisateur=1,
            pseudo="alice",
            mail="alice@example.com",
            mot_de_passe_hashed="hashed",
            date_naissance="2000-01-01",
            date_inscription="2024-01-01",
        )

        liste_course_dao_mock = MagicMock(spec=ListeCourseDAO)
        liste_course_dao_mock.get_liste_course.return_value = rows

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        ingredient_dao_mock = MagicMock(spec=IngredientDAO)

        utilisateur_svc_mock = MagicMock(spec=UtilisateurService)
        utilisateur_svc_mock.read.return_value = utilisateur

        # WHEN
        service = ListeCourseService()
        service.liste_course_dao = liste_course_dao_mock
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock
        service.utilisateur_svc = utilisateur_svc_mock

        resultat = service.get_liste_course(id_utilisateur)

        # THEN
        if not isinstance(resultat, dict):
            raise TypeError(
                message=f"Le résultat devrait être un dict, obtenu: {type(resultat)}",
            )
        if resultat["pseudo"] != "alice":
            raise AssertionError(
                message=f"Le pseudo devrait être 'alice', obtenu: {resultat['pseudo']}",
            )
        nb_items = 2
        if len(resultat["items"]) != nb_items:
            raise AssertionError(
                message=f"2 items attendus, obtenu: {len(resultat['items'])}",
            )
        if resultat["nombre_items"] != nb_items:
            raise AssertionError(
                message=f"nombre_items devrait être 2, obtenu:"
                f"{resultat['nombre_items']}",
            )
        if resultat["nombre_effectues"] != 1:
            raise AssertionError(
                message=f"nombre_effectues devrait être 1, obtenu:"
                f"{resultat['nombre_effectues']}",
            )

    def test_get_liste_course_vide(self) -> None:
        """Teste la récupération d'une liste de course vide."""
        # GIVEN
        id_utilisateur = 1

        utilisateur = User(
            id_utilisateur=1,
            pseudo="alice",
            mail="alice@example.com",
            mot_de_passe_hashed="hashed",
            date_naissance="2000-01-01",
            date_inscription="2024-01-01",
        )

        liste_course_dao_mock = MagicMock(spec=ListeCourseDAO)
        liste_course_dao_mock.get_liste_course.return_value = []

        stock_dao_mock = MagicMock(spec=StockCourseDAO)
        ingredient_dao_mock = MagicMock(spec=IngredientDAO)

        utilisateur_svc_mock = MagicMock(spec=UtilisateurService)
        utilisateur_svc_mock.read.return_value = utilisateur

        # WHEN
        service = ListeCourseService()
        service.liste_course_dao = liste_course_dao_mock
        service.stock_dao = stock_dao_mock
        service.ingredient_dao = ingredient_dao_mock
        service.utilisateur_svc = utilisateur_svc_mock

        resultat = service.get_liste_course(id_utilisateur)

        # THEN
        if resultat["nombre_items"] != 0:
            raise AssertionError(
                message=f"nombre_items devrait être 0, obtenu:"
                f"{resultat['nombre_items']}",
            )
        if resultat["nombre_effectues"] != 0:
            raise AssertionError(
                message=f"nombre_effectues devrait être 0, obtenu:"
                f"{resultat['nombre_effectues']}",
            )

    # ========== Tests pour add_to_liste_course ==========


class TestListeCourseServiceAdd:
    """Classe pour tester l'ajout d'ingrédients dans la liste de course."""

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

        # Créer une instance réelle pour le test, pas un mock
        stock_dao_instance = MagicMock(spec=StockCourseDAO)
        stock_dao_instance.get_unite_id_by_abbreviation.return_value = 1

        # WHEN
        service = ListeCourseService()
        service.ingredient_svc = ingredient_service_mock
        service.liste_course_dao = liste_course_dao_mock
        service.stock_dao = stock_dao_instance  # Utiliser l'instance mockée

        resultat = service.add_to_liste_course(
            id_utilisateur,
            nom_ingredient,
            quantite,
            abbreviation_unite,
        )

        # THEN
        if "Vodka" not in resultat:
            raise AssertionError(
                message=f"'Vodka' devrait être dans le résultat: {resultat}",
            )
        if str(quantite) not in resultat:
            raise AssertionError(
                message=f"'{quantite}' devrait être dans le résultat: {resultat}",
            )

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

        if "DB error" not in str(exc_info.value):
            raise AssertionError(
                message=f"'DB error' devrait être dans l'erreur:{exc_info.value}",
            )

    # ========== Tests pour remove_from_liste_course ==========


class TestListeCourseServiceRemovie:
    """Classe pour tester la suppression d'ingrédients dans la liste de course."""

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

        ingredient_svc_mock = MagicMock(spec=IngredientService)
        ingredient_svc_mock.get_by_name_with_suggestions.return_value = ingredient

        # WHEN
        service = ListeCourseService()
        service.liste_course_dao = liste_course_dao_mock
        service.stock_dao = stock_dao_mock
        service.ingredient_svc = ingredient_svc_mock

        resultat = service.remove_from_liste_course(id_utilisateur, nom_ingredient)

        # THEN
        if "Vodka" not in resultat:
            raise AssertionError(
                message=f"'Vodka' devrait être dans le résultat: {resultat}",
            )
        if "retiré de la liste de course" not in resultat:
            raise AssertionError(
                message=f"'retiré de la liste de course' devrait être dans le résultat:"
                f"{resultat}",
            )

    def test_remove_from_liste_course_non_present(self) -> None:
        """Teste le retrait d'un ingrédient non présent dans la liste."""
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

        ingredient_svc_mock = MagicMock(spec=IngredientService)
        ingredient_svc_mock.get_by_name_with_suggestions.return_value = ingredient

        # WHEN
        service = ListeCourseService()
        service.liste_course_dao = liste_course_dao_mock
        service.stock_dao = stock_dao_mock
        service.ingredient_svc = ingredient_svc_mock
        # THEN
        with pytest.raises(ServiceError) as exc_info:
            service.remove_from_liste_course(id_utilisateur, nom_ingredient)

        if "n'est pas dans votre" not in str(exc_info.value):
            raise AssertionError(
                message=f"Le message devrait contenir 'n'est pas dans votre':"
                f"{exc_info.value}",
            )

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
        if "déjà vide" not in resultat:
            raise AssertionError(
                message=f"'déjà vide' devrait être dans le résultat: {resultat}",
            )

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
        if "1 ingrédient" not in resultat:
            raise AssertionError(
                message=f"'1 ingrédient' devrait être dans le résultat: {resultat}",
            )
        if "supprimé" not in resultat:
            raise AssertionError(
                message=f"'supprimé' devrait être dans le résultat: {resultat}",
            )

    # ========== Tests pour toggle_effectue ==========


class TestListeCourseServiceEffectue:
    """Classe pour tester l'ajout le changement de l'état "effectué" d'un ingrédient
    dans la liste de course.
    """

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

        ingredient_svc_mock = MagicMock(spec=IngredientService)
        ingredient_svc_mock.get_by_name_with_suggestions.return_value = ingredient

        # WHEN
        service = ListeCourseService()
        service.liste_course_dao = liste_course_dao_mock
        service.stock_dao = stock_dao_mock
        service.ingredient_svc = ingredient_svc_mock

        resultat = service.toggle_effectue(id_utilisateur, nom_ingredient)

        # THEN
        if resultat["effectue"] is not True:
            raise AssertionError(
                message=f"effectue devrait être True, obtenu: {resultat['effectue']}",
            )
        if "coché" not in resultat["message"]:
            raise AssertionError(
                message=f"'coché' devrait être dans le message: {resultat['message']}",
            )
        if "Vodka" not in resultat["message"]:
            raise AssertionError(
                message=f"'Vodka' devrait être dans le message: {resultat['message']}",
            )

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

        ingredient_svc_mock = MagicMock(spec=IngredientService)
        ingredient_svc_mock.get_by_name_with_suggestions.return_value = ingredient

        # WHEN
        service = ListeCourseService()
        service.liste_course_dao = liste_course_dao_mock
        service.stock_dao = stock_dao_mock
        service.ingredient_svc = ingredient_svc_mock

        resultat = service.toggle_effectue(id_utilisateur, nom_ingredient)

        # THEN
        if resultat["effectue"] is not False:
            raise AssertionError(
                message=f"effectue devrait être False, obtenu: {resultat['effectue']}",
            )
        if "décoché" not in resultat["message"]:
            raise AssertionError(
                message=f"'décoché' devrait être dans le message:{resultat['message']}",
            )

    # ========== Tests pour remove_from_liste_course_and_add_to_stock ==========


class TestListeCourseServiceRemoveAddStock:
    """Classe pour tester la suppression d'ingrédients de la liste de course et leur
    ajout au stock de l'utilisateur.
    """

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
        stock_dao_mock.set_stock_item.return_value = None
        stock_dao_mock.get_unite_info.return_value = unite_info

        ingredient_svc_mock = MagicMock(spec=IngredientService)
        ingredient_svc_mock.get_by_name_with_suggestions.return_value = ingredient

        # WHEN
        service = ListeCourseService()
        service.liste_course_dao = liste_course_dao_mock
        service.stock_dao = stock_dao_mock
        service.ingredient_svc = ingredient_svc_mock

        resultat = service.remove_from_liste_course_and_add_to_stock(
            id_utilisateur,
            nom_ingredient,
        )

        # THEN
        if "Vodka" not in resultat:
            raise AssertionError(
                message=f"'Vodka' devrait être dans le résultat: {resultat}",
            )
        if "ajouté au stock" not in resultat:
            raise AssertionError(
                message=f"'ajouté au stock' devrait être dans le résultat: {resultat}",
            )

        stock_dao_mock.set_stock_item.assert_called_once()

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
        stock_dao_mock.set_stock_item.return_value = None
        stock_dao_mock.get_unite_info.return_value = unite_info

        ingredient_svc_mock = MagicMock(spec=IngredientService)
        ingredient_svc_mock.get_by_name_with_suggestions.return_value = ingredient

        # WHEN
        service = ListeCourseService()
        service.liste_course_dao = liste_course_dao_mock
        service.stock_dao = stock_dao_mock
        service.ingredient_svc = ingredient_svc_mock

        resultat = service.remove_from_liste_course_and_add_to_stock(
            id_utilisateur,
            nom_ingredient,
        )

        # THEN
        if "Vodka" not in resultat:
            raise AssertionError(
                message=f"'Vodka' devrait être dans le résultat:{resultat}",
            )

        stock_dao_mock.set_stock_item.assert_called_once()

        # Vérifier que la quantité est 800 (300 + 500)
        qte_verif = 800.0
        call_args = stock_dao_mock.set_stock_item.call_args
        if call_args[1]["quantite"] != qte_verif:
            raise AssertionError(
                message=f"La quantité devrait être 800.0, obtenu:"
                f"{call_args[1]['quantite']}",
            )

    def test_remove_and_add_to_stock_non_dans_liste(self) -> None:
        """Teste le transfert d'un ingrédient non présent dans la liste."""
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

        ingredient_svc_mock = MagicMock(spec=IngredientService)
        ingredient_svc_mock.get_by_name_with_suggestions.return_value = ingredient

        # WHEN
        service = ListeCourseService()
        service.liste_course_dao = liste_course_dao_mock
        service.stock_dao = stock_dao_mock
        service.ingredient_svc = ingredient_svc_mock
        # THEN
        with pytest.raises(ServiceError) as exc_info:
            service.remove_from_liste_course_and_add_to_stock(
                id_utilisateur,
                nom_ingredient,
            )

        if "n'est pas dans votre liste" not in str(exc_info.value):
            raise AssertionError(
                message=f"Le message devrait contenir 'n'est pas dans votre liste':"
                f"{exc_info.value}",
            )
