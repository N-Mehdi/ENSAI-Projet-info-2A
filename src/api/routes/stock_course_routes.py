"""stock_course_routes.py
Routes API pour la gestion du stock et de la liste de courses.
"""

from fastapi import APIRouter, HTTPException, status

from src.business_object.stock import Stock
from src.service.stock_course_service import Stock_course_service

router = APIRouter(prefix="/stock-course", tags=["Stock et Courses"])


@router.get("/stock/{id_stock}")
def get_stock(id_stock: int, nom_stock: str = "Stock"):
    """Récupère le stock d'un utilisateur.

    Parameters
    ----------
    id_stock : int\n
        Identifiant unique du stock
    nom_stock : str, optional\n
        Nom du stock (par défaut "Stock")

    Returns
    -------
    dict\n
        Dictionnaire contenant les informations du stock et ses ingrédients

    Raises
    ------
    HTTPException\n
        - 400 si id_stock n'est pas valide
        - 404 si le stock n'est pas trouvé
        - 500 en cas d'erreur serveur

    """
    if not isinstance(id_stock, int) or id_stock < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le paramètre 'id_stock' doit être un entier supérieur à 0.",
        )

    try:
        # Créer l'objet Stock
        stock = Stock(id_stock=id_stock, nom=nom_stock)

        # Récupérer le stock via le service
        stock_resultat = Stock_course_service.get_stock(stock)

        if not stock_resultat:
            raise LookupError(f"Aucun stock trouvé pour l'id {id_stock}")

        # Formater la réponse
        return {
            "id_stock": stock_resultat.id_stock,
            "nom": stock_resultat.nom,
            "ingredients": [
                {
                    "id_ingredient": ing[0],
                    "quantite": ing[1],
                    "id_unite": ing[2],
                }
                for ing in stock_resultat.ingredients
            ],
            "count": len(stock_resultat.ingredients),
        }

    except LookupError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur serveur: {e!s}",
        )


@router.put("/stock/ingredient")
def modifier_ingredient_stock(
    id_ingredient: int,
    quantite: float,
    id_unite: int,
):
    """Modifie la quantité d'un ingrédient dans le stock.

    Parameters
    ----------
    id_ingredient : int\n
        Identifiant unique de l'ingrédient
    quantite : float\n
        Nouvelle quantité
    id_unite : int\n
        Identifiant de l'unité de mesure

    Returns
    -------
    dict\n
        Message de confirmation

    Raises
    ------
    HTTPException\n
        - 400 si les paramètres ne sont pas valides
        - 500 en cas d'erreur serveur

    """
    if not isinstance(id_ingredient, int) or id_ingredient < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le paramètre 'id_ingredient' doit être un entier supérieur à 0.",
        )

    if not isinstance(quantite, (int, float)) or quantite < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le paramètre 'quantite' doit être un nombre positif.",
        )

    if not isinstance(id_unite, int) or id_unite < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le paramètre 'id_unite' doit être un entier supérieur à 0.",
        )

    try:
        updated = Stock_course_service.modifier_quantite_ingredient(
            id_ingredient,
            quantite,
            id_unite,
        )

        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="La modification n'a pas pu être effectuée.",
            )

        return {
            "message": "Ingrédient modifié avec succès",
            "id_ingredient": id_ingredient,
            "nouvelle_quantite": quantite,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur serveur: {e!s}",
        )


@router.delete("/stock/ingredient")
def retirer_ingredient_stock(
    id_ingredient: int,
    quantite: float,
    id_unite: int,
):
    """Retire une certaine quantité d'un ingrédient du stock.

    Parameters
    ----------
    id_ingredient : int\n
        Identifiant unique de l'ingrédient
    quantite : float\n
        Quantité à retirer
    id_unite : int\n
        Identifiant de l'unité de mesure

    Returns
    -------
    dict\n
        Message de confirmation

    Raises
    ------
    HTTPException\n
        - 400 si les paramètres ne sont pas valides
        - 500 en cas d'erreur serveur

    """
    if not isinstance(id_ingredient, int) or id_ingredient < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le paramètre 'id_ingredient' doit être un entier supérieur à 0.",
        )

    if not isinstance(quantite, (int, float)) or quantite <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le paramètre 'quantite' doit être un nombre strictement positif.",
        )

    if not isinstance(id_unite, int) or id_unite < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le paramètre 'id_unite' doit être un entier supérieur à 0.",
        )

    try:
        updated = Stock_course_service.retirer_du_stock(
            id_ingredient,
            quantite,
            id_unite,
        )

        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="La suppression n'a pas pu être effectuée.",
            )

        return {
            "message": "Quantité retirée avec succès",
            "id_ingredient": id_ingredient,
            "quantite_retiree": quantite,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur serveur: {e!s}",
        )
