"""test_stock_course_service.py .
----------------------------
Tests unitaires pour Stock_course_service.
"""

import unittest
from datetime import date
from unittest.mock import patch

from src.business_object.stock import Stock
from src.business_object.utilisateur import Utilisateur
from src.service.stock_course_service import Stock_course_service


class TestStockCourseService(unittest.TestCase):
    """Tests unitaires pour Stock_course_service."""

    def setUp(self):
        self.stock = Stock(1, "Stock_Mehdi")
        self.utilisateur = Utilisateur(1, "Mehdi", date(2000, 1, 1))

    @patch("src.service.stock_course_service.Stock_course_dao.get_stock")
    def test_get_stock_succes(self, mock_get_stock):
        """Teste la récupération d'un stock avec des ingrédients."""
        mock_get_stock.return_value = [(1, 2.5, 3), (2, 1.0, 1)]

        result = Stock_course_service.get_stock(self.stock)

        self.assertIsInstance(result, Stock)
        self.assertEqual(result.id_stock, 1)
        self.assertEqual(result.nom, "Stock_Mehdi")
        self.assertEqual(result.ingredients, [(1, 2.5, 3), (2, 1.0, 1)])
        mock_get_stock.assert_called_once_with(self.stock)

    @patch("src.service.stock_course_service.Stock_course_dao.get_stock")
    def test_get_stock_none(self, mock_get_stock):
        """Teste la récupération d'un stock inexistant."""
        mock_get_stock.return_value = None

        result = Stock_course_service.get_stock(self.stock)
        self.assertIsNone(result)

    @patch("src.service.stock_course_service.Stock_course_dao.update_ingredient_stock")
    def test_modifier_quantite_ingredient(self, mock_update):
        """Teste la modification de la quantité d'un ingrédient."""
        mock_update.return_value = True
        updated = Stock_course_service.modifier_quantite_ingredient(1, 5.0, 1)
        self.assertTrue(updated)
        mock_update.assert_called_once_with(1, 5.0, 1)

    @patch("src.service.stock_course_service.Stock_course_dao.delete_ingredient_stock")
    def test_retirer_du_stock(self, mock_delete):
        """Teste la suppression d'un ingrédient du stock."""
        mock_delete.return_value = True
        updated = Stock_course_service.retirer_du_stock(1, 2.0, 1)
        self.assertTrue(updated)
        mock_delete.assert_called_once_with(1, 2.0, 1)

    @patch("src.service.stock_course_service.Stock_course_dao.get_liste_course")
    def test_get_liste_course_utilisateur(self, mock_get_list):
        """Teste la récupération de la liste de courses."""
        mock_get_list.return_value = [(1, 3.0, 1)]
        result = Stock_course_service.get_liste_course_utilisateur(self.utilisateur)
        self.assertEqual(result, [(1, 3.0, 1)])
        mock_get_list.assert_called_once_with(self.utilisateur)

    @patch("src.service.stock_course_service.Stock_course_dao.updtate_liste_course")
    def test_modifier_liste_course(self, mock_update_list):
        """Teste la modification d'un ingrédient dans la liste de courses."""
        mock_update_list.return_value = True
        updated = Stock_course_service.modifier_liste_course(1, 5.0, 1)
        self.assertTrue(updated)
        mock_update_list.assert_called_once_with(1, 5.0, 1)

    @patch(
        "src.service.stock_course_service.Stock_course_dao.delete_ingredient_liste_course",
    )
    def test_retirer_de_liste_course(self, mock_delete_list):
        """Teste la suppression d'un ingrédient de la liste de courses."""
        mock_delete_list.return_value = True
        updated = Stock_course_service.retirer_de_liste_course(1, 2.0, 1)
        self.assertTrue(updated)
        mock_delete_list.assert_called_once_with(1, 2.0, 1)


if __name__ == "__main__":
    unittest.main()
