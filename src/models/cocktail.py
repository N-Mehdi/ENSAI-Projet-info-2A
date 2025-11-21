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


class CocktailAvecInstructions(BaseModel):
    """Cocktail avec ses instructions de préparation."""

    id_cocktail: int | None
    nom: str
    categorie: str
    verre: str
    alcool: bool
    image: str
    instructions: str | None


class CocktailCreate(BaseModel):
    """Modèle pour la création d'un cocktail.

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
        URL ou chemin de l'image
    instructions : str | None
        Instructions de préparation (optionnel)
    langue : str
        Langue des instructions (par défaut: "en")

    """

    nom: str = Field(..., min_length=1, max_length=100, description="Nom du cocktail")
    categorie: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Catégorie du cocktail",
    )
    verre: str = Field(..., min_length=1, max_length=100, description="Type de verre")
    alcool: bool = Field(..., description="Contient de l'alcool")
    image: str = Field(..., description="URL de l'image")
    instructions: str | None = Field(
        default=None,
        description="Instructions de préparation",
    )
    langue: str = Field(
        default="en",
        min_length=2,
        max_length=5,
        description="Langue des instructions",
    )


class CocktailCreateResponse(BaseModel):
    """Modèle de réponse après création d'un cocktail.

    Attributes
    ----------
    id_cocktail : int
        Identifiant du cocktail créé
    nom : str
        Nom du cocktail créé
    message : str
        Message de confirmation

    """

    id_cocktail: int = Field(..., description="ID du cocktail créé")
    nom: str = Field(..., description="Nom du cocktail créé")
    message: str = Field(..., description="Message de confirmation")
