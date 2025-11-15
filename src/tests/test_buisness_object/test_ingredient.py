"""import unittest

from src.business_object.ingredient import Ingredient


class TestIngredient(unittest.TestCase):
    def test_creation_ingredient(self):
        ingredient = Ingredient(id_ingredient=1, nom="Vodka", ingredient_alcool=True)
        self.assertEqual(ingredient.nom, "Vodka")
        self.assertTrue(ingredient.ingredient_alcool)
        self.assertEqual(ingredient.id_ingredient, 1)

    def test_str(self):
        alcool = Ingredient(1, "Rhum", True)
        sans_alcool = Ingredient(2, "Jus d'orange", False)
        self.assertIn("alcoolisé", str(alcool))
        self.assertIn("non alcoolisé", str(sans_alcool))

    def test_as_list(self):
        ingredient = Ingredient(3, "Tequila", True)
        result = ingredient.as_list()
        self.assertEqual(result, ["3", "Tequila", "True"])
"""
