"""Tests unitaires pour les fonctions de conversion d'unité."""

from src.utils.conversion_unite import UnitConverter


class TestUnitConverterNormalizeUnit:
    """Tests pour la méthode UnitConverter.normalize_unit."""

    def test_normalize_tbsp_lowercase(self):
        """Teste la normalisation de 'tbsp' en minuscules."""
        result = UnitConverter.normalize_unit("tbsp")
        if result != "tbsp":
            raise AssertionError(
                f"Attendu 'tbsp', obtenu: {result}",
            )

    def test_normalize_tbsp_uppercase(self):
        """Teste la normalisation de 'TBSP' en majuscules."""
        result = UnitConverter.normalize_unit("TBSP")
        if result != "tbsp":
            raise AssertionError(
                f"Attendu 'tbsp', obtenu: {result}",
            )

    def test_normalize_tblsp_to_tbsp(self):
        """Teste la normalisation de 'tblsp' vers 'tbsp'."""
        result = UnitConverter.normalize_unit("tblsp")
        if result != "tbsp":
            raise AssertionError(
                f"Attendu 'tbsp', obtenu: {result}",
            )

    def test_normalize_tblsp_uppercase_to_tbsp(self):
        """Teste la normalisation de 'TBLSP' vers 'tbsp'."""
        result = UnitConverter.normalize_unit("TBLSP")
        if result != "tbsp":
            raise AssertionError(
                f"Attendu 'tbsp', obtenu: {result}",
            )

    def test_normalize_tsp_lowercase(self):
        """Teste la normalisation de 'tsp' en minuscules."""
        result = UnitConverter.normalize_unit("tsp")
        if result != "tsp":
            raise AssertionError(
                f"Attendu 'tsp', obtenu: {result}",
            )

    def test_normalize_tsp_uppercase(self):
        """Teste la normalisation de 'TSP' en majuscules."""
        result = UnitConverter.normalize_unit("TSP")
        if result != "tsp":
            raise AssertionError(
                f"Attendu 'tsp', obtenu: {result}",
            )

    def test_normalize_teaspoon_to_tsp(self):
        """Teste la normalisation de 'teaspoon' vers 'tsp'."""
        result = UnitConverter.normalize_unit("teaspoon")
        if result != "tsp":
            raise AssertionError(
                f"Attendu 'tsp', obtenu: {result}",
            )

    def test_normalize_teaspoon_uppercase_to_tsp(self):
        """Teste la normalisation de 'TEASPOON' vers 'tsp'."""
        result = UnitConverter.normalize_unit("TEASPOON")
        if result != "tsp":
            raise AssertionError(
                f"Attendu 'tsp', obtenu: {result}",
            )

    def test_normalize_unknown_unit(self):
        """Teste qu'une unité inconnue reste inchangée."""
        result = UnitConverter.normalize_unit("ml")
        if result != "ml":
            raise AssertionError(
                f"Attendu 'ml', obtenu: {result}",
            )

    def test_normalize_oz_unchanged(self):
        """Teste qu'une unité 'oz' reste inchangée."""
        result = UnitConverter.normalize_unit("oz")
        if result != "oz":
            raise AssertionError(
                f"Attendu 'oz', obtenu: {result}",
            )

    def test_normalize_none_input(self):
        """Teste la normalisation avec None."""
        result = UnitConverter.normalize_unit(None)
        if result is not None:
            raise AssertionError(
                f"Attendu None, obtenu: {result}",
            )

    def test_normalize_empty_string(self):
        """Teste la normalisation d'une chaîne vide."""
        result = UnitConverter.normalize_unit("")
        if result != "":
            raise AssertionError(
                f"Attendu '', obtenu: {result}",
            )

    def test_normalize_mixed_case_tbsp(self):
        """Teste la normalisation de 'TbSp' en casse mixte."""
        result = UnitConverter.normalize_unit("TbSp")
        if result != "tbsp":
            raise AssertionError(
                f"Attendu 'tbsp', obtenu: {result}",
            )


class TestUnitConverterConvertToMl:
    """Tests pour la méthode UnitConverter.convert_to_ml."""

    def test_convert_oz_to_ml(self):
        """Teste la conversion de oz vers ml."""
        result = UnitConverter.convert_to_ml(2, "oz")
        expected = 59.15  # 2 * 29.5735 arrondi
        if result != expected:
            raise AssertionError(
                f"Attendu {expected}, obtenu: {result}",
            )

    def test_convert_cl_to_ml(self):
        """Teste la conversion de cl vers ml."""
        result = UnitConverter.convert_to_ml(5, "cl")
        expected = 50.0
        if result != expected:
            raise AssertionError(
                f"Attendu {expected}, obtenu: {result}",
            )

    def test_convert_ml_to_ml(self):
        """Teste la conversion de ml vers ml (identité)."""
        result = UnitConverter.convert_to_ml(100, "ml")
        expected = 100.0
        if result != expected:
            raise AssertionError(
                f"Attendu {expected}, obtenu: {result}",
            )

    def test_convert_unknown_unit(self):
        """Teste la conversion d'une unité inconnue."""
        result = UnitConverter.convert_to_ml(10, "unknown")
        if result is not None:
            raise AssertionError(
                f"Attendu None pour unité inconnue, obtenu: {result}",
            )

    def test_convert_empty_unit(self):
        """Teste la conversion avec une unité vide."""
        result = UnitConverter.convert_to_ml(10, "")
        if result is not None:
            raise AssertionError(
                f"Attendu None pour unité vide, obtenu: {result}",
            )

    def test_convert_case_insensitive(self):
        """Teste que la conversion est insensible à la casse."""
        result = UnitConverter.convert_to_ml(1, "OZ")
        expected = 29.57
        if result != expected:
            raise AssertionError(
                f"Attendu {expected}, obtenu: {result}",
            )


class TestUnitConverterConvertToG:
    """Tests pour la méthode UnitConverter.convert_to_g."""

    def test_convert_tsp_to_g(self):
        """Teste la conversion de tsp vers g."""
        result = UnitConverter.convert_to_g(1, "tsp")
        expected = 4.2
        if result != expected:
            raise AssertionError(
                f"Attendu {expected}, obtenu: {result}",
            )

    def test_convert_cube_to_g(self):
        """Teste la conversion de cube vers g."""
        result = UnitConverter.convert_to_g(2, "cube")
        expected = 10.0
        if result != expected:
            raise AssertionError(
                f"Attendu {expected}, obtenu: {result}",
            )

    def test_convert_g_to_g(self):
        """Teste la conversion de g vers g (identité)."""
        result = UnitConverter.convert_to_g(50, "g")
        expected = 50.0
        if result != expected:
            raise AssertionError(
                f"Attendu {expected}, obtenu: {result}",
            )

    def test_convert_unknown_solid_unit(self):
        """Teste la conversion d'une unité solide inconnue."""
        result = UnitConverter.convert_to_g(10, "unknown")
        if result is not None:
            raise AssertionError(
                f"Attendu None pour unité inconnue, obtenu: {result}",
            )


class TestUnitConverterIsLiquidUnit:
    """Tests pour la méthode UnitConverter.is_liquid_unit."""

    def test_is_liquid_unit_ml(self):
        """Teste qu'une unité ml est reconnue comme liquide."""
        result = UnitConverter.is_liquid_unit("ml")
        if result is not True:
            raise AssertionError("'ml' devrait être une unité liquide")

    def test_is_liquid_unit_oz(self):
        """Teste qu'une unité oz est reconnue comme liquide."""
        result = UnitConverter.is_liquid_unit("oz")
        if result is not True:
            raise AssertionError("'oz' devrait être une unité liquide")

    def test_is_not_liquid_unit(self):
        """Teste qu'une unité g n'est pas reconnue comme liquide."""
        result = UnitConverter.is_liquid_unit("g")
        if result is not False:
            raise AssertionError("'g' ne devrait pas être une unité liquide")

    def test_is_liquid_unit_empty(self):
        """Teste avec une chaîne vide."""
        result = UnitConverter.is_liquid_unit("")
        if result is not False:
            raise AssertionError("Une chaîne vide ne devrait pas être liquide")


class TestUnitConverterIsSolidUnit:
    """Tests pour la méthode UnitConverter.is_solid_unit."""

    def test_is_solid_unit_g(self):
        """Teste qu'une unité g est reconnue comme solide."""
        result = UnitConverter.is_solid_unit("g")
        if result is not True:
            raise AssertionError("'g' devrait être une unité solide")

    def test_is_solid_unit_cube(self):
        """Teste qu'une unité cube est reconnue comme solide."""
        result = UnitConverter.is_solid_unit("cube")
        if result is not True:
            raise AssertionError("'cube' devrait être une unité solide")

    def test_is_not_solid_unit(self):
        """Teste qu'une unité ml n'est pas reconnue comme solide."""
        result = UnitConverter.is_solid_unit("ml")
        if result is not False:
            raise AssertionError("'ml' ne devrait pas être une unité solide")


class TestUnitConverterIsSpecialUnit:
    """Tests pour la méthode UnitConverter.is_special_unit."""

    def test_is_special_unit_dash(self):
        """Teste qu'une unité dash est reconnue comme spéciale."""
        result = UnitConverter.is_special_unit("dash")
        if result is not True:
            raise AssertionError("'dash' devrait être une unité spéciale")

    def test_is_special_unit_pinch(self):
        """Teste qu'une unité pinch est reconnue comme spéciale."""
        result = UnitConverter.is_special_unit("pinch")
        if result is not True:
            raise AssertionError("'pinch' devrait être une unité spéciale")

    def test_is_not_special_unit(self):
        """Teste qu'une unité ml n'est pas reconnue comme spéciale."""
        result = UnitConverter.is_special_unit("ml")
        if result is not False:
            raise AssertionError("'ml' ne devrait pas être une unité spéciale")


class TestUnitConverterGetUnitType:
    """Tests pour la méthode UnitConverter.get_unit_type."""

    def test_get_unit_type_liquid(self):
        """Teste la détection d'une unité liquide."""
        result = UnitConverter.get_unit_type("ml")
        if result != "liquide":
            raise AssertionError(
                f"Attendu 'liquide', obtenu: {result}",
            )

    def test_get_unit_type_solid(self):
        """Teste la détection d'une unité solide."""
        result = UnitConverter.get_unit_type("g")
        if result != "solide":
            raise AssertionError(
                f"Attendu 'solide', obtenu: {result}",
            )

    def test_get_unit_type_special(self):
        """Teste la détection d'une unité spéciale."""
        result = UnitConverter.get_unit_type("dash")
        if result != "autre":
            raise AssertionError(
                f"Attendu 'autre', obtenu: {result}",
            )

    def test_get_unit_type_unknown(self):
        """Teste la détection d'une unité inconnue."""
        result = UnitConverter.get_unit_type("unknown")
        if result is not None:
            raise AssertionError(
                f"Attendu None pour unité inconnue, obtenu: {result}",
            )

    def test_get_unit_type_none(self):
        """Teste avec None."""
        result = UnitConverter.get_unit_type(None)
        if result is not None:
            raise AssertionError(
                f"Attendu None, obtenu: {result}",
            )
