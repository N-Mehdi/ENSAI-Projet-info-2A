"""Modèles pydantic pour l'avis."""

from datetime import datetime

from pydantic import BaseModel, Field


class AvisCreate(BaseModel):
    """Modèle pour créer ou modifier un avis."""

    nom_cocktail: str = Field(
        ...,
        min_length=2,
        description="Nom du cocktail",
        example="Mojito",
    )
    note: int | None = Field(
        None,
        ge=0,
        le=10,
        description="Note entre 0 et 10",
        example=8,
    )
    commentaire: str | None = Field(
        None,
        max_length=1000,
        description="Commentaire sur le cocktail (max 1000 caractères)",
        example="Excellent cocktail, très rafraîchissant !",
    )


class AvisResponse(BaseModel):
    """Modèle de réponse pour un avis."""

    id_utilisateur: int
    pseudo_utilisateur: str
    id_cocktail: int
    nom_cocktail: str
    note: int | None
    commentaire: str | None
    favoris: bool
    date_creation: datetime
    date_modification: datetime


class AvisSummary(BaseModel):
    """Résumé des avis pour un cocktail."""

    id_cocktail: int
    nom_cocktail: str
    nombre_avis: int
    note_moyenne: float | None
    nombre_favoris: int


class FavorisListResponse(BaseModel):
    """Réponse simplifiée pour la liste des favoris."""

    pseudo_utilisateur: str
    cocktails_favoris: list[str]  # Liste des noms de cocktails


class AvisListResponse(BaseModel):
    """Réponse simplifiée pour la liste des avis."""

    pseudo_utilisateur: str
    nom_cocktail: str
    note: int | None
    commentaire: str | None
