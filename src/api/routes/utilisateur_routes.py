from fastapi import APIRouter, HTTPException, status

from src.dao.utilisateur_dao import UtilisateurDao
from src.models.utilisateurs import UserLogin, UserRegister
from src.service.utilisateur_service import UtilisateurService
from src.utils.exceptions import DAOError, UserAlreadyExistsError

router = APIRouter(prefix="/utilisateurs", tags=["Utilisateurs"])

service = UtilisateurService(utilisateur_dao=UtilisateurDao())


@router.post("/inscription")
def creer_compte(donnees: UserRegister) -> str:
    """Doc."""
    try:
        return service.creer_compte(donnees)
    except UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        ) from None
    except DAOError:  # Ok faudra vraiment faire un truc c'est éclaté
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not register user.",
        ) from None


@router.post("/connexion", status_code=200)
def connexion(donnees: UserLogin):
    """Endpoint pour se connecter à un compte existant."""
    try:
        message = service.se_connecter(donnees)
        return {"message": message}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
