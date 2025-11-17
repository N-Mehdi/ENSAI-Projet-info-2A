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

    def test_grant_access_to_user_succes(self) -> None:
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
        assert isinstance(resultat, AccessResponse)
        assert resultat.success is True
        assert "bob" in resultat.message
        assert resultat.owner_pseudo == owner_pseudo
        assert resultat.user_pseudo == user_pseudo
        dao_mock.grant_access.assert_called_once_with(owner_id, user_id)

    def test_grant_access_to_user_owner_inexistant(self) -> None:
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
        assert "inconnu" in str(exc_info.value)

    def test_grant_access_to_user_user_inexistant(self):
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
        assert "inconnu" in str(exc_info.value)

    def test_grant_access_to_user_self_access(self):
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
        assert "vous-même" in str(exc_info.value)

    def test_grant_access_to_user_deja_existant(self):
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
        assert "déjà accès" in str(exc_info.value)

    # ========== Tests pour revoke_access_from_user ==========

    def test_revoke_access_from_user_succes(self):
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
        assert isinstance(resultat, AccessResponse)
        assert resultat.success is True
        assert "retiré" in resultat.message
        dao_mock.revoke_access.assert_called_once_with(owner_id, user_id)

    def test_revoke_access_from_user_acces_inexistant(self):
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
        assert "n'a pas d'accès" in str(exc_info.value)

    # ========== Tests pour get_users_with_access ==========

    def test_get_users_with_access_succes(self):
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
        assert isinstance(resultat, AccessList)
        assert resultat.owner_pseudo == owner_pseudo
        assert resultat.users_with_access == users
        assert resultat.total_users == 2

    def test_get_users_with_access_utilisateur_inexistant(self):
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

    def test_get_users_with_access_liste_vide(self):
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
        assert resultat.total_users == 0
        assert resultat.users_with_access == []

    # ========== Tests pour view_private_cocktails ==========

    def test_view_private_cocktails_succes(self):
        # GIVEN
        owner_pseudo = "alice"
        viewer_pseudo = "bob"
        owner_id = 1
        viewer_id = 2

        cocktails_data = [
            {
                "id_cocktail": 1,
                "nom_cocktail": "Mojito",
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
        assert isinstance(resultat, PrivateCocktailsList)
        assert resultat.owner_pseudo == owner_pseudo
        assert resultat.total_cocktails == 1
        assert len(resultat.cocktails) == 1
        assert resultat.cocktails[0].nom_cocktail == "Mojito"

    def test_view_private_cocktails_acces_refuse(self):
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
        assert "n'avez pas accès" in str(exc_info.value)

    # ========== Tests pour get_my_private_cocktails ==========

    def test_get_my_private_cocktails_succes(self):
        # GIVEN
        owner_pseudo = "alice"
        owner_id = 1

        cocktails_data = [
            {
                "id_cocktail": 1,
                "nom_cocktail": "Mojito",
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
        assert isinstance(resultat, PrivateCocktailsList)
        assert resultat.owner_pseudo == owner_pseudo

    # ========== Tests pour add_cocktail_to_private_list ==========

    def test_add_cocktail_to_private_list_succes(self):
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
        assert isinstance(resultat, AccessResponse)
        assert resultat.success is True
        assert "ajouté" in resultat.message

    def test_add_cocktail_to_private_list_deja_present(self):
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
        assert "déjà dans" in str(exc_info.value)

    # ========== Tests pour add_cocktail_to_private_list_by_name ==========

    def test_add_cocktail_to_private_list_by_name_succes(self):
        # GIVEN
        owner_pseudo = "alice"
        cocktail_name = "Mojito"
        owner_id = 1
        cocktail_id = 1

        dao_mock = MagicMock(spec=AccesDAO)
        dao_mock.get_user_id_by_pseudo.return_value = owner_id
        dao_mock.add_cocktail_to_private_list.return_value = True

        dao_cocktail_mock = MagicMock(spec=CocktailDAO)
        dao_cocktail_mock.get_cocktail_id_by_name.return_value = cocktail_id

        # WHEN
        service = AccesService()
        service.dao = dao_mock
        service.dao_cocktail = dao_cocktail_mock
        resultat = service.add_cocktail_to_private_list_by_name(owner_pseudo, cocktail_name)

        # THEN
        assert isinstance(resultat, AccessResponse)
        assert resultat.success is True
        assert "Mojito" in resultat.message

    def test_add_cocktail_to_private_list_by_name_cocktail_inexistant(self):
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
            service.add_cocktail_to_private_list_by_name(owner_pseudo, cocktail_name)
        assert "CocktailInconnu" in str(exc_info.value)

    # ========== Tests pour remove_cocktail_from_private_list ==========

    def test_remove_cocktail_from_private_list_succes(self):
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
        assert isinstance(resultat, AccessResponse)
        assert resultat.success is True
        assert "retiré" in resultat.message

    def test_remove_cocktail_from_private_list_non_present(self):
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
        assert "n'est pas dans" in str(exc_info.value)

    # ========== Tests pour remove_cocktail_from_private_list_by_name ==========

    def test_remove_cocktail_from_private_list_by_name_succes(self):
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
        resultat = service.remove_cocktail_from_private_list_by_name(owner_pseudo, cocktail_name)

        # THEN
        assert isinstance(resultat, AccessResponse)
        assert resultat.success is True
        assert "Mojito" in resultat.message

    def test_remove_cocktail_from_private_list_by_name_cocktail_inexistant(self):
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
            service.remove_cocktail_from_private_list_by_name(owner_pseudo, cocktail_name)
        assert "CocktailInconnu" in str(exc_info.value)
