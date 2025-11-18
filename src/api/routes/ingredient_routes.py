"""doc."""

from fastapi import APIRouter, HTTPException, Query, status

from src.api.deps import CurrentUser
from src.dao.ingredient_dao import IngredientDAO
from src.service.ingredient_service import IngredientService
from src.utils.text_utils import normalize_ingredient_name

router = APIRouter(prefix="/ingredients", tags=["Ingredients"])

service = IngredientService()


@router.get(
    "/recherche/{nom_ingredient}",
    summary="🔍 Rechercher un ingrédient par nom",
    description="""
Recherche des ingrédients dont le nom contient la chaîne donnée.

    Pas d'authentification requise (endpoint public)

Utile pour :
- Vérifier l'orthographe exacte d'un ingrédient avant de l'ajouter
- Explorer les ingrédients disponibles
- Auto-complétion

**Exemple :**
- Recherche "rum" → retourne "151 Proof Rum", "Dark Rum", "Light Rum", etc.
- Recherche "juice" → retourne "Apple Juice", "Orange Juice", "Cranberry Juice", etc.
""",
)
def search_ingredient(
    query: str = Query(
        ...,
        min_length=2,
        description="Terme de recherche (minimum 2 caractères)",
        example="vodka",
    ),
    limit: int = Query(
        10,
        ge=1,
        le=50,
        description="Nombre maximum de résultats",
    ),
) -> dict:
    """Recherche des ingrédients par nom (insensible à la casse)."""
    try:
        normalized_query = normalize_ingredient_name(query)
        ingredient_dao = IngredientDAO()
        results = ingredient_dao.search_by_name(normalized_query, limit=limit)

        return {
            "query_originale": query,
            "query_normalisee": normalized_query,
            "nombre_resultats": len(results),
            "resultats": results,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la recherche : {e!s}",
        ) from e


@router.get("/vérifier-alcool", summary="Vérifier si un ingrédient contient de l'alcool (par nom)")
def check_ingredient_alcohol_by_name(
    _current_user: CurrentUser,
    name: str = Query(..., description="Le nom de l'ingrédient", min_length=1),
) -> dict:
    """Doc."""
    try:
        result = service.check_if_alcoholic_by_name(name)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {e!s}") from e
    return result
