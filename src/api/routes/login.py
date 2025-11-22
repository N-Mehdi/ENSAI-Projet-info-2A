"""Login route for obtaining access tokens."""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.dao.utilisateur_dao import UtilisateurDAO
from src.models import Token, UserRegister
from src.service.utilisateur_service import UtilisateurService
from src.utils import securite
from src.utils.exceptions import (
    AuthError,
    DAOError,
    EmptyFieldError,
    InvalidBirthDateError,
    InvalidPasswordError,
    MailAlreadyExistsError,
    ServiceError,
    UserAlreadyExistsError,
)
from src.utils.settings import settings

router = APIRouter(tags=["Inscription"])

service = UtilisateurService(utilisateur_dao=UtilisateurDAO())


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
        user = UtilisateurService(UtilisateurDAO()).authenticate(
            pseudo=form_data.username,
            mot_de_passe=form_data.password,
        )

        access_token_expires = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
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


@router.post("/login/inscription")
def creer_compte(donnees: UserRegister) -> str:
    """Créer un nouveau compte utilisateur."""
    try:
        return service.creer_compte(donnees)
    except EmptyFieldError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except InvalidPasswordError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Le mot de passe ne respecte pas les critères de sécurité",
                "errors": e.errors,
            },
        ) from e
    except InvalidBirthDateError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        ) from None
    except MailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        ) from None
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
    except DAOError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not register user.",
        ) from e
