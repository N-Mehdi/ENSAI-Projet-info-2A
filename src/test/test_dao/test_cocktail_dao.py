# import pytest

from src.business_object.cocktail import Cocktail
from src.dao.cocktail_dao import CocktailDao


class TestCocktailDao:
    # Tests pour rechercher_cocktail_par_nom

    def test_rechercher_cocktail_par_nom_succes(self):
        # GIVEN
        nom = "Margarita"

        # WHEN
        dao = CocktailDao()
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
        dao = CocktailDao()
        resultat = dao.rechercher_cocktail_par_nom(nom)

        # THEN
        assert resultat is None
