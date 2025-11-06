from src.dao.utilisateur_dao import UtilisateurDao
from src.models.utilisateurs import User, UserCreate, UserLogin, UserRegister
from src.utils.exceptions import AuthError, UserAlreadyExistsError
from src.utils.securite import hacher_mot_de_passe, verifier_mot_de_passe


class UtilisateurService:
    """doc."""

    def __init__(self, utilisateur_dao: UtilisateurDao):
        """Doc."""
        self.utilisateur_dao = utilisateur_dao

    def creer_compte(self, donnees: UserRegister) -> str:
        """Créer un compte utilisateur en base de données."""
        if self.utilisateur_dao.pseudo_existe(donnees.pseudo):
            raise UserAlreadyExistsError("pseudo", donnees.pseudo)

        if self.utilisateur_dao.mail_existe(donnees.mail):
            raise UserAlreadyExistsError("mail", donnees.mail)

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
        user_create = UserCreate.model_validate(compte)

        # Créer en BDD
        self.utilisateur_dao.create_compte(user_create)

        return "compte crée avec succès."

    def se_connecter(self, donnees: UserLogin) -> User:
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
        utilisateur = self.utilisateur_dao.recuperer_par_pseudo(
            donnees.pseudo,
        )

        if not utilisateur:
            raise AuthError

        # Hacher le mot de passe fourni et le comparer avec celui en base

        if not verifier_mot_de_passe(donnees.mot_de_passe, utilisateur.mot_de_passe):
            raise AuthError

        return utilisateur
