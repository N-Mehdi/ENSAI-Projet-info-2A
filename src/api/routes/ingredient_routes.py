from fastapi import APIRouter, HTTPException, Query, status

router = APIRouter(prefix="/ingredients", tags=["Ingredients"])


@router.get(
    "/search",
    summary="🔍 Rechercher un ingrédient par nom",
    description="""
Recherche des ingrédients dont le nom contient la chaîne donnée.

✅ Pas d'authentification requise (endpoint public)

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
):
    """Recherche des ingrédients par nom (insensible à la casse)."""
    try:
        from src.dao.ingredient_dao import IngredientDao
        from src.utils.text_utils import normalize_ingredient_name

        normalized_query = normalize_ingredient_name(query)
        ingredient_dao = IngredientDao()
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
        )
