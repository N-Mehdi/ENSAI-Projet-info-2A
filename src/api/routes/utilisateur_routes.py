from fastapi import APIRouter, HTTPException, status

from src.api.deps import CurrentUser
from src.dao.utilisateur_dao import UtilisateurDao
from src.models.utilisateurs import UserRegister
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


@router.post("/logout")
def logout(utilisateur: CurrentUser) -> dict:
    """Déconnecter l'utilisateur.

    Le vrai logout se fait côté client en supprimant le token.

    :param utilisateur: Utilisateur actuellement connecté
    :return: Message de confirmation
    """
    return {
        "message": f"Utilisateur {utilisateur.pseudo} déconnecté avec succès",
        "detail": "Supprimez le token de votre stockage local",
    }
