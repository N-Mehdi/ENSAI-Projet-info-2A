import hashlib
from datetime import UTC, datetime, timedelta

import jwt
from passlib.context import CryptContext

from src.utils.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def hacher_mot_de_passe(mot_de_passe: str) -> str:
    """Hache un mot de passe avec bcrypt."""
    mot_de_passe_sha256 = hashlib.sha256(mot_de_passe.encode("utf-8")).hexdigest()
    return pwd_context.hash(mot_de_passe_sha256)


def verifier_mot_de_passe(mot_de_passe: str, hashed_mot_de_passe: str) -> bool:
    """Vérifie un mot de passe avec son hachage."""
    mot_de_passe_sha256 = hashlib.sha256(mot_de_passe.encode("utf-8")).hexdigest()
    return pwd_context.verify(mot_de_passe_sha256, hashed_mot_de_passe)


'''def create_access_token(subject: int, expires_delta: timedelta) -> str:
    """Create a JWT access token.

    :param subject: Subject (user ID) for the token
    :param expires_delta: Expiration time delta
    :return: Encoded JWT token
    """
    expire = datetime.now(UTC) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
'''


def create_access_token(subject: int, expires_delta: timedelta) -> str:
    """Create a JWT access token.

    :param subject: Subject (user ID) for the token
    :param expires_delta: Expiration time delta
    :return: Encoded JWT token
    """
    expire = datetime.now(UTC) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
