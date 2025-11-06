"""Dependency injection utilities for FastAPI routes.
Provides token and user authentication dependencies.
"""

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from src.dao.utilisateur_dao import UtilisateurDao
from src.models import TokenPayload, User
from src.service.utilisateur_service import UtilisateurService
from src.utils import securite
from src.utils.config import settings
from src.utils.exceptions import UserNotFoundError

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_STR}/login/access-token",
)

TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_user(token: TokenDep) -> User:
    """Retrieve the current user from a JWT token.

    :param token: JWT token dependency
    :raises HTTPException: Raised if credentials are invalid or user not found
    :return: The authenticated User object
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[securite.ALGORITHM],
        )
        token_data = TokenPayload.model_validate(payload)

        if not token_data.sub:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_service = UtilisateurService(UtilisateurDao())
        return user_service.read(id_utilisateur=int(token_data.sub))

    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such user in database",
        ) from None


CurrentUser = Annotated[User, Depends(get_user)]
