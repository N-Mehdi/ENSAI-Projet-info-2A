"""Classe de test de AvisService."""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from src.dao.avis_dao import AvisDAO
from src.dao.cocktail_dao import CocktailDAO
from src.models.avis import AvisResponse, AvisSummary
from src.models.cocktail import Cocktail
from src.service.avis_service import AvisService
from src.utils.exceptions import (
    AvisNotFoundError,
    CocktailNotFoundError,
    InvalidAvisError,
    ServiceError,
)


class TestAvisService:
    """Tests pour AvisService."""

    # ========== Tests pour get_cocktail_by_name ==========
    @staticmethod
    def test_get_cocktail_by_name_succes() -> None:
        """Teste la méthode get_cocktail_by_name lorsque le cocktail est trouvé
        avec succès.
        """
        # GIVEN
        nom_cocktail = "margarita"
        cocktail_attendu = Cocktail(
            id_cocktail=1,
            nom="Margarita",
            categorie="Ordinary Drink",
            verre="Cocktail glass",
            alcool=True,
            image="https://example.com/margarita.jpg",
        )

        avis_dao_mock = MagicMock(spec=AvisDAO)
        cocktail_dao_mock = MagicMock(spec=CocktailDAO)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = cocktail_attendu

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock
        resultat = service.get_cocktail_by_name(nom_cocktail)

        # THEN
        if resultat["id_cocktail"] != 1:
            raise AssertionError(
                message=f"L'id_cocktail devrait être 1, obtenu:"
                f"{resultat['id_cocktail']}",
            )
        if resultat["nom"] != "Margarita":
            raise AssertionError(
                message=f"Le nom devrait être 'Margarita', obtenu: {resultat['nom']}",
            )
        cocktail_dao_mock.rechercher_cocktail_par_nom.assert_called_once_with(
            "Margarita",
        )

    @staticmethod
    def test_get_cocktail_by_name_non_trouve() -> None:
        """Teste la méthode get_cocktail_by_name lorsque le cocktail n'est pas
        trouvé.
        """
        # GIVEN
        nom_cocktail = "cocktailinconnu"
        suggestions = [
            Cocktail(
                id_cocktail=1,
                nom="Cocktail A",
                categorie="",
                verre="",
                alcool=True,
                image="",
            ),
        ]

        avis_dao_mock = MagicMock(spec=AvisDAO)
        cocktail_dao_mock = MagicMock(spec=CocktailDAO)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = None
        cocktail_dao_mock.rechercher_cocktail_par_sequence_debut.return_value = (
            suggestions
        )

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock

        # THEN
        with pytest.raises(CocktailNotFoundError):
            service.get_cocktail_by_name(nom_cocktail)

    # ========== Tests pour create_or_update_avis ==========
    @staticmethod
    def test_create_or_update_avis_succes_avec_note_et_commentaire() -> None:
        """Teste la création/mise à jour d'un avis avec note et commentaire."""
        # GIVEN
        id_utilisateur = 1
        nom_cocktail = "margarita"
        note = 8
        commentaire = "Excellent cocktail!"

        cocktail = Cocktail(
            id_cocktail=1,
            nom="Margarita",
            categorie="Ordinary Drink",
            verre="Cocktail glass",
            alcool=True,
            image="https://example.com/margarita.jpg",
        )

        avis_dao_mock = MagicMock(spec=AvisDAO)
        avis_dao_mock.create_or_update_avis.return_value = None

        cocktail_dao_mock = MagicMock(spec=CocktailDAO)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = cocktail

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock
        resultat = service.create_or_update_avis(
            id_utilisateur,
            nom_cocktail,
            note,
            commentaire,
        )

        # THEN
        if "Margarita" not in resultat:
            raise AssertionError(
                message=f"'Margarita' devrait être dans le résultat: {resultat}",
            )
        if "ajouté/modifié avec succès" not in resultat:
            raise AssertionError(
                message=f"'ajouté/modifié avec succès' devrait être dans le résultat:"
                f"{resultat}",
            )
        avis_dao_mock.create_or_update_avis.assert_called_once_with(
            id_utilisateur=id_utilisateur,
            id_cocktail=1,
            note=note,
            commentaire=commentaire,
        )

    @staticmethod
    def test_create_or_update_avis_succes_avec_note_seulement() -> None:
        """Teste la création/mise à jour d'un avis avec seulement une note."""
        # GIVEN
        id_utilisateur = 1
        nom_cocktail = "margarita"
        note = 8
        commentaire = None

        cocktail = Cocktail(
            id_cocktail=1,
            nom="Margarita",
            categorie="Ordinary Drink",
            verre="Cocktail glass",
            alcool=True,
            image="https://example.com/margarita.jpg",
        )

        avis_dao_mock = MagicMock(spec=AvisDAO)
        cocktail_dao_mock = MagicMock(spec=CocktailDAO)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = cocktail

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock
        resultat = service.create_or_update_avis(
            id_utilisateur,
            nom_cocktail,
            note,
            commentaire,
        )

        # THEN
        if "Margarita" not in resultat:
            raise AssertionError(
                message=f"'Margarita' devrait être dans le résultat: {resultat}",
            )
        if "ajouté/modifié avec succès" not in resultat:
            raise AssertionError(
                message=f"'ajouté/modifié avec succès' devrait être dans le résultat:"
                f"{resultat}",
            )

    @staticmethod
    def test_create_or_update_avis_note_et_commentaire_vides() -> None:
        """Teste la création d'un avis sans note ni commentaire."""
        # GIVEN
        id_utilisateur = 1
        nom_cocktail = "margarita"
        note = None
        commentaire = None

        avis_dao_mock = MagicMock(spec=AvisDAO)
        cocktail_dao_mock = MagicMock(spec=CocktailDAO)

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock

        # THEN
        with pytest.raises(InvalidAvisError) as exc_info:
            service.create_or_update_avis(
                id_utilisateur,
                nom_cocktail,
                note,
                commentaire,
            )

        error_message = str(exc_info.value)
        if "Au moins la note ou le commentaire" not in error_message:
            raise AssertionError(
                message=f"'Au moins la note ou le commentaire' devrait être dans le"
                f"message d'erreur: {error_message}",
            )

    @staticmethod
    def test_create_or_update_avis_cocktail_inexistant() -> None:
        """Teste la création d'un avis pour un cocktail inexistant."""
        # GIVEN
        id_utilisateur = 1
        nom_cocktail = "cocktailinconnu"
        note = 8
        commentaire = "Test"

        avis_dao_mock = MagicMock(spec=AvisDAO)
        cocktail_dao_mock = MagicMock(spec=CocktailDAO)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = None
        cocktail_dao_mock.rechercher_cocktail_par_sequence_debut.return_value = []

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock

        # THEN
        with pytest.raises(CocktailNotFoundError):
            service.create_or_update_avis(
                id_utilisateur,
                nom_cocktail,
                note,
                commentaire,
            )

    # ========== Tests pour get_avis_cocktail ==========
    @staticmethod
    def test_get_avis_cocktail_succes() -> None:
        """Teste la récupération des avis d'un cocktail avec succès."""
        # GIVEN
        nom_cocktail = "margarita"
        cocktail = Cocktail(
            id_cocktail=1,
            nom="Margarita",
            categorie="Ordinary Drink",
            verre="Cocktail glass",
            alcool=True,
            image="https://example.com/margarita.jpg",
        )

        avis_data = [
            {
                "id_utilisateur": 1,
                "pseudo_utilisateur": "alice",
                "id_cocktail": 1,
                "nom_cocktail": "Margarita",
                "note": 8,
                "commentaire": "Excellent!",
                "favoris": True,
                "date_creation": datetime(2024, 1, 1),
                "date_modification": datetime(2024, 1, 2),
            },
        ]

        avis_dao_mock = MagicMock(spec=AvisDAO)
        avis_dao_mock.get_avis_by_cocktail.return_value = avis_data

        cocktail_dao_mock = MagicMock(spec=CocktailDAO)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = cocktail

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock
        resultat = service.get_avis_cocktail(nom_cocktail)

        # THEN
        if len(resultat) != 1:
            raise AssertionError(
                message=f"1 avis attendu, obtenu: {len(resultat)}",
            )
        if not isinstance(resultat[0], AvisResponse):
            raise TypeError(
                message=f"Le résultat devrait être de type AvisResponse, obtenu:"
                f"{type(resultat[0])}",
            )
        if resultat[0].pseudo_utilisateur != "alice":
            raise AssertionError(
                message=f"Le pseudo devrait être 'alice', obtenu:"
                f"{resultat[0].pseudo_utilisateur}",
            )
        note = 8
        if resultat[0].note != note:
            raise AssertionError(
                message=f"La note devrait être 8, obtenu: {resultat[0].note}",
            )

    @staticmethod
    def test_get_avis_cocktail_aucun_avis() -> None:
        """Teste la récupération des avis d'un cocktail sans avis."""
        # GIVEN
        nom_cocktail = "margarita"
        cocktail = Cocktail(
            id_cocktail=1,
            nom="Margarita",
            categorie="Ordinary Drink",
            verre="Cocktail glass",
            alcool=True,
            image="https://example.com/margarita.jpg",
        )

        avis_dao_mock = MagicMock(spec=AvisDAO)
        avis_dao_mock.get_avis_by_cocktail.return_value = []

        cocktail_dao_mock = MagicMock(spec=CocktailDAO)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = cocktail

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock
        resultat = service.get_avis_cocktail(nom_cocktail)

        # THEN
        if len(resultat) != 0:
            raise AssertionError(
                message=f"Aucun avis attendu, obtenu: {len(resultat)}",
            )

    # ========== Tests pour get_mes_avis_simple ==========
    @staticmethod
    def test_get_mes_avis_simple_succes() -> None:
        """Teste la récupération des avis d'un utilisateur avec succès."""
        # GIVEN
        id_utilisateur = 1
        pseudo = "alice"

        avis_data = [
            {
                "nom_cocktail": "Margarita",
                "note": 8,
                "commentaire": "Excellent!",
            },
            {
                "nom_cocktail": "Mojito",
                "note": 7,
                "commentaire": "Très bon",
            },
        ]

        avis_dao_mock = MagicMock(spec=AvisDAO)
        avis_dao_mock.get_avis_by_user.return_value = avis_data

        cocktail_dao_mock = MagicMock(spec=CocktailDAO)

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock
        resultat = service.get_mes_avis_simple(id_utilisateur, pseudo)

        # THEN
        if resultat["pseudo_utilisateur"] != "alice":
            raise AssertionError(
                message=f"Le pseudo devrait être 'alice', obtenu:"
                f"{resultat['pseudo_utilisateur']}",
            )
        nb_avis = 2
        if len(resultat["avis"]) != nb_avis:
            raise AssertionError(
                message=f"2 avis attendus, obtenu: {len(resultat['avis'])}",
            )
        if resultat["avis"][0]["nom_cocktail"] != "Margarita":
            raise AssertionError(
                message=f"Le premier cocktail devrait être 'Margarita', obtenu:"
                f"{resultat['avis'][0]['nom_cocktail']}",
            )

    @staticmethod
    def test_get_mes_avis_simple_aucun_avis() -> None:
        """Teste la récupération des avis d'un utilisateur sans avis."""
        # GIVEN
        id_utilisateur = 1
        pseudo = "alice"

        avis_dao_mock = MagicMock(spec=AvisDAO)
        avis_dao_mock.get_avis_by_user.return_value = []

        cocktail_dao_mock = MagicMock(spec=CocktailDAO)

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock
        resultat = service.get_mes_avis_simple(id_utilisateur, pseudo)

        # THEN
        if resultat["pseudo_utilisateur"] != "alice":
            raise AssertionError(
                message=f"Le pseudo devrait être 'alice', obtenu:"
                f"{resultat['pseudo_utilisateur']}",
            )
        if len(resultat["avis"]) != 0:
            raise AssertionError(
                message=f"Aucun avis attendu, obtenu: {len(resultat['avis'])}",
            )

    # ========== Tests pour delete_avis ==========
    @staticmethod
    def test_delete_avis_succes() -> None:
        """Teste la suppression d'un avis avec succès."""
        # GIVEN
        id_utilisateur = 1
        nom_cocktail = "margarita"

        cocktail = Cocktail(
            id_cocktail=1,
            nom="Margarita",
            categorie="Ordinary Drink",
            verre="Cocktail glass",
            alcool=True,
            image="https://example.com/margarita.jpg",
        )

        avis_dao_mock = MagicMock(spec=AvisDAO)
        avis_dao_mock.delete_avis.return_value = True

        cocktail_dao_mock = MagicMock(spec=CocktailDAO)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = cocktail

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock
        resultat = service.delete_avis(id_utilisateur, nom_cocktail)

        # THEN
        if "supprimé avec succès" not in resultat:
            raise AssertionError(
                message="'supprimé avec succès' devrait être dans le résultat:"
                f"{resultat}",
            )
        if "Margarita" not in resultat:
            raise AssertionError(
                message=f"'Margarita' devrait être dans le résultat: {resultat}",
            )

    @staticmethod
    def test_delete_avis_non_trouve() -> None:
        """Teste la suppression d'un avis inexistant."""
        # GIVEN
        id_utilisateur = 1
        nom_cocktail = "margarita"

        cocktail = Cocktail(
            id_cocktail=1,
            nom="Margarita",
            categorie="Ordinary Drink",
            verre="Cocktail glass",
            alcool=True,
            image="https://example.com/margarita.jpg",
        )

        avis_dao_mock = MagicMock(spec=AvisDAO)
        avis_dao_mock.delete_avis.return_value = False

        cocktail_dao_mock = MagicMock(spec=CocktailDAO)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = cocktail

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock

        # THEN
        with pytest.raises(AvisNotFoundError):
            service.delete_avis(id_utilisateur, nom_cocktail)

    # ========== Tests pour add_favoris ==========
    @staticmethod
    def test_add_favoris_succes_nouveau() -> None:
        """Teste l'ajout d'un nouveau cocktail aux favoris."""
        # GIVEN
        id_utilisateur = 1
        nom_cocktail = "margarita"

        cocktail = Cocktail(
            id_cocktail=1,
            nom="Margarita",
            categorie="Ordinary Drink",
            verre="Cocktail glass",
            alcool=True,
            image="https://example.com/margarita.jpg",
        )

        avis_dao_mock = MagicMock(spec=AvisDAO)
        avis_dao_mock.add_favoris.return_value = {"deja_en_favoris": False}

        cocktail_dao_mock = MagicMock(spec=CocktailDAO)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = cocktail

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock
        resultat = service.add_favoris(id_utilisateur, nom_cocktail)

        # THEN
        if resultat["favoris"] is not True:
            raise AssertionError(
                message=f"favoris devrait être True, obtenu: {resultat['favoris']}",
            )
        if resultat["deja_en_favoris"] is not False:
            raise AssertionError(
                message=f"deja_en_favoris devrait être False, obtenu:"
                f"{resultat['deja_en_favoris']}",
            )
        if "ajouté aux favoris" not in resultat["message"]:
            raise AssertionError(
                message=f"'ajouté aux favoris' devrait être dans le message:"
                f"{resultat['message']}",
            )

    @staticmethod
    def test_add_favoris_deja_en_favoris() -> None:
        """Teste l'ajout d'un cocktail déjà en favoris."""
        # GIVEN
        id_utilisateur = 1
        nom_cocktail = "margarita"

        cocktail = Cocktail(
            id_cocktail=1,
            nom="Margarita",
            categorie="Ordinary Drink",
            verre="Cocktail glass",
            alcool=True,
            image="https://example.com/margarita.jpg",
        )

        avis_dao_mock = MagicMock(spec=AvisDAO)
        avis_dao_mock.add_favoris.return_value = {"deja_en_favoris": True}

        cocktail_dao_mock = MagicMock(spec=CocktailDAO)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = cocktail

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock
        resultat = service.add_favoris(id_utilisateur, nom_cocktail)

        # THEN
        if resultat["favoris"] is not True:
            raise AssertionError(
                message=f"favoris devrait être True, obtenu: {resultat['favoris']}",
            )
        if resultat["deja_en_favoris"] is not True:
            raise AssertionError(
                message=f"deja_en_favoris devrait être True, obtenu:"
                f"{resultat['deja_en_favoris']}",
            )
        if "déjà dans vos favoris" not in resultat["message"]:
            raise AssertionError(
                message=f"'déjà dans vos favoris' devrait être dans le message:"
                f"{resultat['message']}",
            )

    # ========== Tests pour remove_favoris ==========
    @staticmethod
    def test_remove_favoris_succes() -> None:
        """Teste le retrait d'un cocktail des favoris avec succès."""
        # GIVEN
        id_utilisateur = 1
        nom_cocktail = "margarita"

        cocktail = Cocktail(
            id_cocktail=1,
            nom="Margarita",
            categorie="Ordinary Drink",
            verre="Cocktail glass",
            alcool=True,
            image="https://example.com/margarita.jpg",
        )

        avis_dao_mock = MagicMock(spec=AvisDAO)
        avis_dao_mock.remove_favoris.return_value = True

        cocktail_dao_mock = MagicMock(spec=CocktailDAO)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = cocktail

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock
        resultat = service.remove_favoris(id_utilisateur, nom_cocktail)

        # THEN
        if "retiré des favoris" not in resultat:
            raise AssertionError(
                message=f"'retiré des favoris' devrait être dans le"
                f"résultat: {resultat}",
            )
        if "Margarita" not in resultat:
            raise AssertionError(
                message=f"'Margarita' devrait être dans le résultat: {resultat}",
            )

    @staticmethod
    def test_remove_favoris_non_trouve() -> None:
        """Teste le retrait d'un favori inexistant."""
        # GIVEN
        id_utilisateur = 1
        nom_cocktail = "margarita"

        cocktail = Cocktail(
            id_cocktail=1,
            nom="Margarita",
            categorie="Ordinary Drink",
            verre="Cocktail glass",
            alcool=True,
            image="https://example.com/margarita.jpg",
        )

        avis_dao_mock = MagicMock(spec=AvisDAO)
        avis_dao_mock.remove_favoris.return_value = False

        cocktail_dao_mock = MagicMock(spec=CocktailDAO)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = cocktail

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock

        # THEN
        with pytest.raises(AvisNotFoundError):
            service.remove_favoris(id_utilisateur, nom_cocktail)

    # ========== Tests pour get_mes_favoris_simple ==========
    @staticmethod
    def test_get_mes_favoris_simple_succes() -> None:
        """Teste la récupération des favoris d'un utilisateur avec succès."""
        # GIVEN
        id_utilisateur = 1
        pseudo = "alice"

        favoris_data = [
            {"nom_cocktail": "Margarita"},
            {"nom_cocktail": "Mojito"},
        ]

        avis_dao_mock = MagicMock(spec=AvisDAO)
        avis_dao_mock.get_favoris_by_user.return_value = favoris_data

        cocktail_dao_mock = MagicMock(spec=CocktailDAO)

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock
        resultat = service.get_mes_favoris_simple(id_utilisateur, pseudo)

        # THEN
        if resultat["pseudo_utilisateur"] != "alice":
            raise AssertionError(
                message=f"Le pseudo devrait être 'alice', obtenu:"
                f"{resultat['pseudo_utilisateur']}",
            )
        nb_fav = 2
        if len(resultat["cocktails_favoris"]) != nb_fav:
            raise AssertionError(
                message=f"2 favoris attendus, obtenu:"
                f"{len(resultat['cocktails_favoris'])}",
            )
        if "Margarita" not in resultat["cocktails_favoris"]:
            raise AssertionError(
                message=f"'Margarita' devrait être dans les favoris:"
                f"{resultat['cocktails_favoris']}",
            )
        if "Mojito" not in resultat["cocktails_favoris"]:
            raise AssertionError(
                message=f"'Mojito' devrait être dans les favoris:"
                f"{resultat['cocktails_favoris']}",
            )

    @staticmethod
    def test_get_mes_favoris_simple_aucun_favori() -> None:
        """Teste la récupération des favoris d'un utilisateur sans favoris."""
        # GIVEN
        id_utilisateur = 1
        pseudo = "alice"

        avis_dao_mock = MagicMock(spec=AvisDAO)
        avis_dao_mock.get_favoris_by_user.return_value = []

        cocktail_dao_mock = MagicMock(spec=CocktailDAO)

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock
        resultat = service.get_mes_favoris_simple(id_utilisateur, pseudo)

        # THEN
        if resultat["pseudo_utilisateur"] != "alice":
            raise AssertionError(
                message=f"Le pseudo devrait être 'alice', obtenu:"
                f"{resultat['pseudo_utilisateur']}",
            )
        if len(resultat["cocktails_favoris"]) != 0:
            raise AssertionError(
                message=f"Aucun favori attendu, obtenu:"
                f"{len(resultat['cocktails_favoris'])}",
            )

    # ========== Tests pour get_avis_summary ==========
    @staticmethod
    def test_get_avis_summary_succes() -> None:
        """Teste la récupération du résumé des avis avec succès."""
        # GIVEN
        nom_cocktail = "margarita"

        cocktail = Cocktail(
            id_cocktail=1,
            nom="Margarita",
            categorie="Ordinary Drink",
            verre="Cocktail glass",
            alcool=True,
            image="https://example.com/margarita.jpg",
        )

        summary_data = {
            "id_cocktail": 1,
            "nom_cocktail": "Margarita",
            "nombre_avis": 10,
            "note_moyenne": 8.5,
            "nombre_favoris": 5,
        }

        avis_dao_mock = MagicMock(spec=AvisDAO)
        avis_dao_mock.get_avis_summary.return_value = summary_data

        cocktail_dao_mock = MagicMock(spec=CocktailDAO)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = cocktail

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock
        resultat = service.get_avis_summary(nom_cocktail)

        # THEN
        if not isinstance(resultat, AvisSummary):
            raise TypeError(
                message=f"Le résultat devrait être de type AvisSummary, obtenu:"
                f"{type(resultat)}",
            )
        if resultat.nom_cocktail != "Margarita":
            raise AssertionError(
                message=f"Le nom du cocktail devrait être 'Margarita',"
                f"obtenu: {resultat.nom_cocktail}",
            )
        nb_avis = 10
        if resultat.nombre_avis != nb_avis:
            raise AssertionError(
                message=f"Le nombre d'avis devrait être 10, obtenu:"
                f"{resultat.nombre_avis}",
            )
        note_moy = 8.5
        if resultat.note_moyenne != note_moy:
            raise AssertionError(
                message=f"La note moyenne devrait être 8.5, obtenu:"
                f"{resultat.note_moyenne}",
            )
        nb_fav = 5
        if resultat.nombre_favoris != nb_fav:
            raise AssertionError(
                message=f"Le nombre de favoris devrait être 5, obtenu:"
                f"{resultat.nombre_favoris}",
            )

    @staticmethod
    def test_get_avis_summary_echec() -> None:
        """Teste l'échec de récupération du résumé des avis."""
        # GIVEN
        nom_cocktail = "margarita"

        cocktail = Cocktail(
            id_cocktail=1,
            nom="Margarita",
            categorie="Ordinary Drink",
            verre="Cocktail glass",
            alcool=True,
            image="https://example.com/margarita.jpg",
        )

        avis_dao_mock = MagicMock(spec=AvisDAO)
        avis_dao_mock.get_avis_summary.return_value = None

        cocktail_dao_mock = MagicMock(spec=CocktailDAO)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = cocktail

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock

        # THEN
        with pytest.raises(ServiceError) as exc_info:
            service.get_avis_summary(nom_cocktail)

        error_message = str(exc_info.value)
        if "Impossible de récupérer le résumé" not in error_message:
            raise AssertionError(
                message=f"'Impossible de récupérer le résumé' devrait être dans le"
                f"message d'erreur: {error_message}",
            )
