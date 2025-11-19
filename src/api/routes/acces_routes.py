"""doc."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query

from src.api.deps import CurrentUser
from src.models.acces import AccessList, AccessResponse, PrivateCocktailsList
from src.service.acces_service import AccesService
from utils.exceptions import (
    AccessAlreadyExistsError,
    AccessDeniedError,
    AccessNotFoundError,
    CocktailNotFoundError,
    SelfAccessError,
    UserNotFoundError,
)

router = APIRouter(prefix="/cocktails-prives", tags=["Cocktails Privés"])

acces_service = AccesService()


# GESTION DE LA LISTE PRIVÉE (AJOUT/SUPPRESSION DE COCKTAILS)


@router.post(
    "/ajouter-cocktail",
    summary="Ajouter un cocktail à ma liste privée (par nom)",
    status_code=201,
)
def add_cocktail_to_private_list_by_name(
    current_user: CurrentUser,
    cocktail_name: Annotated[str, Query(..., description="Le nom du cocktail à ajouter", min_length=1)],
) -> AccessResponse:
    """Ajoute un cocktail à votre liste privée en utilisant son nom.

    L'utilisateur est automatiquement récupéré depuis le token JWT.

    Parameters
    ----------
    current_user : CurrentUser
        L'utilisateur authentifié (injecté automatiquement)
    cocktail_name : str
        Le nom du cocktail à ajouter (insensible à la casse)

    Returns
    -------
    AccessResponse
        Objet contenant le succès de l'opération et un message de confirmation

    Raises
    ------
    HTTPException(404)
        Si l'utilisateur ou le cocktail n'existe pas
    HTTPException(409)
        Si le cocktail est déjà dans la liste privée
    HTTPException(401/403)
        Si non authentifié ou token invalide
    HTTPException(500)
        En cas d'erreur serveur

    """
    try:
        result = acces_service.add_cocktail_to_private_list_by_name(current_user.pseudo, cocktail_name)

    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except CocktailNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except AccessAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {e!s}") from e
    return result


@router.delete(
    "/retirer-cocktail",
    summary="Retirer un cocktail de ma liste privée (par nom)",
)
def remove_cocktail_from_private_list_by_name(
    current_user: CurrentUser,
    cocktail_name: Annotated[str, Query(..., description="Le nom du cocktail à retirer", min_length=1)],
) -> AccessResponse:
    """Retire un cocktail de votre liste privée en utilisant son nom.

    L'utilisateur est automatiquement récupéré depuis le token JWT.

    Parameters
    ----------
    current_user : CurrentUser
        L'utilisateur authentifié (injecté automatiquement)
    cocktail_name : str
        Le nom du cocktail à retirer (insensible à la casse)

    Returns
    -------
    AccessResponse
        Objet contenant le succès de l'opération et un message de confirmation

    Raises
    ------
    HTTPException(404)
        Si l'utilisateur, le cocktail n'existe pas ou le cocktail n'est pas dans la liste privée
    HTTPException(401/403)
        Si non authentifié ou token invalide
    HTTPException(500)
        En cas d'erreur serveur

    """
    try:
        result = acces_service.remove_cocktail_from_private_list_by_name(current_user.pseudo, cocktail_name)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except CocktailNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except AccessNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {e!s}") from e
    return result


# GESTION DES ACCÈS (PARTAGE AVEC D'AUTRES UTILISATEURS)


@router.post(
    "/donner-acces",
    summary="Donner l'accès à un utilisateur",
    status_code=201,
)
def grant_access(
    current_user: CurrentUser,
    user_pseudo: Annotated[str, Query(..., description="Le pseudo de l'utilisateur à qui donner l'accès")],
) -> AccessResponse:
    """Donne l'accès à un autre utilisateur pour qu'il puisse voir vos cocktails privés.

    L'utilisateur propriétaire est automatiquement récupéré depuis le token JWT.

    Parameters
    ----------
    current_user : CurrentUser
        L'utilisateur authentifié (injecté automatiquement)
    user_pseudo : str
        Le pseudo de l'utilisateur qui recevra l'accès

    Returns
    -------
    AccessResponse
        Objet contenant le succès de l'opération, un message de confirmation
        et les informations sur l'accès créé

    Raises
    ------
    HTTPException(404)
        Si un des utilisateurs n'existe pas
    HTTPException(400)
        Si vous essayez de vous donner accès à vous-même
    HTTPException(409)
        Si l'accès existe déjà
    HTTPException(401/403)
        Si non authentifié ou token invalide
    HTTPException(500)
        En cas d'erreur serveur

    """
    try:
        result = acces_service.grant_access_to_user(current_user.pseudo, user_pseudo)

    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except SelfAccessError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except AccessAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {e!s}") from e
    return result


@router.delete(
    "/retirer-acces",
    summary="Retirer l'accès à un utilisateur",
)
def revoke_access(
    current_user: CurrentUser,
    user_pseudo: Annotated[str, Query(..., description="Le pseudo de l'utilisateur dont retirer l'accès")],
) -> AccessResponse:
    """Retire l'accès d'un utilisateur à vos cocktails privés.

    L'utilisateur propriétaire est automatiquement récupéré depuis le token JWT.

    Parameters
    ----------
    current_user : CurrentUser
        L'utilisateur authentifié (injecté automatiquement)
    user_pseudo : str
        Le pseudo de l'utilisateur dont retirer l'accès

    Returns
    -------
    AccessResponse
        Objet contenant le succès de l'opération et un message de confirmation

    Raises
    ------
    HTTPException(404)
        Si un des utilisateurs n'existe pas ou l'accès n'existe pas
    HTTPException(401/403)
        Si non authentifié ou token invalide
    HTTPException(500)
        En cas d'erreur serveur

    """
    try:
        result = acces_service.revoke_access_from_user(current_user.pseudo, user_pseudo)

    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except AccessNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {e!s}") from e
    return result


@router.get(
    "/liste-acces",
    summary="Voir qui a accès à mes cocktails privés",
)
def get_access_list(
    current_user: CurrentUser,
) -> AccessList:
    """Récupère la liste des utilisateurs ayant accès à vos cocktails privés.

    L'utilisateur est automatiquement récupéré depuis le token JWT.

    Parameters
    ----------
    current_user : CurrentUser
        L'utilisateur authentifié (injecté automatiquement)

    Returns
    -------
    AccessList
        Objet contenant la liste des pseudos des utilisateurs ayant accès
        et le nombre total d'utilisateurs

    Raises
    ------
    HTTPException(404)
        Si l'utilisateur n'existe pas
    HTTPException(401/403)
        Si non authentifié ou token invalide
    HTTPException(500)
        En cas d'erreur serveur

    """
    try:
        result = acces_service.get_users_with_access(current_user.pseudo)

    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {e!s}") from e
    return result


# CONSULTATION DES COCKTAILS PRIVÉS


@router.get(
    "/voir-liste/{owner_pseudo}",
    summary="Voir les cocktails privés d'un autre utilisateur",
)
def view_private_cocktails(
    current_user: CurrentUser,
    owner_pseudo: Annotated[str, Path(description="Le pseudo du propriétaire des cocktails")],
) -> PrivateCocktailsList:
    """Permet de voir les cocktails privés d'un autre utilisateur (si vous avez l'accès).

    L'utilisateur qui consulte est automatiquement récupéré depuis le token JWT.

    Parameters
    ----------
    current_user : CurrentUser
        L'utilisateur authentifié (injecté automatiquement)
    owner_pseudo : str
        Le pseudo du propriétaire des cocktails à consulter

    Returns
    -------
    PrivateCocktailsList
        Objet contenant la liste des cocktails privés avec leurs ingrédients,
        le nom de chaque cocktail et la composition détaillée
        (nom ingrédient, quantité, unité)

    Raises
    ------
    HTTPException(404)
        Si un des utilisateurs n'existe pas
    HTTPException(403)
        Si vous n'avez pas l'accès aux cocktails de cet utilisateur
    HTTPException(401/403)
        Si non authentifié ou token invalide
    HTTPException(500)
        En cas d'erreur serveur

    """
    try:
        result = acces_service.view_private_cocktails(owner_pseudo, current_user.pseudo)

    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except AccessDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {e!s}") from e
    return result


@router.get(
    "/mes-cocktails",
    summary="Voir mes propres cocktails privés",
)
def get_my_private_cocktails(
    current_user: CurrentUser,
) -> PrivateCocktailsList:
    """Récupère la liste de vos propres cocktails privés.

    L'utilisateur est automatiquement récupéré depuis le token JWT.

    Parameters
    ----------
    current_user : CurrentUser
        L'utilisateur authentifié (injecté automatiquement)

    Returns
    -------
    PrivateCocktailsList
        Objet contenant la liste de vos cocktails privés avec leurs ingrédients,
        le nom de chaque cocktail et la composition détaillée
        (nom ingrédient, quantité, unité)

    Raises
    ------
    HTTPException(404)
        Si l'utilisateur n'existe pas
    HTTPException(401/403)
        Si non authentifié ou token invalide
    HTTPException(500)
        En cas d'erreur serveur

    """
    try:
        result = acces_service.get_my_private_cocktails(current_user.pseudo)

    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {e!s}") from e
    return result
