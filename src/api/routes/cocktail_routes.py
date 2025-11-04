from fastapi import APIRouter, HTTPException, status

from src.dao.cocktail_dao import CocktailDao
from src.service.cocktail_service import CocktailService

router = APIRouter(prefix="/cocktails", tags=["Cocktails"])

cocktail_service = CocktailService(cocktail_dao=CocktailDao())


@router.get("/lettre/{lettre}")
def rechercher_cocktail_par_lettre(lettre: str):
    """Récupère tous les cocktails qui commencent par une lettre donnée

    Parameters
    ----------
    lettre : str \n
        Une lettre de a à z

    Returns
    -------
    dict\n
        Dictionnaire contenant la liste des cocktails, leur nombre et la lettre en question

    Raises
    ------
    HTTPException\n
        - 400 si la lettre n'est pas valide
        - 500 si erreur serveur

    """
    if len(lettre) != 1 or not lettre.isalpha():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La lettre doit être un caractère alphabétique unique",
        )

    try:
        cocktails = cocktail_service.rechercher_cocktail_par_premiere_lettre(lettre.upper())

        cocktails_dict = [
            {
                "id_cocktail": c.id_cocktail,
                "nom": c.nom,
                "categorie": c.categorie,
                "verre": c.verre,
                "alcool": c.alcool,
                "image": c.image,
            }
            for c in cocktails
        ]

        return {
            "drinks": cocktails_dict,
            "count": len(cocktails),
            "lettre": lettre.upper(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur serveur: {e!s}",
        )


@router.get("/nom/{nom}")
def rechercher_cocktail_par_nom(nom: str):
    """Récupère tous le cocktail via son nom

    Parameters
    ----------
    nom : str \n
        Le nom du cocktail

    Returns
    -------
    Cocktail\n
        Le cocktail en question

    Raises
    ------
        à compléter

    """
    try:
        cocktail = cocktail_service.rechercher_cocktail_par_nom(nom)
        if cocktail is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cocktail '{nom}' non trouvé",
            )
        cocktail_json = {
            "id_cocktail": cocktail.id_cocktail,
            "nom": cocktail.nom,
            "categorie": cocktail.categorie,
            "verre": cocktail.verre,
            "alcool": cocktail.alcool,
            "image": cocktail.image,
        }

        return cocktail_json
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur serveur: {e!s}",
        )
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
