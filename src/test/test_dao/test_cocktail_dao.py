# import pytest
from src.business_object.cocktail import Cocktail
from src.dao.cocktail_dao import CocktailDao


class TestCocktailDao:
    def test_rechercher_cocktail_par_nom(self):
        # GIVEN
        nom = "Margarita"

        # WHEN
        resultat = CocktailDao.rechercher_cocktail_par_nom(nom)

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
