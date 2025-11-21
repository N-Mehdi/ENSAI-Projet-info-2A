"""Modèles pydantic pour les cocktails privés."""

from pydantic import BaseModel, Field


class CocktailCreate(BaseModel):
    """Modèle pour créer un cocktail privé."""

    nom: str = Field(..., description="Nom du cocktail")
    categorie: str | None = Field(None, description="Catégorie du cocktail")
    verre: str | None = Field(None, description="Type de verre")
    alcool: bool | None = Field(None, description="Contient de l'alcool")
    image: str | None = Field(None, description="URL de l'image")


class IngredientUpdate(BaseModel):
    """Modèle pour ajouter ou modifier un ingrédient."""

    id_ingredient: int = Field(..., description="ID de l'ingrédient")
    quantite: float = Field(..., gt=0, description="Quantité de l'ingrédient")


class CocktailResponse(BaseModel):
    """Modèle de réponse pour un cocktail."""

    id_cocktail: int
    nom: str
    categorie: str | None
    verre: str | None
    alcool: bool | None
    image: str | None


class CocktailPriveCreate(BaseModel):
    """Modèle pour la création d'un cocktail privé.

    Attributes
    ----------
    nom : str
        Nom du cocktail
    categorie : str
        Catégorie du cocktail
    verre : str
        Type de verre
    alcool : bool
        Contient de l'alcool
    image : str
        URL de l'image
    instructions : str | None
        Instructions de préparation (optionnel)

    """

    nom: str = Field(..., min_length=1, max_length=100)
    categorie: str = Field(..., min_length=1, max_length=100)
    verre: str = Field(..., min_length=1, max_length=100)
    alcool: bool
    image: str
    instructions: str | None = None


class Config:
    """Configuration Pydantic."""

    json_schema_extra = {
        "example": {
            "nom": "Mon Mojito Spécial",
            "categorie": "Cocktail",
            "verre": "Highball glass",
            "alcool": True,
            "image": "https://example.com/mon_mojito.jpg",
            "instructions": "Ma recette personnelle de mojito...",
        },
    }
