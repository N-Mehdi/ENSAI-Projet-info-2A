"""doc."""

from fastapi import APIRouter, HTTPException, Query, status

from src.api.deps import CurrentUser
from src.service.ingredient_service import IngredientService

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


'''@router.get("/{ingredient_id}/is-alcoholic", summary="Vérifier si un ingrédient contient de l'alcool (par ID)")
def check_ingredient_alcohol_by_id(
    ingredient_id: int = Path(..., description="L'ID de l'ingrédient", gt=0)
):
    """
    Vérifie si un ingrédient contient de l'alcool en utilisant son ID
    
    - **ingredient_id**: L'ID unique de l'ingrédient
    
    Retourne:
    - **ingredient_id**: L'ID de l'ingrédient
    - **is_alcoholic**: True si l'ingrédient contient de l'alcool, False sinon
    - **message**: Message descriptif
    """
    try:
        result = service.check_if_alcoholic(ingredient_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")
'''


@router.get("/vérifier-alcool", summary="Vérifier si un ingrédient contient de l'alcool (par nom)")
def check_ingredient_alcohol_by_name(
    current_user: CurrentUser,
    name: str = Query(..., description="Le nom de l'ingrédient", min_length=1),
):
    """Vérifie si un ingrédient contient de l'alcool en utilisant son nom

    - **name**: Le nom de l'ingrédient (insensible à la casse)

    Retourne:
    - **ingredient_name**: Le nom de l'ingrédient recherché
    - **is_alcoholic**: True si l'ingrédient contient de l'alcool, False sinon
    - **message**: Message descriptif
    """
    try:
        result = service.check_if_alcoholic_by_name(name)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {e!s}")
