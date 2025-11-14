from src.dao.utilisateur_dao import UtilisateurDao
from src.models.utilisateurs import (
    DateInscriptionResponse,
    User,
    UserChangePassword,
    UserCreate,
    UserDelete,
    UserRegister,
    UserUpdatePassword,
)
from src.utils.exceptions import AuthError, EmptyFieldError, ServiceError, UserNotFoundError
from src.utils.securite import hacher_mot_de_passe, verifier_mot_de_passe


class UtilisateurService:
    """doc."""

    def __init__(self, utilisateur_dao: UtilisateurDao):
        """Doc."""
        self.utilisateur_dao = utilisateur_dao

    def creer_compte(self, donnees: UserRegister) -> str:
        """Créer un compte utilisateur en base de données."""
        # Validation des champs vides
        if not donnees.pseudo or not donnees.pseudo.strip():
            raise EmptyFieldError("pseudo")
        if not donnees.mail or not donnees.mail.strip():
            raise EmptyFieldError("mail")
        if not donnees.mot_de_passe or not donnees.mot_de_passe.strip():
            raise EmptyFieldError("mot_de_passe")
        if not donnees.date_naissance:
            raise EmptyFieldError("date_naissance")
        # Récupérer le mot de passe brut
        mot_de_passe = donnees.mot_de_passe

        # Tronquer pour bcrypt si >72 bytes
        mot_de_passe = mot_de_passe[:72]

        # Hachage
        try:
            mot_de_passe_hashed = hacher_mot_de_passe(mot_de_passe)
        except Exception as e:
            raise ServiceError(f"Erreur lors du hachage du mot de passe : {e}")  # CHANGÉ

        # Préparer dict pour UserCreate
        compte = donnees.model_dump()
        compte.pop("mot_de_passe", None)
        compte["mot_de_passe_hashed"] = mot_de_passe_hashed

        # Valider le modèle
        try:
            user_create = UserCreate.model_validate(compte)
        except Exception as e:
            raise ServiceError(f"Erreur lors de la validation du modèle : {e}")

        succes = self.utilisateur_dao.create_compte(user_create)
        if not succes:
            raise ServiceError("Impossible de créer le compte")

        return "compte créé avec succès."

    def authenticate(self, pseudo: str, mot_de_passe: str) -> User:
        """Authentifie un utilisateur par son pseudo et son mot de passe."""
        db_utilisateur = self.utilisateur_dao.recuperer_par_pseudo(pseudo)
        if db_utilisateur is None:
            raise UserNotFoundError(pseudo=pseudo)
        if not verifier_mot_de_passe(mot_de_passe, db_utilisateur.mot_de_passe_hashed):
            raise AuthError
        return db_utilisateur

    def supprimer_compte(self, donnees: UserDelete) -> str:
        """Supprimer un compte utilisateur après authentification.

        Vérifie le mot de passe avant de supprimer le compte pour des raisons de sécurité.

        Parameters
        ----------
        donnees : UserDelete
            Contient le pseudo et mot_de_passe pour authentification

        Returns
        -------
        str
            Message de confirmation

        Raises
        ------
        EmptyFieldError
            Si un champ est vide
        UserNotFoundError
            Si l'utilisateur n'existe pas
        AuthError
            Si le mot de passe est incorrect
        ServiceError
            En cas d'erreur générale

        """
        # Validation des champs vides
        if not donnees.pseudo or not donnees.pseudo.strip():
            raise EmptyFieldError("pseudo")
        if not donnees.mot_de_passe or not donnees.mot_de_passe.strip():
            raise EmptyFieldError("mot_de_passe")

        # Récupérer l'utilisateur pour vérifier le mot de passe
        utilisateur = self.utilisateur_dao.recuperer_par_pseudo(donnees.pseudo)
        if not utilisateur:
            raise UserNotFoundError(pseudo=donnees.pseudo)

        # Vérifier le mot de passe
        if not verifier_mot_de_passe(donnees.mot_de_passe, utilisateur.mot_de_passe_hashed):
            raise AuthError()

        # Supprimer le compte
        succes = self.utilisateur_dao.delete_compte(donnees.pseudo)
        if not succes:
            raise ServiceError("Impossible de supprimer le compte")

        return "Compte supprimé avec succès."

    def changer_mot_de_passe(self, donnees: UserChangePassword) -> str:
        """Changer le mot de passe d'un utilisateur après vérification.

        Vérifie l'ancien mot de passe avant de permettre le changement.

        Parameters
        ----------
        donnees : UserChangePassword
            Contient le pseudo, ancien et nouveau mot de passe

        Returns
        -------
        str
            Message de confirmation

        Raises
        ------
        EmptyFieldError
            Si un champ est vide
        UserNotFoundError
            Si l'utilisateur n'existe pas
        AuthError
            Si le mot de passe actuel est incorrect
        ServiceError
            En cas d'erreur générale

        """
        # Validation des champs vides
        if not donnees.pseudo or not donnees.pseudo.strip():
            raise EmptyFieldError("pseudo")
        if not donnees.mot_de_passe_actuel or not donnees.mot_de_passe_actuel.strip():
            raise EmptyFieldError("mot_de_passe_actuel")
        if not donnees.mot_de_passe_nouveau or not donnees.mot_de_passe_nouveau.strip():
            raise EmptyFieldError("mot_de_passe_nouveau")

        # Vérifier que les deux mots de passe ne sont pas identiques
        if donnees.mot_de_passe_actuel == donnees.mot_de_passe_nouveau:
            raise ServiceError("Le nouveau mot de passe doit être différent de l'ancien")

        # Récupérer l'utilisateur pour vérifier le mot de passe actuel
        utilisateur = self.utilisateur_dao.recuperer_par_pseudo(donnees.pseudo)
        if not utilisateur:
            raise UserNotFoundError(pseudo=donnees.pseudo)

        # Vérifier le mot de passe actuel
        if not verifier_mot_de_passe(donnees.mot_de_passe_actuel, utilisateur.mot_de_passe_hashed):
            raise AuthError()

        # Hacher le nouveau mot de passe
        mot_de_passe_nouveau = donnees.mot_de_passe_nouveau[:72]  # Tronquer pour bcrypt
        try:
            mot_de_passe_nouveau_hashed = hacher_mot_de_passe(mot_de_passe_nouveau)
        except Exception as e:
            raise ServiceError(f"Erreur lors du hachage du mot de passe : {e}")

        # Préparer l'objet pour la DAO
        mdps_update = UserUpdatePassword(
            pseudo=donnees.pseudo,
            mot_de_passe_nouveau_hashed=mot_de_passe_nouveau_hashed,
        )

        # Mettre à jour le mot de passe
        succes = self.utilisateur_dao.update_mot_de_passe(mdps_update)
        if not succes:
            raise ServiceError("Impossible de mettre à jour le mot de passe")

        return "Mot de passe modifié avec succès."

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

    def obtenir_date_inscription(self, pseudo: str) -> DateInscriptionResponse:
        """Obtenir la date d'inscription d'un utilisateur.

        Parameters
        ----------
        pseudo : str
            Pseudo de l'utilisateur connecté

        Returns
        -------
        DateInscriptionResponse
            Contient le pseudo et la date d'inscription

        Raises
        ------
        EmptyFieldError
            Si le pseudo est vide
        UserNotFoundError
            Si l'utilisateur n'existe pas
        ServiceError
            En cas d'erreur générale

        """
        # Validation du pseudo
        if not pseudo or not pseudo.strip():
            raise EmptyFieldError("pseudo")

        # Récupérer la date d'inscription
        date_inscription = self.utilisateur_dao.get_date_inscription(pseudo)

        if date_inscription is None:
            raise UserNotFoundError(pseudo=pseudo)

        # Créer la réponse
        return DateInscriptionResponse(
            pseudo=pseudo,
            date_inscription=date_inscription,
        )
