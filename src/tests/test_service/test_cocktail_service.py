"""Tests pour le service CocktailService."""

from unittest.mock import MagicMock

import pytest

from src.business_object.cocktail import Cocktail
from src.dao.cocktail_dao import CocktailDAO
from src.service.cocktail_service import CocktailService
from src.utils.exceptions import (
    CocktailSearchError,
    DAOError,
    EmptyFieldError,
    ServiceError,
)


@pytest.fixture
def mock_cocktail_dao() -> MagicMock:
    """Fixture pour créer un mock de CocktailDAO."""
    return MagicMock(spec=CocktailDAO)


@pytest.fixture
def mock_stock_dao() -> MagicMock:
    """Fixture pour créer un mock de StockDAO."""
    return MagicMock()


@pytest.fixture
def cocktail_service(mock_cocktail_dao) -> CocktailService:
    """Fixture pour créer une instance de CocktailService avec des mocks."""
    return CocktailService(mock_cocktail_dao)


@pytest.fixture
def sample_cocktail() -> Cocktail:
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

    def rechercher_cocktail_par_nom(self, nom: str) -> tuple[Cocktail, str | None]:
        """Recherche un cocktail par son nom avec ses instructions.

        Parameters
        ----------
        nom : str
            Nom du cocktail à rechercher.

        Raises
        ------
        CocktailSearchError
            Si le nom n'est pas une chaîne de caractères.
        CocktailSearchError
            Si le nom est vide ou None.
        CocktailSearchError
            Si aucun cocktail n'est trouvé pour le nom donné.

        Returns
        -------
        tuple[Cocktail, str | None]
            Un tuple contenant le cocktail et ses instructions (ou None)

        """
        if not nom:
            raise EmptyFieldError(nom)

        if not isinstance(nom, str):
            raise CocktailSearchError(
                message="Le nom du cocktail doit être une chaîne de caractères.",
            )

        cocktail = self.cocktail_dao.rechercher_cocktail_par_nom(nom)

        if cocktail is None:
            raise CocktailSearchError(
                message=f"Aucun cocktail trouvé pour le nom '{nom}'",
            )

        instructions = self.instruction_dao.get_instruction(cocktail.id_cocktail)

        return cocktail, instructions

    @staticmethod
    def test_rechercher_cocktail_par_nom_vide(cocktail_service) -> None:
        """Test avec un nom vide."""
        # Act & Assert
        with pytest.raises(EmptyFieldError):
            cocktail_service.rechercher_cocktail_par_nom("")

    @staticmethod
    def test_rechercher_cocktail_par_nom_none(cocktail_service) -> None:
        """Test avec None comme nom."""
        # Act & Assert
        with pytest.raises(EmptyFieldError):
            cocktail_service.rechercher_cocktail_par_nom(None)

    @staticmethod
    def test_rechercher_cocktail_par_nom_type_invalide(cocktail_service) -> None:
        """Test avec un type invalide (non string)."""
        # Act & Assert
        with pytest.raises(CocktailSearchError):
            cocktail_service.rechercher_cocktail_par_nom(123)

    @staticmethod
    def test_rechercher_cocktail_par_nom_non_trouve(
        cocktail_service,
        mock_cocktail_dao,
    ) -> None:
        """Test quand aucun cocktail n'est trouvé."""
        # Arrange
        mock_cocktail_dao.rechercher_cocktail_par_nom.return_value = None

        # Act & Assert
        with pytest.raises(CocktailSearchError):
            cocktail_service.rechercher_cocktail_par_nom("CocktailInexistant")


class TestRechercherCocktailParSequenceDebut:
    """Tests pour la méthode rechercher_cocktail_par_sequence_debut."""

    @staticmethod
    def test_rechercher_par_sequence_success(
        cocktail_service,
        mock_cocktail_dao,
        sample_cocktail,
    ) -> None:
        """Test de recherche réussie par séquence."""
        # Arrange
        cocktails = [sample_cocktail]
        mock_cocktail_dao.rechercher_cocktail_par_sequence_debut.return_value = (
            cocktails
        )

        # Mock l'instruction_dao si le service l'utilise
        cocktail_service.instruction_dao = MagicMock()
        cocktail_service.instruction_dao.get_instruction.return_value = (
            "Mélanger tous les ingrédients"
        )

        # Act
        result = cocktail_service.rechercher_cocktail_par_sequence_debut("Moj", 10)

        # Assert
        if len(result) != 1:
            raise AssertionError(
                message=f"Devrait avoir 1 résultat, obtenu: {len(result)}",
            )

        result_cocktail, result_instructions = result[0]

        if result_cocktail != sample_cocktail:
            raise AssertionError(
                message=f"Le cocktail devrait être {sample_cocktail},"
                f"obtenu: {result_cocktail}",
            )

        if result_instructions != "Mélanger tous les ingrédients":
            raise AssertionError(
                message=f"Les instructions devraient être 'Mélanger tous "
                f"les ingrédients', obtenu: {result_instructions}",
            )

        mock_cocktail_dao.rechercher_cocktail_par_sequence_debut.assert_called_once_with(
            "Moj",
            10,
        )
        cocktail_service.instruction_dao.get_instruction.assert_called_once_with(
            sample_cocktail.id_cocktail,
        )

    @staticmethod
    def test_rechercher_par_sequence_vide(cocktail_service) -> None:
        """Test avec une séquence vide."""
        # Act & Assert
        with pytest.raises(EmptyFieldError):
            cocktail_service.rechercher_cocktail_par_sequence_debut("", 10)

    @staticmethod
    def test_rechercher_par_sequence_type_invalide(cocktail_service) -> None:
        """Test avec un type invalide pour la séquence."""
        # Act & Assert
        with pytest.raises(CocktailSearchError):
            cocktail_service.rechercher_cocktail_par_sequence_debut(123, 10)

    @staticmethod
    def test_rechercher_par_sequence_max_resultats_invalide_type(
        cocktail_service,
    ) -> None:
        """Test avec un type invalide pour max_resultats."""
        # Act & Assert
        with pytest.raises(CocktailSearchError):
            cocktail_service.rechercher_cocktail_par_sequence_debut("Moj", "10")

    @staticmethod
    def test_rechercher_par_sequence_max_resultats_invalide_valeur(
        cocktail_service,
    ) -> None:
        """Test avec une valeur invalide pour max_resultats."""
        # Act & Assert
        with pytest.raises(CocktailSearchError):
            cocktail_service.rechercher_cocktail_par_sequence_debut("Moj", 0)

    @staticmethod
    def test_rechercher_par_sequence_aucun_resultat(
        cocktail_service,
        mock_cocktail_dao,
    ) -> None:
        """Test quand aucun cocktail n'est trouvé."""
        # Arrange
        mock_cocktail_dao.rechercher_cocktail_par_sequence_debut.return_value = []

        # Act & Assert
        with pytest.raises(CocktailSearchError):
            cocktail_service.rechercher_cocktail_par_sequence_debut("Xyz", 10)


class TestGetCocktailsRealisables:
    """Tests pour la méthode get_cocktails_realisables."""

    @staticmethod
    def test_get_cocktails_realisables_success(cocktail_service) -> None:
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
        if "cocktails_realisables" not in result:
            raise AssertionError(
                message="La clé 'cocktails_realisables' devrait être présente",
            )
        if "nombre_cocktails" not in result:
            raise AssertionError(
                message="La clé 'nombre_cocktails' devrait être présente",
            )
        if result["nombre_cocktails"] != 1:
            raise AssertionError(
                message=f"Devrait avoir 1 cocktail, obtenu:"
                f"{result['nombre_cocktails']}",
            )
        if len(result["cocktails_realisables"]) != 1:
            raise AssertionError(
                message=f"Devrait avoir 1 cocktail réalisable, obtenu: "
                f"{len(result['cocktails_realisables'])}",
            )
        if result["cocktails_realisables"][0]["nom"] != "Screwdriver":
            raise AssertionError(
                message=f"Le cocktail devrait être 'Screwdriver', obtenu: "
                f"{result['cocktails_realisables'][0]['nom']}",
            )

    @staticmethod
    def test_get_cocktails_realisables_quantite_insuffisante(
        cocktail_service,
    ) -> None:
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
        if result["nombre_cocktails"] != 0:
            raise AssertionError(
                message=f"Devrait avoir 0 cocktail, obtenu:"
                f"{result['nombre_cocktails']}",
            )

    @staticmethod
    def test_get_cocktails_realisables_conversion_unites(
        cocktail_service,
    ) -> None:
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
        if result["nombre_cocktails"] != 1:
            raise AssertionError(
                message=f"Devrait avoir 1 cocktail, obtenu:"
                f"{result['nombre_cocktails']}",
            )

    @staticmethod
    def test_get_cocktails_realisables_dao_error(cocktail_service) -> None:
        """Test avec erreur DAO."""
        # Arrange
        cocktail_service.stock_dao.get_stock = MagicMock(
            side_effect=DAOError("Erreur DAO"),
        )

        # Act & Assert
        with pytest.raises(ServiceError):
            cocktail_service.get_cocktails_realisables(1)


class TestGetCocktailsQuasiRealisables:
    """Tests pour la méthode get_cocktails_quasi_realisables."""

    @staticmethod
    def test_get_cocktails_quasi_realisables_success(
        cocktail_service,
        mock_cocktail_dao,
    ) -> None:
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
                "quantite_stock": None,
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
                "quantite_stock": 20.0,
                "unite_stock": "g",
            },
        ]

        mock_cocktail_dao.get_cocktails_quasi_realisables.return_value = rows

        # Act
        result = cocktail_service.get_cocktails_quasi_realisables(
            id_utilisateur,
            max_ingredients_manquants=1,
        )

        # Assert
        if "cocktails_quasi_realisables" not in result:
            raise AssertionError(
                message="La clé 'cocktails_quasi_realisables' devrait être présente",
            )
        if "nombre_cocktails" not in result:
            raise AssertionError(
                message="La clé 'nombre_cocktails' devrait êtreprésente",
            )
        if result["nombre_cocktails"] != 1:
            raise AssertionError(
                message=f"Devrait avoir 1 cocktail, obtenu:"
                f"{result['nombre_cocktails']}",
            )
        if result["max_ingredients_manquants"] != 1:
            raise AssertionError(
                message=f"max_ingredients_manquants devrait être 1, obtenu: "
                f"{result['max_ingredients_manquants']}",
            )

        cocktail = result["cocktails_quasi_realisables"][0]
        if cocktail["nom"] != "Mojito":
            raise AssertionError(
                message=f"Le cocktail devrait être 'Mojito', obtenu:{cocktail['nom']}",
            )
        if cocktail["nombre_ingredients_manquants"] != 1:
            raise AssertionError(
                message=f"Devrait avoir 1 ingrédient manquant, obtenu: "
                f"{cocktail['nombre_ingredients_manquants']}",
            )
        if "Rhum Blanc" not in cocktail["ingredients_manquants"]:
            raise AssertionError(
                message="Rhum Blanc devrait être dans les ingrédients manquants",
            )

    @staticmethod
    def test_get_cocktails_quasi_realisables_aucun_resultat(
        cocktail_service,
        mock_cocktail_dao,
    ) -> None:
        """Test quand aucun cocktail quasi-réalisable n'est trouvé."""
        # Arrange
        mock_cocktail_dao.get_cocktails_quasi_realisables.return_value = []

        # Act
        result = cocktail_service.get_cocktails_quasi_realisables(
            1,
            max_ingredients_manquants=1,
        )

        # Assert
        if result["nombre_cocktails"] != 0:
            raise AssertionError(
                message=f"Devrait avoir 0 cocktail, obtenu:"
                f"{result['nombre_cocktails']}",
            )
        if result["cocktails_quasi_realisables"] != []:
            raise AssertionError(
                message=f"La liste devrait être vide, obtenu: "
                f"{result['cocktails_quasi_realisables']}",
            )

    @staticmethod
    def test_get_cocktails_quasi_realisables_tri(
        cocktail_service,
        mock_cocktail_dao,
    ) -> None:
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
        result = cocktail_service.get_cocktails_quasi_realisables(
            1,
            max_ingredients_manquants=2,
        )

        # Assert
        nb_cocktail = 2
        cocktails = result["cocktails_quasi_realisables"]
        if len(cocktails) != nb_cocktail:
            raise AssertionError(
                message=f"Devrait avoir {nb_cocktail} cocktails, obtenu:"
                f"{len(cocktails)}",
            )
        # Cocktail B devrait être en premier (1 manquant vs 2 manquants)
        if cocktails[0]["nom"] != "Cocktail B":
            raise AssertionError(
                message=f"Le premier cocktail devrait être 'Cocktail B',"
                f"obtenu: {cocktails[0]['nom']}",
            )
        if cocktails[1]["nom"] != "Cocktail A":
            raise AssertionError(
                message=f"Le deuxième cocktail devrait être 'Cocktail A', obtenu: "
                f"{cocktails[1]['nom']}",
            )

    @staticmethod
    def test_get_cocktails_quasi_realisables_dao_error(
        cocktail_service,
        mock_cocktail_dao,
    ) -> None:
        """Test avec erreur DAO."""
        # Arrange
        mock_cocktail_dao.get_cocktails_quasi_realisables.side_effect = DAOError(
            "Erreur DAO",
        )

        # Act & Assert
        with pytest.raises(ServiceError):
            cocktail_service.get_cocktails_quasi_realisables(1)


class TestIsIngredientAvailable:
    """Tests pour la méthode is_ingredient_available."""

    @staticmethod
    def test_is_ingredient_available_pas_de_stock(cocktail_service) -> None:
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
        result = cocktail_service.is_ingredient_available(row)

        # Assert
        if result is not False:
            raise AssertionError(message=f"Devrait être False, obtenu: {result}")

    @staticmethod
    def test_is_ingredient_available_meme_unite_suffisant(
        cocktail_service,
    ) -> None:
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
        result = cocktail_service.is_ingredient_available(row)

        # Assert
        if result is not True:
            raise AssertionError(message=f"Devrait être True, obtenu: {result}")

    @staticmethod
    def test_is_ingredient_available_meme_unite_insuffisant(
        cocktail_service,
    ) -> None:
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
        result = cocktail_service.is_ingredient_available(row)

        # Assert
        if result is not False:
            raise AssertionError(message=f"Devrait être False, obtenu: {result}")

    @staticmethod
    def test_is_ingredient_available_conversion_liquide(cocktail_service) -> None:
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
        result = cocktail_service.is_ingredient_available(row)

        # Assert
        if result is not True:
            raise AssertionError(message=f"Devrait être True, obtenu: {result}")

    @staticmethod
    def test_is_ingredient_available_conversion_solide(cocktail_service) -> None:
        """Test avec conversion d'unités solides (kg vers g)."""
        # Arrange
        row = {
            "quantite_requise": 50.0,  # 50 g requis
            "unite_requise": "g",
            "quantite_stock": 1.0,
            "unite_stock": "kg",
            "nom_ingredient": "Sucre",
        }

        # Act
        result = cocktail_service.is_ingredient_available(row)

        # Assert
        if result is not True:
            raise AssertionError(message=f"Devrait être True, obtenu: {result}")

    @staticmethod
    def test_is_ingredient_available_unites_incompatibles(
        cocktail_service,
    ) -> None:
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
        result = cocktail_service.is_ingredient_available(row)

        # Assert
        if result is not False:
            raise AssertionError(message=f"Devrait être False, obtenu: {result}")

    @staticmethod
    def test_is_ingredient_available_sans_unite(cocktail_service) -> None:
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
        result = cocktail_service.is_ingredient_available(row)

        # Assert
        if result is not True:
            raise AssertionError(message=f"Devrait être True, obtenu: {result}")


class TestCompareLiquidQuantities:
    """Tests pour la méthode _compare_liquid_quantities."""

    @staticmethod
    def test_compare_liquid_quantities_suffisant(cocktail_service) -> None:
        """Test avec quantité suffisante."""
        # Act
        result = cocktail_service.compare_liquid_quantities(50.0, "ml", 100.0, "ml")

        # Assert
        if result is not True:
            raise AssertionError(message=f"Devrait être True, obtenu: {result}")

    @staticmethod
    def test_compare_liquid_quantities_insuffisant(cocktail_service) -> None:
        """Test avec quantité insuffisante."""
        # Act
        result = cocktail_service.compare_liquid_quantities(100.0, "ml", 50.0, "ml")

        # Assert
        if result is not False:
            raise AssertionError(message=f"Devrait être False, obtenu: {result}")

    @staticmethod
    def test_compare_liquid_quantities_conversion(cocktail_service) -> None:
        """Test avec conversion d'unités."""
        # Act (50 ml requis, 10 cl = 100 ml en stock)
        result = cocktail_service.compare_liquid_quantities(50.0, "ml", 10.0, "cl")

        # Assert
        if result is not True:
            raise AssertionError(message=f"Devrait être True, obtenu: {result}")


class TestCompareSolidQuantities:
    """Tests pour la méthode compare_solid_quantities."""

    @staticmethod
    def test_compare_solid_quantities_suffisant(cocktail_service) -> None:
        """Test avec quantité suffisante."""
        # Act
        result = cocktail_service.compare_solid_quantities(50.0, "g", 100.0, "g")

        # Assert
        if result is not True:
            raise AssertionError(message=f"Devrait être True, obtenu: {result}")

    @staticmethod
    def test_compare_solid_quantities_insuffisant(cocktail_service) -> None:
        """Test avec quantité insuffisante."""
        # Act
        result = cocktail_service.compare_solid_quantities(100.0, "g", 50.0, "g")

        # Assert
        if result is not False:
            raise AssertionError(message=f"Devrait être False, obtenu: {result}")

    @staticmethod
    def test_compare_solid_quantities_conversion(cocktail_service) -> None:
        """Test avec conversion d'unités."""
        # Act (50 g requis, 1 kg = 1000 g en stock)
        result = cocktail_service.compare_solid_quantities(50.0, "g", 1.0, "kg")

        # Assert
        if result is not True:
            raise AssertionError(message=f"Devrait être True, obtenu: {result}")
