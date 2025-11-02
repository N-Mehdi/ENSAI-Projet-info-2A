from fastapi import APIRouter, HTTPException, status
from src.dao.cocktail_dao import CocktailDao

router = APIRouter(prefix="/cocktails", tags=["Cocktails"])

@router.get("/lettre/{lettre}")
def get_cocktails_by_letter(lettre: str):
    """
    Récupère tous les cocktails qui commencent par une lettre donnée
    
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
            detail="La lettre doit être un caractère alphabétique unique"
        )
    
    try:
        cocktails = CocktailDao().rechercher_cocktail_par_premiere_lettre(lettre.upper())
        
        cocktails_dict = [
            {
                "id_cocktail": c.id_cocktail,
                "nom": c.nom,
                "categorie": c.categorie,
                "verre": c.verre,
                "alcool": c.alcool,
                "image": c.image
            }
            for c in cocktails
        ]

        return {
            "drinks": cocktails_dict,
            "count": len(cocktails),
            "lettre": lettre.upper()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur serveur: {str(e)}"
        )



