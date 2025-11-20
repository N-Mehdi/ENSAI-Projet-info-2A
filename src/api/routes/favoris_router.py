"""doc."""

from fastapi import APIRouter, HTTPException

from src.api.deps import CurrentUser
from src.service.avis_service import AvisService
from src.utils.exceptions import AvisNotFoundError, CocktailNotFoundError, ServiceError

router = APIRouter(prefix="/favoris", tags=["Favoris"])
service = AvisService()


@router.post(
    "/favoris/{nom_cocktail}",
    summary=" + Ajouter aux favoris",
    description="""
Ajoute un cocktail aux favoris.

🔒 Authentification requise

**Comportement :**
- Si le cocktail n'est pas encore en favoris : Ajoute aux favoris
- Si le cocktail est déjà en favoris : Message "déjà en favoris"

**Note :** Cette action peut créer un avis avec note et commentaire NULL.
Vous pourrez ajouter note/commentaire plus tard avec POST /add.
""",
)
def add_favoris(
    nom_cocktail: str,
    current_user: CurrentUser,
) -> dict:
    """Ajoute un cocktail aux favoris de l'utilisateur connecté.

    Crée un avis avec favoris=TRUE si l'avis n'existe pas encore.
    Si l'avis existe déjà, met à jour le champ favoris.

    L'utilisateur est automatiquement récupéré depuis le token JWT.

    Parameters
    ----------
    nom_cocktail : str
        Le nom du cocktail à ajouter aux favoris
    current_user : CurrentUser
        L'utilisateur authentifié (injecté automatiquement)

    Returns
    -------
    dict
        Dictionnaire contenant le message de confirmation

    Raises
    ------
    HTTPException(404)
        Si le cocktail n'existe pas (avec suggestions)
    HTTPException(400)
        En cas d'erreur lors de l'ajout aux favoris
    HTTPException(401/403)
        Si non authentifié ou token invalide

    """
    try:
        return service.add_favoris(
            id_utilisateur=current_user.id_utilisateur,
            nom_cocktail=nom_cocktail,
        )
    except CocktailNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail={
                "error": str(e),
                "cocktail_recherche": e.nom_cocktail,
                "suggestions": e.suggestions,
            },
        ) from e
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


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
def get_mes_favoris(current_user: CurrentUser) -> dict:
    """Récupère la liste des cocktails favoris de l'utilisateur connecté.

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
        - cocktails_favoris : list[str] (liste des noms de cocktails)

    Raises
    ------
    HTTPException(400)
        En cas d'erreur lors de la récupération
    HTTPException(401/403)
        Si non authentifié ou token invalide

    """
    try:
        return service.get_mes_favoris_simple(
            id_utilisateur=current_user.id_utilisateur,
            pseudo=current_user.pseudo,
        )
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete(
    "/favoris/{nom_cocktail}",
    summary="🗑️ Retirer des favoris",
    description="""
Retire un cocktail des favoris.

🔒 Authentification requise

**Comportement :**
- Si le cocktail est en favoris : Retire des favoris
- Si le cocktail n'est pas en favoris : Erreur 404
""",
)
def remove_favoris(
    nom_cocktail: str,
    current_user: CurrentUser,
) -> dict:
    """Retire un cocktail des favoris de l'utilisateur connecté.

    Met le champ favoris à FALSE dans l'avis correspondant.

    L'utilisateur est automatiquement récupéré depuis le token JWT.

    Parameters
    ----------
    nom_cocktail : str
        Le nom du cocktail à retirer des favoris
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
        Si le cocktail n'existe pas (avec suggestions) ou n'est pas dans les favoris
    HTTPException(400)
        En cas d'erreur lors du retrait des favoris
    HTTPException(401/403)
        Si non authentifié ou token invalide

    """
    try:
        message = service.remove_favoris(
            id_utilisateur=current_user.id_utilisateur,
            nom_cocktail=nom_cocktail,
        )

    except AvisNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Le cocktail '{nom_cocktail}' n'est pas dans vos favoris",
        ) from e
    except CocktailNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail={
                "error": str(e),
                "cocktail_recherche": e.nom_cocktail,
                "suggestions": e.suggestions,
            },
        ) from e
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"status": "success", "message": message}
