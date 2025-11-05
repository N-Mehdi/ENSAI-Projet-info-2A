"""test_stock.py .
-------------
Tests unitaires pour la classe Stock.
"""

import unittest

from src.business_object.stock import Stock


class TestStock(unittest.TestCase):
    """Tests unitaires pour le business object Stock."""

    def test_creation_stock(self):
        """Teste la création d'un objet Stock et ses attributs."""
        stock = Stock(1, "Stock_Test")

        self.assertEqual(stock.id_stock, 1)
        self.assertEqual(stock.nom, "Stock_Test")

    def test_attributs_types(self):
        """Teste que les attributs ont le bon type."""
        stock = Stock(42, "Stock_Test")

        self.assertIsInstance(stock.id_stock, int)
        self.assertIsInstance(stock.nom, str)


if __name__ == "__main__":
    unittest.main()
