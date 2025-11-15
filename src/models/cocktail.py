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
