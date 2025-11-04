from src.dao.utilisateur_dao import UtilisateurDao
from src.models.utilisateurs import UserCreate, UserRegister, Utilisateur
from src.utils.securite import hacher_mot_de_passe


class UtilisateurService:
    """doc."""

    def __init__(self, utilisateur_dao: UtilisateurDao):
        """Doc."""
        self.utilisateur_dao = utilisateur_dao

    def creer_compte(self, donnees: UserRegister) -> Utilisateur:
        """Doc."""
        compte = UserCreate.model_validate(
            {
                **donnees.model_dump(),
                "hashed_password": hacher_mot_de_passe(donnees.mot_de_passe),
            },
            from_attributes=True,
        )
        return self.dao.create_compte(compte)
