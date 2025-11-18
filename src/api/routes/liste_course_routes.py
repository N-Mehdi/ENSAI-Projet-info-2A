"""doc."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from src.api.deps import CurrentUser
from src.models.liste_course import ListeCourse
from src.service.liste_course_service import ListeCourseService
from src.utils.exceptions import IngredientNotFoundError, InvalidQuantityError, ServiceError, UniteNotFoundError

router = APIRouter(prefix="/liste-course", tags=["Liste de Courses"])
service = ListeCourseService()


@router.get(
    "/",
    summary="📋 Ma liste de course",
    description="""
Récupère ma liste de course complète.

🔒 Authentification requise

**Informations retournées :**
- Liste des ingrédients avec quantités et unités
- Statut 'effectué' (coché/décoché)
- Nombre total d'items
- Nombre d'items cochés
""",
)
def get_my_liste_course(current_user: CurrentUser) -> ListeCourse:
    """Récupère la liste de course."""
    try:
        return service.get_liste_course(current_user.id_utilisateur)
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post(
    "/ajouter",
    summary=" + Ajouter à la liste de course",
    description="""
Ajoute un ingrédient à la liste de course.

🔒 Authentification requise

**Comportement intelligent :**
- Si l'ingrédient existe déjà avec la **même unité** → additionne les quantités
- Si l'ingrédient existe avec une **unité différente** (même type) → convertit et additionne
- Si les unités ne sont pas compatibles → remplace

**Unités acceptées :**
- **Liquides** : ml, cl, l, dl, oz, fl oz, tsp, tbsp, cup, shot
- **Solides** : g, kg, oz, lb, tsp, tbsp, cup, cube
- **Spéciales** : dash, drop, pinch, piece, slice, wedge, etc.

**Exemple :**
- J'ai déjà "2 oz" de Vodka
- J'ajoute "30 ml" de Vodka
- Résultat : 2 oz + 30 ml = 3.01 oz (conversion automatique)
""",
    responses={
        200: {
            "description": "Ingrédient ajouté à la liste de course",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Ingrédient 'Vodka' ajouté à la liste de course (500.0 ml)",
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
                                "detail": "Unité 'mml' non trouvée. Unités valides : ml, cl, l, g, kg, oz, etc.",
                            },
                        },
                    },
                },
            },
        },
    },
)
def add_to_liste_course(
    nom_ingredient: Annotated[str, Query(min_length=2, description="Nom de l'ingrédient", example="Vodka")],
    quantite: Annotated[float, Query(gt=0, description="Quantité à acheter (doit être > 0)", example=500.0)],
    unite: Annotated[str, Query(min_length=1, description="Abréviation de l'unité (ex: 'ml', 'cl', 'g', 'kg')", example="ml")],
    current_user: CurrentUser,
) -> dict:
    """Ajoute un ingrédient à la liste de course."""
    try:
        message = service.add_to_liste_course(
            id_utilisateur=current_user.id_utilisateur,
            nom_ingredient=nom_ingredient,
            quantite=quantite,
            abbreviation_unite=unite,
        )

    except InvalidQuantityError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except IngredientNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail={
                "error": str(e),
                "ingredient_recherche": e.nom_ingredient,
                "suggestions": e.suggestions,
            },
        ) from e
    except UniteNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Unité '{e.abbreviation}' non trouvée. Unités valides : ml, cl, l, g, kg, oz, etc.",
        ) from e
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"status": "success", "message": message}


@router.delete(
    "/achete/{nom_ingredient}",
    summary="✅ Marquer comme acheté (retire et ajoute au stock)",
    description="""
Retire un ingrédient de la liste de course et l'ajoute au stock.

🔒 Authentification requise

**Comportement :**
1. Retire l'ingrédient de la liste de course
2. Ajoute cet ingrédient au stock avec sa quantité

**Conversion automatique :**
Si l'ingrédient existe déjà dans le stock avec une unité différente,
la conversion se fait automatiquement si les unités sont compatibles.
""",
)
def mark_as_bought(
    nom_ingredient: str,
    current_user: CurrentUser,
) -> dict:
    """Retire de la liste et ajoute au stock."""
    try:
        message = service.remove_from_liste_course_and_add_to_stock(
            id_utilisateur=current_user.id_utilisateur,
            nom_ingredient=nom_ingredient,
        )

    except IngredientNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail={
                "error": str(e),
                "ingredient_recherche": e.nom_ingredient,
                "suggestions": e.suggestions,
            },
        ) from e
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"status": "success", "message": message}


@router.delete(
    "/{nom_ingredient}",
    summary="🗑️ Supprimer de la liste (sans ajouter au stock)",
    description="""
Retire un ingrédient de la liste de course SANS l'ajouter au stock.

🔒 Authentification requise

**Différence avec `/achete/{nom}` :**
- `/achete/{nom}` : Retire ET ajoute au stock
- `/{nom}` : Retire uniquement (suppression)
""",
)
def remove_from_liste_course(
    nom_ingredient: str,
    current_user: CurrentUser,
) -> dict:
    """Retire de la liste sans ajouter au stock."""
    try:
        message = service.remove_from_liste_course(
            id_utilisateur=current_user.id_utilisateur,
            nom_ingredient=nom_ingredient,
        )

    except IngredientNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail={
                "error": str(e),
                "ingredient_recherche": e.nom_ingredient,
                "suggestions": e.suggestions,
            },
        ) from e
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"status": "success", "message": message}


@router.delete(
    "/",
    summary="🗑️ Vider la liste de course",
    description="""
Vide complètement la liste de course.

🔒 Authentification requise

⚠️ **Attention :** Cette action supprime TOUS les ingrédients de la liste.
Les ingrédients ne sont PAS ajoutés au stock.
""",
)
def clear_liste_course(current_user: CurrentUser) -> dict:
    """Vide la liste de course."""
    try:
        message = service.clear_liste_course(current_user.id_utilisateur)

    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {"status": "success", "message": message}


@router.put(
    "/cocher/{nom_ingredient}",
    summary="✓ Cocher/Décocher un ingrédient",
    description="""
Toggle le statut 'effectué' d'un item de la liste de course.

🔒 Authentification requise

**Comportement :**
- Si non coché → coche
- Si coché → décoche

**Note :** Ceci ne retire PAS l'ingrédient de la liste, c'est juste un indicateur visuel.
Pour retirer et ajouter au stock, utilisez `/achete/{nom}`.
""",
)
def toggle_effectue(
    nom_ingredient: str,
    current_user: CurrentUser,
) -> dict:
    """Toggle le statut effectué."""
    try:
        return service.toggle_effectue(
            id_utilisateur=current_user.id_utilisateur,
            nom_ingredient=nom_ingredient,
        )

    except IngredientNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail={
                "error": str(e),
                "ingredient_recherche": e.nom_ingredient,
                "suggestions": e.suggestions,
            },
        ) from e
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
