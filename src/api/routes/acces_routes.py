from fastapi import APIRouter, HTTPException, Path, Query

from src.api.deps import CurrentUser
from src.models.acces import AccessList, AccessResponse, PrivateCocktailsList
from src.service.acces_service import AccesService
from utils.exceptions import (
    AccessAlreadyExistsException,
    AccessDeniedException,
    AccessNotFoundException,
    CocktailNotFoundException,
    SelfAccessException,
    UserNotFoundException,
)

router = APIRouter(prefix="/cocktails-prives", tags=["Cocktails Privés"])

acces_service = AccesService()


# GESTION DE LA LISTE PRIVÉE (AJOUT/SUPPRESSION DE COCKTAILS)

'''
@router.post(
    "/ajouter-cocktail/{cocktail_id}",
    response_model=AccessResponse,
    summary="Ajouter un cocktail à ma liste privée (par ID)",
    status_code=201,
)
def add_cocktail_to_private_list(
    current_user: CurrentUser,
    cocktail_id: int = Path(..., description="L'ID du cocktail à ajouter", gt=0),
):
    """Ajoute un cocktail à votre liste privée.

    L'utilisateur est automatiquement récupéré depuis le token JWT.

    **Paramètres:**
    - **cocktail_id**: L'ID du cocktail à ajouter

    **Retourne:**
    - Message de confirmation

    **Erreurs possibles:**
    - 401/403: Non authentifié ou token invalide
    - 404: L'utilisateur ou le cocktail n'existe pas
    - 409: Le cocktail est déjà dans la liste privée
    """
    try:
        result = acces_service.add_cocktail_to_private_list(current_user.pseudo, cocktail_id)
        return result
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CocktailNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AccessAlreadyExistsException as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {e!s}")

'''


@router.post(
    "/ajouter-cocktail",
    response_model=AccessResponse,
    summary="Ajouter un cocktail à ma liste privée (par nom)",
    status_code=201,
)
def add_cocktail_to_private_list_by_name(
    current_user: CurrentUser,
    cocktail_name: str = Query(..., description="Le nom du cocktail à ajouter", min_length=1),
):
    """Ajoute un cocktail à votre liste privée en utilisant son nom.

    L'utilisateur est automatiquement récupéré depuis le token JWT.

    **Paramètres:**
    - **cocktail_name**: Le nom du cocktail à ajouter (insensible à la casse)

    **Retourne:**
    - Message de confirmation avec le nom du cocktail

    **Erreurs possibles:**
    - 401/403: Non authentifié ou token invalide
    - 404: L'utilisateur ou le cocktail n'existe pas
    - 409: Le cocktail est déjà dans la liste privée
    """
    try:
        result = acces_service.add_cocktail_to_private_list_by_name(current_user.pseudo, cocktail_name)
        return result
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CocktailNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AccessAlreadyExistsException as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {e!s}")


'''
@router.delete(
    "/remove-cocktail/{cocktail_id}",
    response_model=AccessResponse,
    summary="Retirer un cocktail de ma liste privée (par ID)",
)
def remove_cocktail_from_private_list(
    current_user: CurrentUser,
    cocktail_id: int = Path(..., description="L'ID du cocktail à retirer", gt=0),
):
    """Retire un cocktail de votre liste privée.

    L'utilisateur est automatiquement récupéré depuis le token JWT.

    **Paramètres:**
    - **cocktail_id**: L'ID du cocktail à retirer

    **Retourne:**
    - Message de confirmation

    **Erreurs possibles:**
    - 401/403: Non authentifié ou token invalide
    - 404: L'utilisateur n'existe pas ou le cocktail n'est pas dans la liste privée
    """
    try:
        result = acces_service.remove_cocktail_from_private_list(current_user.pseudo, cocktail_id)
        return result
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AccessNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {e!s}")

'''


@router.delete(
    "/retirer-cocktail",
    response_model=AccessResponse,
    summary="Retirer un cocktail de ma liste privée (par nom)",
)
def remove_cocktail_from_private_list_by_name(
    current_user: CurrentUser,
    cocktail_name: str = Query(..., description="Le nom du cocktail à retirer", min_length=1),
):
    """Retire un cocktail de votre liste privée en utilisant son nom.

    L'utilisateur est automatiquement récupéré depuis le token JWT.

    **Paramètres:**
    - **cocktail_name**: Le nom du cocktail à retirer (insensible à la casse)

    **Retourne:**
    - Message de confirmation avec le nom du cocktail

    **Erreurs possibles:**
    - 401/403: Non authentifié ou token invalide
    - 404: L'utilisateur, le cocktail n'existe pas ou le cocktail n'est pas dans la liste privée
    """
    try:
        result = acces_service.remove_cocktail_from_private_list_by_name(current_user.pseudo, cocktail_name)
        return result
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CocktailNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AccessNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {e!s}")


# GESTION DES ACCÈS (PARTAGE AVEC D'AUTRES UTILISATEURS)


@router.post(
    "/donner-acces",
    response_model=AccessResponse,
    summary="Donner l'accès à un utilisateur",
    status_code=201,
)
def grant_access(
    current_user: CurrentUser,
    user_pseudo: str = Query(..., description="Le pseudo de l'utilisateur à qui donner l'accès"),
):
    """Donne l'accès à un autre utilisateur pour qu'il puisse voir vos cocktails privés.

    L'utilisateur propriétaire est automatiquement récupéré depuis le token JWT.

    **Paramètres:**
    - **user_pseudo**: Le pseudo de l'utilisateur qui recevra l'accès

    **Retourne:**
    - Message de confirmation
    - Informations sur l'accès créé

    **Erreurs possibles:**
    - 401/403: Non authentifié ou token invalide
    - 404: Un des utilisateurs n'existe pas
    - 400: Vous essayez de vous donner accès à vous-même
    - 409: L'accès existe déjà
    """
    try:
        result = acces_service.grant_access_to_user(current_user.pseudo, user_pseudo)
        return result
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SelfAccessException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AccessAlreadyExistsException as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {e!s}")


@router.delete(
    "/retirer-acces",
    response_model=AccessResponse,
    summary="Retirer l'accès à un utilisateur",
)
def revoke_access(
    current_user: CurrentUser,
    user_pseudo: str = Query(..., description="Le pseudo de l'utilisateur dont retirer l'accès"),
):
    """Retire l'accès d'un utilisateur à vos cocktails privés.

    L'utilisateur propriétaire est automatiquement récupéré depuis le token JWT.

    **Paramètres:**
    - **user_pseudo**: Le pseudo de l'utilisateur dont retirer l'accès

    **Retourne:**
    - Message de confirmation

    **Erreurs possibles:**
    - 401/403: Non authentifié ou token invalide
    - 404: Un des utilisateurs n'existe pas ou l'accès n'existe pas
    """
    try:
        result = acces_service.revoke_access_from_user(current_user.pseudo, user_pseudo)
        return result
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AccessNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {e!s}")


@router.get(
    "/liste-acces",
    response_model=AccessList,
    summary="Voir qui a accès à mes cocktails privés",
)
def get_access_list(
    current_user: CurrentUser,
):
    """Récupère la liste des utilisateurs ayant accès à vos cocktails privés.

    L'utilisateur est automatiquement récupéré depuis le token JWT.

    **Retourne:**
    - Liste des pseudos des utilisateurs ayant accès
    - Nombre total d'utilisateurs

    **Erreurs possibles:**
    - 401/403: Non authentifié ou token invalide
    - 404: L'utilisateur n'existe pas
    """
    try:
        result = acces_service.get_users_with_access(current_user.pseudo)
        return result
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {e!s}")


# CONSULTATION DES COCKTAILS PRIVÉS


@router.get(
    "/voir-liste/{owner_pseudo}",
    response_model=PrivateCocktailsList,
    summary="Voir les cocktails privés d'un autre utilisateur",
)
def view_private_cocktails(
    current_user: CurrentUser,
    owner_pseudo: str = Path(..., description="Le pseudo du propriétaire des cocktails"),
):
    """Permet de voir les cocktails privés d'un autre utilisateur (si vous avez l'accès).

    L'utilisateur qui consulte est automatiquement récupéré depuis le token JWT.

    **Paramètres:**
    - **owner_pseudo**: Le pseudo du propriétaire des cocktails à consulter

    **Retourne:**
    - Liste des cocktails privés avec leurs ingrédients
    - Nom de chaque cocktail
    - Composition détaillée (nom ingrédient, quantité, unité)

    **Erreurs possibles:**
    - 401/403: Non authentifié ou token invalide
    - 404: Un des utilisateurs n'existe pas
    - 403: Vous n'avez pas l'accès aux cocktails de cet utilisateur
    """
    try:
        result = acces_service.view_private_cocktails(owner_pseudo, current_user.pseudo)
        return result
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AccessDeniedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {e!s}")


@router.get(
    "/mes-cocktails",
    response_model=PrivateCocktailsList,
    summary="Voir mes propres cocktails privés",
)
def get_my_private_cocktails(
    current_user: CurrentUser,
):
    """Récupère la liste de vos propres cocktails privés.

    L'utilisateur est automatiquement récupéré depuis le token JWT.

    **Retourne:**
    - Liste de vos cocktails privés avec leurs ingrédients
    - Nom de chaque cocktail
    - Composition détaillée (nom ingrédient, quantité, unité)

    **Erreurs possibles:**
    - 401/403: Non authentifié ou token invalide
    - 404: L'utilisateur n'existe pas
    """
    try:
        result = acces_service.get_my_private_cocktails(current_user.pseudo)
        return result
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {e!s}")
