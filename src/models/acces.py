"""Modèles Pydantic pour l'accès des cocktails privés."""

from pydantic import BaseModel, Field


class CocktailIngredient(BaseModel):
    """Modèle pour un ingrédient dans un cocktail."""

    nom_ingredient: str
    quantite: float | None = None
    unite: str | None = None


class PrivateCocktailDetail(BaseModel):
    """Modèle pour les cocktails privés d'un utilisateur avec tous les
    détails pour chaque cocktail.
    """

    id_cocktail: int
    nom_cocktail: str
    ingredients: list[CocktailIngredient]

    categorie: str
    verre: str
    alcool: bool
    image: str
    instructions: str | None


class PrivateCocktailsList(BaseModel):
    """Modèle pour la liste des cocktails privés d'un utilisateur."""

    owner_pseudo: str
    cocktails: list[PrivateCocktailDetail]
    total_cocktails: int


class AccessRequest(BaseModel):
    """Modèle pour une demande d'accès."""

    user_pseudo: str = Field(
        ...,
        description="Le pseudo de l'utilisateur à qui donner l'accès",
    )


class AccessResponse(BaseModel):
    """Modèle pour la réponse d'une opération d'accès."""

    success: bool
    message: str
    owner_pseudo: str | None = None
    user_pseudo: str | None = None


class AccessStatus(BaseModel):
    """Modèle pour le statut d'accès d'un utilisateur."""

    user_pseudo: str
    has_access: bool
    is_owner: bool


class AccessList(BaseModel):
    """Modèle pour la liste des accès donnés."""

    owner_pseudo: str
    users_with_access: list[str]
    total_users: int
