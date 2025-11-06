"""Login route for obtaining access tokens."""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.api.deps import CursorDep
from src.dao.utilisateur_dao import UtilisateurDao
from src.models.misc import Token
from src.models.utilisateurs import UserLogin
from src.service.utilisateur_service import UtilisateurService
from src.utils import securite
from src.utils.config import settings
from src.utils.exceptions import AuthError

router = APIRouter(prefix="/connexion", tags=["connexion"])


@router.post("/access-token", include_in_schema=False)
def login_access_token(
    cur: CursorDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """Authenticate user and return an access token.

    :param cur: Database cursor dependency
    :param form_data: OAuth2 password request form
    :raises HTTPException: Raised if authentication fails
    :return: Token object with access token and type
    """
    if not form_data.username or not form_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le nom d'utilisateur et le mot de passe sont requis",
        )

    try:
        service = UtilisateurService(UtilisateurDao(cur))
        user = service.se_connecter(
            UserLogin(pseudo=form_data.username, mot_de_passe=form_data.password),
        )
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = securite.create_access_token(
            user.id_utilisateur,
            expires_delta=access_token_expires,
        )
        return Token(access_token=access_token, token_type=settings.TOKEN_TYPE)
    except AuthError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        ) from None
