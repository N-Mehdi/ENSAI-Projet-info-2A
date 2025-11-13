from fastapi import APIRouter, HTTPException, Query, status

from src.api.deps import CurrentUser
from src.models.stock import StockItemAddByName, StockItemRemove
from src.service.stock_course_service import StockCourseService
from src.utils.exceptions import IngredientNotFoundError, InsufficientQuantityError, InvalidQuantityError, ServiceError

router = APIRouter(prefix="/stock", tags=["Stock"])
service = StockCourseService()


@router.post(
    "/aajouterdd",
    summary="➕ Ajouter un ingrédient à mon stock",
    description="""
Ajoute ou met à jour un ingrédient dans le stock de l'utilisateur connecté.

🔒 Authentification requise

**Normalisation automatique du nom :**
- "vodka" → "Vodka"
- "POMEGRANATE JUICE" → "Pomegranate Juice"
- "  rhum   blanc  " → "Rhum Blanc"
- "151 proof rum" → "151 Proof Rum"

**Comportement :**
- Si l'ingrédient n'existe pas dans le stock → il est créé
- Si l'ingrédient existe déjà → sa quantité et son unité sont mises à jour

**En cas d'erreur :**
Si l'ingrédient n'est pas trouvé, l'API vous suggèrera des noms similaires.

**Exemples d'ingrédients valides :**
- Apple
- Vodka
- Pomegranate Juice
- 151 Proof Rum
- 7-Up

Pour voir la liste complète : `GET /api/ref/ingredients`
""",
)
def add_to_stock(
    item: StockItemAddByName,
    current_user: CurrentUser,
):
    """Ajoute un ingrédient au stock en utilisant son nom."""
    try:
        message = service.add_or_update_ingredient_by_name(
            id_utilisateur=current_user.id_utilisateur,
            nom_ingredient=item.nom_ingredient,
            quantite=item.quantite,
            id_unite=item.id_unite,
        )
        return {"status": "success", "message": message}

    except InvalidQuantityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except IngredientNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": str(e),
                "ingredient_recherche": e.nom_ingredient,
                "suggestions": e.suggestions,
            },
        )
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne : {e!s}",
        )


@router.get(
    "/",
    summary="📦 Récupérer mon stock",
    description="""
Récupère le stock de l'utilisateur connecté.

🔒 Authentification requise

**Paramètres :**
- `only_available=true` (défaut) : Seulement les ingrédients avec quantité > 0
- `only_available=false` : Tous les ingrédients du stock (même ceux à 0)
""",
)
def get_my_stock(
    current_user: CurrentUser,
    only_available: bool = Query(
        True,
        description="Si True, retourne seulement les ingrédients disponibles",
    ),
):
    try:
        stock = service.get_user_stock(
            id_utilisateur=current_user.id_utilisateur,
            only_available=only_available,
        )
        return stock

    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne : {e!s}",
        )


@router.get(
    "/ingredient/{nom_ingredient}",
    summary="🔍 Récupérer un ingrédient de mon stock",
    description="""
Récupère un ingrédient spécifique du stock de l'utilisateur connecté en utilisant son nom.

🔒 Authentification requise

**Normalisation automatique :**
Le nom sera normalisé automatiquement (ex: "vodka" → "Vodka")

**Exemples :**
- `/api/stock/ingredient/Vodka`
- `/api/stock/ingredient/Orange Juice` (les espaces sont autorisés dans l'URL)
- `/api/stock/ingredient/151 Proof Rum`
""",
)
def get_my_ingredient(
    nom_ingredient: str,
    current_user: CurrentUser,
):
    """Récupère un ingrédient spécifique de mon stock par son nom."""
    try:
        item = service.get_ingredient_from_stock_by_name(
            id_utilisateur=current_user.id_utilisateur,
            nom_ingredient=nom_ingredient,
        )

        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"L'ingrédient '{nom_ingredient}' n'est pas dans votre stock",
            )

        return item

    except HTTPException:
        raise
    except IngredientNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": str(e),
                "ingredient_recherche": e.nom_ingredient,
                "suggestions": e.suggestions,
            },
        )
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne : {e!s}",
        )


@router.delete(
    "/retirer",
    summary="➖ Retirer une quantité d'un ingrédient",
    description="""
Retire une quantité spécifique d'un ingrédient du stock.

🔒 Authentification requise

**Comportement :**
- Si la quantité retirée = quantité disponible → l'ingrédient est supprimé du stock
- Si la quantité retirée < quantité disponible → la quantité est décrémentée
- Si la quantité retirée > quantité disponible → erreur 400

**Exemples :**
- Stock : Vodka = 500ml
- Retirer 100ml → Stock : Vodka = 400ml
- Retirer 500ml → Vodka supprimé du stock
- Retirer 600ml → ❌ Erreur (quantité insuffisante)

**Note :** Pour supprimer complètement un ingrédient sans préciser la quantité,
utilisez `DELETE /ingredient/{nom_ingredient}`
""",
)
def remove_quantity_from_stock(
    item: StockItemRemove,
    current_user: CurrentUser,
):
    """Retire une quantité d'un ingrédient du stock."""
    try:
        message = service.remove_ingredient_by_name(
            id_utilisateur=current_user.id_utilisateur,
            nom_ingredient=item.nom_ingredient,
            quantite=item.quantite,
        )
        return {"status": "success", "message": message}

    except InvalidQuantityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except InsufficientQuantityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": str(e),
                "quantite_demandee": e.quantite_demandee,
                "quantite_disponible": e.quantite_disponible,
            },
        )
    except IngredientNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": str(e),
                "ingredient_recherche": e.nom_ingredient,
                "suggestions": e.suggestions,
            },
        )
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne : {e!s}",
        )


@router.delete(
    "/ingredient/{nom_ingredient}",
    summary="🗑️ Supprimer complètement un ingrédient",
    description="""
Supprime complètement un ingrédient du stock (quelle que soit la quantité).

🔒 Authentification requise

**Différence avec DELETE /remove :**
- `DELETE /remove` : Retire une **quantité spécifique** (décrémente)
- `DELETE /ingredient/{nom}` : **Supprime complètement** l'ingrédient

**Exemple :**
- Stock : Vodka = 500ml
- `DELETE /ingredient/Vodka` → Vodka supprimée complètement du stock

**Normalisation automatique :**
Le nom sera normalisé automatiquement (ex: "vodka" → "Vodka")
""",
)
def delete_ingredient_completely(
    nom_ingredient: str,
    current_user: CurrentUser,
):
    """Supprime complètement un ingrédient du stock."""
    try:
        message = service.delete_ingredient_by_name(
            id_utilisateur=current_user.id_utilisateur,
            nom_ingredient=nom_ingredient,
        )
        return {"status": "success", "message": message}

    except IngredientNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": str(e),
                "ingredient_recherche": e.nom_ingredient,
                "suggestions": e.suggestions,
            },
        )
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne : {e!s}",
        )


@router.get(
    "/tout",
    summary="📋 Récupérer tous les ingrédients avec mon stock",
    description="""
Récupère TOUS les ingrédients existants avec leur quantité dans mon stock.

🔒 Authentification requise

Les ingrédients non présents dans le stock auront quantité = 0.

Utile pour afficher une liste complète de tous les ingrédients disponibles
avec indication de ce que vous possédez.
""",
)
def get_full_stock(
    current_user: CurrentUser,
):
    """Récupère tous les ingrédients avec indication de quantité dans mon stock."""
    try:
        return service.get_full_stock_list(current_user.id_utilisateur)

    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne : {e!s}",
        )
