"""doc."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from src.api.deps import CurrentUser
from src.models.cocktail_prive import CocktailResponse
from src.service.cocktail_utilisateur_service import CocktailUtilisateurService

router = APIRouter(prefix="/cocktails-teste", tags=["Cocktails testés"])

service = CocktailUtilisateurService()


@router.get(
    "/voir/cocktails-testes",
    summary="Récupérer les cocktails testés",
    description="Récupère tous les cocktails testés par l'utilisateur connecté. "
    "L'utilisateur propriétaire est automatiquement récupéré depuis le token JWT.",
)
def get_mes_cocktails_testes(current_user: CurrentUser) -> list[CocktailResponse]:
    """Récupère tous les cocktails testés par l'utilisateur connecté."""
    try:
        cocktails = service.get_cocktails_testes(current_user.id_utilisateur)
        return [
            CocktailResponse(
                id_cocktail=c.id_cocktail,
                nom=c.nom,
                categorie=c.categorie,
                verre=c.verre,
                alcool=c.alcool,
                image=c.image,
            )
            for c in cocktails
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des cocktails testés : {e!s}",
        ) from e


@router.post(
    "/ajouter/cocktail-teste",
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter un cocktail aux testés",
    description="Ajoute un cocktail aux cocktails testés de l'utilisateur connecté. "
    "L'utilisateur propriétaire est automatiquement récupéré depuis le token JWT.",
)
def ajouter_cocktail_teste(
    nom_cocktail: Annotated[str, Query(description="Le nom du cocktail à marquer comme testé")],
    current_user: CurrentUser,
) -> dict:
    """Ajoute un cocktail aux cocktails testés pour l'utilisateur connecté."""
    try:
        result = service.ajouter_cocktail_teste(
            current_user.id_utilisateur,
            nom_cocktail,
        )

        if result.get("deja_teste"):
            return {
                "message": f"Le cocktail '{result['nom_cocktail']}' est déjà dans vos cocktails testés",
                "nom_cocktail": result["nom_cocktail"],
                "teste": True,
            }

        return {
            "message": f"Cocktail '{result['nom_cocktail']}' ajouté aux testés",
            "nom_cocktail": result["nom_cocktail"],
            "teste": True,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'ajout : {e!s}",
        ) from e


@router.delete(
    "/retirer/cocktails/testes",
    status_code=status.HTTP_200_OK,
    summary="Retirer un cocktail des testés",
    description="Retire un cocktail des cocktails testés de l'utilisateur connecté. "
    "L'utilisateur propriétaire est automatiquement récupéré depuis le token JWT.",
)
def retirer_cocktail_teste(
    nom_cocktail: Annotated[str, Query(description="Le nom du cocktail dont retirer le statut testé")],
    current_user: CurrentUser,
) -> dict:
    """Retire un cocktail des cocktails testés pour l'utilisateur connecté."""
    try:
        result = service.retirer_cocktail_teste(
            current_user.id_utilisateur,
            nom_cocktail,
        )

        return {
            "message": f"Cocktail '{result['nom_cocktail']}' retiré des testés",
            "nom_cocktail": result["nom_cocktail"],
            "teste": False,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du retrait : {e!s}",
        ) from e
