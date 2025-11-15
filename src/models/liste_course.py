"""doc."""

from pydantic import BaseModel, Field


class ListeCourseItemAdd(BaseModel):
    """Modèle pour ajouter un ingrédient à la liste de course."""

    nom_ingredient: str = Field(
        ...,
        min_length=2,
        description="Nom de l'ingrédient",
        json_schema_extra={"example": "Vodka"},
    )
    quantite: float = Field(
        ...,
        gt=0,
        description="Quantité à acheter (doit être > 0)",
        json_schema_extra={"example": 500.0},
    )
    id_unite: int = Field(
        ...,
        description="ID de l'unité (voir GET /api/ref/unites)",
        json_schema_extra={"example": 2},
    )


class ListeCourseItem(BaseModel):
    """Représente un item dans la liste de course."""

    id_ingredient: int
    nom_ingredient: str
    quantite: float
    effectue: bool
    id_unite: int | None
    code_unite: str | None
    nom_unite_complet: str | None


class ListeCourse(BaseModel):
    """Représente la liste de course complète d'un utilisateur."""

    id_utilisateur: int
    items: list[ListeCourseItem]
    nombre_items: int = Field(description="Nombre total d'items")
    nombre_effectues: int = Field(description="Nombre d'items cochés")
