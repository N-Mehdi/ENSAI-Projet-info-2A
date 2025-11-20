"""doc."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, status

from src.api.deps import CurrentUser
from src.dao.ingredient_dao import IngredientDAO
from src.service.ingredient_service import IngredientService
from src.utils.exceptions import IngredientNotFoundError
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
- Recherche "rum" : retourne "151 Proof Rum", "Dark Rum", "Light Rum", etc.
- Recherche "juice" : retourne "Apple Juice", "Orange Juice", "Cranberry Juice", etc.
""",
)
def search_ingredient(
    nom_ingredient: Annotated[
        str,
        Path(
            ...,
            min_length=2,
            description="Terme de recherche (minimum 2 caractères)",
            example="vodka",
        ),
    ],
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=50,
            description="Nombre maximum de résultats",
        ),
    ] = 10,
) -> dict:
    """Recherche des ingrédients par nom (insensible à la casse, endpoint public).

    La recherche normalise le terme de recherche et trouve tous les ingrédients
    dont le nom contient la chaîne donnée.

    Parameters
    ----------
    nom_ingredient : str
        Terme de recherche (minimum 2 caractères)
    limit : int, optional
        Nombre maximum de résultats (entre 1 et 50, défaut: 10)

    Returns
    -------
    dict
        Dictionnaire contenant :
        - query_originale : str (terme de recherche original)
        - query_normalisee : str (terme normalisé utilisé)
        - nombre_resultats : int
        - resultats : list[dict] (liste des ingrédients trouvés)

    Raises
    ------
    HTTPException(500)
        En cas d'erreur lors de la recherche

    """
    try:
        normalized_nom_ingredient = normalize_ingredient_name(nom_ingredient)
        ingredient_dao = IngredientDAO()
        results = ingredient_dao.search_by_name(normalized_nom_ingredient, limit=limit)

        return {
            "query_originale": nom_ingredient,
            "query_normalisee": normalized_nom_ingredient,
            "nombre_resultats": len(results),
            "resultats": results,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la recherche : {e!s}",
        ) from e


@router.get(
    "/vérifier-alcool",
    summary="Vérifier si un ingrédient contient de l'alcool (par nom)",
)
def check_ingredient_alcohol_by_name(
    _current_user: CurrentUser,
    name: Annotated[
        str,
        Query(
            ...,
            description="Le nom de l'ingrédient",
            min_length=1,
        ),
    ],
) -> dict:
    """Vérifie si un ingrédient contient de l'alcool par son nom.

    Parameters
    ----------
    _current_user : CurrentUser
        L'utilisateur authentifié (injecté automatiquement)
    name : str
        Le nom de l'ingrédient à vérifier

    Returns
    -------
    dict
        Dictionnaire contenant :
        - ingredient_name : str
        - is_alcoholic : bool
        - message : str (message descriptif)

    Raises
    ------
    HTTPException(404)
        Si l'ingrédient n'existe pas
    HTTPException(500)
        En cas d'erreur serveur
    HTTPException(401/403)
        Si non authentifié ou token invalide

    """
    try:
        result = service.check_if_alcoholic_by_name(name)

    except IngredientNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {e!s}") from e
    return result
