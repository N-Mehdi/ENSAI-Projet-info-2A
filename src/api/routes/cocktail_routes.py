"""doc."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from src.api.deps import CurrentUser
from src.dao.cocktail_dao import CocktailDAO
from src.models.cocktail import CocktailAvecInstructions
from src.service.cocktail_service import CocktailService
from src.utils.exceptions import CocktailSearchError, ServiceError

router = APIRouter(prefix="/cocktails", tags=["Cocktails"])

cocktail_service = CocktailService(cocktail_dao=CocktailDAO())


@router.get("/sequence/{sequence}")
def rechercher_cocktail_par_sequence_debut(
    sequence: str,
    max_resultats: int = 10,
) -> dict:
    """Récupère les cocktails qui commencent par une séquence donnée.
       (dans la limite de max_resultats).

    Parameters
    ----------
    sequence : str
        Une chaîne de caractères.
    max_resultats : int
        Le nombre maximal de cocktails à récupérer.

    Returns
    -------
    dict
        Dictionnaire contenant la liste des cocktails, leur nombre et la séquence
        en question.

    Raises
    ------
    HTTPException
        - 400 si la séquence n'est pas valide
        (pas une chaîne de caractères, vide, ou None)
        - 400 si max_resultats n'est pas un entier supérieur ou égal à 1
        - 404 si aucun cocktail n'est trouvé pour la séquence
        - 500 si erreur serveur.

    """
    if (
        not isinstance(sequence, str)
        or not sequence
        or not sequence.isalpha()
        or not isinstance(max_resultats, int)
        or max_resultats < 1
    ):
        detail_message = ""

        if not isinstance(sequence, str):
            detail_message = (
                "Le paramètre 'sequence' doit être une chaîne de caractères (string)."
            )
        elif not sequence:
            detail_message = "La séquence de recherche ne doit pas être vide."
        elif not isinstance(max_resultats, int):
            detail_message = (
                "Le paramètre 'max_resultats' doit être un entier (integer)."
            )
        elif max_resultats < 1:
            detail_message = (
                "Le nombre maximum de résultats doit être supérieur ou égal à 1."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail_message,
        )

    try:
        cocktails_avec_instructions = (
            cocktail_service.rechercher_cocktail_par_sequence_debut(
                sequence,
                max_resultats,
            )
        )

        cocktails_dict = []
        for cocktail, instructions in cocktails_avec_instructions:
            cocktails_dict.append(
                {
                    "id_cocktail": cocktail.id_cocktail,
                    "nom": cocktail.nom,
                    "categorie": cocktail.categorie,
                    "verre": cocktail.verre,
                    "alcool": cocktail.alcool,
                    "image": cocktail.image,
                    "instructions": instructions,
                },
            )

        return {
            "drinks": cocktails_dict,
            "count": len(cocktails_dict),
            "sequence": sequence,
        }

    except CocktailSearchError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur serveur: {e!s}",
        ) from e
        if not cocktails_dict:
            raise LookupError(
                message=f"Aucun cocktail trouvé pour la séquence '{sequence}'",
            ) from None


@router.get("/nom/{nom}")
def rechercher_cocktail_par_nom(nom: str) -> CocktailAvecInstructions:
    """Récupère tous le cocktail via son nom.

    Parameters
    ----------
    nom : str
        Le nom du cocktail

    Returns
    -------
    Cocktail
        Le cocktail en question

    Raises
    ------
    HTTPException
        - 404 si le cocktail n'est pas trouvé
        - 500 en cas d'erreur serveur.

    """
    try:
        cocktail, instructions = cocktail_service.rechercher_cocktail_par_nom(nom)

    except CocktailSearchError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur serveur: {e!s}",
        ) from e
    return CocktailAvecInstructions(
        id_cocktail=cocktail.id_cocktail,
        nom=cocktail.nom,
        categorie=cocktail.categorie,
        verre=cocktail.verre,
        alcool=cocktail.alcool,
        image=cocktail.image,
        instructions=instructions,
    )


@router.get(
    "/realisables",
    status_code=status.HTTP_200_OK,
    summary="Récupérer les cocktails réalisables",
)
def get_cocktails_realisables(
    current_user: CurrentUser,
) -> dict:
    """Récupère les cocktails réalisables avec le stock actuel de l'utilisateur.

    Analyse le stock de l'utilisateur et identifie tous les cocktails
    qui peuvent être préparés avec les ingrédients disponibles en
    quantité suffisante.

    L'utilisateur est automatiquement récupéré depuis le token JWT.

    Parameters
    ----------
    current_user : CurrentUser
        L'utilisateur authentifié (injecté automatiquement)

    Returns
    -------
    dict
        Dictionnaire contenant la liste des cocktails réalisables
        avec leurs informations

    Raises
    ------
    HTTPException(500)
        En cas d'erreur lors de la récupération des cocktails réalisables
    HTTPException(401/403)
        Si non authentifié ou token invalide

    """
    try:
        service = CocktailService(CocktailDAO())
        return service.get_cocktails_realisables(current_user.id_utilisateur)
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get(
    "/quasi-realisables",
    status_code=status.HTTP_200_OK,
    summary="🔍 Cocktails presque réalisables",
    description="""
Retourne les cocktails que l'utilisateur peut **presque** réaliser.

🔒 Authentification requise

**Fonctionnalité :**
Trouve les cocktails pour lesquels il ne manque que quelques ingrédients,
triés par nombre d'ingrédients manquants croissant.

**Cas d'usage :**
- Découvrir de nouveaux cocktails accessibles
- Savoir quoi acheter pour compléter son stock
- Planifier ses courses intelligemment

**Exemple de réponse :**
```json
{
  "cocktails_quasi_realisables": [
    {
      "nom": "Mojito",
      "ingredients_manquants": ["Menthe fraîche"],
      "nombre_ingredients_manquants": 1,
      "nombre_ingredients_total": 5,
      "pourcentage_possession": 80.0
    }
  ],
  "nombre_cocktails": 1,
  "max_ingredients_manquants": 3
}
```
""",
)
def get_cocktails_quasi_realisables(
    current_user: CurrentUser,
    max_ingredients_manquants: Annotated[
        int,
        Query(
            ge=0,
            le=5,
            description="Nombre maximum d'ingrédients manquants acceptés",
        ),
    ] = 3,
) -> dict:
    """Récupérer les cocktails quasi-réalisables.

    Parameters
    ----------
    current_user : CurrentUser
        Dépendance de l'utilisateur connecté
    max_ingredients_manquants : int
        Nombre max d'ingrédients manquants (1-5, défaut: 3)

    Returns
    -------
    dict
        Liste des cocktails avec détails des ingrédients manquants

    Raises
    ------
    HTTPException
        500 si erreur serveur

    """
    if max_ingredients_manquants == 0:
        try:
            service = CocktailService(CocktailDAO())
            return service.get_cocktails_realisables(current_user.id_utilisateur)
        except ServiceError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            ) from e
    try:
        service = CocktailService(CocktailDAO())
        return service.get_cocktails_quasi_realisables(
            current_user.id_utilisateur,
            max_ingredients_manquants,
        )
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur serveur : {e}",
        ) from e
