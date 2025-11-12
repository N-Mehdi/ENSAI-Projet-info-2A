from fastapi import APIRouter, HTTPException

from src.api.deps import CurrentUser
from src.service.avis_service import AvisService
from src.utils.exceptions import (
    AvisNotFoundError,
    IngredientNotFoundError,
    ServiceError,
)

router = APIRouter(prefix="/favoris", tags=["Favoris"])
service = AvisService()


@router.post(
    "/favoris/{nom_cocktail}",
    summary="➕ Ajouter aux favoris",
    description="""
Ajoute un cocktail aux favoris.

🔒 Authentification requise

**Comportement :**
- Si le cocktail n'est pas encore en favoris → Ajoute aux favoris
- Si le cocktail est déjà en favoris → Message "déjà en favoris"

**Note :** Cette action peut créer un avis avec note et commentaire NULL.
Vous pourrez ajouter note/commentaire plus tard avec POST /add.
""",
)
def add_favoris(
    nom_cocktail: str,
    current_user: CurrentUser,
):
    """Ajoute un cocktail aux favoris."""
    try:
        return service.add_favoris(
            id_utilisateur=current_user.id_utilisateur,
            nom_cocktail=nom_cocktail,
        )
    except IngredientNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail={
                "error": str(e),
                "cocktail_recherche": e.nom_ingredient,
                "suggestions": e.suggestions,
            },
        )
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/mes-favoris",
    summary="⭐ Mes cocktails favoris",
    description="""
Récupère la liste de mes cocktails favoris (format simplifié).

🔒 Authentification requise

**Format de réponse :**
```json
{
  "pseudo_utilisateur": "mehdi",
  "cocktails_favoris": ["Mojito", "Piña Colada", "Margarita"]
}
```
""",
)
def get_mes_favoris(current_user: CurrentUser):
    """Récupère les cocktails favoris (format simplifié)."""
    try:
        return service.get_mes_favoris_simple(
            id_utilisateur=current_user.id_utilisateur,
            pseudo=current_user.pseudo,
        )
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/favoris/{nom_cocktail}",
    summary="🗑️ Retirer des favoris",
    description="""
Retire un cocktail des favoris.

🔒 Authentification requise

**Comportement :**
- Si le cocktail est en favoris → Retire des favoris
- Si le cocktail n'est pas en favoris → Erreur 404
""",
)
def remove_favoris(
    nom_cocktail: str,
    current_user: CurrentUser,
):
    """Retire un cocktail des favoris."""
    try:
        message = service.remove_favoris(
            id_utilisateur=current_user.id_utilisateur,
            nom_cocktail=nom_cocktail,
        )
        return {"status": "success", "message": message}

    except AvisNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Le cocktail '{nom_cocktail}' n'est pas dans vos favoris",
        )
    except IngredientNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail={
                "error": str(e),
                "cocktail_recherche": e.nom_ingredient,
                "suggestions": e.suggestions,
            },
        )
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
