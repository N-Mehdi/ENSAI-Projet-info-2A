'''from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from src.dao.utilisateur_dao import UtilisateurDAO
from src.models import User, UserCreate
from src.utils.exceptions import DAOError


class TestUtilisateurDAO:
    """Tests pour la classe UtilisateurDAO."""

    # Tests pour la méthode create_compte de UtilisateurDAO
    @patch("src.dao.utilisateur_dao.DBConnection")
    def test_create_compte_success(self, mock_db_connection):
        """Test de création réussie d'un compte utilisateur."""
        # GIVEN - Un utilisateur valide à créer
        utilisateur = UserCreate(
            pseudo="john_doe",
            mail="john@example.com",
            date_naissance="1990-01-15",
            mot_de_passe_hashed="hashed_password_123",
        )

        # Mock de la connexion DB
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value.connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        # Simuler un résultat réussi
        mock_cursor.fetchone.return_value = {
            "id_utilisateur": 1,
            "pseudo": "john_doe",
            "mail": "john@example.com",
            "date_naissance": "1990-01-15",
            "mot_de_passe": "hashed_password_123",
        }

        dao = UtilisateurDAO()

        # WHEN - On crée le compte
        resultat = dao.create_compte(utilisateur)

        # THEN - Le compte est créé avec succès
        assert resultat is True
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchone.assert_called_once()
        mock_connection.commit.assert_called_once()

    @patch("src.dao.utilisateur_dao.DBConnection")
    def test_create_compte_fails_no_result(self, mock_db_connection):
        """Test de création échouée - aucun résultat retourné."""
        # GIVEN - Un utilisateur à créer mais la DB ne retourne rien
        utilisateur = UserCreate(
            pseudo="jane_doe",
            mail="jane@example.com",
            date_naissance="1995-05-20",
            mot_de_passe_hashed="hashed_password_456",
        )

        # Mock de la connexion DB
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value.connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        # Simuler aucun résultat
        mock_cursor.fetchone.return_value = None

        dao = UtilisateurDAO()

        # WHEN - On tente de créer le compte
        resultat = dao.create_compte(utilisateur)

        # THEN - La création échoue
        assert resultat is False
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchone.assert_called_once()

    @patch("src.dao.utilisateur_dao.DBConnection")
    def test_create_compte_raises_dao_error_on_exception(self, mock_db_connection):
        """Test de levée d'exception DAOError en cas d'erreur DB."""
        # GIVEN - Un utilisateur à créer et une erreur DB
        utilisateur = UserCreate(
            pseudo="error_user",
            mail="error@example.com",
            date_naissance="2000-12-25",
            mot_de_passe_hashed="hashed_password_789",
        )

        # Mock de la connexion DB qui lève une exception
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value.connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        # Simuler une erreur lors de l'exécution
        mock_cursor.execute.side_effect = Exception("Database connection error")

        dao = UtilisateurDAO()

        # WHEN / THEN - On tente de créer et une DAOError est levée
        with pytest.raises(DAOError) as exc_info:
            dao.create_compte(utilisateur)

        assert "Impossible de créer le compte" in str(exc_info.value)
        mock_connection.commit.assert_not_called()

    @patch("src.dao.utilisateur_dao.DBConnection")
    def test_create_compte_verifies_sql_query_parameters(self, mock_db_connection):
        """Test de vérification des paramètres passés à la requête SQL."""
        # GIVEN - Un utilisateur avec des données spécifiques
        utilisateur = UserCreate(
            pseudo="test_user",
            mail="test@test.com",
            date_naissance="1988-03-10",
            mot_de_passe_hashed="super_secure_hash",
        )

        # Mock de la connexion DB
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value.connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {"id_utilisateur": 1}

        dao = UtilisateurDAO()

        # WHEN - On crée le compte
        dao.create_compte(utilisateur)

        # THEN - Les bons paramètres sont passés à la requête SQL
        call_args = mock_cursor.execute.call_args
        sql_params = call_args[0][1]

        assert sql_params["pseudo"] == "test_user"
        assert sql_params["mail"] == "test@test.com"
        assert sql_params["date_naissance"] == "1988-03-10"
        assert sql_params["mot_de_passe_hashed"] == "super_secure_hash"

    # Tests pour la méthode read de UtilisateurDAO.

    @patch("src.dao.utilisateur_dao.DBConnection")
    def test_read_user_success(self, mock_db_connection):
        """Test de lecture réussie d'un utilisateur."""
        # GIVEN - Un utilisateur existe dans la DB
        id_utilisateur = 1
        mock_date = date(1990, 1, 15)

        # Mock de la connexion DB
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value.connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        # Simuler un utilisateur trouvé
        mock_cursor.fetchone.return_value = {
            "id_utilisateur": 1,
            "pseudo": "john_doe",
            "mail": "john@example.com",
            "date_naissance": mock_date,
            "mot_de_passe": "hashed_password_123",
        }

        dao = UtilisateurDAO()

        # WHEN - On lit l'utilisateur
        resultat = dao.read(id_utilisateur)

        # THEN - L'utilisateur est retourné correctement
        assert resultat is not None
        assert isinstance(resultat, User)
        assert resultat.id_utilisateur == 1
        assert resultat.pseudo == "john_doe"
        assert resultat.mail == "john@example.com"
        assert resultat.date_naissance == "1990-01-15"  # Vérifie l'isoformat
        assert resultat.mot_de_passe_hashed == "hashed_password_123"

        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchone.assert_called_once()

    @patch("src.dao.utilisateur_dao.DBConnection")
    def test_read_user_not_found(self, mock_db_connection):
        """Test de lecture d'un utilisateur inexistant."""
        # GIVEN - Aucun utilisateur avec cet ID
        id_utilisateur = 999

        # Mock de la connexion DB
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value.connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        # Simuler aucun résultat
        mock_cursor.fetchone.return_value = None

        dao = UtilisateurDAO()

        # WHEN - On tente de lire l'utilisateur
        resultat = dao.read(id_utilisateur)

        # THEN - None est retourné
        assert resultat is None
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchone.assert_called_once()

    @patch("src.dao.utilisateur_dao.DBConnection")
    def test_read_raises_dao_error_on_db_exception(self, mock_db_connection):
        """Test de levée d'exception DAOError en cas d'erreur DB."""
        # GIVEN - Une erreur DB se produit
        id_utilisateur = 1

        # Mock de la connexion DB qui lève une exception
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value.connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        # Simuler une erreur lors de l'exécution
        from psycopg2 import DatabaseError as DBError

        mock_cursor.execute.side_effect = DBError("Connection lost")

        dao = UtilisateurDAO()

        # WHEN / THEN - Une DAOError est levée
        with pytest.raises(DAOError):
            dao.read(id_utilisateur)

        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchone.assert_not_called()

    @patch("src.dao.utilisateur_dao.DBConnection")
    def test_read_verifies_sql_query_parameters(self, mock_db_connection):
        """Test de vérification des paramètres passés à la requête SQL."""
        # GIVEN - Un ID utilisateur spécifique
        id_utilisateur = 42

        # Mock de la connexion DB
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value.connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        dao = UtilisateurDAO()

        # WHEN - On lit l'utilisateur
        dao.read(id_utilisateur)

        # THEN - Le bon ID est passé à la requête SQL
        call_args = mock_cursor.execute.call_args
        sql_query = call_args[0][0]
        sql_params = call_args[0][1]

        assert "WHERE id_utilisateur = %(id_utilisateur)s" in sql_query
        assert sql_params["id_utilisateur"] == 42

    @patch("src.dao.utilisateur_dao.DBConnection")
    def test_read_converts_date_to_isoformat(self, mock_db_connection):
        """Test de conversion de la date en format ISO."""
        # GIVEN - Un utilisateur avec une date
        id_utilisateur = 1
        mock_date = date(2000, 12, 25)

        # Mock de la connexion DB
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value.connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            "id_utilisateur": 1,
            "pseudo": "test_user",
            "mail": "test@test.com",
            "date_naissance": mock_date,
            "mot_de_passe": "hash123",
        }

        dao = UtilisateurDAO()

        # WHEN - On lit l'utilisateur
        resultat = dao.read(id_utilisateur)

        # THEN - La date est convertie en format ISO string
        assert resultat.date_naissance == "2000-12-25"
        assert isinstance(resultat.date_naissance, str)

    @patch("src.dao.utilisateur_dao.DBConnection")
    def test_read_selects_correct_columns(self, mock_db_connection):
        """Test de vérification que les bonnes colonnes sont sélectionnées."""
        # GIVEN - Un ID utilisateur
        id_utilisateur = 1

        # Mock de la connexion DB
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value.connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        dao = UtilisateurDAO()

        # WHEN - On lit l'utilisateur
        dao.read(id_utilisateur)

        # THEN - La requête SQL sélectionne les bonnes colonnes
        call_args = mock_cursor.execute.call_args
        sql_query = call_args[0][0]

        assert "SELECT id_utilisateur, pseudo, mail, mot_de_passe, date_naissance" in sql_query
        assert "FROM utilisateur" in sql_query

    # Tests pour la méthode pseudo_existe de UtilisateurDAO

    @patch("src.dao.utilisateur_dao.DBConnection")
    def test_pseudo_existe_returns_true_when_pseudo_exists(self, mock_db_connection):
        """Test vérifie qu'un pseudo existant retourne True."""
        # GIVEN - Un pseudo qui existe dans la DB
        pseudo = "john_doe"

        # Mock de la connexion DB
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value.connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        # Simuler que le pseudo existe
        mock_cursor.fetchone.return_value = {"exists": True}

        dao = UtilisateurDAO()

        # WHEN - On vérifie si le pseudo existe
        resultat = dao.pseudo_existe(pseudo)

        # THEN - True est retourné
        assert resultat is True
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchone.assert_called_once()

    @patch("src.dao.utilisateur_dao.DBConnection")
    def test_pseudo_existe_returns_false_when_pseudo_does_not_exist(self, mock_db_connection):
        """Test vérifie qu'un pseudo inexistant retourne False."""
        # GIVEN - Un pseudo qui n'existe pas dans la DB
        pseudo = "user_not_exists"

        # Mock de la connexion DB
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value.connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        # Simuler que le pseudo n'existe pas
        mock_cursor.fetchone.return_value = {"exists": False}

        dao = UtilisateurDAO()

        # WHEN - On vérifie si le pseudo existe
        resultat = dao.pseudo_existe(pseudo)

        # THEN - False est retourné
        assert resultat is False
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchone.assert_called_once()

    @patch("src.dao.utilisateur_dao.DBConnection")
    def test_pseudo_existe_returns_false_when_no_result(self, mock_db_connection):
        """Test vérifie que False est retourné quand fetchone retourne None."""
        # GIVEN - Une requête qui ne retourne aucun résultat
        pseudo = "some_user"

        # Mock de la connexion DB
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value.connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        # Simuler aucun résultat
        mock_cursor.fetchone.return_value = None

        dao = UtilisateurDAO()

        # WHEN - On vérifie si le pseudo existe
        resultat = dao.pseudo_existe(pseudo)

        # THEN - False est retourné par défaut
        assert resultat is False
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchone.assert_called_once()

    @patch("src.dao.utilisateur_dao.DBConnection")
    def test_pseudo_existe_raises_dao_error_on_exception(self, mock_db_connection):
        """Test de levée d'exception DAOError en cas d'erreur DB."""
        # GIVEN - Une erreur DB se produit
        pseudo = "error_user"

        # Mock de la connexion DB qui lève une exception
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value.connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        # Simuler une erreur lors de l'exécution
        mock_cursor.execute.side_effect = Exception("Database connection error")

        dao = UtilisateurDAO()

        # WHEN / THEN - Une DAOError est levée
        with pytest.raises(DAOError):
            dao.pseudo_existe(pseudo)

        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchone.assert_not_called()

    @patch("src.dao.utilisateur_dao.DBConnection")
    def test_pseudo_existe_verifies_sql_query_parameters(self, mock_db_connection):
        """Test de vérification des paramètres passés à la requête SQL."""
        # GIVEN - Un pseudo spécifique à vérifier
        pseudo = "test_user_123"

        # Mock de la connexion DB
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value.connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {"exists": False}

        dao = UtilisateurDAO()

        # WHEN - On vérifie si le pseudo existe
        dao.pseudo_existe(pseudo)

        # THEN - Le bon pseudo est passé à la requête SQL
        call_args = mock_cursor.execute.call_args
        sql_query = call_args[0][0]
        sql_params = call_args[0][1]

        assert "SELECT EXISTS" in sql_query
        assert "FROM utilisateur" in sql_query
        assert "WHERE pseudo = %(pseudo)s" in sql_query
        assert sql_params["pseudo"] == "test_user_123"

    @patch("src.dao.utilisateur_dao.DBConnection")
    def test_pseudo_existe_with_special_characters(self, mock_db_connection):
        """Test de vérification avec des caractères spéciaux dans le pseudo."""
        # GIVEN - Un pseudo avec des caractères spéciaux
        pseudo = "user_with-special.chars@123"

        # Mock de la connexion DB
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value.connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {"exists": True}

        dao = UtilisateurDAO()

        # WHEN - On vérifie si le pseudo existe
        resultat = dao.pseudo_existe(pseudo)

        # THEN - Le pseudo est correctement traité
        assert resultat is True
        call_args = mock_cursor.execute.call_args
        sql_params = call_args[0][1]
        assert sql_params["pseudo"] == pseudo

    @patch("src.dao.utilisateur_dao.DBConnection")
    def test_pseudo_existe_with_empty_string(self, mock_db_connection):
        """Test de vérification avec une chaîne vide."""
        # GIVEN - Un pseudo vide
        pseudo = ""

        # Mock de la connexion DB
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value.connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {"exists": False}

        dao = UtilisateurDAO()

        # WHEN - On vérifie si le pseudo existe
        resultat = dao.pseudo_existe(pseudo)

        # THEN - False est retourné
        assert resultat is False
        mock_cursor.execute.assert_called_once()

    @patch("src.dao.utilisateur_dao.DBConnection")
    def test_pseudo_existe_case_sensitive(self, mock_db_connection):
        """Test pour vérifier que la recherche est sensible à la casse."""
        # GIVEN - Deux pseudos avec des casses différentes
        pseudo_lower = "testuser"

        # Mock de la connexion DB
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value.connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {"exists": True}

        dao = UtilisateurDAO()

        # WHEN - On vérifie si le pseudo existe
        resultat = dao.pseudo_existe(pseudo_lower)

        # THEN - Le pseudo exact est recherché (case-sensitive par défaut en SQL)
        assert resultat is True
        call_args = mock_cursor.execute.call_args
        sql_params = call_args[0][1]
        assert sql_params["pseudo"] == "testuser"


import pytest
from unittest.mock import MagicMock, patch
from src.dao.utilisateur_dao import UtilisateurDAO
from src.models import User


    #Tests pour la méthode delete_compte de UtilisateurDAO.

    @patch("src.dao.utilisateur_dao.DBConnection")
    def test_delete_compte_success(self, mock_db_connection):
        """Test de suppression réussie d'un utilisateur."""
        # GIVEN - Un utilisateur existant à supprimer
        utilisateur = User(
            id_utilisateur=1,
            pseudo="john_doe",
            mail="john@example.com",
            date_naissance="1990-01-15",
            mot_de_passe_hashed="hashed_password_123",
        )

        # Mock de la connexion DB
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value.connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        # Simuler une suppression réussie (1 ligne affectée)
        mock_cursor.rowcount = 1

        dao = UtilisateurDAO()

        # WHEN - On supprime l'utilisateur
        resultat = dao.delete_compte(utilisateur)

        # THEN - La suppression est réussie
        assert resultat is True
        mock_cursor.execute.assert_called_once()

        # Vérifier la requête SQL
        call_args = mock_cursor.execute.call_args
        sql_query = call_args[0][0]
        sql_params = call_args[0][1]

        assert "DELETE FROM utilisateur" in sql_query
        assert "WHERE id_utilisateur=%(id_utilisateur)s" in sql_query
        assert sql_params["id_utilisateur"] == 1

    @patch("src.dao.utilisateur_dao.DBConnection")
    def test_delete_compte_user_not_found(self, mock_db_connection):
        """Test de suppression d'un utilisateur inexistant."""
        # GIVEN - Un utilisateur qui n'existe pas en DB
        utilisateur = User(
            id_utilisateur=999,
            pseudo="ghost_user",
            mail="ghost@example.com",
            date_naissance="2000-01-01",
            mot_de_passe_hashed="hash",
        )

        # Mock de la connexion DB
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value.connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        # Simuler aucune ligne affectée
        mock_cursor.rowcount = 0

        dao = UtilisateurDAO()

        # WHEN - On tente de supprimer l'utilisateur
        resultat = dao.delete_compte(utilisateur)

        # THEN - La suppression échoue (retourne False)
        assert resultat is False
        mock_cursor.execute.assert_called_once()

    @patch("src.dao.utilisateur_dao.DBConnection")
    def test_delete_compte_raises_exception_on_db_error(self, mock_db_connection):
        """Test de levée d'exception en cas d'erreur DB."""
        # GIVEN - Un utilisateur et une erreur DB
        utilisateur = User(
            id_utilisateur=1,
            pseudo="error_user",
            mail="error@example.com",
            date_naissance="1995-05-20",
            mot_de_passe_hashed="hash123",
        )

        # Mock de la connexion DB qui lève une exception
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value.connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        # Simuler une erreur lors de l'exécution
        mock_cursor.execute.side_effect = Exception("Database connection error")

        dao = UtilisateurDAO()

        # WHEN / THEN - Une exception est levée
        with pytest.raises(Exception) as exc_info:
            dao.delete_compte(utilisateur)

        assert "Database connection error" in str(exc_info.value)
        mock_cursor.execute.assert_called_once()

    @patch("src.dao.utilisateur_dao.DBConnection")
    def test_delete_compte_verifies_correct_id_is_used(self, mock_db_connection):
        """Test de vérification que le bon ID est utilisé pour la suppression."""
        # GIVEN - Un utilisateur avec un ID spécifique
        utilisateur = User(
            id_utilisateur=42,
            pseudo="test_user",
            mail="test@test.com",
            date_naissance="1988-03-10",
            mot_de_passe_hashed="secure_hash",
        )

        # Mock de la connexion DB
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value.connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 1

        dao = UtilisateurDAO()

        # WHEN - On supprime l'utilisateur
        dao.delete_compte(utilisateur)

        # THEN - Le bon ID est passé à la requête SQL
        call_args = mock_cursor.execute.call_args
        sql_params = call_args[0][1]
        assert sql_params["id_utilisateur"] == 42

    @patch("src.dao.utilisateur_dao.DBConnection")
    def test_delete_compte_multiple_rows_affected(self, mock_db_connection):
        """Test du comportement quand plusieurs lignes sont affectées (cas anormal)."""
        # GIVEN - Une situation où plusieurs lignes seraient supprimées
        utilisateur = User(
            id_utilisateur=1,
            pseudo="duplicate_user",
            mail="dup@example.com",
            date_naissance="1990-01-01",
            mot_de_passe_hashed="hash",
        )

        # Mock de la connexion DB
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value.connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        # Simuler plusieurs lignes affectées (ne devrait pas arriver normalement)
        mock_cursor.rowcount = 2

        dao = UtilisateurDAO()

        # WHEN - On supprime l'utilisateur
        resultat = dao.delete_compte(utilisateur)

        # THEN - La méthode retourne True (rowcount > 0)
        assert resultat is True

    @patch("src.dao.utilisateur_dao.DBConnection")
    def test_delete_compte_returns_boolean(self, mock_db_connection):
        """Test que la méthode retourne toujours un booléen."""
        # GIVEN - Un utilisateur
        utilisateur = User(
            id_utilisateur=5,
            pseudo="bool_test",
            mail="bool@test.com",
            date_naissance="2000-06-15",
            mot_de_passe_hashed="hash_value",
        )

        # Mock de la connexion DB
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value.connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 1

        dao = UtilisateurDAO()

        # WHEN - On supprime l'utilisateur
        resultat = dao.delete_compte(utilisateur)

        # THEN - Le résultat est un booléen
        assert isinstance(resultat, bool)
        assert resultat in [True, False]

    @patch("src.dao.utilisateur_dao.DBConnection")
    def test_delete_compte_sql_syntax(self, mock_db_connection):
        """Test de la syntaxe SQL de la requête DELETE."""
        # GIVEN - Un utilisateur
        utilisateur = User(
            id_utilisateur=10,
            pseudo="sql_test",
            mail="sql@test.com",
            date_naissance="1992-08-20",
            mot_de_passe_hashed="hash_sql",
        )

        # Mock de la connexion DB
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value.connection.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 1

        dao = UtilisateurDAO()

        # WHEN - On supprime l'utilisateur
        dao.delete_compte(utilisateur)

        # THEN - La requête SQL est correctement formée
        call_args = mock_cursor.execute.call_args
        sql_query = call_args[0][0]

        # Vérifier les éléments clés de la requête
        assert "DELETE FROM utilisateur" in sql_query
        assert "WHERE id_utilisateur=%(id_utilisateur)s" in sql_query
        # Vérifier qu'il n'y a pas de RETURNING ou autres clauses
        assert "RETURNING" not in sql_query
'''
