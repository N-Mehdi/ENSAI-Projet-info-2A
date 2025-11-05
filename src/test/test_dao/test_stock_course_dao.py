import unittest
from unittest.mock import MagicMock

from src.business_object.stock import Stock
from src.dao.stock_course_dao import Stock_course_dao


class TestStockCourseDao(unittest.TestCase):
    """Tests unitaires de la classe Stock_course_dao."""

    def setUp(self):
        """Initialisation d'un DAO simulé avant chaque test."""
        self.dao = Stock_course_dao()
        self.dao.get_stock = MagicMock()
        self.dao.update_ingredient_stock = MagicMock()
        self.dao.delete_ingredient_stock = MagicMock()
        self.dao.get_liste_course = MagicMock()
        self.dao.updtate_liste_course = MagicMock()
        self.dao.delete_ingredient_liste_course = MagicMock()

        # Stock d'exemple pour le test
        self.stock = Stock(1, "Stock_Mehdi")

    def test_get_stock_succes(self):
        """Teste que get_stock renvoie bien le stock attendu."""
        resultat_attendu = [(1, 2.5, 3)]
        self.dao.get_stock.return_value = resultat_attendu

        res = self.dao.get_stock(self.stock)

        self.assertEqual(res, resultat_attendu)
        self.dao.get_stock.assert_called_once_with(self.stock)

    def test_get_stock_aucun_resultat(self):
        """Teste que get_stock renvoie None si aucun stock trouvé."""
        self.dao.get_stock.return_value = None

        res = self.dao.get_stock(self.stock)
        self.assertIsNone(res)

    def test_update_ingredient_stock_succes(self):
        """Teste la mise à jour réussie d’un ingrédient dans le stock."""
        self.dao.update_ingredient_stock.return_value = True

        res = self.dao.update_ingredient_stock(1, 100.0, 2)
        self.assertTrue(res)

    def test_update_ingredient_stock_echec(self):
        """Teste la mise à jour échouée d’un ingrédient."""
        self.dao.update_ingredient_stock.return_value = False

        res = self.dao.update_ingredient_stock(1, 50.0, 2)
        self.assertFalse(res)

    def test_delete_ingredient_stock(self):
        """Teste la suppression d’un ingrédient du stock."""
        self.dao.delete_ingredient_stock.return_value = True

        res = self.dao.delete_ingredient_stock(1, 20.0, 2)
        self.assertTrue(res)

    def test_get_liste_course(self):
        """Teste la récupération de la liste de course d’un utilisateur."""
        resultat_attendu = [(1, 2.0, 3)]
        self.dao.get_liste_course.return_value = resultat_attendu

        utilisateur = MagicMock()
        utilisateur.id_utilisateur = 5

        res = self.dao.get_liste_course(utilisateur)

        self.assertEqual(res, resultat_attendu)
        self.dao.get_liste_course.assert_called_once_with(utilisateur)

    def test_updtate_liste_course_succes(self):
        """Teste la mise à jour réussie d’un ingrédient dans la liste de course."""
        self.dao.updtate_liste_course.return_value = True

        res = self.dao.updtate_liste_course(1, 50.0, 3)
        self.assertTrue(res)

    def test_delete_ingredient_liste_course(self):
        """Teste la suppression d’un ingrédient dans la liste de course."""
        self.dao.delete_ingredient_liste_course.return_value = True

        res = self.dao.delete_ingredient_liste_course(1, 20.0, 3)
        self.assertTrue(res)


if __name__ == "__main__":
    unittest.main()
