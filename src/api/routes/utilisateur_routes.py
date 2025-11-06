from fastapi import APIRouter, HTTPException, status

from src.dao.utilisateur_dao import UtilisateurDao
from src.models.utilisateurs import UserRegister, UserUpdatePassword, UserUpdatePseudo
from src.service.utilisateur_service import UtilisateurService
from src.utils.exceptions import DAOError, ServiceError, UserAlreadyExistsError

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
    except DAOError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not register user.",
        ) from None


'''
router.post("/changer_mot_de_passe")
def changer_mot_de_passe(
    data: UserUpdatePassword,
    pseudo: str = Depends(verify_token),  # récupère l'utilisateur connecté
):
    """Change le mot de passe de l'utilisateur connecté"""
    try:
        # Récupérer l'utilisateur depuis la DAO
        utilisateur = service.dao.recuperer_par_pseudo(pseudo)
        if not utilisateur:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé")

        # Appel au service
        succes = service.changer_mot_de_passe(
            utilisateur,
            data.ancien_mot_de_passe,
            data.nouveau_mot_de_passe,
        )
        if succes:
            return {"message": "Mot de passe changé avec succès"}
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Impossible de changer le mot de passe")
    except ServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None


@router.post("/changer_pseudo")
def changer_pseudo(
    data: UserUpdatePseudo,
    pseudo: str = Depends(verify_token)  # récupère l'utilisateur connecté
):
    """
    Change le pseudo de l'utilisateur connecté
    """
    try:
        utilisateur = service.dao.recuperer_par_pseudo(pseudo)
        if not utilisateur:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé")

        succes = service.changer_pseudo(utilisateur, data.nouveau_pseudo)
        if succes:
            return {"message": "Pseudo changé avec succès"}
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Impossible de changer le pseudo")
    except ServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None
'''

'''@router.post("/connexion", status_code=200)
def connexion(donnees: UserLogin):
    """Endpoint pour se connecter à un compte existant."""
    try:
        message = service.se_connecter(donnees)
        return {"message": message}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
'''
