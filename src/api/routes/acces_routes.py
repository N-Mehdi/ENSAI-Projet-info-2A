"""Route contenant les endpoints sur les cocktails privés."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, status

from src.api.deps import CurrentUser
from src.dao.cocktail_dao import CocktailDAO
from src.models.acces import AccessList, AccessResponse, PrivateCocktailsList
from src.models.cocktail import CocktailPriveCreate, IngredientCreate
from src.service.acces_service import AccesService
from src.service.cocktail_service import CocktailService
from src.service.ingredient_service import IngredientService
from utils.exceptions import (
    AccessAlreadyExistsError,
    AccessDeniedError,
    AccessNotFoundError,
    CocktailDupeError,
    CocktailNotFoundError,
    OneIngredientError,
    SelfAccessError,
    ServiceError,
    UserNotFoundError,
)

router = APIRouter(prefix="/cocktails-prives", tags=["Cocktails Privés"])

ingredient_service = IngredientService()
acces_service = AccesService()
cocktail_service = CocktailService(CocktailDAO())

# GESTION DE LA LISTE PRIVÉE (AJOUT/SUPPRESSION DE COCKTAILS)


@router.post(
    "/cocktails-prives",
    summary="Créer un cocktail privé",
    status_code=status.HTTP_201_CREATED,
)
def create_private_cocktail(
    current_user: CurrentUser,
    cocktail_prive: CocktailPriveCreate,
) -> dict:
    """Crée un nouveau cocktail privé pour l'utilisateur connecté.

    Le cocktail est automatiquement ajouté à votre liste privée avec is_owner=TRUE.
    Les ingrédients sont normalisés et créés s'ils n'existent pas dans la base.

    Parameters
    ----------
    current_user : CurrentUser
        L'utilisateur authentifié (injecté automatiquement)
    cocktail_prive : CocktailPriveCreate
        Données du cocktail à créer avec ses ingrédients

    Returns
    -------
    dict
        Le cocktail créé avec ses informations complètes

    Raises
    ------
    HTTPException(404)
        Si l'utilisateur n'existe pas
    HTTPException(401/403)
        Si non authentifié ou token invalide
    HTTPException(500)
        En cas d'erreur serveur

    Examples
    --------
    ```json
    {
        "nom": "Mon Mojito",
        "categorie": "Cocktail",
        "verre": "Highball",
        "alcool": true,
        "image": "mojito.jpg",
        "instructions": "Piler la menthe avec le sucre...",
        "ingredients": [
            {
                "nom_ingredient": "Rhum blanc",
                "quantite": 50,
                "unite": "ml"
            },
            {
                "nom_ingredient": "Menthe fraîche",
                "quantite": 10,
                "unite": "feuilles"
            },
            {
                "nom_ingredient": "Sucre",
                "quantite": 2,
                "unite": "cuillères à café"
            }
        ]
    }
    ```

    """
    try:
        cocktail_data = {
            "nom": cocktail_prive.nom,
            "categorie": cocktail_prive.categorie,
            "verre": cocktail_prive.verre,
            "alcool": cocktail_prive.alcool,
            "image": cocktail_prive.image,
        }
        ingredients = [
            {
                "nom_ingredient": ing.nom_ingredient,
                "quantite": ing.quantite,
                "unite": ing.unite,
            }
            for ing in cocktail_prive.ingredients
            if ing.nom_ingredient and ing.quantite > 0
        ]
        try:
            assert ingredients is not None
            # au moins 1 ingrédient
        except ValueError as e:
            raise OneIngredientError(
                message="Erreur dans la création ducocktail privé.",
            ) from e

        result = acces_service.create_private_cocktail_with_ingredients(
            owner_pseudo=current_user.pseudo,
            cocktail_data=cocktail_data,
            ingredients=ingredients,  # Le service reçoit maintenant la liste filtrée
            instructions=cocktail_prive.instructions,
        )

    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except CocktailDupeError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur serveur: {e!s}",
        ) from e

    return result


@router.post(
    "/ingredients",
    summary="Créer un nouvel ingrédient",
    status_code=status.HTTP_201_CREATED,
)
def create_ingredient(
    current_user: CurrentUser,
    ingredient: IngredientCreate,
) -> dict:
    """Crée un nouvel ingrédient dans la base de données.

    Le nom de l'ingrédient est automatiquement normalisé pour éviter les doublons.
    Si l'ingrédient existe déjà, retourne l'ingrédient existant.

    Parameters
    ----------
    current_user : CurrentUser
        L'utilisateur authentifié
    ingredient : IngredientCreate
        Données de l'ingrédient à créer

    Returns
    -------
    dict
        L'ingrédient créé ou existant

    """
    try:
        result = ingredient_service.get_or_create_ingredient(
            nom=ingredient.nom,
            alcool=ingredient.alcool,
        )

    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
    return result


@router.delete(
    "/retirer-cocktail",
    summary="Retirer un cocktail de ma liste privée (par nom)",
)
def remove_cocktail_from_private_list_by_name(
    current_user: CurrentUser,
    cocktail_name: Annotated[
        str,
        Query(..., description="Le nom du cocktail à retirer", min_length=1),
    ],
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
        Si l'utilisateur, le cocktail n'existe pas ou le cocktail n'est pas dans la
        liste privée
    HTTPException(401/403)
        Si non authentifié ou token invalide
    HTTPException(500)
        En cas d'erreur serveur

    """
    try:
        result = acces_service.remove_cocktail_from_private_list_by_name(
            current_user.pseudo,
            cocktail_name,
        )
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
    user_pseudo: Annotated[
        str,
        Query(..., description="Le pseudo de l'utilisateur à qui donner l'accès"),
    ],
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
    user_pseudo: Annotated[
        str,
        Query(..., description="Le pseudo de l'utilisateur dont retirer l'accès"),
    ],
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
    owner_pseudo: Annotated[
        str,
        Path(description="Le pseudo du propriétaire des cocktails"),
    ],
) -> PrivateCocktailsList:
    """Permet de voir les cocktails privés d'un autre utilisateur, si vous avez l'accès.

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
