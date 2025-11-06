import unittest
from datetime import date
from unittest.mock import MagicMock, patch

from src.business_object.stock import Stock
from src.business_object.utilisateur import Utilisateur
from src.dao.stock_course_dao import Stock_course_dao


class TestStockCourseDao(unittest.TestCase):
    """Tests unitaires de la classe Stock_course_dao."""

    def _setup_mock_db(self, mock_db, fetchone_return=None):
        """Helper pour configurer le mock de la base de données."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = fetchone_return

        # Configure les context managers
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection.cursor.return_value.__exit__.return_value = None
        mock_db.return_value.connection.__enter__.return_value = mock_connection
        mock_db.return_value.connection.__exit__.return_value = None

        return mock_cursor

    @patch("src.dao.stock_course_dao.DBConnection")
    def test_get_stock_succes(self, mock_db):
        """Teste que get_stock renvoie bien le stock attendu."""
        mock_cursor = self._setup_mock_db(mock_db, fetchone_return=(1, 2.5, 3))

        stock = Stock(1, "Stock_Mehdi")
        res = Stock_course_dao.get_stock(stock)

        self.assertEqual(res, (1, 2.5, 3))
        mock_cursor.execute.assert_called_once()

    @patch("src.dao.stock_course_dao.DBConnection")
    def test_get_stock_aucun_resultat(self, mock_db):
        """Teste que get_stock renvoie None si aucun stock trouvé."""
        mock_cursor = self._setup_mock_db(mock_db, fetchone_return=None)

        stock = Stock(1, "Stock_Mehdi")
        res = Stock_course_dao.get_stock(stock)

        self.assertIsNone(res)

    @patch("src.dao.stock_course_dao.DBConnection")
    def test_update_ingredient_stock_succes(self, mock_db):
        """Teste la mise à jour réussie d'un ingrédient dans le stock."""
        mock_cursor = self._setup_mock_db(mock_db, fetchone_return=(1,))

        res = Stock_course_dao.update_ingredient_stock(1, 100.0, 2)

        self.assertTrue(res)
        mock_cursor.execute.assert_called_once()

    @patch("src.dao.stock_course_dao.DBConnection")
    def test_update_ingredient_stock_echec(self, mock_db):
        """Teste la mise à jour échouée d'un ingrédient (fetchone retourne None)."""
        mock_cursor = self._setup_mock_db(mock_db, fetchone_return=None)

        # Avec le bug corrigé (updated = False au début), ça devrait retourner False
        res = Stock_course_dao.update_ingredient_stock(1, 50.0, 2)
        self.assertFalse(res)

    @patch("src.dao.stock_course_dao.DBConnection")
    def test_delete_ingredient_stock_succes(self, mock_db):
        """Teste la suppression réussie d'un ingrédient du stock."""
        mock_cursor = self._setup_mock_db(mock_db, fetchone_return=(1,))

        res = Stock_course_dao.delete_ingredient_stock(1, 20.0, 2)

        self.assertTrue(res)
        mock_cursor.execute.assert_called_once()

    @patch("src.dao.stock_course_dao.DBConnection")
    def test_delete_ingredient_stock_echec(self, mock_db):
        """Teste l'échec de suppression d'un ingrédient."""
        mock_cursor = self._setup_mock_db(mock_db, fetchone_return=None)

        res = Stock_course_dao.delete_ingredient_stock(1, 20.0, 2)
        self.assertFalse(res)

    @patch("src.dao.stock_course_dao.DBConnection")
    def test_get_liste_course_succes(self, mock_db):
        """Teste la récupération de la liste de course d'un utilisateur."""
        mock_cursor = self._setup_mock_db(mock_db, fetchone_return=(1, 2.0, 3))

        utilisateur = Utilisateur(5, "Mehdi", date(2000, 1, 1))
        res = Stock_course_dao.get_liste_course(utilisateur)

        self.assertEqual(res, (1, 2.0, 3))
        mock_cursor.execute.assert_called_once()

    @patch("src.dao.stock_course_dao.DBConnection")
    def test_get_liste_course_aucun_resultat(self, mock_db):
        """Teste la récupération d'une liste de course vide."""
        mock_cursor = self._setup_mock_db(mock_db, fetchone_return=None)

        utilisateur = Utilisateur(5, "Mehdi", date(2000, 1, 1))
        res = Stock_course_dao.get_liste_course(utilisateur)

        self.assertIsNone(res)

    @patch("src.dao.stock_course_dao.DBConnection")
    def test_updtate_liste_course_succes(self, mock_db):
        """Teste la mise à jour réussie d'un ingrédient dans la liste de course."""
        mock_cursor = self._setup_mock_db(mock_db, fetchone_return=(1,))

        res = Stock_course_dao.updtate_liste_course(1, 50.0, 3)

        self.assertTrue(res)
        mock_cursor.execute.assert_called_once()

    @patch("src.dao.stock_course_dao.DBConnection")
    def test_updtate_liste_course_echec(self, mock_db):
        """Teste l'échec de mise à jour dans la liste de course."""
        mock_cursor = self._setup_mock_db(mock_db, fetchone_return=None)

        res = Stock_course_dao.updtate_liste_course(1, 50.0, 3)
        self.assertFalse(res)

    @patch("src.dao.stock_course_dao.DBConnection")
    def test_delete_ingredient_liste_course_succes(self, mock_db):
        """Teste la suppression réussie d'un ingrédient dans la liste de course."""
        mock_cursor = self._setup_mock_db(mock_db, fetchone_return=(1,))

        res = Stock_course_dao.delete_ingredient_liste_course(1, 20.0, 3)

        self.assertTrue(res)
        mock_cursor.execute.assert_called_once()

    @patch("src.dao.stock_course_dao.DBConnection")
    def test_delete_ingredient_liste_course_echec(self, mock_db):
        """Teste l'échec de suppression dans la liste de course."""
        mock_cursor = self._setup_mock_db(mock_db, fetchone_return=None)

        res = Stock_course_dao.delete_ingredient_liste_course(1, 20.0, 3)
        self.assertFalse(res)


if __name__ == "__main__":
    unittest.main()
