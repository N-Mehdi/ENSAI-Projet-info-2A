"""Couche service pour les opérations utilisateur."""

from datetime import UTC, date, datetime

from src.dao.utilisateur_dao import UtilisateurDAO
from src.models.utilisateurs import (
    DateInscriptionResponse,
    User,
    UserChangePassword,
    UserCreate,
    UserDelete,
    UserRegister,
    UserUpdatePassword,
)
from src.utils.exceptions import (
    AuthError,
    EmptyFieldError,
    InvalidBirthDateError,
    PseudoChangingError,
    ServiceError,
    UserNotFoundError,
)
from src.utils.securite import hacher_mot_de_passe, verifier_mot_de_passe


class UtilisateurService:
    """Service pour la logique utilisateur."""

    def __init__(self, utilisateur_dao: UtilisateurDAO) -> None:
        """Initialise un UtilisateurService."""
        self.utilisateur_dao = utilisateur_dao

    def creer_compte(self, donnees: UserRegister) -> str:
        """Créer un nouveau compte utilisateur à partir des données fournies.

        Parameters
        ----------
        donnees : UserRegister
            Objet contenant les informations nécessaires à l'inscription,
            telles que le pseudo, l'email, le mot de passe et la date de naissance.

        Returns
        -------
        "compte créé avec succès." : str
            Message indiquant le succès de la création du compte.

        Raises
        ------
        EmptyFieldError
            Si un champ obligatoire (pseudo, mail, mot de passe, date de naissance)
            est vide.
        ServiceError
            En cas d'erreur lors du hachage du mot de passe, de la validation du modèle
            ou de la création en base.

        """
        # Validation des champs vides
        if not donnees.pseudo or not donnees.pseudo.strip():
            raise EmptyFieldError(field="pseudo")
        if not donnees.mail or not donnees.mail.strip():
            raise EmptyFieldError(field="mail")
        if not donnees.mot_de_passe or not donnees.mot_de_passe.strip():
            raise EmptyFieldError(field="mot_de_passe")
        if not donnees.date_naissance:
            raise EmptyFieldError(field="date_naissance")

        # valider la date de naissance
        birth_date = self._parse_and_validate_birth_date(donnees.date_naissance)

        # Récupérer le mot de passe brut
        mot_de_passe = donnees.mot_de_passe

        # Hachage
        try:
            mot_de_passe_hashed = hacher_mot_de_passe(mot_de_passe)
        except Exception as e:
            raise ServiceError(
                message=f"Erreur lors du hachage du mot de passe : {e}",
            ) from e

        # Préparer dict pour UserCreate
        compte = donnees.model_dump()
        compte.pop("mot_de_passe", None)
        compte["mot_de_passe_hashed"] = mot_de_passe_hashed
        compte["date_naissance"] = birth_date.isoformat()

        # Valider le modèle
        try:
            user_create = UserCreate.model_validate(compte)
        except Exception as e:
            raise ServiceError(
                message=f"Erreur lors de la validation du modèle : {e}",
            ) from e

        succes = self.utilisateur_dao.create_compte(user_create)
        if not succes:
            raise ServiceError(message="Impossible de créer le compte")

        return "compte créé avec succès."

    def authenticate(self, pseudo: str, mot_de_passe: str) -> User:
        """Authentifier un utilisateur à partir de son pseudo et de son mot de passe.

        Parameters
        ----------
        pseudo : str
            Pseudo de l'utilisateur.
        mot_de_passe : str
            Mot de passe à vérifier.

        Returns
        -------
        db_utilisateur : User
            L'utilisateur authentifié correspondant au pseudo fourni.

        Raises
        ------
        UserNotFoundError
            Si aucun utilisateur ne correspond au pseudo fourni.
        AuthError
            Si le mot de passe fourni est incorrect.
        ServiceError
            En cas d'erreur générale lors de l'authentification.

        """
        db_utilisateur = self.utilisateur_dao.recuperer_par_pseudo(pseudo)
        if db_utilisateur is None:
            raise UserNotFoundError(message=f"Utilisateur '{pseudo}' introuvable.")
        if not verifier_mot_de_passe(mot_de_passe, db_utilisateur.mot_de_passe_hashed):
            raise AuthError
        return db_utilisateur

    def supprimer_compte(self, donnees: UserDelete) -> str:
        """Supprimer un compte utilisateur après authentification.

        Vérifie le mot de passe avant de supprimer le compte.

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
            raise EmptyFieldError(donnees.pseudo)
        if not donnees.mot_de_passe or not donnees.mot_de_passe.strip():
            raise EmptyFieldError(donnees.mot_de_passe)

        # Récupérer l'utilisateur pour vérifier le mot de passe
        utilisateur = self.utilisateur_dao.recuperer_par_pseudo(donnees.pseudo)
        if not utilisateur:
            raise UserNotFoundError(
                message=f"L'utilisateur '{donnees.pseudo}' est introuvable.",
            )

        # Vérifier le mot de passe
        if not verifier_mot_de_passe(
            donnees.mot_de_passe,
            utilisateur.mot_de_passe_hashed,
        ):
            raise AuthError

        # Supprimer le compte
        succes = self.utilisateur_dao.delete_compte(donnees.pseudo)
        if not succes:
            raise ServiceError(message="Impossible de supprimer le compte")

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
            raise EmptyFieldError(field="pseudo")
        if not donnees.mot_de_passe_actuel or not donnees.mot_de_passe_actuel.strip():
            raise EmptyFieldError(field="mot_de_passe_actuel")
        if not donnees.mot_de_passe_nouveau or not donnees.mot_de_passe_nouveau.strip():
            raise EmptyFieldError(field="mot_de_passe_nouveau")

        # Vérifier que les deux mots de passe ne sont pas identiques
        if donnees.mot_de_passe_actuel == donnees.mot_de_passe_nouveau:
            raise ServiceError(
                message="Le nouveau mot de passe doit être différent de l'ancien",
            )

        # Récupérer l'utilisateur pour vérifier le mot de passe actuel
        utilisateur = self.utilisateur_dao.recuperer_par_pseudo(donnees.pseudo)
        if not utilisateur:
            raise UserNotFoundError(
                message=f"L'utilisateur '{donnees.pseudo}' est introuvable.",
            )

        # Vérifier le mot de passe actuel
        if not verifier_mot_de_passe(
            donnees.mot_de_passe_actuel,
            utilisateur.mot_de_passe_hashed,
        ):
            raise AuthError

        # Hacher le nouveau mot de passe
        try:
            mot_de_passe_nouveau_hashed = hacher_mot_de_passe(
                donnees.mot_de_passe_nouveau,
            )
        except Exception as e:
            raise ServiceError(
                message=f"Erreur lors du hachage du mot de passe : {e}",
            ) from e

        # Préparer l'objet pour la DAO
        mdps_update = UserUpdatePassword(
            pseudo=donnees.pseudo,
            mot_de_passe_nouveau_hashed=mot_de_passe_nouveau_hashed,
        )

        # Mettre à jour le mot de passe
        succes = self.utilisateur_dao.update_mot_de_passe(mdps_update)
        if not succes:
            raise ServiceError(message="Impossible de mettre à jour le mot de passe")

        return "Mot de passe modifié avec succès."

    @staticmethod
    def _parse_and_validate_birth_date(birth_date_input) -> date:
        """Parse et valide la date de naissance.

        Parameters
        ----------
        birth_date_input : date | str
            Date de naissance à parser et valider

        Returns
        -------
        date
            Date de naissance parsée et validée

        Raises
        ------
        InvalidBirthDateError
            Si la date est invalide, dans le futur, si l'utilisateur a moins de 13 ans,
            ou si la date est non réaliste (>150 ans)

        """
        # Si c'est déjà un objet date, on l'utilise directement
        if isinstance(birth_date_input, date):
            birth_date = birth_date_input
        # Sinon, on parse la string

        elif isinstance(birth_date_input, str):
            try:
                birth_date = date.fromisoformat(birth_date_input)
            except ValueError as e:
                raise InvalidBirthDateError(
                    message=(
                        "Date de naissance invalide. Format attendu : AAAA-MM-JJ"
                        "(ex: 2000-12-25). Vérifiez que le mois (1-12) et le jour"
                        "sont valides pour ce mois."
                    ),
                ) from e
        else:
            raise InvalidBirthDateError(
                message=(
                    "Date de naissance doit être une chaîne de caractères ou un objet"
                    "date",
                ),
            )

        # Validation de la logique métier
        today = datetime.now(UTC).date()

        # Date dans le futur
        if birth_date >= today:
            raise InvalidBirthDateError(
                message="La date de naissance doit être dans le passé",
            )

        # Calculer l'âge
        age = (today - birth_date).days / 365.25

        # Âge minimum
        majeur = 18
        if age < majeur:
            raise InvalidBirthDateError(
                message="Vous devez avoir au moins 18 ans pour créer un compte",
            )

        # Âge maximum
        age_max = 122
        if age > age_max:
            raise InvalidBirthDateError(
                message="Date de naissance non réaliste",
            )
        return birth_date

    def changer_pseudo(self, ancien_pseudo, nouveau_pseudo: str) -> bool:
        """Change le pseudo d'un utilisateur après vérification qu'il n'existe pas déjà.

        Parameters
        ----------
        ancien_pseudo :str
            L'ancien pseudo de l'utilisateur
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
        if not nouveau_pseudo or not nouveau_pseudo.strip():
            raise EmptyFieldError(field="pseudo")
        if self.utilisateur_dao.pseudo_existe(nouveau_pseudo):
            raise PseudoChangingError(
                message=(
                    f"Le pseudo '{nouveau_pseudo}' est déjà utilisé. Choisissez un"
                    "nouveau pseudo.",
                ),
            )

        try:
            succes = self.utilisateur_dao.update_pseudo(ancien_pseudo, nouveau_pseudo)

        except Exception as e:
            raise ServiceError from e
        if ancien_pseudo == nouveau_pseudo:
            raise PseudoChangingError(
                message="Veuillez choisir un pseudo différent de l'ancien.",
            )
        if not succes:
            raise PseudoChangingError(message="Impossible de changer le pseudo")
        return f"Pseudo changé avec succès de '{ancien_pseudo}' vers '{nouveau_pseudo}'"

    def read(self, id_utilisateur: int) -> User:
        """Récupérer un utilisateur à partir de son identifiant.

        Parameters
        ----------
        id_utilisateur : int
            Identifiant unique de l'utilisateur recherché.

        Returns
        -------
        utilisateur : User
            L'utilisateur correspondant à l'identifiant fourni.

        Raises
        ------
        UserNotFoundError
            Si aucun utilisateur ne correspond à l'identifiant fourni.
        ServiceError
            En cas d'erreur générale lors de la récupération.

        """
        utilisateur = self.utilisateur_dao.read(id_utilisateur)
        if utilisateur is None:
            raise UserNotFoundError(message="L'utilisateur est introuvable")
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
        # Récupérer la date d'inscription
        date_inscription = self.utilisateur_dao.get_date_inscription(pseudo)

        # Créer la réponse
        return DateInscriptionResponse(
            pseudo=pseudo,
            date_inscription=date_inscription,
        )
