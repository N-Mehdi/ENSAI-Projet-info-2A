"""Classe de test de src/service/acces_service.py."""

from unittest.mock import MagicMock

import pytest

from src.dao.acces_dao import AccesDAO
from src.dao.cocktail_dao import CocktailDAO
from src.models.acces import (
    AccessList,
    AccessResponse,
    PrivateCocktailsList,
)
from src.service.acces_service import AccesService
from src.utils.exceptions import (
    AccessAlreadyExistsError,
    AccessDeniedError,
    AccessNotFoundError,
    CocktailNotFoundError,
    SelfAccessError,
    UserNotFoundError,
)


class TestAccesService:
    """Tests pour AccesService."""

    # ========== Tests pour grant_access_to_user ==========
    @staticmethod
    def test_grant_access_to_user_succes() -> None:
        """Teste l'octroi d'accès avec succès."""
        # GIVEN
        owner_pseudo = "alice"
        user_pseudo = "bob"
        owner_id = 1
        user_id = 2

        dao_mock = MagicMock(spec=AccesDAO)
        dao_mock.get_user_id_by_pseudo.side_effect = [owner_id, user_id]
        dao_mock.grant_access.return_value = True

        dao_cocktail_mock = MagicMock(spec=CocktailDAO)

        # WHEN
        service = AccesService()
        service.dao = dao_mock
        service.dao_cocktail = dao_cocktail_mock
        resultat = service.grant_access_to_user(owner_pseudo, user_pseudo)

        # THEN
        if not isinstance(resultat, dict):
            raise TypeError(
                message=f"Le résultat devrait être un dict, obtenu: {type(resultat)}",
            )
        if resultat["success"] is not True:
            raise AssertionError(
                message=f"success devrait être True, obtenu: {resultat['success']}",
            )
        if "bob" not in resultat["message"]:
            raise AssertionError(
                message=f"'bob' devrait être dans le message"
                f"obtenu: {resultat['message']}",
            )
        if resultat["owner_pseudo"] != owner_pseudo:
            raise AssertionError(
                message=f"owner_pseudo devrait être '{owner_pseudo}', obtenu: "
                f"{resultat['owner_pseudo']}",
            )
        dao_mock.grant_access.assert_called_once_with(owner_id, user_id)

    @staticmethod
    def test_grant_access_to_user_owner_inexistant() -> None:
        """Teste l'octroi d'accès avec un propriétaire inexistant."""
        # GIVEN
        owner_pseudo = "inconnu"
        user_pseudo = "bob"

        dao_mock = MagicMock(spec=AccesDAO)
        dao_mock.get_user_id_by_pseudo.return_value = None

        dao_cocktail_mock = MagicMock(spec=CocktailDAO)

        # WHEN
        service = AccesService()
        service.dao = dao_mock
        service.dao_cocktail = dao_cocktail_mock

        # THEN
        with pytest.raises(UserNotFoundError) as exc_info:
            service.grant_access_to_user(owner_pseudo, user_pseudo)
        if "inconnu" not in str(exc_info.value):
            raise AssertionError(
                message=f"'inconnu' devrait être dans l'erreur,"
                f"obtenu: {exc_info.value}",
            )

    @staticmethod
    def test_grant_access_to_user_user_inexistant() -> None:
        """Teste l'octroi d'accès avec un utilisateur inexistant."""
        # GIVEN
        owner_pseudo = "alice"
        user_pseudo = "inconnu"
        owner_id = 1

        dao_mock = MagicMock(spec=AccesDAO)
        dao_mock.get_user_id_by_pseudo.side_effect = [owner_id, None]

        dao_cocktail_mock = MagicMock(spec=CocktailDAO)

        # WHEN
        service = AccesService()
        service.dao = dao_mock
        service.dao_cocktail = dao_cocktail_mock

        # THEN
        with pytest.raises(UserNotFoundError) as exc_info:
            service.grant_access_to_user(owner_pseudo, user_pseudo)
        if "inconnu" not in str(exc_info.value):
            raise AssertionError(
                message=f"'inconnu' devrait être dans l'erreur,"
                f"obtenu: {exc_info.value}",
            )

    @staticmethod
    def test_grant_access_to_user_self_access() -> None:
        """Teste l'octroi d'accès à soi-même."""
        # GIVEN
        owner_pseudo = "alice"
        user_pseudo = "alice"
        owner_id = 1

        dao_mock = MagicMock(spec=AccesDAO)
        dao_mock.get_user_id_by_pseudo.side_effect = [owner_id, owner_id]

        dao_cocktail_mock = MagicMock(spec=CocktailDAO)

        # WHEN
        service = AccesService()
        service.dao = dao_mock
        service.dao_cocktail = dao_cocktail_mock

        # THEN
        with pytest.raises(SelfAccessError) as exc_info:
            service.grant_access_to_user(owner_pseudo, user_pseudo)
        if "vous-même" not in str(exc_info.value):
            raise AssertionError(
                message=f"'vous-même' devrait être dans l'erreur,"
                f"obtenu: {exc_info.value}",
            )

    @staticmethod
    def test_grant_access_to_user_deja_existant() -> None:
        """Teste l'octroi d'accès déjà existant."""
        # GIVEN
        owner_pseudo = "alice"
        user_pseudo = "bob"
        owner_id = 1
        user_id = 2

        dao_mock = MagicMock(spec=AccesDAO)
        dao_mock.get_user_id_by_pseudo.side_effect = [owner_id, user_id]
        dao_mock.grant_access.return_value = False

        dao_cocktail_mock = MagicMock(spec=CocktailDAO)

        # WHEN
        service = AccesService()
        service.dao = dao_mock
        service.dao_cocktail = dao_cocktail_mock

        # THEN
        with pytest.raises(AccessAlreadyExistsError) as exc_info:
            service.grant_access_to_user(owner_pseudo, user_pseudo)
        if "déjà accès" not in str(exc_info.value):
            raise AssertionError(
                message=f"'déjà accès' devrait être dans l'erreur,"
                f"obtenu: {exc_info.value}",
            )

    # ========== Tests pour revoke_access_from_user ==========
    @staticmethod
    def test_revoke_access_from_user_succes() -> None:
        """Teste le retrait d'accès avec succès."""
        # GIVEN
        owner_pseudo = "alice"
        user_pseudo = "bob"
        owner_id = 1
        user_id = 2

        dao_mock = MagicMock(spec=AccesDAO)
        dao_mock.get_user_id_by_pseudo.side_effect = [owner_id, user_id]
        dao_mock.revoke_access.return_value = True

        dao_cocktail_mock = MagicMock(spec=CocktailDAO)

        # WHEN
        service = AccesService()
        service.dao = dao_mock
        service.dao_cocktail = dao_cocktail_mock
        resultat = service.revoke_access_from_user(owner_pseudo, user_pseudo)

        # THEN
        if not isinstance(resultat, AccessResponse):
            raise TypeError(
                message=f"Le résultat devrait être AccessResponse,"
                f"obtenu: {type(resultat)}",
            )
        if resultat.success is not True:
            raise AssertionError(
                message=f"success devrait être True, obtenu: {resultat.success}",
            )
        if "retiré" not in resultat.message:
            raise AssertionError(
                message=f"'retiré' devrait être dans le message,"
                f"obtenu: {resultat.message}",
            )
        dao_mock.revoke_access.assert_called_once_with(owner_id, user_id)

    @staticmethod
    def test_revoke_access_from_user_acces_inexistant() -> None:
        """Teste le retrait d'accès inexistant."""
        # GIVEN
        owner_pseudo = "alice"
        user_pseudo = "bob"
        owner_id = 1
        user_id = 2

        dao_mock = MagicMock(spec=AccesDAO)
        dao_mock.get_user_id_by_pseudo.side_effect = [owner_id, user_id]
        dao_mock.revoke_access.return_value = False

        dao_cocktail_mock = MagicMock(spec=CocktailDAO)

        # WHEN
        service = AccesService()
        service.dao = dao_mock
        service.dao_cocktail = dao_cocktail_mock

        # THEN
        with pytest.raises(AccessNotFoundError) as exc_info:
            service.revoke_access_from_user(owner_pseudo, user_pseudo)
        if "n'a pas d'accès" not in str(exc_info.value):
            raise AssertionError(
                message=f"'n'a pas d'accès' devrait être dans l'erreur,"
                f"obtenu: {exc_info.value}",
            )

    # ========== Tests pour get_users_with_access ==========
    @staticmethod
    def test_get_users_with_access_succes() -> None:
        """Teste la récupération des utilisateurs avec accès."""
        # GIVEN
        owner_pseudo = "alice"
        owner_id = 1
        users = ["bob", "charlie"]

        dao_mock = MagicMock(spec=AccesDAO)
        dao_mock.get_user_id_by_pseudo.return_value = owner_id
        dao_mock.get_users_with_access.return_value = users

        dao_cocktail_mock = MagicMock(spec=CocktailDAO)

        # WHEN
        service = AccesService()
        service.dao = dao_mock
        service.dao_cocktail = dao_cocktail_mock
        resultat = service.get_users_with_access(owner_pseudo)

        # THEN
        if not isinstance(resultat, AccessList):
            raise TypeError(
                message=f"Le résultat devrait être AccessList,obtenu: {type(resultat)}",
            )
        if resultat.owner_pseudo != owner_pseudo:
            raise AssertionError(
                message=f"owner_pseudo devrait être '{owner_pseudo}',"
                f"obtenu: {resultat.owner_pseudo}",
            )
        if resultat.users_with_access != users:
            raise AssertionError(
                message=f"users_with_access devrait être {users},"
                f"obtenu: {resultat.users_with_access}",
            )
        nb_user = 2
        if resultat.total_users != nb_user:
            raise AssertionError(
                message=f"total_users devrait être 2,obtenu: {resultat.total_users}",
            )

    @staticmethod
    def test_get_users_with_access_utilisateur_inexistant() -> None:
        """Teste la récupération avec un utilisateur inexistant."""
        # GIVEN
        owner_pseudo = "inconnu"

        dao_mock = MagicMock(spec=AccesDAO)
        dao_mock.get_user_id_by_pseudo.return_value = None

        dao_cocktail_mock = MagicMock(spec=CocktailDAO)

        # WHEN
        service = AccesService()
        service.dao = dao_mock
        service.dao_cocktail = dao_cocktail_mock

        # THEN
        with pytest.raises(UserNotFoundError):
            service.get_users_with_access(owner_pseudo)

    @staticmethod
    def test_get_users_with_access_liste_vide() -> None:
        """Teste la récupération avec une liste vide."""
        # GIVEN
        owner_pseudo = "alice"
        owner_id = 1

        dao_mock = MagicMock(spec=AccesDAO)
        dao_mock.get_user_id_by_pseudo.return_value = owner_id
        dao_mock.get_users_with_access.return_value = []

        dao_cocktail_mock = MagicMock(spec=CocktailDAO)

        # WHEN
        service = AccesService()
        service.dao = dao_mock
        service.dao_cocktail = dao_cocktail_mock
        resultat = service.get_users_with_access(owner_pseudo)

        # THEN
        if resultat.total_users != 0:
            raise AssertionError(
                message=f"total_users devrait être 0, obtenu: {resultat.total_users}",
            )
        if resultat.users_with_access != []:
            raise AssertionError(
                message=f"users_with_access devrait être [], obtenu: "
                f"{resultat.users_with_access}",
            )

    # ========== Tests pour view_private_cocktails ==========
    @staticmethod
    def test_view_private_cocktails_succes() -> None:
        """Teste la visualisation des cocktails privés avec succès."""
        # GIVEN
        owner_pseudo = "alice"
        viewer_pseudo = "bob"
        owner_id = 1
        viewer_id = 2

        cocktails_data = [
            {
                "id_cocktail": 1,
                "nom_cocktail": "Mojito",
                "categorie": "Cocktail",
                "verre": "Highball",
                "alcool": True,
                "image": "mojito.jpg",
                "instruction": "Mélanger tous les ingrédients",
                "ingredients": [
                    {"nom_ingredient": "Rhum", "quantite": 50.0, "unite": "ml"},
                    {"nom_ingredient": "Menthe", "quantite": 10.0, "unite": "feuilles"},
                ],
            },
        ]

        dao_mock = MagicMock(spec=AccesDAO)
        dao_mock.get_user_id_by_pseudo.side_effect = [owner_id, viewer_id]
        dao_mock.has_access.return_value = True
        dao_mock.get_private_cocktails.return_value = cocktails_data

        dao_cocktail_mock = MagicMock(spec=CocktailDAO)

        # WHEN
        service = AccesService()
        service.dao = dao_mock
        service.dao_cocktail = dao_cocktail_mock
        resultat = service.view_private_cocktails(owner_pseudo, viewer_pseudo)

        # THEN
        if not isinstance(resultat, PrivateCocktailsList):
            raise TypeError(
                message=f"Le résultat devrait être PrivateCocktailsList, obtenu: "
                f"{type(resultat)}",
            )
        if resultat.owner_pseudo != owner_pseudo:
            raise AssertionError(
                message=f"owner_pseudo devrait être '{owner_pseudo}', obtenu: "
                f"{resultat.owner_pseudo}",
            )
        if resultat.total_cocktails != 1:
            raise AssertionError(
                message=f"total_cocktails devrait être 1,"
                f"obtenu: {resultat.total_cocktails}",
            )
        if len(resultat.cocktails) != 1:
            raise AssertionError(
                message=f"Devrait avoir 1 cocktail, obtenu: {len(resultat.cocktails)}",
            )
        if resultat.cocktails[0].nom_cocktail != "Mojito":
            raise AssertionError(
                message=f"Le nom devrait être 'Mojito', obtenu: "
                f"{resultat.cocktails[0].nom_cocktail}",
            )
        if resultat.cocktails[0].categorie != "Cocktail":
            raise AssertionError(
                message=f"La catégorie devrait être 'Cocktail', obtenu: "
                f"{resultat.cocktails[0].categorie}",
            )
        if resultat.cocktails[0].verre != "Highball":
            raise AssertionError(
                message=f"Le verre devrait être 'Highball', obtenu: "
                f"{resultat.cocktails[0].verre}",
            )
        if resultat.cocktails[0].alcool is not True:
            raise AssertionError(
                message=f"alcool devrait être True, obtenu:"
                f"{resultat.cocktails[0].alcool}",
            )

    @staticmethod
    def test_view_private_cocktails_acces_refuse() -> None:
        """Teste la visualisation avec accès refusé."""
        # GIVEN
        owner_pseudo = "alice"
        viewer_pseudo = "bob"
        owner_id = 1
        viewer_id = 2

        dao_mock = MagicMock(spec=AccesDAO)
        dao_mock.get_user_id_by_pseudo.side_effect = [owner_id, viewer_id]
        dao_mock.has_access.return_value = False

        dao_cocktail_mock = MagicMock(spec=CocktailDAO)

        # WHEN
        service = AccesService()
        service.dao = dao_mock
        service.dao_cocktail = dao_cocktail_mock

        # THEN
        with pytest.raises(AccessDeniedError) as exc_info:
            service.view_private_cocktails(owner_pseudo, viewer_pseudo)
        if "n'avez pas accès" not in str(exc_info.value):
            raise AssertionError(
                message=f"'n'avez pas accès' devrait être dans l'erreur, obtenu: "
                f"{exc_info.value}",
            )

    # ========== Tests pour get_my_private_cocktails ==========
    @staticmethod
    def test_get_my_private_cocktails_succes() -> None:
        """Teste la récupération de ses propres cocktails privés."""
        # GIVEN
        owner_pseudo = "alice"
        owner_id = 1

        cocktails_data = [
            {
                "id_cocktail": 1,
                "nom_cocktail": "Mojito",
                "categorie": "Cocktail",
                "verre": "Highball",
                "alcool": True,
                "image": "mojito.jpg",
                "instruction": "Mélanger tous les ingrédients",
                "ingredients": [],
            },
        ]

        dao_mock = MagicMock(spec=AccesDAO)
        dao_mock.get_user_id_by_pseudo.side_effect = [owner_id, owner_id]
        dao_mock.has_access.return_value = True
        dao_mock.get_private_cocktails.return_value = cocktails_data

        dao_cocktail_mock = MagicMock(spec=CocktailDAO)

        # WHEN
        service = AccesService()
        service.dao = dao_mock
        service.dao_cocktail = dao_cocktail_mock
        resultat = service.get_my_private_cocktails(owner_pseudo)

        # THEN
        if not isinstance(resultat, PrivateCocktailsList):
            raise TypeError(
                message=f"Le résultat devrait être PrivateCocktailsList,"
                f"obtenu: {type(resultat)}",
            )
        if resultat.owner_pseudo != owner_pseudo:
            raise AssertionError(
                message=f"owner_pseudo devrait être '{owner_pseudo}', obtenu: "
                f"{resultat.owner_pseudo}",
            )
        if resultat.total_cocktails != 1:
            raise AssertionError(
                message=f"total_cocktails devrait être 1,"
                f"obtenu: {resultat.total_cocktails}",
            )
        if len(resultat.cocktails) != 1:
            raise AssertionError(
                message=f"Devrait avoir 1 cocktail, obtenu: {len(resultat.cocktails)}",
            )
        if resultat.cocktails[0].nom_cocktail != "Mojito":
            raise AssertionError(
                message=f"Le nom devrait être 'Mojito', obtenu: "
                f"{resultat.cocktails[0].nom_cocktail}",
            )

    # ========== Tests pour add_cocktail_to_private_list ==========
    @staticmethod
    def test_add_cocktail_to_private_list_succes() -> None:
        """Teste l'ajout d'un cocktail à la liste privée."""
        # GIVEN
        owner_pseudo = "alice"
        cocktail_id = 1
        owner_id = 1

        dao_mock = MagicMock(spec=AccesDAO)
        dao_mock.get_user_id_by_pseudo.return_value = owner_id
        dao_mock.add_cocktail_to_private_list.return_value = True

        dao_cocktail_mock = MagicMock(spec=CocktailDAO)

        # WHEN
        service = AccesService()
        service.dao = dao_mock
        service.dao_cocktail = dao_cocktail_mock
        resultat = service.add_cocktail_to_private_list(owner_pseudo, cocktail_id)

        # THEN
        if not isinstance(resultat, AccessResponse):
            raise TypeError(
                message=f"Le résultat devrait être AccessResponse,"
                f"obtenu: {type(resultat)}",
            )
        if resultat.success is not True:
            raise AssertionError(
                message=f"success devrait être True, obtenu: {resultat.success}",
            )
        if "ajouté" not in resultat.message:
            raise AssertionError(
                message=f"'ajouté' devrait être dans le message,"
                f"obtenu: {resultat.message}",
            )

    @staticmethod
    def test_add_cocktail_to_private_list_deja_present() -> None:
        """Teste l'ajout d'un cocktail déjà présent."""
        # GIVEN
        owner_pseudo = "alice"
        cocktail_id = 1
        owner_id = 1

        dao_mock = MagicMock(spec=AccesDAO)
        dao_mock.get_user_id_by_pseudo.return_value = owner_id
        dao_mock.add_cocktail_to_private_list.return_value = False

        dao_cocktail_mock = MagicMock(spec=CocktailDAO)

        # WHEN
        service = AccesService()
        service.dao = dao_mock
        service.dao_cocktail = dao_cocktail_mock

        # THEN
        with pytest.raises(AccessAlreadyExistsError) as exc_info:
            service.add_cocktail_to_private_list(owner_pseudo, cocktail_id)
        if "déjà dans" not in str(exc_info.value):
            raise AssertionError(
                message=f"'déjà dans' devrait être dans l'erreur,"
                f"obtenu: {exc_info.value}",
            )

    # ========== Tests pour remove_cocktail_from_private_list ==========
    @staticmethod
    def test_remove_cocktail_from_private_list_succes() -> None:
        """Teste le retrait d'un cocktail de la liste privée."""
        # GIVEN
        owner_pseudo = "alice"
        cocktail_id = 1
        owner_id = 1

        dao_mock = MagicMock(spec=AccesDAO)
        dao_mock.get_user_id_by_pseudo.return_value = owner_id
        dao_mock.remove_cocktail_from_private_list.return_value = True

        dao_cocktail_mock = MagicMock(spec=CocktailDAO)

        # WHEN
        service = AccesService()
        service.dao = dao_mock
        service.dao_cocktail = dao_cocktail_mock
        resultat = service.remove_cocktail_from_private_list(owner_pseudo, cocktail_id)

        # THEN
        if not isinstance(resultat, AccessResponse):
            raise TypeError(
                message=f"Le résultat devrait être AccessResponse,"
                f"obtenu: {type(resultat)}",
            )
        if resultat.success is not True:
            raise AssertionError(
                message=f"success devrait être True, obtenu: {resultat.success}",
            )
        if "retiré" not in resultat.message:
            raise AssertionError(
                message=f"'retiré' devrait être dans le message,"
                f"obtenu: {resultat.message}",
            )

    @staticmethod
    def test_remove_cocktail_from_private_list_non_present() -> None:
        """Teste le retrait d'un cocktail non présent."""
        # GIVEN
        owner_pseudo = "alice"
        cocktail_id = 1
        owner_id = 1

        dao_mock = MagicMock(spec=AccesDAO)
        dao_mock.get_user_id_by_pseudo.return_value = owner_id
        dao_mock.remove_cocktail_from_private_list.return_value = False

        dao_cocktail_mock = MagicMock(spec=CocktailDAO)

        # WHEN
        service = AccesService()
        service.dao = dao_mock
        service.dao_cocktail = dao_cocktail_mock

        # THEN
        with pytest.raises(AccessNotFoundError) as exc_info:
            service.remove_cocktail_from_private_list(owner_pseudo, cocktail_id)
        if "n'est pas dans" not in str(exc_info.value):
            raise AssertionError(
                message=f"'n'est pas dans' devrait être dans l'erreur,"
                f"obtenu: {exc_info.value}",
            )

    # ========== Tests pour remove_cocktail_from_private_list_by_name ==========
    @staticmethod
    def test_remove_cocktail_from_private_list_by_name_succes() -> None:
        """Teste le retrait d'un cocktail par nom."""
        # GIVEN
        owner_pseudo = "alice"
        cocktail_name = "Mojito"
        owner_id = 1
        cocktail_id = 1

        dao_mock = MagicMock(spec=AccesDAO)
        dao_mock.get_user_id_by_pseudo.return_value = owner_id
        dao_mock.remove_cocktail_from_private_list.return_value = True

        dao_cocktail_mock = MagicMock(spec=CocktailDAO)
        dao_cocktail_mock.get_cocktail_id_by_name.return_value = cocktail_id

        # WHEN
        service = AccesService()
        service.dao = dao_mock
        service.dao_cocktail = dao_cocktail_mock
        resultat = service.remove_cocktail_from_private_list_by_name(
            owner_pseudo,
            cocktail_name,
        )

        # THEN
        if not isinstance(resultat, AccessResponse):
            raise TypeError(
                message=f"Le résultat devrait être AccessResponse, obtenu:"
                f"{type(resultat)}",
            )
        if resultat.success is not True:
            raise AssertionError(
                message=f"success devrait être True, obtenu: {resultat.success}",
            )
        if "Mojito" not in resultat.message:
            raise TypeError(
                message=f"'Mojito' devrait être dans le message,"
                f"obtenu:{resultat.message}",
            )

    @staticmethod
    def test_remove_cocktail_from_private_list_by_name_cocktail_inexistant() -> None:
        """Teste le retrait d'un cocktail inexistant par nom."""
        # GIVEN
        owner_pseudo = "alice"
        cocktail_name = "CocktailInconnu"
        owner_id = 1

        dao_mock = MagicMock(spec=AccesDAO)
        dao_mock.get_user_id_by_pseudo.return_value = owner_id

        dao_cocktail_mock = MagicMock(spec=CocktailDAO)
        dao_cocktail_mock.get_cocktail_id_by_name.return_value = None

        # WHEN
        service = AccesService()
        service.dao = dao_mock
        service.dao_cocktail = dao_cocktail_mock

        # THEN
        with pytest.raises(CocktailNotFoundError) as exc_info:
            service.remove_cocktail_from_private_list_by_name(
                owner_pseudo,
                cocktail_name,
            )
        if "CocktailInconnu" not in str(exc_info.value):
            raise AssertionError(
                message=f"'CocktailInconnu' devrait être dans l'erreur, obtenu: "
                f"{exc_info.value}",
            )
