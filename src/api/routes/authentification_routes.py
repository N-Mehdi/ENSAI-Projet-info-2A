"""Login route for obtaining access tokens."""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.dao.db_connection import DBConnection
from src.dao.utilisateur_dao import UtilisateurDao
from src.models import Token
from src.service.utilisateur_service import UtilisateurService
from src.utils import securite
from src.utils.config import settings
from src.utils.exceptions import AuthError

router = APIRouter(tags=["Login"])


@router.post("/login/access-token")
def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """Authenticate user and return an access token.

    :param form_data: OAuth2 password request form
    :raises HTTPException: Raised if authentication fails
    :return: Token object with access token and type
    """
    try:
        # Utiliser votre connexion singleton
        user = UtilisateurService(UtilisateurDao()).authenticate(
            pseudo=form_data.username,
            mot_de_passe=form_data.password,
        )

        access_token_expires = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
        access_token = securite.create_access_token(
            user.id,
            expires_delta=access_token_expires,
        )
        return Token(access_token=access_token, token_type=settings.TOKEN_TYPE)

    except AuthError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        ) from None
