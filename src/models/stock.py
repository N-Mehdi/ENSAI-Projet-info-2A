"""Modèles pydantic pour le stock."""

from pydantic import BaseModel, Field


class StockItem(BaseModel):
    """Représente un item dans le stock."""

    id_ingredient: int
    nom_ingredient: str
    quantite: float
    id_unite: int | None
    code_unite: str | None
    nom_unite_complet: str | None


class Stock(BaseModel):
    """Représente le stock complet d'un utilisateur."""

    id_utilisateur: int
    items: list[StockItem]


class StockItemAdd(BaseModel):
    """Modèle pour ajouter un ingrédient au stock."""

    id_ingredient: int = Field(
        ...,
        description="ID de l'ingrédient (voir GET /api/ref/ingredients)",
        json_schema_extra={"example": 5},
    )
    quantite: float = Field(
        ...,
        gt=0,
        description="Quantité de l'ingrédient (doit être > 0)",
        json_schema_extra={"example": 500.0},
    )
    id_unite: int = Field(
        ...,
        description="ID de l'unité (voir GET /api/ref/unites)",
        json_schema_extra={"example": 2},
    )


class StockItemAddByName(BaseModel):
    """Modèle pour ajouter un ingrédient au stock par nom."""

    nom_ingredient: str = Field(
        ...,
        description="Nom de l'ingrédient (insensible à la casse, sera normalisé automatiquement)",
        min_length=2,
        json_schema_extra={"example": "Vodka"},
    )
    quantite: float = Field(
        ...,
        gt=0,
        description="Quantité de l'ingrédient (doit être > 0)",
        json_schema_extra={"example": 500.0},
    )
    unite: str = Field(
        ...,
        description="Abréviation de l'unité (ex: 'ml', 'cl', 'l', 'g', 'kg')",
        min_length=1,
        max_length=10,
        json_schema_extra={"example": "ml"},
    )


class StockItemRemove(BaseModel):
    """Modèle pour retirer une quantité d'un ingrédient du stock."""

    nom_ingredient: str = Field(
        ...,
        description="Nom de l'ingrédient",
        min_length=2,
        json_schema_extra={"example": "Vodka"},
    )
    quantite: float = Field(
        ...,
        gt=0,
        description="Quantité à retirer (doit être > 0 et <= quantité disponible)",
        json_schema_extra={"example": 100.0},
    )
