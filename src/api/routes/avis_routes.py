"""doc."""

from fastapi import APIRouter, HTTPException

from src.api.deps import CurrentUser
from src.models.avis import AvisCreate, AvisSummary
from src.service.avis_service import AvisService
from src.utils.exceptions import (
    AvisNotFoundError,
    IngredientNotFoundError,
    InvalidAvisError,
    ServiceError,
)

router = APIRouter(prefix="/avis", tags=["Avis"])
service = AvisService()


@router.post(
    "/ajouter",
    summary=" + Ajouter ou modifier un avis",
    description="""
Ajoute ou modifie un avis sur un cocktail.

🔒 Authentification requise

**Règles :**
- Au moins la note OU le commentaire doit être renseigné
- Note : entier entre 0 et 10
- Commentaire : max 1000 caractères
- Si un avis existe déjà pour ce cocktail, il est mis à jour

**Comportement UPSERT :**
- Première fois → Crée l'avis
- Déjà un avis → Met à jour note et commentaire
""",
)
def add_avis(
    avis: AvisCreate,
    current_user: CurrentUser,
) -> dict:
    """Ajoute ou modifie un avis sur un cocktail.

    Utilise le comportement UPSERT : crée l'avis s'il n'existe pas,
    sinon met à jour l'avis existant.

    L'utilisateur est automatiquement récupéré depuis le token JWT.

    Parameters
    ----------
    avis : AvisCreate
        Objet contenant nom_cocktail, note (optionnel), commentaire (optionnel)
    current_user : CurrentUser
        L'utilisateur authentifié (injecté automatiquement)

    Returns
    -------
    dict
        Dictionnaire contenant :
        - status : str ("success")
        - message : str (message de confirmation)

    Raises
    ------
    HTTPException(400)
        Si l'avis est invalide (ni note ni commentaire renseigné)
    HTTPException(404)
        Si le cocktail n'existe pas (avec suggestions)
    HTTPException(401/403)
        Si non authentifié ou token invalide

    """
    try:
        message = service.create_or_update_avis(
            id_utilisateur=current_user.id_utilisateur,
            nom_cocktail=avis.nom_cocktail,
            note=avis.note,
            commentaire=avis.commentaire,
        )

    except InvalidAvisError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except IngredientNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail={
                "error": str(e),
                "cocktail_recherche": e.nom_ingredient,
                "suggestions": e.suggestions,
            },
        ) from e
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {"status": "success", "message": message}


@router.delete(
    "/{nom_cocktail}",
    summary="🗑️ Supprimer mon avis",
    description="""
Supprime mon avis sur un cocktail.

🔒 Authentification requise
""",
)
def delete_avis(
    nom_cocktail: str,
    current_user: CurrentUser,
) -> dict:
    """Supprime l'avis de l'utilisateur connecté sur un cocktail.

    L'utilisateur est automatiquement récupéré depuis le token JWT.

    Parameters
    ----------
    nom_cocktail : str
        Le nom du cocktail dont supprimer l'avis
    current_user : CurrentUser
        L'utilisateur authentifié (injecté automatiquement)

    Returns
    -------
    dict
        Dictionnaire contenant :
        - status : str ("success")
        - message : str (message de confirmation)

    Raises
    ------
    HTTPException(404)
        Si l'avis ou le cocktail n'existe pas (avec suggestions)
    HTTPException(400)
        En cas d'erreur lors de la suppression
    HTTPException(401/403)
        Si non authentifié ou token invalide

    """
    try:
        message = service.delete_avis(
            id_utilisateur=current_user.id_utilisateur,
            nom_cocktail=nom_cocktail,
        )

    except AvisNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except IngredientNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail={
                "error": str(e),
                "cocktail_recherche": e.nom_ingredient,
                "suggestions": e.suggestions,
            },
        ) from e
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"status": "success", "message": message}


@router.get(
    "/mes-avis",
    summary="📝 Mes avis",
    description="""
Récupère tous mes avis (format simplifié).

🔒 Authentification requise

**Format de réponse :**
```json
{
  "pseudo_utilisateur": "mehdi",
  "avis": [
    {
      "nom_cocktail": "Mojito",
      "note": 9,
      "commentaire": "Excellent cocktail !"
    },
    {
      "nom_cocktail": "Margarita",
      "note": 8,
      "commentaire": null
    }
  ]
}
```
""",
)
def get_mes_avis(current_user: CurrentUser) -> dict:
    """Récupère tous les avis de l'utilisateur connecté au format simplifié.

    L'utilisateur est automatiquement récupéré depuis le token JWT.

    Parameters
    ----------
    current_user : CurrentUser
        L'utilisateur authentifié (injecté automatiquement)

    Returns
    -------
    dict
        Dictionnaire contenant :
        - pseudo_utilisateur : str
        - avis : list[dict] avec nom_cocktail, note, commentaire

    Raises
    ------
    HTTPException(400)
        En cas d'erreur lors de la récupération
    HTTPException(401/403)
        Si non authentifié ou token invalide

    """
    try:
        return service.get_mes_avis_simple(
            id_utilisateur=current_user.id_utilisateur,
            pseudo=current_user.pseudo,
        )
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get(
    "/cocktail/{nom_cocktail}",
    summary="📋 Voir tous les avis d'un cocktail",
    description="""
Récupère tous les avis d'un cocktail.

✅ Pas d'authentification requise (endpoint public)

**Informations retournées :**
- Pseudo de l'utilisateur
- Note
- Commentaire
- Date de création
- Date de modification
""",
)
def get_avis_cocktail(nom_cocktail: str, _current_user: CurrentUser) -> list:
    """Récupère tous les avis d'un cocktail (endpoint public).

    Parameters
    ----------
    nom_cocktail : str
        Le nom du cocktail
    _current_user : CurrentUser
        L'utilisateur authentifié (non utilisé, endpoint public)

    Returns
    -------
    list
        Liste des avis du cocktail avec pseudo_utilisateur, note,
        commentaire, date_creation, date_modification

    Raises
    ------
    HTTPException(404)
        Si le cocktail n'existe pas (avec suggestions)
    HTTPException(400)
        En cas d'erreur lors de la récupération

    """
    try:
        return service.get_avis_cocktail(nom_cocktail)
    except IngredientNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail={
                "error": str(e),
                "cocktail_recherche": e.nom_ingredient,
                "suggestions": e.suggestions,
            },
        ) from e
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get(
    "/summary/{nom_cocktail}",
    summary="📊 Résumé des avis d'un cocktail",
    description="""
Récupère un résumé statistique des avis d'un cocktail.

**Informations retournées :**
- Nombre total d'avis
- Note moyenne
- Nombre de favoris
""",
)
def get_avis_summary(nom_cocktail: str, _current_user: CurrentUser) -> AvisSummary:
    """Récupère un résumé statistique des avis d'un cocktail.

    Parameters
    ----------
    nom_cocktail : str
        Le nom du cocktail
    _current_user : CurrentUser
        L'utilisateur authentifié (non utilisé, endpoint public)

    Returns
    -------
    AvisSummary
        Objet contenant id_cocktail, nom_cocktail, nombre_avis,
        note_moyenne, nombre_favoris

    Raises
    ------
    HTTPException(404)
        Si le cocktail n'existe pas (avec suggestions)
    HTTPException(400)
        En cas d'erreur lors de la récupération

    """
    try:
        return service.get_avis_summary(nom_cocktail)
    except IngredientNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail={
                "error": str(e),
                "cocktail_recherche": e.nom_ingredient,
                "suggestions": e.suggestions,
            },
        ) from e
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
