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
    id_stock : int
        Identifiant unique du stock
    nom_stock : str, optional
        Nom du stock (par défaut "Stock")

    Returns
    -------
    dict
        Dictionnaire contenant les informations du stock et ses ingrédients

    Raises
    ------
    HTTPException
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
