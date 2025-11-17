"""Modèles Pydantic pour les cocktails."""

from pydantic import BaseModel, Field


class Cocktail(BaseModel):
    """Représente un cocktail."""

    id_cocktail: int = Field(
        description="ID unique du cocktail",
        json_schema_extra={"example": 1},
    )
    nom: str = Field(
        min_length=2,
        description="Nom du cocktail",
        json_schema_extra={"example": "Margarita"},
    )
    categorie: str = Field(
        description="Catégorie du cocktail",
        json_schema_extra={"example": "Ordinary Drink"},
    )
    verre: str = Field(
        description="Type de verre utilisé",
        json_schema_extra={"example": "Cocktail glass"},
    )
    alcool: bool = Field(
        description="Indique si le cocktail contient de l'alcool",
        json_schema_extra={"example": True},
    )
    image: str = Field(
        description="URL de l'image du cocktail",
        json_schema_extra={"example": "https://example.com/margarita.jpg"},
    )


class CocktailQuasiRealisable(BaseModel):
    """Schéma pour un cocktail quasi-réalisable."""

    id_cocktail: int
    nom: str
    categorie: str
    verre: str
    alcool: bool
    image: str
    ingredients_manquants: list[str]
    nombre_ingredients_manquants: int
    nombre_ingredients_total: int
    pourcentage_possession: float = Field(
        description="Pourcentage d'ingrédients possédés",
        ge=0,
        le=100,
    )


class CocktailsQuasiRealisablesResponse(BaseModel):
    """Schéma de réponse pour les cocktails quasi-réalisables."""

    cocktails_quasi_realisables: list[CocktailQuasiRealisable]
    nombre_cocktails: int
    max_ingredients_manquants: int
