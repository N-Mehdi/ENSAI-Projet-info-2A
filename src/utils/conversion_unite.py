"""Module qui gère la conversion des unités de la base de données."""

from typing import ClassVar, Literal


class UnitConverter:
    """Convertisseur d'unités pour les ingrédients de cocktails.
    Gère la conversion des unités liquides vers ml et des unités solides vers g.
    """

    # Conversions liquides → ml
    LIQUID_TO_ML: ClassVar[dict[str, float]] = {
        "oz": 29.5735,  # Fluid ounce
        "fl oz": 29.5735,  # Fluid ounce (explicite)
        "ml": 1.0,  # Millilitre
        "cl": 10.0,  # Centilitre
        "l": 1000.0,  # Litre
        "dl": 100.0,  # Décilitre
        "tsp": 4.92892,  # Teaspoon (cuillère à café) - liquide
        "tbsp": 14.7868,  # Tablespoon (cuillère à soupe) - liquide
        "tblsp": 14.7868,  # Tablespoon aussi
        "cup": 236.588,  # Cup américaine
        "pint": 473.176,  # Pinte américaine
        "quart": 946.353,  # Quart américain
        "gallon": 3785.41,  # Gallon américain
        "shot": 44.3603,  # Shot (1.5 oz)
        "jigger": 44.3603,  # Jigger (1.5 oz)
        "splash": 5.0,  # Splash (approximatif)
        "dash": 0.92,  # Dash pour liquides (approximatif)
    }

    # Conversions solides → g
    SOLID_TO_G: ClassVar[dict[str, float]] = {
        "g": 1.0,  # Gramme
        "kg": 1000.0,  # Kilogramme
        "oz": 28.3495,  # Ounce (masse) - pour ingrédients solides
        "lb": 453.592,  # Livre
        "tsp": 4.2,  # Teaspoon de sucre (approximatif)
        "tbsp": 12.5,  # Tablespoon de sucre (approximatif)
        "tblsp": 12.5,  # Tablespoon aussi
        "cup": 200.0,  # Cup de sucre (approximatif)
        "cube": 5.0,  # Cube de sucre (approximatif, ~5g)
    }

    # Unités spéciales sans conversion
    SPECIAL_UNITS: ClassVar[set[str]] = {
        "dash",  # Pour bitters (compte, pas volume exact)
        "drop",  # Goutte
        "pinch",  # Pincée
        "piece",  # Pièce
        "slice",  # Tranche
        "wedge",  # Quartier
        "sprig",  # Brin
        "leaf",  # Feuille
        "peel",  # Zeste
        "twist",  # Twist
        "garnish",  # Garniture
        "top",  # Top (remplir)
        "fill",  # Remplir
        "juice",  # Jus de (X fruits)
    }

    @classmethod
    def convert_to_ml(cls, value: float, from_unit: str) -> float | None:
        """Convertit une quantité d'unité liquide vers ml.

        Parameters
        ----------
        value : float
            La valeur à convertir
        from_unit : str
            L'unité source (ex: "oz", "cl")

        Returns
        -------
        float | None
            La valeur en ml, ou None si l'unité n'est pas reconnue

        Examples
        --------
        >>> UnitConverter.convert_to_ml(2, "oz")
        59.147
        >>> UnitConverter.convert_to_ml(5, "cl")
        50.0
        >>> UnitConverter.convert_to_ml(1.5, "oz")
        44.36025

        """
        if not from_unit:
            return None

        from_unit_lower = from_unit.lower().strip()

        if from_unit_lower in cls.LIQUID_TO_ML:
            return round(value * cls.LIQUID_TO_ML[from_unit_lower], 2)

        return None

    @classmethod
    def convert_to_g(cls, value: float, from_unit: str) -> float | None:
        """Convertit une quantité d'unité solide vers g.

        Parameters
        ----------
        value : float
            La valeur à convertir
        from_unit : str
            L'unité source (ex: "tsp", "cube")

        Returns
        -------
        float | None
            La valeur en g, ou None si l'unité n'est pas reconnue

        Examples
        --------
        >>> UnitConverter.convert_to_g(1, "tsp")
        4.2
        >>> UnitConverter.convert_to_g(2, "cube")
        10.0

        """
        if not from_unit:
            return None

        from_unit_lower = from_unit.lower().strip()

        if from_unit_lower in cls.SOLID_TO_G:
            return round(value * cls.SOLID_TO_G[from_unit_lower], 2)

        return None

    @classmethod
    def convert(
        cls,
        value: float,
        from_unit: str,
        unit_type: Literal["liquide", "solide", "autre"] = "liquide",
    ) -> dict:
        """Convertit une quantité vers l'unité standard selon le type.

        Parameters
        ----------
        value : float
            La valeur à convertir
        from_unit : str
            L'unité source
        unit_type : Literal['liquide', 'solide', 'autre']
            Le type d'unité

        Returns
        -------
        dict
            {
                "valeur_originale": float,
                "unite_originale": str,
                "valeur_convertie": float | None,
                "unite_convertie": str | None,
                "type": str,
                "convertible": bool
            }

        Examples
        --------
        >>> UnitConverter.convert(2, "oz", "liquide")
        {
            "valeur_originale": 2.0,
            "unite_originale": "oz",
            "valeur_convertie": 59.15,
            "unite_convertie": "ml",
            "type": "liquide",
            "convertible": True
        }

        """
        if not from_unit:
            return {
                "valeur_originale": value,
                "unite_originale": None,
                "valeur_convertie": None,
                "unite_convertie": None,
                "type": unit_type,
                "convertible": False,
            }

        from_unit_lower = from_unit.lower().strip()

        # Unités spéciales (non convertibles)
        if from_unit_lower in cls.SPECIAL_UNITS:
            return {
                "valeur_originale": value,
                "unite_originale": from_unit,
                "valeur_convertie": None,
                "unite_convertie": None,
                "type": "autre",
                "convertible": False,
                "raison": "Unité spéciale (compte, pas mesure)",
            }

        # Conversion selon le type
        if unit_type == "liquide":
            valeur_convertie = cls.convert_to_ml(value, from_unit)
            if valeur_convertie is not None:
                return {
                    "valeur_originale": value,
                    "unite_originale": from_unit,
                    "valeur_convertie": valeur_convertie,
                    "unite_convertie": "ml",
                    "type": "liquide",
                    "convertible": True,
                }

        elif unit_type == "solide":
            valeur_convertie = cls.convert_to_g(value, from_unit)
            if valeur_convertie is not None:
                return {
                    "valeur_originale": value,
                    "unite_originale": from_unit,
                    "valeur_convertie": valeur_convertie,
                    "unite_convertie": "g",
                    "type": "solide",
                    "convertible": True,
                }

        # Pas de conversion possible
        return {
            "valeur_originale": value,
            "unite_originale": from_unit,
            "valeur_convertie": None,
            "unite_convertie": None,
            "type": unit_type,
            "convertible": False,
            "raison": "Unité inconnue",
        }

    @classmethod
    def is_liquid_unit(cls, unit: str) -> bool:
        """Vérifie si une unité est une unité liquide."""
        if not unit:
            return False
        return unit.lower().strip() in cls.LIQUID_TO_ML

    @classmethod
    def is_solid_unit(cls, unit: str) -> bool:
        """Vérifie si une unité est une unité solide."""
        if not unit:
            return False
        return unit.lower().strip() in cls.SOLID_TO_G

    @classmethod
    def is_special_unit(cls, unit: str) -> bool:
        """Vérifie si une unité est une unité spéciale (non convertible)."""
        if not unit:
            return False
        return unit.lower().strip() in cls.SPECIAL_UNITS

    @classmethod
    def get_unit_type(cls, unit: str) -> Literal["liquide", "solide", "autre"] | None:
        """Détermine automatiquement le type d'une unité.

        Returns
        -------
        Literal['liquide', 'solide', 'autre'] | None
            Le type d'unité

        """
        if not unit:
            return None

        unit_lower = unit.lower().strip()

        if unit_lower in cls.LIQUID_TO_ML:
            return "liquide"
        if unit_lower in cls.SOLID_TO_G:
            return "solide"
        if unit_lower in cls.SPECIAL_UNITS:
            return "autre"

        return None

    def normalize_unit(unit_code: str) -> str:
        """Normalise les variantes d'unités."""
        if unit_code:
            unit_lower = unit_code.lower()
            if unit_lower in ("tbsp", "tblsp"):
                return "tbsp"
            if unit_lower in ("tsp", "teaspoon"):
                return "tsp"
        return unit_code


# Alias pour faciliter l'import
convert_to_ml = UnitConverter.convert_to_ml
convert_to_g = UnitConverter.convert_to_g
convert_unit = UnitConverter.convert
