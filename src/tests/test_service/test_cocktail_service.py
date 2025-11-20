"""Tests pour le service CocktailService."""

from unittest.mock import MagicMock

import pytest

from src.business_object.cocktail import Cocktail
from src.dao.cocktail_dao import CocktailDAO
from src.service.cocktail_service import CocktailService
from src.utils.exceptions import DAOError, EmptyFieldError, ServiceError, CocktailSearchError


@pytest.fixture
def mock_cocktail_dao():
    """Fixture pour créer un mock de CocktailDAO."""
    return MagicMock(spec=CocktailDAO)


@pytest.fixture
def mock_stock_dao():
    """Fixture pour créer un mock de StockCourseDAO."""
    return MagicMock()


@pytest.fixture
def cocktail_service(mock_cocktail_dao):
    """Fixture pour créer une instance de CocktailService avec des mocks."""
    service = CocktailService(mock_cocktail_dao)
    return service


@pytest.fixture
def sample_cocktail():
    """Fixture pour créer un cocktail de test."""
    return Cocktail(
        id_cocktail=1,
        nom="Mojito",
        categorie="Cocktail",
        verre="Highball glass",
        alcool=True,
        image="mojito.jpg",
    )


class TestRechercherCocktailParNom:
    """Tests pour la méthode rechercher_cocktail_par_nom."""

    def test_rechercher_cocktail_par_nom_success(self, cocktail_service, mock_cocktail_dao, sample_cocktail):
        """Test de recherche réussie d'un cocktail par nom."""
        # Arrange
        mock_cocktail_dao.rechercher_cocktail_par_nom.return_value = sample_cocktail

        # Act
        result = cocktail_service.rechercher_cocktail_par_nom("Mojito")

        # Assert
        assert result == sample_cocktail
        mock_cocktail_dao.rechercher_cocktail_par_nom.assert_called_once_with("Mojito")

    def test_rechercher_cocktail_par_nom_vide(self, cocktail_service):
        """Test avec un nom vide."""
        # Act & Assert
        with pytest.raises(EmptyFieldError):
            cocktail_service.rechercher_cocktail_par_nom("")

    def test_rechercher_cocktail_par_nom_none(self, cocktail_service):
        """Test avec None comme nom."""
        # Act & Assert
        with pytest.raises(EmptyFieldError):
            cocktail_service.rechercher_cocktail_par_nom(None)

    def test_rechercher_cocktail_par_nom_type_invalide(self, cocktail_service):
        """Test avec un type invalide (non string)."""
        # Act & Assert
        with pytest.raises(CocktailSearchError):
            cocktail_service.rechercher_cocktail_par_nom(123)

    def test_rechercher_cocktail_par_nom_non_trouve(self, cocktail_service, mock_cocktail_dao):
        """Test quand aucun cocktail n'est trouvé."""
        # Arrange
        mock_cocktail_dao.rechercher_cocktail_par_nom.return_value = None

        # Act & Assert
        with pytest.raises(CocktailSearchError):
            cocktail_service.rechercher_cocktail_par_nom("CocktailInexistant")


class TestRechercherCocktailParSequenceDebut:
    """Tests pour la méthode rechercher_cocktail_par_sequence_debut."""

    def test_rechercher_par_sequence_success(self, cocktail_service, mock_cocktail_dao, sample_cocktail):
        """Test de recherche réussie par séquence."""
        # Arrange
        cocktails = [sample_cocktail]
        mock_cocktail_dao.rechercher_cocktail_par_sequence_debut.return_value = cocktails

        # Act
        result = cocktail_service.rechercher_cocktail_par_sequence_debut("Moj", 10)

        # Assert
        assert result == cocktails
        mock_cocktail_dao.rechercher_cocktail_par_sequence_debut.assert_called_once_with("Moj", 10)

    def test_rechercher_par_sequence_vide(self, cocktail_service):
        """Test avec une séquence vide."""
        # Act & Assert
        with pytest.raises(EmptyFieldError):
            cocktail_service.rechercher_cocktail_par_sequence_debut("", 10)

    def test_rechercher_par_sequence_type_invalide(self, cocktail_service):
        """Test avec un type invalide pour la séquence."""
        # Act & Assert
        with pytest.raises(CocktailSearchError):
            cocktail_service.rechercher_cocktail_par_sequence_debut(123, 10)

    def test_rechercher_par_sequence_max_resultats_invalide_type(self, cocktail_service):
        """Test avec un type invalide pour max_resultats."""
        # Act & Assert
        with pytest.raises(CocktailSearchError):
            cocktail_service.rechercher_cocktail_par_sequence_debut("Moj", "10")

    def test_rechercher_par_sequence_max_resultats_invalide_valeur(self, cocktail_service):
        """Test avec une valeur invalide pour max_resultats."""
        # Act & Assert
        with pytest.raises(CocktailSearchError):
            cocktail_service.rechercher_cocktail_par_sequence_debut("Moj", 0)

    def test_rechercher_par_sequence_aucun_resultat(self, cocktail_service, mock_cocktail_dao):
        """Test quand aucun cocktail n'est trouvé."""
        # Arrange
        mock_cocktail_dao.rechercher_cocktail_par_sequence_debut.return_value = []

        # Act & Assert
        with pytest.raises(CocktailSearchError):
            cocktail_service.rechercher_cocktail_par_sequence_debut("Xyz", 10)


class TestGetCocktailsRealisables:
    """Tests pour la méthode get_cocktails_realisables."""

    def test_get_cocktails_realisables_success(self, cocktail_service):
        """Test de récupération réussie des cocktails réalisables."""
        # Arrange
        id_utilisateur = 1

        # Mock du stock
        stock_rows = [
            {
                "id_ingredient": 1,
                "nom_ingredient": "Vodka",
                "quantite": 500.0,
                "code_unite": "ml",
            },
            {
                "id_ingredient": 2,
                "nom_ingredient": "Orange Juice",
                "quantite": 1000.0,
                "code_unite": "ml",
            },
        ]

        # Mock des cocktails
        cocktails_rows = [
            {
                "id_cocktail": 1,
                "nom": "Screwdriver",
                "categorie": "Ordinary Drink",
                "verre": "Highball glass",
                "alcool": True,
                "image": "screwdriver.jpg",
                "id_ingredient": 1,
                "qte": 50.0,
                "unite": "ml",
            },
            {
                "id_cocktail": 1,
                "nom": "Screwdriver",
                "categorie": "Ordinary Drink",
                "verre": "Highball glass",
                "alcool": True,
                "image": "screwdriver.jpg",
                "id_ingredient": 2,
                "qte": 200.0,
                "unite": "ml",
            },
        ]

        cocktail_service.stock_dao.get_stock = MagicMock(return_value=stock_rows)
        cocktail_service.cocktail_dao.get_tous_cocktails_avec_ingredients = MagicMock(
            return_value=cocktails_rows,
        )

        # Act
        result = cocktail_service.get_cocktails_realisables(id_utilisateur)

        # Assert
        assert "cocktails_realisables" in result
        assert "nombre_cocktails" in result
        assert result["nombre_cocktails"] == 1
        assert len(result["cocktails_realisables"]) == 1
        assert result["cocktails_realisables"][0]["nom"] == "Screwdriver"

    def test_get_cocktails_realisables_quantite_insuffisante(self, cocktail_service):
        """Test quand la quantité en stock est insuffisante."""
        # Arrange
        id_utilisateur = 1
        stock_rows = [
            {
                "id_ingredient": 1,
                "nom_ingredient": "Vodka",
                "quantite": 30.0,  # Insuffisant pour faire le cocktail
                "code_unite": "ml",
            },
        ]

        cocktails_rows = [
            {
                "id_cocktail": 1,
                "nom": "Vodka Shot",
                "categorie": "Shot",
                "verre": "Shot glass",
                "alcool": True,
                "image": "vodka_shot.jpg",
                "id_ingredient": 1,
                "qte": 50.0,
                "unite": "ml",
            },
        ]

        cocktail_service.stock_dao.get_stock = MagicMock(return_value=stock_rows)
        cocktail_service.cocktail_dao.get_tous_cocktails_avec_ingredients = MagicMock(
            return_value=cocktails_rows,
        )

        # Act
        result = cocktail_service.get_cocktails_realisables(id_utilisateur)

        # Assert
        assert result["nombre_cocktails"] == 0

    def test_get_cocktails_realisables_conversion_unites(self, cocktail_service):
        """Test avec conversion d'unités (cl vers ml)."""
        # Arrange
        id_utilisateur = 1
        stock_rows = [
            {
                "id_ingredient": 1,
                "nom_ingredient": "Vodka",
                "quantite": 10.0,  # 10 cl = 100 ml
                "code_unite": "cl",
            },
        ]

        cocktails_rows = [
            {
                "id_cocktail": 1,
                "nom": "Vodka Shot",
                "categorie": "Shot",
                "verre": "Shot glass",
                "alcool": True,
                "image": "vodka_shot.jpg",
                "id_ingredient": 1,
                "qte": 50.0,  # 50 ml requis
                "unite": "ml",
            },
        ]

        cocktail_service.stock_dao.get_stock = MagicMock(return_value=stock_rows)
        cocktail_service.cocktail_dao.get_tous_cocktails_avec_ingredients = MagicMock(
            return_value=cocktails_rows,
        )

        # Act
        result = cocktail_service.get_cocktails_realisables(id_utilisateur)

        # Assert
        assert result["nombre_cocktails"] == 1

    def test_get_cocktails_realisables_dao_error(self, cocktail_service):
        """Test avec erreur DAO."""
        # Arrange
        cocktail_service.stock_dao.get_stock = MagicMock(side_effect=DAOError("Erreur DAO"))

        # Act & Assert
        with pytest.raises(ServiceError):
            cocktail_service.get_cocktails_realisables(1)


class TestGetCocktailsQuasiRealisables:
    """Tests pour la méthode get_cocktails_quasi_realisables."""

    def test_get_cocktails_quasi_realisables_success(self, cocktail_service, mock_cocktail_dao):
        """Test de récupération réussie des cocktails quasi-réalisables."""
        # Arrange
        id_utilisateur = 1
        rows = [
            {
                "id_cocktail": 1,
                "nom": "Mojito",
                "categorie": "Cocktail",
                "verre": "Highball glass",
                "alcool": True,
                "image": "mojito.jpg",
                "id_ingredient": 1,
                "nom_ingredient": "Rhum Blanc",
                "quantite_requise": 50.0,
                "unite_requise": "ml",
                "quantite_stock": None,  # Manquant
                "unite_stock": None,
            },
            {
                "id_cocktail": 1,
                "nom": "Mojito",
                "categorie": "Cocktail",
                "verre": "Highball glass",
                "alcool": True,
                "image": "mojito.jpg",
                "id_ingredient": 2,
                "nom_ingredient": "Menthe",
                "quantite_requise": 10.0,
                "unite_requise": "g",
                "quantite_stock": 20.0,  # Disponible
                "unite_stock": "g",
            },
        ]

        mock_cocktail_dao.get_cocktails_quasi_realisables.return_value = rows

        # Act
        result = cocktail_service.get_cocktails_quasi_realisables(id_utilisateur, max_ingredients_manquants=1)

        # Assert
        assert "cocktails_quasi_realisables" in result
        assert "nombre_cocktails" in result
        assert result["nombre_cocktails"] == 1
        assert result["max_ingredients_manquants"] == 1
        cocktail = result["cocktails_quasi_realisables"][0]
        assert cocktail["nom"] == "Mojito"
        assert cocktail["nombre_ingredients_manquants"] == 1
        assert "Rhum Blanc" in cocktail["ingredients_manquants"]

    def test_get_cocktails_quasi_realisables_aucun_resultat(self, cocktail_service, mock_cocktail_dao):
        """Test quand aucun cocktail quasi-réalisable n'est trouvé."""
        # Arrange
        mock_cocktail_dao.get_cocktails_quasi_realisables.return_value = []

        # Act
        result = cocktail_service.get_cocktails_quasi_realisables(1, max_ingredients_manquants=1)

        # Assert
        assert result["nombre_cocktails"] == 0
        assert result["cocktails_quasi_realisables"] == []

    def test_get_cocktails_quasi_realisables_tri(self, cocktail_service, mock_cocktail_dao):
        """Test du tri des cocktails quasi-réalisables."""
        # Arrange
        rows = [
            # Cocktail A : 2 ingrédients manquants sur 3 (33% possession)
            {
                "id_cocktail": 1,
                "nom": "Cocktail A",
                "categorie": "Cocktail",
                "verre": "Glass",
                "alcool": True,
                "image": "a.jpg",
                "id_ingredient": 1,
                "nom_ingredient": "Ing1",
                "quantite_requise": 50.0,
                "unite_requise": "ml",
                "quantite_stock": None,
                "unite_stock": None,
            },
            {
                "id_cocktail": 1,
                "nom": "Cocktail A",
                "categorie": "Cocktail",
                "verre": "Glass",
                "alcool": True,
                "image": "a.jpg",
                "id_ingredient": 2,
                "nom_ingredient": "Ing2",
                "quantite_requise": 50.0,
                "unite_requise": "ml",
                "quantite_stock": None,
                "unite_stock": None,
            },
            {
                "id_cocktail": 1,
                "nom": "Cocktail A",
                "categorie": "Cocktail",
                "verre": "Glass",
                "alcool": True,
                "image": "a.jpg",
                "id_ingredient": 3,
                "nom_ingredient": "Ing3",
                "quantite_requise": 50.0,
                "unite_requise": "ml",
                "quantite_stock": 50.0,
                "unite_stock": "ml",
            },
            # Cocktail B : 1 ingrédient manquant sur 2 (50% possession)
            {
                "id_cocktail": 2,
                "nom": "Cocktail B",
                "categorie": "Cocktail",
                "verre": "Glass",
                "alcool": True,
                "image": "b.jpg",
                "id_ingredient": 4,
                "nom_ingredient": "Ing4",
                "quantite_requise": 50.0,
                "unite_requise": "ml",
                "quantite_stock": None,
                "unite_stock": None,
            },
            {
                "id_cocktail": 2,
                "nom": "Cocktail B",
                "categorie": "Cocktail",
                "verre": "Glass",
                "alcool": True,
                "image": "b.jpg",
                "id_ingredient": 5,
                "nom_ingredient": "Ing5",
                "quantite_requise": 50.0,
                "unite_requise": "ml",
                "quantite_stock": 50.0,
                "unite_stock": "ml",
            },
        ]

        mock_cocktail_dao.get_cocktails_quasi_realisables.return_value = rows

        # Act
        result = cocktail_service.get_cocktails_quasi_realisables(1, max_ingredients_manquants=2)

        # Assert
        cocktails = result["cocktails_quasi_realisables"]
        assert len(cocktails) == 2
        # Cocktail B devrait être en premier (1 manquant vs 2 manquants)
        assert cocktails[0]["nom"] == "Cocktail B"
        assert cocktails[1]["nom"] == "Cocktail A"

    def test_get_cocktails_quasi_realisables_dao_error(self, cocktail_service, mock_cocktail_dao):
        """Test avec erreur DAO."""
        # Arrange
        mock_cocktail_dao.get_cocktails_quasi_realisables.side_effect = DAOError("Erreur DAO")

        # Act & Assert
        with pytest.raises(ServiceError):
            cocktail_service.get_cocktails_quasi_realisables(1)


class TestIsIngredientAvailable:
    """Tests pour la méthode _is_ingredient_available."""

    def test_is_ingredient_available_pas_de_stock(self, cocktail_service):
        """Test quand l'ingrédient n'est pas en stock."""
        # Arrange
        row = {
            "quantite_requise": 50.0,
            "unite_requise": "ml",
            "quantite_stock": None,
            "unite_stock": None,
            "nom_ingredient": "Vodka",
        }

        # Act
        result = cocktail_service._is_ingredient_available(row)

        # Assert
        assert result is False

    def test_is_ingredient_available_meme_unite_suffisant(self, cocktail_service):
        """Test avec même unité et quantité suffisante."""
        # Arrange
        row = {
            "quantite_requise": 50.0,
            "unite_requise": "ml",
            "quantite_stock": 100.0,
            "unite_stock": "ml",
            "nom_ingredient": "Vodka",
        }

        # Act
        result = cocktail_service._is_ingredient_available(row)

        # Assert
        assert result is True

    def test_is_ingredient_available_meme_unite_insuffisant(self, cocktail_service):
        """Test avec même unité mais quantité insuffisante."""
        # Arrange
        row = {
            "quantite_requise": 100.0,
            "unite_requise": "ml",
            "quantite_stock": 50.0,
            "unite_stock": "ml",
            "nom_ingredient": "Vodka",
        }

        # Act
        result = cocktail_service._is_ingredient_available(row)

        # Assert
        assert result is False

    def test_is_ingredient_available_conversion_liquide(self, cocktail_service):
        """Test avec conversion d'unités liquides (cl vers ml)."""
        # Arrange
        row = {
            "quantite_requise": 50.0,  # 50 ml requis
            "unite_requise": "ml",
            "quantite_stock": 10.0,  # 10 cl = 100 ml en stock
            "unite_stock": "cl",
            "nom_ingredient": "Vodka",
        }

        # Act
        result = cocktail_service._is_ingredient_available(row)

        # Assert
        assert result is True

    def test_is_ingredient_available_conversion_solide(self, cocktail_service):
        """Test avec conversion d'unités solides (kg vers g)."""
        # Arrange
        row = {
            "quantite_requise": 50.0,  # 50 g requis
            "unite_requise": "g",
            "quantite_stock": 1.0,  # 1 kg = 1000 g en stock
            "unite_stock": "kg",
            "nom_ingredient": "Sucre",
        }

        # Act
        result = cocktail_service._is_ingredient_available(row)

        # Assert
        assert result is True

    def test_is_ingredient_available_unites_incompatibles(self, cocktail_service):
        """Test avec unités incompatibles (liquide vs solide)."""
        # Arrange
        row = {
            "quantite_requise": 50.0,
            "unite_requise": "ml",  # Liquide
            "quantite_stock": 50.0,
            "unite_stock": "g",  # Solide
            "nom_ingredient": "Vodka",
        }

        # Act
        result = cocktail_service._is_ingredient_available(row)

        # Assert
        assert result is False

    def test_is_ingredient_available_sans_unite(self, cocktail_service):
        """Test sans unité définie."""
        # Arrange
        row = {
            "quantite_requise": 2.0,
            "unite_requise": None,
            "quantite_stock": 5.0,
            "unite_stock": None,
            "nom_ingredient": "Citron",
        }

        # Act
        result = cocktail_service._is_ingredient_available(row)

        # Assert
        assert result is True


class TestCompareLiquidQuantities:
    """Tests pour la méthode _compare_liquid_quantities."""

    def test_compare_liquid_quantities_suffisant(self, cocktail_service):
        """Test avec quantité suffisante."""
        # Act
        result = cocktail_service._compare_liquid_quantities(50.0, "ml", 100.0, "ml")

        # Assert
        assert result is True

    def test_compare_liquid_quantities_insuffisant(self, cocktail_service):
        """Test avec quantité insuffisante."""
        # Act
        result = cocktail_service._compare_liquid_quantities(100.0, "ml", 50.0, "ml")

        # Assert
        assert result is False

    def test_compare_liquid_quantities_conversion(self, cocktail_service):
        """Test avec conversion d'unités."""
        # Act (50 ml requis, 10 cl = 100 ml en stock)
        result = cocktail_service._compare_liquid_quantities(50.0, "ml", 10.0, "cl")

        # Assert
        assert result is True


class TestCompareSolidQuantities:
    """Tests pour la méthode _compare_solid_quantities."""

    def test_compare_solid_quantities_suffisant(self, cocktail_service):
        """Test avec quantité suffisante."""
        # Act
        result = cocktail_service._compare_solid_quantities(50.0, "g", 100.0, "g")

        # Assert
        assert result is True

    def test_compare_solid_quantities_insuffisant(self, cocktail_service):
        """Test avec quantité insuffisante."""
        # Act
        result = cocktail_service._compare_solid_quantities(100.0, "g", 50.0, "g")

        # Assert
        assert result is False

    def test_compare_solid_quantities_conversion(self, cocktail_service):
        """Test avec conversion d'unités."""
        # Act (50 g requis, 1 kg = 1000 g en stock)
        result = cocktail_service._compare_solid_quantities(50.0, "g", 1.0, "kg")

        # Assert
        assert result is True
