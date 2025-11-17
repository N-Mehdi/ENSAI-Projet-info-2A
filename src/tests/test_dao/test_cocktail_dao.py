"""test_cocktail_dao.py
Classe de test de cocktail_dao.
"""

from src.business_object.cocktail import Cocktail
from src.dao.cocktail_dao import CocktailDAO


class TestCocktailDAO:
    # Tests pour rechercher_cocktail_par_nom

    def test_rechercher_cocktail_par_nom_succes(self):
        # GIVEN
        nom = "Margarita"

        # WHEN
        dao = CocktailDAO()
        resultat = dao.rechercher_cocktail_par_nom(nom)

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

        # WHEN
        dao = CocktailDAO()
        resultat = dao.rechercher_cocktail_par_nom(nom)

        # THEN
        assert resultat is None

    # Tests pour rechercher_cocktail_sequence_debut

    def test_rechercher_cocktail_par_sequence_debut_succes(self):
        # GIVEN
        sequence = "ma"
        max_resultats = 3

        # WHEN
        dao = CocktailDAO()
        resultat = dao.rechercher_cocktail_par_sequence_debut(sequence, max_resultats)

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

        # WHEN
        dao = CocktailDAO()
        resultat = dao.rechercher_cocktail_par_sequence_debut(sequence, max_resultats)

        # THEN
        assert resultat == []
