import unittest
from unittest.mock import MagicMock
from src.business_object.Ingredient import Ingredient
from src.service.ingredient_dao import IngredientDao
from src.service.verification_service import est_alcoolise_par_nom  # si tu as mis la fonction dans un autre module

class TestIngredientDao(unittest.TestCase):

    def setUp(self):
        # Crée un DAO simulé
        self.dao = IngredientDao()
        # On "mock" la méthode rechercher_ingredient_par_nom
        self.dao.rechercher_ingredient_par_nom = MagicMock()

    def test_rechercher_ingredient_par_nom_avec_alcool(self):
        # Simule une réponse de base de données
        ingr = Ingredient(1, "Vodka", True)
        self.dao.rechercher_ingredient_par_nom.return_value = ingr

        result = self.dao.rechercher_ingredient_par_nom("Vodka")
        self.assertTrue(result.ingredient_alcool)
        self.assertEqual(result.nom, "Vodka")

    def test_rechercher_ingredient_par_nom_sans_alcool(self):
        ingr = Ingredient(2, "Jus d'orange", False)
        self.dao.rechercher_ingredient_par_nom.return_value = ingr

        result = self.dao.rechercher_ingredient_par_nom("Jus d'orange")
        self.assertFalse(result.ingredient_alcool)

    def test_rechercher_ingredient_par_nom_introuvable(self):
        self.dao.rechercher_ingredient_par_nom.return_value = None
        result = self.dao.rechercher_ingredient_par_nom("Inconnu")
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
