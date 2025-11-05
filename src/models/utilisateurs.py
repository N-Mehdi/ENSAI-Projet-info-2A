"""Modèles Pydantic pour les entités utilisateur.
Définit des schémas pour la création d’utilisateur, l’inscription, la mise à jour,
le changement de mot de passe, et la représentation en base de données.
"""

from pydantic import BaseModel


class UserBase(BaseModel):
    """Schéma de base pour les attributs de Utilisateur."""

    pseudo: str
    mail: str
    date_naissance: str


class UserRegister(UserBase):
    """Schema pour créer un nouveau compte."""

    mot_de_passe: str


class UserRead(UserBase):
    """Schema pour lire des données sur l'utilisateur."""

    id_utilisateur: int


class UserCreate(UserBase):
    """Schema pour créer un utilisateur dans la base de données."""

    mot_de_passe_hashed: str


class UserUpdate(BaseModel):
    """Schema pour modifier les attributs d'un utilisateur."""

    pseudo: str | None = None
    mail: str | None = None
    date_naissance: str | None = None


class UserUpdateFull(UserUpdate):
    """Schema pour modifier tous les attributs d'un utilisateur."""

    mot_de_passe_hashed: str | None = None


class UserUpdatePassword(BaseModel):
    """Schema pour changer le mot de passe d'un utilisateur."""

    mot_de_passe_actuel: str
    mot_de_passe_nouveau: str


class User(UserRead, UserCreate):
    """Schema pour un utilisateur dans la base de données."""
