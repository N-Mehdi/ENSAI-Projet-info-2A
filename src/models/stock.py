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
        example=5,
    )
    quantite: float = Field(
        ...,
        gt=0,
        description="Quantité de l'ingrédient (doit être > 0)",
        example=500.0,
    )
    id_unite: int = Field(
        ...,
        description="ID de l'unité (voir GET /api/ref/unites)",
        example=2,
    )


class StockItemAddByName(BaseModel):
    """Modèle pour ajouter un ingrédient au stock par nom."""

    nom_ingredient: str = Field(
        ...,
        description="Nom de l'ingrédient (insensible à la casse, sera normalisé automatiquement)",
        min_length=2,
        example="Vodka",
    )
    quantite: float = Field(
        ...,
        gt=0,
        description="Quantité de l'ingrédient (doit être > 0)",
        example=500.0,
    )
    id_unite: int = Field(
        ...,
        description="ID de l'unité (voir GET /api/ref/unites)",
        example=2,
    )


class StockItemRemove(BaseModel):
    """Modèle pour retirer une quantité d'un ingrédient du stock."""

    nom_ingredient: str = Field(
        ...,
        description="Nom de l'ingrédient",
        min_length=2,
        example="Vodka",
    )
    quantite: float = Field(
        ...,
        gt=0,
        description="Quantité à retirer (doit être > 0 et <= quantité disponible)",
        example=100.0,
    )
