"""Module contenant les fonctions de hachage, de validation du mot de passe et
de création de token JWT.
"""

import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
from passlib.context import CryptContext

from src.utils.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)
ALGORITHM = "HS256"


def hacher_mot_de_passe(mot_de_passe: str) -> str:
    """Hache un mot de passe avec bcrypt (avec sel automatique)."""
    return pwd_context.hash(mot_de_passe)


def verifier_mot_de_passe(mot_de_passe: str, hashed_mot_de_passe: str) -> bool:
    """Vérifie un mot de passe avec son hachage."""
    return pwd_context.verify(mot_de_passe, hashed_mot_de_passe)


def create_access_token(subject: int, expires_delta: timedelta) -> str:
    """Create a JWT access token.

    :param subject: Subject (user ID) for the token
    :param expires_delta: Expiration time delta
    :return: Encoded JWT token
    """
    expire = datetime.now(UTC) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


"""Module de validation des mots de passe."""


@dataclass
class PasswordCriteria:
    """Critères de validation d'un mot de passe.

    Attributes
    ----------
    min_length : int
        Longueur minimale du mot de passe
    require_uppercase : bool
        Exige au moins une majuscule
    require_lowercase : bool
        Exige au moins une minuscule
    require_digit : bool
        Exige au moins un chiffre
    require_special : bool
        Exige au moins un caractère spécial
    special_chars : str
        Caractères spéciaux autorisés
    max_length : int | None
        Longueur maximale du mot de passe (None = pas de limite)
    forbid_common : bool
        Interdit les mots de passe courants

    """

    min_length: int = 8
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digit: bool = True
    require_special: bool = True
    special_chars: str = "! @ # $ % ^ & * ( ) _ + - = [ ] { } | ; : , . < > ? "
    max_length: int | None = None
    forbid_common: bool = True


@dataclass
class PasswordValidationResult:
    """Résultat de la validation d'un mot de passe.

    Attributes
    ----------
    is_valid : bool
        Indique si le mot de passe est valide
    errors : list[str]
        Liste des erreurs de validation
    strength : str
        Force du mot de passe ('faible', 'moyen', 'fort', 'très fort')

    """

    is_valid: bool
    errors: list[str]
    strength: str


# Liste des mots de passe courants à éviter
COMMON_PASSWORDS = {
    "password",
    "123456",
    "12345678",
    "qwerty",
    "azerty",
    "abc123",
    "password123",
    "admin",
    "letmein",
    "welcome",
    "monkey",
    "dragon",
    "master",
    "sunshine",
    "princess",
    "football",
    "baseball",
    "123456789",
    "12345",
    "1234567",
}


def validate_password(
    password: str,
    criteria: PasswordCriteria | None = None,
) -> PasswordValidationResult:
    """Validate un mot de passe selon les critères spécifiés.

    Parameters
    ----------
    password : str
        Le mot de passe à valider
    criteria : PasswordCriteria | None
        Les critères de validation (utilise les critères par défaut si None)

    Returns
    -------
    PasswordValidationResult
        Résultat de la validation avec les erreurs et la force

    Examples
    --------
    >>> result = validate_password("MyP@ssw0rd")
    >>> result.is_valid
    True
    >>> result.strength
    'fort'

    >>> result = validate_password("weak")
    >>> result.is_valid
    False
    >>> len(result.errors) > 0
    True

    """
    if criteria is None:
        criteria = PasswordCriteria()

    errors = []

    # Vérifier la longueur minimale
    if len(password) < criteria.min_length:
        errors.append(
            f"Le mot de passe doit contenir au moins {criteria.min_length} caractères",
        )

    # Vérifier la longueur maximale
    if criteria.max_length and len(password) > criteria.max_length:
        errors.append(
            f"Le mot de passe ne doit pas dépasser {criteria.max_length} caractères",
        )

    # Vérifier la présence d'une majuscule
    if criteria.require_uppercase and not re.search(r"[A-Z]", password):
        errors.append("Le mot de passe doit contenir au moins une majuscule")

    # Vérifier la présence d'une minuscule
    if criteria.require_lowercase and not re.search(r"[a-z]", password):
        errors.append("Le mot de passe doit contenir au moins une minuscule")

    # Vérifier la présence d'un chiffre
    if criteria.require_digit and not re.search(r"\d", password):
        errors.append("Le mot de passe doit contenir au moins un chiffre")

    # Vérifier la présence d'un caractère spécial
    if criteria.require_special:
        special_pattern = f"[{re.escape(criteria.special_chars)}]"
        if not re.search(special_pattern, password):
            errors.append(
                f"Le mot de passe doit contenir au moins un caractère spécial: "
                f"{criteria.special_chars}",
            )

    # Vérifier les mots de passe courants
    if criteria.forbid_common and password.lower() in COMMON_PASSWORDS:
        errors.append(
            "Ce mot de passe est trop courant et facilement devinable",
        )

    # Calculer la force du mot de passe
    strength = calculate_password_strength(password, criteria)

    return PasswordValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        strength=strength,
    )


def calculate_password_strength(
    password: str,
    criteria: PasswordCriteria,
) -> str:
    """Donne la force d'un mot de passe.

    La force est déterminée par :
    - La longueur du mot de passe
    - La diversité des types de caractères
    - La présence de caractères spéciaux multiples

    Parameters
    ----------
    password : str
        Le mot de passe à évaluer
    criteria : PasswordCriteria
        Les critères de validation

    Returns
    -------
    str
        'faible', 'moyen', 'fort', ou 'très fort'

    """
    score = 0

    # Points pour la longueur
    for i in (0, 4, 8):
        if len(password) >= criteria.min_length + i:
            score += 1

    # Points pour la diversité des caractères
    if re.search(r"[a-z]", password):
        score += 1
    if re.search(r"[A-Z]", password):
        score += 1
    if re.search(r"\d", password):
        score += 1

    # Points pour les caractères spéciaux
    special_pattern = f"[{re.escape(criteria.special_chars)}]"
    special_count = len(re.findall(special_pattern, password))
    if special_count >= 1:
        score += 1
    nb_spec = 2
    if special_count >= nb_spec:
        score += 1

    # Déterminer la force
    mdp_f = 2
    mdp_m = 4
    if score <= mdp_f:
        return "faible"
    if score <= mdp_m:
        return "moyen"
    return "fort"


def check_password_criteria_detailed(password: str) -> dict[str, bool]:
    """Vérifie chaque critère individuellement pour un retour détaillé.

    Utile pour afficher des indicateurs visuels dans une interface.

    Parameters
    ----------
    password : str
        Le mot de passe à vérifier

    Returns
    -------
    dict[str, bool]
        Dictionnaire avec chaque critère et son statut

    Examples
    --------
    >>> check_password_criteria_detailed("MyP@ssw0rd")
    {
        'min_length': True,
        'has_uppercase': True,
        'has_lowercase': True,
        'has_digit': True,
        'has_special': True,
        'not_common': True
    }

    """
    mdp_len = 8
    return {
        "min_length": len(password) >= mdp_len,
        "has_uppercase": bool(re.search(r"[A-Z]", password)),
        "has_lowercase": bool(re.search(r"[a-z]", password)),
        "has_digit": bool(re.search(r"\d", password)),
        "has_special": bool(re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]", password)),
        "not_common": password.lower() not in COMMON_PASSWORDS,
    }


def generate_password_hints(
    validation_result: PasswordValidationResult,
) -> list[str]:
    """Génère des conseils pour améliorer le mot de passe.

    Parameters
    ----------
    validation_result : PasswordValidationResult
        Résultat de la validation

    Returns
    -------
    list[str]
        Liste de conseils pour améliorer le mot de passe

    """
    if validation_result.is_valid:
        return ["Votre mot de passe est valide et sécurisé !"]

    hints = ["Pour améliorer votre mot de passe :"]
    hints.extend(f"• {error}" for error in validation_result.errors)

    return hints
