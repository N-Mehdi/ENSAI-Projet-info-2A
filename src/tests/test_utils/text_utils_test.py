"""Tests unitaires pour les fonctions normalisation de texte."""

from src.utils.text_utils import normalize_ingredient_name


class TestNormalizeIngredientName:
    """Tests pour la fonction normalize_ingredient_name."""

    def test_normalize_lowercase_simple(self) -> None:
        """Teste la normalisation d'un mot simple en minuscules."""
        result = normalize_ingredient_name("apple")
        if result != "Apple":
            raise AssertionError(
                message=f"Attendu 'Apple', obtenu: {result}",
            )

    def test_normalize_uppercase_simple(self) -> None:
        """Teste la normalisation d'un mot simple en majuscules."""
        result = normalize_ingredient_name("APPLE")
        if result != "Apple":
            raise AssertionError(
                message=f"Attendu 'Apple', obtenu: {result}",
            )

    def test_normalize_multiple_words_uppercase(self) -> None:
        """Teste la normalisation de plusieurs mots en majuscules."""
        result = normalize_ingredient_name("POMEGRANATE JUICE")
        if result != "Pomegranate Juice":
            raise AssertionError(
                message=f"Attendu 'Pomegranate Juice', obtenu: {result}",
            )

    def test_normalize_multiple_words_lowercase(self) -> None:
        """Teste la normalisation de plusieurs mots en minuscules."""
        result = normalize_ingredient_name("pomegranate juice")
        if result != "Pomegranate Juice":
            raise AssertionError(
                message=f"Attendu 'Pomegranate Juice', obtenu: {result}",
            )

    def test_normalize_with_leading_trailing_spaces(self) -> None:
        """Teste la normalisation avec espaces au début et à la fin."""
        result = normalize_ingredient_name("  rhum   blanc  ")
        if result != "Rhum Blanc":
            raise AssertionError(
                message=f"Attendu 'Rhum Blanc', obtenu: {result}",
            )

    def test_normalize_with_multiple_spaces(self) -> None:
        """Teste la normalisation avec espaces multiples entre les mots."""
        result = normalize_ingredient_name("rhum     blanc")
        if result != "Rhum Blanc":
            raise AssertionError(
                message=f"Attendu 'Rhum Blanc', obtenu: {result}",
            )

    def test_normalize_starting_with_number(self) -> None:
        """Teste la normalisation d'un nom commençant par un chiffre."""
        result = normalize_ingredient_name("151 proof rum")
        if result != "151 Proof Rum":
            raise AssertionError(
                message=f"Attendu '151 Proof Rum', obtenu: {result}",
            )

    def test_normalize_with_hyphen_and_number(self) -> None:
        """Teste la normalisation d'un nom avec chiffre et tiret."""
        result = normalize_ingredient_name("7-up")
        if result != "7-Up":
            raise AssertionError(
                message=f"Attendu '7-Up', obtenu: {result}",
            )

    def test_normalize_already_normalized(self) -> None:
        """Teste qu'un nom déjà normalisé reste inchangé."""
        result = normalize_ingredient_name("Vodka")
        if result != "Vodka":
            raise AssertionError(
                message=f"Attendu 'Vodka', obtenu: {result}",
            )

    def test_normalize_mixed_case(self) -> None:
        """Teste la normalisation d'un nom en casse mixte."""
        result = normalize_ingredient_name("vOdKa LiMe")
        if result != "Vodka Lime":
            raise AssertionError(
                message=f"Attendu 'Vodka Lime', obtenu: {result}",
            )

    def test_normalize_empty_string(self) -> None:
        """Teste la normalisation d'une chaîne vide."""
        result = normalize_ingredient_name("")
        if result != "":
            raise AssertionError(
                message=f"Attendu '', obtenu: {result}",
            )

    def test_normalize_only_spaces(self) -> None:
        """Teste la normalisation d'une chaîne avec seulement des espaces."""
        result = normalize_ingredient_name("   ")
        if result != "":
            raise AssertionError(
                message=f"Attendu '', obtenu: {result}",
            )

    def test_normalize_with_apostrophe(self) -> None:
        """Teste la normalisation avec apostrophe."""
        result = normalize_ingredient_name("o'douls")
        if result != "O'Douls":
            raise AssertionError(
                message=f"Attendu 'O'Douls', obtenu: {result}",
            )

    def test_normalize_special_characters(self) -> None:
        """Teste la normalisation avec caractères spéciaux."""
        result = normalize_ingredient_name("coca-cola")
        if result != "Coca-Cola":
            raise AssertionError(
                message=f"Attendu 'Coca-Cola', obtenu: {result}",
            )
