from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def hacher_mot_de_passe(mot_de_passe: str) -> str:
    """Hache un du mot de passe."""
    return pwd_context.hash(mot_de_passe)


def verifier_mot_de_passe(mot_de_passe: str, hashed_mot_de_passe: str) -> bool:
    """Vérifie un mot de passe avec son hachage."""
    return pwd_context.verify(mot_de_passe, hashed_mot_de_passe)


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
