from src.dao.utilisateur_dao import UtilisateurDao
from src.models.utilisateurs import UserCreate, UserLogin, UserRegister
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
        user_create = UserCreate.model_validate(compte)

        # Créer en BDD
        self.utilisateur_dao.create_compte(user_create)

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
