from src.dao.utilisateur_dao import UtilisateurDao
from src.models.utilisateurs import User, UserCreate, UserRegister
from src.utils.exceptions import AuthError, ServiceError, UserNotFoundError
from src.utils.securite import hacher_mot_de_passe, verifier_mot_de_passe


class UtilisateurService:
    """doc."""

    def __init__(self, utilisateur_dao: UtilisateurDao):
        """Doc."""
        self.utilisateur_dao = utilisateur_dao

    def creer_compte(self, donnees: UserRegister) -> str:
        """Créer un compte utilisateur en base de données."""
        # Récupérer le mot de passe brut
        mot_de_passe = donnees.mot_de_passe

        # Tronquer pour bcrypt si >72 bytes
        mot_de_passe = mot_de_passe[:72]

        # Hachage
        try:
            mot_de_passe_hashed = hacher_mot_de_passe(mot_de_passe)
        except Exception as e:
            raise ValueError(f"Erreur lors du hachage du mot de passe : {e}")

        # Préparer dict pour UserCreate
        compte = donnees.model_dump()
        compte.pop("mot_de_passe", None)
        compte["mot_de_passe_hashed"] = mot_de_passe_hashed

        # Valider le modèle
        try:
            user_create = UserCreate.model_validate(compte)
        except Exception as e:
            raise ServiceError(f"Erreur lors de la validation du modèle : {e}")
        # Créer en BDD
        try:
            succes = self.utilisateur_dao.create_compte(user_create)
            if not succes:
                raise ServiceError("Impossible de créer le compte")
        except Exception as e:
            raise ServiceError(f"Erreur DAO lors de la création du compte : {e}") from e
        return "compte crée avec succès."

    def authenticate(self, pseudo: str, mot_de_passe: str) -> User:
        """Authenticate a user by pseudo and mot_de_passe."""
        db_utilisateur = self.utilisateur_dao.recuperer_par_pseudo(pseudo)
        if db_utilisateur is None:
            raise UserNotFoundError(pseudo=pseudo)
        if not verifier_mot_de_passe(mot_de_passe, db_utilisateur.mot_de_passe):
            raise AuthError
        return db_utilisateur

    def changer_mot_de_passe(self, utilisateur: User, ancien_mot_de_passe: str, nouveau_mot_de_passe: str) -> bool:
        """Change le mot de passe d'un utilisateur après vérification de l'ancien mot de passe.

        Parameters
        ----------
        utilisateur : User ou Utilisateur
            L'utilisateur dont on veut changer le mot de passe
        ancien_mot_de_passe : str
            L'ancien mot de passe en clair
        nouveau_mot_de_passe : str
            Le nouveau mot de passe en clair

        Returns
        -------
        bool
            True si le mot de passe a été changé, False sinon.

        Raises
        ------
        ServiceError
            Si l'ancien mot de passe est incorrect ou si la mise à jour échoue.

        """
        # Vérifier l'ancien mot de passe
        if not verifier_mot_de_passe(ancien_mot_de_passe, utilisateur.mot_de_passe_hashed):
            raise ServiceError("L'ancien mot de passe est incorrect")

        # Hasher le nouveau mot de passe
        mot_de_passe_hashed = hacher_mot_de_passe(nouveau_mot_de_passe)

        # Déléguer la mise à jour à la DAO
        try:
            succes = self.dao.update_mot_de_passe(utilisateur.id_utilisateur, mot_de_passe_hashed)
            if not succes:
                raise ServiceError("Impossible de changer le mot de passe")
            return True
        except Exception as e:
            raise ServiceError("Impossible de changer le mot de passe") from e

    def changer_pseudo(self, utilisateur, nouveau_pseudo: str) -> bool:
        """Change le pseudo d'un utilisateur après vérification qu'il n'existe pas déjà.

        Parameters
        ----------
        utilisateur : User ou Utilisateur
            L'utilisateur dont on veut changer le pseudo
        nouveau_pseudo : str
            Le nouveau pseudo souhaité

        Returns
        -------
        bool
            True si le pseudo a été changé, False sinon.

        Raises
        ------
        ServiceError
            Si le pseudo est déjà utilisé ou si la mise à jour échoue.

        """
        # Vérifier si le pseudo existe déjà
        if self.dao.pseudo_existe(nouveau_pseudo):
            raise ServiceError(f"Le pseudo '{nouveau_pseudo}' est déjà utilisé")

        # Déléguer la mise à jour à la DAO
        try:
            succes = self.dao.update_pseudo(utilisateur.id_utilisateur, nouveau_pseudo)
            if not succes:
                raise ServiceError("Impossible de changer le pseudo")
            return True
        except Exception as e:
            raise ServiceError("Impossible de changer le pseudo") from e

    def read(self, id_utilisateur: int) -> User:
        """Read a user by their ID."""
        utilisateur = self.utilisateur_dao.read(id_utilisateur)
        if utilisateur is None:
            raise UserNotFoundError(id_utilisateur=id_utilisateur)
        return utilisateur
