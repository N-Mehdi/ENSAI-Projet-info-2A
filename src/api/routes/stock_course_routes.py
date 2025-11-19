"""doc."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from src.api.deps import CurrentUser
from src.models.stock import Stock, StockItem, StockItemAddByName, StockItemRemove
from src.service.stock_course_service import StockCourseService
from src.utils.exceptions import (
    IngredientNotFoundError,
    InsufficientQuantityError,
    InvalidQuantityError,
    ServiceError,
    UniteNotFoundError,
)

router = APIRouter(prefix="/stock", tags=["Stock"])
service = StockCourseService()


@router.post(
    "/ajouter",
    summary=" +  Ajouter un ingrédient à mon stock",
    description="""
Ajoute ou met à jour un ingrédient dans le stock de l'utilisateur connecté.

🔒 Authentification requise

**Normalisation automatique du nom :**
- "vodka" → "Vodka"
- "POMEGRANATE JUICE" → "Pomegranate Juice"
- "  rhum   blanc  " → "Rhum Blanc"
- "151 proof rum" → "151 Proof Rum"

**Unités acceptées :**
- **Liquides** : ml, cl, l, dl, oz, fl oz, tsp, tbsp, cup, shot
- **Solides** : g, kg, oz, lb, tsp, tbsp, cup, cube
- **Spéciales** : dash, drop, pinch, piece, slice, wedge, etc.

**Comportement :**
- Si l'ingrédient n'existe pas dans le stock → il est créé
- Si l'ingrédient existe déjà → sa quantité et son unité sont mises à jour

**En cas d'erreur :**
- Si l'ingrédient n'est pas trouvé, l'API vous suggèrera des noms similaires
- Si l'unité n'est pas reconnue, une erreur 404 sera retournée

**Exemples d'ingrédients valides :**
- Apple
- Vodka
- Pomegranate Juice
- 151 Proof Rum
- 7-Up

Pour voir la liste complète : `GET /api/ref/ingredients`
""",
    responses={
        200: {
            "description": "Ingrédient ajouté/mis à jour avec succès",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Ingrédient 'Vodka' ajouté/mis à jour avec succès (500.0 ml)",
                    },
                },
            },
        },
        400: {
            "description": "Quantité invalide",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "La quantité doit être supérieure à 0",
                    },
                },
            },
        },
        404: {
            "description": "Ingrédient ou unité non trouvé(e)",
            "content": {
                "application/json": {
                    "examples": {
                        "ingredient_not_found": {
                            "summary": "Ingrédient non trouvé",
                            "value": {
                                "detail": {
                                    "error": "Ingrédient 'Vdka' non trouvé.",
                                    "ingredient_recherche": "Vdka",
                                    "suggestions": ["Vodka", "Vodka Citron"],
                                },
                            },
                        },
                        "unite_not_found": {
                            "summary": "Unité non trouvée",
                            "value": {
                                "detail": "Unité 'mml' non trouvée",
                            },
                        },
                    },
                },
            },
        },
        500: {
            "description": "Erreur serveur",
        },
    },
)
def add_to_stock(
    item: StockItemAddByName,
    current_user: CurrentUser,
) -> dict[str, str]:
    """Ajoute ou met à jour un ingrédient dans le stock de l'utilisateur connecté.

    Normalise automatiquement le nom de l'ingrédient.
    Si l'ingrédient existe déjà, met à jour sa quantité et son unité.

    L'utilisateur est automatiquement récupéré depuis le token JWT.

    Parameters
    ----------
    item : StockItemAddByName
        Objet contenant nom_ingredient, quantite, unite (abréviation)
    current_user : CurrentUser
        L'utilisateur authentifié (injecté automatiquement)

    Returns
    -------
    dict[str, str]
        Dictionnaire contenant :
        - status : str ("success")
        - message : str (confirmation avec quantité et unité)

    Raises
    ------
    HTTPException(400)
        Si la quantité est invalide (≤ 0)
    HTTPException(404)
        Si l'ingrédient ou l'unité n'existe pas (avec suggestions pour l'ingrédient)
    HTTPException(500)
        En cas d'erreur serveur
    HTTPException(401/403)
        Si non authentifié ou token invalide

    """
    try:
        message = service.add_or_update_ingredient_by_name(
            id_utilisateur=current_user.id_utilisateur,
            nom_ingredient=item.nom_ingredient,
            quantite=item.quantite,
            abbreviation_unite=item.unite,
        )

    except InvalidQuantityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except IngredientNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": str(e),
                "ingredient_recherche": e.nom_ingredient,
                "suggestions": e.suggestions,
            },
        ) from e
    except UniteNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unité '{e.abbreviation}' non trouvée. Unités valides : ml, cl, l, g, kg, oz, etc.",
        ) from e
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne : {e!s}",
        ) from e
    return {"status": "success", "message": message}


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
    *,
    only_available: Annotated[
        bool,
        Query(description="Si True, retourne seulement les ingrédients disponibles"),
    ] = True,
) -> Stock:
    """Récupère le stock de l'utilisateur connecté.

    L'utilisateur est automatiquement récupéré depuis le token JWT.

    Parameters
    ----------
    current_user : CurrentUser
        L'utilisateur authentifié (injecté automatiquement)
    only_available : bool, optional
        Si True, retourne uniquement les ingrédients avec quantité > 0 (défaut: True)
        Si False, retourne tous les ingrédients du stock

    Returns
    -------
    Stock
        Objet contenant :
        - id_utilisateur : int
        - items : list[StockItem]
        - nombre_items : int

    Raises
    ------
    HTTPException(400)
        En cas d'erreur lors de la récupération
    HTTPException(500)
        En cas d'erreur serveur
    HTTPException(401/403)
        Si non authentifié ou token invalide

    """
    try:
        stock = service.get_user_stock(
            id_utilisateur=current_user.id_utilisateur,
            only_available=only_available,
        )

    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne : {e!s}",
        ) from e
    return stock


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
) -> StockItem:
    """Récupère un ingrédient spécifique du stock par son nom.

    Le nom est normalisé automatiquement.

    L'utilisateur est automatiquement récupéré depuis le token JWT.

    Parameters
    ----------
    nom_ingredient : str
        Le nom de l'ingrédient à récupérer
    current_user : CurrentUser
        L'utilisateur authentifié (injecté automatiquement)

    Returns
    -------
    StockItem
        Objet contenant id_ingredient, nom_ingredient, quantite,
        id_unite, code_unite, nom_unite_complet

    Raises
    ------
    HTTPException(404)
        Si l'ingrédient n'existe pas ou n'est pas dans le stock (avec suggestions)
    HTTPException(400)
        En cas d'erreur lors de la récupération
    HTTPException(500)
        En cas d'erreur serveur
    HTTPException(401/403)
        Si non authentifié ou token invalide

    """
    try:
        item = service.get_ingredient_from_stock_by_name(
            id_utilisateur=current_user.id_utilisateur,
            nom_ingredient=nom_ingredient,
        )

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
        ) from e
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne : {e!s}",
        ) from e
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"L'ingrédient '{nom_ingredient}' n'est pas dans votre stock",
        )
    return item


@router.delete(
    "/retirer",
    summary=" - Retirer une quantité d'un ingrédient",
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
) -> dict[str, str]:
    """Retire une quantité spécifique d'un ingrédient du stock.

    Si quantité retirée = quantité disponible → supprime l'ingrédient
    Si quantité retirée < quantité disponible → décrémente la quantité
    Si quantité retirée > quantité disponible → erreur

    L'utilisateur est automatiquement récupéré depuis le token JWT.

    Parameters
    ----------
    item : StockItemRemove
        Objet contenant nom_ingredient et quantite à retirer
    current_user : CurrentUser
        L'utilisateur authentifié (injecté automatiquement)

    Returns
    -------
    dict[str, str]
        Dictionnaire contenant :
        - status : str ("success")
        - message : str (confirmation)

    Raises
    ------
    HTTPException(400)
        Si la quantité est invalide ou insuffisante (avec quantités demandée/disponible)
    HTTPException(404)
        Si l'ingrédient n'existe pas (avec suggestions)
    HTTPException(500)
        En cas d'erreur serveur
    HTTPException(401/403)
        Si non authentifié ou token invalide

    """
    try:
        message = service.remove_ingredient_by_name(
            id_utilisateur=current_user.id_utilisateur,
            nom_ingredient=item.nom_ingredient,
            quantite=item.quantite,
        )

    except InvalidQuantityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except InsufficientQuantityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": str(e),
                "quantite_demandee": e.quantite_demandee,
                "quantite_disponible": e.quantite_disponible,
            },
        ) from e
    except IngredientNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": str(e),
                "ingredient_recherche": e.nom_ingredient,
                "suggestions": e.suggestions,
            },
        ) from e
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne : {e!s}",
        ) from e
    return {"status": "success", "message": message}


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
) -> dict[str, str]:
    """Supprime complètement un ingrédient du stock.

    Suppression totale quelle que soit la quantité, contrairement à
    DELETE /retirer qui retire une quantité spécifique.

    Le nom est normalisé automatiquement.

    L'utilisateur est automatiquement récupéré depuis le token JWT.

    Parameters
    ----------
    nom_ingredient : str
        Le nom de l'ingrédient à supprimer complètement
    current_user : CurrentUser
        L'utilisateur authentifié (injecté automatiquement)

    Returns
    -------
    dict[str, str]
        Dictionnaire contenant :
        - status : str ("success")
        - message : str (confirmation)

    Raises
    ------
    HTTPException(404)
        Si l'ingrédient n'existe pas (avec suggestions)
    HTTPException(400)
        En cas d'erreur lors de la suppression
    HTTPException(500)
        En cas d'erreur serveur
    HTTPException(401/403)
        Si non authentifié ou token invalide

    """
    try:
        message = service.delete_ingredient_by_name(
            id_utilisateur=current_user.id_utilisateur,
            nom_ingredient=nom_ingredient,
        )

    except IngredientNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": str(e),
                "ingredient_recherche": e.nom_ingredient,
                "suggestions": e.suggestions,
            },
        ) from e
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne : {e!s}",
        ) from e

    return {"status": "success", "message": message}


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
) -> list[dict]:
    """Récupère TOUS les ingrédients existants avec leur quantité dans le stock.

    Les ingrédients non présents dans le stock ont quantité = 0.
    Utile pour afficher une liste complète avec indication des possessions.

    L'utilisateur est automatiquement récupéré depuis le token JWT.

    Parameters
    ----------
    current_user : CurrentUser
        L'utilisateur authentifié (injecté automatiquement)

    Returns
    -------
    list[dict]
        Liste de tous les ingrédients avec leurs informations et
        la quantité possédée (0 si non en stock)

    Raises
    ------
    HTTPException(400)
        En cas d'erreur lors de la récupération
    HTTPException(500)
        En cas d'erreur serveur
    HTTPException(401/403)
        Si non authentifié ou token invalide

    """
    try:
        return service.get_full_stock_list(current_user.id_utilisateur)

    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne : {e!s}",
        ) from e
