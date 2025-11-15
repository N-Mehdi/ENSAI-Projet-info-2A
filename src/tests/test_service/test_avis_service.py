"""Classe de test de src/service/avis_service.py."""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from src.dao.avis_dao import AvisDao
from src.dao.cocktail_dao import CocktailDao
from src.models.avis import AvisResponse, AvisSummary
from src.models.cocktail import Cocktail
from src.service.avis_service import AvisService
from src.utils.exceptions import (
    AvisNotFoundError,
    IngredientNotFoundError,
    InvalidAvisError,
    ServiceError,
)


class TestAvisService:
    """Tests pour AvisService."""

    # ========== Tests pour _get_cocktail_by_name ==========

    def test_get_cocktail_by_name_succes(self) -> None:
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

        avis_dao_mock = MagicMock(spec=AvisDao)
        cocktail_dao_mock = MagicMock(spec=CocktailDao)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = cocktail_attendu

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock
        resultat = service._get_cocktail_by_name(nom_cocktail)

        # THEN
        assert resultat["id_cocktail"] == 1
        assert resultat["nom"] == "Margarita"
        cocktail_dao_mock.rechercher_cocktail_par_nom.assert_called_once_with("Margarita")

    def test_get_cocktail_by_name_non_trouve(self) -> None:
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

        avis_dao_mock = MagicMock(spec=AvisDao)
        cocktail_dao_mock = MagicMock(spec=CocktailDao)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = None
        cocktail_dao_mock.rechercher_cocktail_par_sequence_debut.return_value = suggestions

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock

        # THEN
        with pytest.raises(IngredientNotFoundError) as exc_info:
            service._get_cocktail_by_name(nom_cocktail)
        assert exc_info.value.nom_ingredient == "Cocktailinconnu"
        assert exc_info.value.suggestions == ["Cocktail A"]

    # ========== Tests pour create_or_update_avis ==========

    def test_create_or_update_avis_succes_avec_note_et_commentaire(self) -> None:
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

        avis_dao_mock = MagicMock(spec=AvisDao)
        avis_dao_mock.create_or_update_avis.return_value = None

        cocktail_dao_mock = MagicMock(spec=CocktailDao)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = cocktail

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock
        resultat = service.create_or_update_avis(id_utilisateur, nom_cocktail, note, commentaire)

        # THEN
        assert "Margarita" in resultat
        assert "ajouté/modifié avec succès" in resultat
        avis_dao_mock.create_or_update_avis.assert_called_once_with(
            id_utilisateur=id_utilisateur,
            id_cocktail=1,
            note=note,
            commentaire=commentaire,
        )

    def test_create_or_update_avis_succes_avec_note_seulement(self) -> None:
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

        avis_dao_mock = MagicMock(spec=AvisDao)
        cocktail_dao_mock = MagicMock(spec=CocktailDao)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = cocktail

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock
        resultat = service.create_or_update_avis(id_utilisateur, nom_cocktail, note, commentaire)

        # THEN
        assert "Margarita" in resultat
        assert "ajouté/modifié avec succès" in resultat

    def test_create_or_update_avis_note_et_commentaire_vides(self) -> None:
        # GIVEN
        id_utilisateur = 1
        nom_cocktail = "margarita"
        note = None
        commentaire = None

        avis_dao_mock = MagicMock(spec=AvisDao)
        cocktail_dao_mock = MagicMock(spec=CocktailDao)

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock

        # THEN
        with pytest.raises(InvalidAvisError) as exc_info:
            service.create_or_update_avis(id_utilisateur, nom_cocktail, note, commentaire)
        assert "Au moins la note ou le commentaire" in str(exc_info.value)

    def test_create_or_update_avis_cocktail_inexistant(self) -> None:
        # GIVEN
        id_utilisateur = 1
        nom_cocktail = "cocktailinconnu"
        note = 8
        commentaire = "Test"

        avis_dao_mock = MagicMock(spec=AvisDao)
        cocktail_dao_mock = MagicMock(spec=CocktailDao)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = None
        cocktail_dao_mock.rechercher_cocktail_par_sequence_debut.return_value = []

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock

        # THEN
        with pytest.raises(IngredientNotFoundError):
            service.create_or_update_avis(id_utilisateur, nom_cocktail, note, commentaire)

    # ========== Tests pour get_avis_cocktail ==========

    def test_get_avis_cocktail_succes(self) -> None:
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

        avis_dao_mock = MagicMock(spec=AvisDao)
        avis_dao_mock.get_avis_by_cocktail.return_value = avis_data

        cocktail_dao_mock = MagicMock(spec=CocktailDao)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = cocktail

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock
        resultat = service.get_avis_cocktail(nom_cocktail)

        # THEN
        assert len(resultat) == 1
        assert isinstance(resultat[0], AvisResponse)
        assert resultat[0].pseudo_utilisateur == "alice"
        assert resultat[0].note == 8

    def test_get_avis_cocktail_aucun_avis(self) -> None:
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

        avis_dao_mock = MagicMock(spec=AvisDao)
        avis_dao_mock.get_avis_by_cocktail.return_value = []

        cocktail_dao_mock = MagicMock(spec=CocktailDao)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = cocktail

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock
        resultat = service.get_avis_cocktail(nom_cocktail)

        # THEN
        assert len(resultat) == 0

    # ========== Tests pour get_mes_avis_simple ==========

    def test_get_mes_avis_simple_succes(self) -> None:
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

        avis_dao_mock = MagicMock(spec=AvisDao)
        avis_dao_mock.get_avis_by_user.return_value = avis_data

        cocktail_dao_mock = MagicMock(spec=CocktailDao)

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock
        resultat = service.get_mes_avis_simple(id_utilisateur, pseudo)

        # THEN
        assert resultat["pseudo_utilisateur"] == "alice"
        assert len(resultat["avis"]) == 2
        assert resultat["avis"][0]["nom_cocktail"] == "Margarita"

    def test_get_mes_avis_simple_aucun_avis(self) -> None:
        # GIVEN
        id_utilisateur = 1
        pseudo = "alice"

        avis_dao_mock = MagicMock(spec=AvisDao)
        avis_dao_mock.get_avis_by_user.return_value = []

        cocktail_dao_mock = MagicMock(spec=CocktailDao)

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock
        resultat = service.get_mes_avis_simple(id_utilisateur, pseudo)

        # THEN
        assert resultat["pseudo_utilisateur"] == "alice"
        assert len(resultat["avis"]) == 0

    # ========== Tests pour delete_avis ==========

    def test_delete_avis_succes(self) -> None:
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

        avis_dao_mock = MagicMock(spec=AvisDao)
        avis_dao_mock.delete_avis.return_value = True

        cocktail_dao_mock = MagicMock(spec=CocktailDao)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = cocktail

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock
        resultat = service.delete_avis(id_utilisateur, nom_cocktail)

        # THEN
        assert "supprimé avec succès" in resultat
        assert "Margarita" in resultat

    def test_delete_avis_non_trouve(self) -> None:
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

        avis_dao_mock = MagicMock(spec=AvisDao)
        avis_dao_mock.delete_avis.return_value = False

        cocktail_dao_mock = MagicMock(spec=CocktailDao)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = cocktail

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock

        # THEN
        with pytest.raises(AvisNotFoundError):
            service.delete_avis(id_utilisateur, nom_cocktail)

    # ========== Tests pour add_favoris ==========

    def test_add_favoris_succes_nouveau(self) -> None:
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

        avis_dao_mock = MagicMock(spec=AvisDao)
        avis_dao_mock.add_favoris.return_value = {"deja_en_favoris": False}

        cocktail_dao_mock = MagicMock(spec=CocktailDao)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = cocktail

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock
        resultat = service.add_favoris(id_utilisateur, nom_cocktail)

        # THEN
        assert resultat["favoris"] is True
        assert resultat["deja_en_favoris"] is False
        assert "ajouté aux favoris" in resultat["message"]

    def test_add_favoris_deja_en_favoris(self) -> None:
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

        avis_dao_mock = MagicMock(spec=AvisDao)
        avis_dao_mock.add_favoris.return_value = {"deja_en_favoris": True}

        cocktail_dao_mock = MagicMock(spec=CocktailDao)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = cocktail

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock
        resultat = service.add_favoris(id_utilisateur, nom_cocktail)

        # THEN
        assert resultat["favoris"] is True
        assert resultat["deja_en_favoris"] is True
        assert "déjà dans vos favoris" in resultat["message"]

    # ========== Tests pour remove_favoris ==========

    def test_remove_favoris_succes(self) -> None:
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

        avis_dao_mock = MagicMock(spec=AvisDao)
        avis_dao_mock.remove_favoris.return_value = True

        cocktail_dao_mock = MagicMock(spec=CocktailDao)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = cocktail

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock
        resultat = service.remove_favoris(id_utilisateur, nom_cocktail)

        # THEN
        assert "retiré des favoris" in resultat
        assert "Margarita" in resultat

    def test_remove_favoris_non_trouve(self) -> None:
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

        avis_dao_mock = MagicMock(spec=AvisDao)
        avis_dao_mock.remove_favoris.return_value = False

        cocktail_dao_mock = MagicMock(spec=CocktailDao)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = cocktail

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock

        # THEN
        with pytest.raises(AvisNotFoundError):
            service.remove_favoris(id_utilisateur, nom_cocktail)

    # ========== Tests pour get_mes_favoris_simple ==========

    def test_get_mes_favoris_simple_succes(self) -> None:
        # GIVEN
        id_utilisateur = 1
        pseudo = "alice"

        favoris_data = [
            {"nom_cocktail": "Margarita"},
            {"nom_cocktail": "Mojito"},
        ]

        avis_dao_mock = MagicMock(spec=AvisDao)
        avis_dao_mock.get_favoris_by_user.return_value = favoris_data

        cocktail_dao_mock = MagicMock(spec=CocktailDao)

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock
        resultat = service.get_mes_favoris_simple(id_utilisateur, pseudo)

        # THEN
        assert resultat["pseudo_utilisateur"] == "alice"
        assert len(resultat["cocktails_favoris"]) == 2
        assert "Margarita" in resultat["cocktails_favoris"]
        assert "Mojito" in resultat["cocktails_favoris"]

    def test_get_mes_favoris_simple_aucun_favori(self) -> None:
        # GIVEN
        id_utilisateur = 1
        pseudo = "alice"

        avis_dao_mock = MagicMock(spec=AvisDao)
        avis_dao_mock.get_favoris_by_user.return_value = []

        cocktail_dao_mock = MagicMock(spec=CocktailDao)

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock
        resultat = service.get_mes_favoris_simple(id_utilisateur, pseudo)

        # THEN
        assert resultat["pseudo_utilisateur"] == "alice"
        assert len(resultat["cocktails_favoris"]) == 0

    # ========== Tests pour get_avis_summary ==========

    def test_get_avis_summary_succes(self) -> None:
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

        avis_dao_mock = MagicMock(spec=AvisDao)
        avis_dao_mock.get_avis_summary.return_value = summary_data

        cocktail_dao_mock = MagicMock(spec=CocktailDao)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = cocktail

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock
        resultat = service.get_avis_summary(nom_cocktail)

        # THEN
        assert isinstance(resultat, AvisSummary)
        assert resultat.nom_cocktail == "Margarita"
        assert resultat.nombre_avis == 10
        assert resultat.note_moyenne == 8.5
        assert resultat.nombre_favoris == 5

    def test_get_avis_summary_echec(self) -> None:
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

        avis_dao_mock = MagicMock(spec=AvisDao)
        avis_dao_mock.get_avis_summary.return_value = None

        cocktail_dao_mock = MagicMock(spec=CocktailDao)
        cocktail_dao_mock.rechercher_cocktail_par_nom.return_value = cocktail

        # WHEN
        service = AvisService()
        service.avis_dao = avis_dao_mock
        service.cocktail_dao = cocktail_dao_mock

        # THEN
        with pytest.raises(ServiceError) as exc_info:
            service.get_avis_summary(nom_cocktail)
        assert "Impossible de récupérer le résumé" in str(exc_info.value)
