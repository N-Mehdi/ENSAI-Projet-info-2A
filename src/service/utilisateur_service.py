from src.dao.utilisateur_dao import UtilisateurDao
from src.models.utilisateurs import User, UserCreate, UserLogin, UserRegister
from src.utils.exceptions import ServiceError
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

    def se_connecter(self, donnees: UserLogin) -> str:
        """Se connecter à un compte existant.

        Parameters
        ----------
            donnees: UserLogin contenant mail et mot_de_passe.

        Returns
        -------
            str: Message de confirmation avec le pseudo de l'utilisateur.

        Raises
        ------
            ValueError: Si l'email n'existe pas ou si le mot de passe est incorrect.

        """
        donnees_bdd = self.utilisateur_dao.recuperer_mot_de_passe_hashe_par_mail(
            donnees.mail,
        )

        if not donnees_bdd:
            raise ValueError("Email ou mot de passe incorrect")

        # Hacher le mot de passe fourni et le comparer avec celui en base
        mot_de_passe = donnees.mot_de_passe
        mot_de_passe_hache = donnees_bdd["mot_de_passe"]

        if not verifier_mot_de_passe(mot_de_passe, mot_de_passe_hache):
            raise ValueError("Email ou mot de passe incorrect")

        return "Connexion réussie ! Bienvenue"

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
