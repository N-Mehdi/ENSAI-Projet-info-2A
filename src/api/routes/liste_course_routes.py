from fastapi import APIRouter, HTTPException

from src.api.deps import CurrentUser
from src.models.liste_course import ListeCourseItemAdd
from src.service.liste_course_service import ListeCourseService
from src.utils.exceptions import (
    IngredientNotFoundError,
    InvalidQuantityError,
    ServiceError,
)

router = APIRouter(prefix="/liste-course", tags=["Liste de Course"])
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
def get_my_liste_course(current_user: CurrentUser):
    """Récupère la liste de course."""
    try:
        return service.get_liste_course(current_user.id_utilisateur)
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/add",
    summary="➕ Ajouter à la liste de course",
    description="""
Ajoute un ingrédient à la liste de course.

🔒 Authentification requise

**Comportement intelligent :**
- Si l'ingrédient existe déjà avec la **même unité** → additionne les quantités
- Si l'ingrédient existe avec une **unité différente** (même type) → convertit et additionne
- Si les unités ne sont pas compatibles → remplace

**Exemple :**
- J'ai déjà "2 oz" de Vodka
- J'ajoute "30 ml" de Vodka
- Résultat : 2 oz + 30 ml = 3.01 oz (conversion automatique)
""",
)
def add_to_liste_course(
    item: ListeCourseItemAdd,
    current_user: CurrentUser,
):
    """Ajoute un ingrédient à la liste de course."""
    try:
        message = service.add_to_liste_course(
            id_utilisateur=current_user.id_utilisateur,
            nom_ingredient=item.nom_ingredient,
            quantite=item.quantite,
            id_unite=item.id_unite,
        )
        return {"status": "success", "message": message}

    except InvalidQuantityError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IngredientNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail={
                "error": str(e),
                "ingredient_recherche": e.nom_ingredient,
                "suggestions": e.suggestions,
            },
        )
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))


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
):
    """Retire de la liste et ajoute au stock."""
    try:
        message = service.remove_from_liste_course_and_add_to_stock(
            id_utilisateur=current_user.id_utilisateur,
            nom_ingredient=nom_ingredient,
        )
        return {"status": "success", "message": message}

    except IngredientNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail={
                "error": str(e),
                "ingredient_recherche": e.nom_ingredient,
                "suggestions": e.suggestions,
            },
        )
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))


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
):
    """Retire de la liste sans ajouter au stock."""
    try:
        message = service.remove_from_liste_course(
            id_utilisateur=current_user.id_utilisateur,
            nom_ingredient=nom_ingredient,
        )
        return {"status": "success", "message": message}

    except IngredientNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail={
                "error": str(e),
                "ingredient_recherche": e.nom_ingredient,
                "suggestions": e.suggestions,
            },
        )
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))


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
def clear_liste_course(current_user: CurrentUser):
    """Vide la liste de course."""
    try:
        message = service.clear_liste_course(current_user.id_utilisateur)
        return {"status": "success", "message": message}

    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/toggle/{nom_ingredient}",
    summary="✓ Cocher/Décocher un item",
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
):
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
        )
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
