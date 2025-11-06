"""test_cocktail_service.py
Classe de test de cocktail_service.
"""

import pytest

from src.business_object.cocktail import Cocktail
from src.dao.cocktail_dao import CocktailDao
from src.service.cocktail_service import CocktailService


class TestCocktailService:
    # Tests pour rechercher_cocktail_par_nom

    def test_rechercher_cocktail_par_nom_succes(self):
        # GIVEN
        nom = "Margarita"

        # WHEN
        dao = CocktailDao()
        service = CocktailService(dao)
        resultat = service.rechercher_cocktail_par_nom(nom)

        # THEN
        cocktail_attendu = Cocktail(
            id_cocktail=11007,
            nom="Margarita",
            categorie="Ordinary Drink",
            verre="Cocktail glass",
            alcool=True,
            image="https://www.thecocktaildb.com/images/media/drink/5noda61589575158.jpg",
        )
        assert resultat == cocktail_attendu

    def test_rechercher_cocktail_par_nom_non_trouve(self):
        # GIVEN
        nom = "Margaritaa"

        # WHEN & THEN
        dao = CocktailDao()
        service = CocktailService(dao)

        with pytest.raises(LookupError, match=f"Aucun cocktail trouvé pour le nom '{nom}'"):
            service.rechercher_cocktail_par_nom(nom)

    def test_rechercher_cocktail_par_nom_type_error(self):
        # GIVEN
        nom = 12345  # Le nom n'est pas une chaîne de caractères

        # WHEN & THEN
        dao = CocktailDao()
        service = CocktailService(dao)

        with pytest.raises(TypeError, match="Le nom du cocktail doit être une chaîne de caractères."):
            service.rechercher_cocktail_par_nom(nom)

    def test_rechercher_cocktail_par_nom_value_error(self):
        # GIVEN
        nom = ""  # Le nom est une chaîne vide

        # WHEN & THEN
        dao = CocktailDao()
        service = CocktailService(dao)

        with pytest.raises(ValueError, match="Le nom du cocktail doit être fourni."):
            service.rechercher_cocktail_par_nom(nom)

    def test_rechercher_cocktail_par_nom_none(self):
        # GIVEN
        nom = None  # Le nom est None

        # WHEN & THEN
        dao = CocktailDao()
        service = CocktailService(dao)

        with pytest.raises(ValueError, match="Le nom du cocktail doit être fourni."):
            service.rechercher_cocktail_par_nom(nom)

    # Tests pour rechercher_cocktail_sequence_debut

    def test_rechercher_cocktail_par_sequence_debut_succes(self):
        # GIVEN
        sequence = "ma"
        max_resultats = 3

        # WHEN
        dao = CocktailDao()
        service = CocktailService(dao)
        resultat = service.rechercher_cocktail_par_sequence_debut(sequence, max_resultats)

        # THEN
        cocktails_attendus = [
            Cocktail(
                id_cocktail=11690,
                nom="Mai Tai",
                categorie="Ordinary Drink",
                verre="Collins glass",
                alcool=True,
                image="https://www.thecocktaildb.com/images/media/drink/twyrrp1439907470.jpg",
            ),
            Cocktail(
                id_cocktail=15224,
                nom="Malibu Twister",
                categorie="Cocktail",
                verre="Highball glass",
                alcool=True,
                image="https://www.thecocktaildb.com/images/media/drink/2dwae41504885321.jpg",
            ),
            Cocktail(
                id_cocktail=12716,
                nom="Mango Orange Smoothie",
                categorie="Other / Unknown",
                verre="Highball Glass",
                alcool=False,
                image="https://www.thecocktaildb.com/images/media/drink/vdp2do1487603520.jpg",
            ),
        ]
        assert resultat == cocktails_attendus

    def test_rechercher_cocktail_par_sequence_debut_non_trouve(self):
        # GIVEN
        sequence = "Maaa"
        max_resultats = 1

        # WHEN & THEN
        dao = CocktailDao()
        service = CocktailService(dao)

        with pytest.raises(LookupError, match=f"Aucun cocktail trouvé pour la séquence '{sequence}'"):
            service.rechercher_cocktail_par_sequence_debut(sequence, max_resultats)

    def test_rechercher_cocktail_par_sequence_debut_value_error_sequence(self):
        # GIVEN
        sequence = ""
        max_resultats = 1

        # WHEN & THEN
        dao = CocktailDao()
        service = CocktailService(dao)

        with pytest.raises(ValueError, match="La séquence doit être fournie."):
            service.rechercher_cocktail_par_sequence_debut(sequence, max_resultats)

    def test_rechercher_cocktail_par_sequence_debut_none(self):
        # GIVEN
        sequence = None
        max_resultats = 1

        # WHEN & THEN
        dao = CocktailDao()
        service = CocktailService(dao)

        with pytest.raises(ValueError, match="La séquence doit être fournie."):
            service.rechercher_cocktail_par_sequence_debut(sequence, max_resultats)

    def test_rechercher_cocktail_par_sequence_debut_type_error_sequence(self):
        # GIVEN
        sequence = 12345
        max_resultats = 1

        # WHEN & THEN
        dao = CocktailDao()
        service = CocktailService(dao)

        with pytest.raises(TypeError, match="L'argument 'sequence' doit être une chaîne de caractères."):
            service.rechercher_cocktail_par_sequence_debut(sequence, max_resultats)

    def test_rechercher_cocktail_par_sequence_debut_type_error_max_resultats(self):
        # GIVEN
        sequence = "Ma"
        max_resultats = "a"

        # WHEN & THEN
        dao = CocktailDao()
        service = CocktailService(dao)

        with pytest.raises(TypeError, match="L'argument 'max_resultats' doit être un entier."):
            service.rechercher_cocktail_par_sequence_debut(sequence, max_resultats)

    def test_rechercher_cocktail_par_sequence_debut_value_error_max_resultats(self):
        # GIVEN
        sequence = "Ma"
        max_resultats = -1

        # WHEN & THEN
        dao = CocktailDao()
        service = CocktailService(dao)

        with pytest.raises(ValueError, match="L'argument 'max_resultats' doit être supérieur ou égal à 1."):
            service.rechercher_cocktail_par_sequence_debut(sequence, max_resultats)
