"""doc."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from src.api.deps import CurrentUser
from src.dao.cocktail_dao import CocktailDAO
from src.service.cocktail_service import CocktailService
from src.utils.exceptions import ServiceError

router = APIRouter(prefix="/cocktails", tags=["Cocktails"])

cocktail_service = CocktailService(cocktail_dao=CocktailDAO())


@router.get("/sequence/{sequence}")
def rechercher_cocktail_par_sequence_debut(sequence: str, max_resultats: int = 10):
    """Récupère les cocktails qui commencent par une séquence donnée.
       (dans la limite de max_resultats).

    Parameters
    ----------
    sequence : str \n
        Une chaîne de caractères.
    max_resultats : int \n
        Le nombre maximal de cocktails à récupérer.

    Returns
    -------
    dict\n
        Dictionnaire contenant la liste des cocktails, leur nombre et la séquence en question.

    Raises
    ------
    HTTPException\n
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
            detail_message = "Le paramètre 'sequence' doit être une chaîne de caractères (string)."
        elif not sequence:
            detail_message = "La séquence de recherche ne doit pas être vide."
        elif not isinstance(max_resultats, int):
            detail_message = "Le paramètre 'max_resultats' doit être un entier (integer)."
        elif max_resultats < 1:
            detail_message = "Le nombre maximum de résultats doit être supérieur ou égal à 1."
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail_message,
        )

    try:
        # Recherche des cocktails
        cocktails = cocktail_service.rechercher_cocktail_par_sequence_debut(
            sequence,
            max_resultats,
        )

        if not cocktails:
            # Si aucun cocktail n'est trouvé, renvoyer une erreur 404
            raise LookupError(f"Aucun cocktail trouvé pour la séquence '{sequence}'")

        # Si des cocktails sont trouvés, les formater en dictionnaire
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
            "sequence": sequence,
        }

    except LookupError as e:
        # Si aucun cocktail n'est trouvé pour la séquence
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except Exception as e:
        # Erreurs serveur
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur serveur: {e!s}",
        )


@router.get("/nom/{nom}")
def rechercher_cocktail_par_nom(nom: str):
    """Récupère tous le cocktail via son nom.

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
    HTTPException\n
        - 404 si le cocktail n'est pas trouvé
        - 500 en cas d'erreur serveur.

    """
    try:
        cocktail = cocktail_service.rechercher_cocktail_par_nom(nom)

        cocktail_json = {
            "id_cocktail": cocktail.id_cocktail,
            "nom": cocktail.nom,
            "categorie": cocktail.categorie,
            "verre": cocktail.verre,
            "alcool": cocktail.alcool,
            "image": cocktail.image,
        }

        return cocktail_json

    except LookupError as e:
        # Cas où le cocktail n'est pas trouvé
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except Exception as e:
        # Cas pour toutes les autres erreurs
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur serveur: {e!s}",
        )


@router.get(
    "/realisables",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Récupérer les cocktails réalisables",
)
def get_cocktails_realisables(
    current_user: CurrentUser,
) -> dict:
    """Récupérer les cocktails réalisables avec le stock actuel."""
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
    response_model=dict,
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
