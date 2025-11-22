"""Classe pour les exceptions personnalisées."""


class DAOError(Exception):
    """Raised for errors in the Data Access Object (DAO) layer.

    :param message: Error message (optional)
    """

    def __init__(self, message: str | None = None) -> None:
        """Initialize DAOError.

        :param message: Error message (optional)
        :return: None
        """
        if message is None:
            message = "Something went wrong in the DAO."
        super().__init__(message)
        # pour avoir une vrai Exception python avec le message personnalisé


class ServiceError(Exception):
    """Raised for general errors in the Service layer."""

    def __init__(self, message: str | None = None) -> None:
        """Initialize ServiceError.

        :param message: Error message (optional)
        :return: None
        """
        if message is None:
            message = "Something went wrong in the Service."
        super().__init__(message)


class PseudoChangingError(Exception):
    """Raised for errors while changing pseudo."""

    def __init__(self, message: str) -> None:
        """Itilializes an PseudoChangingError."""
        if message is None:
            message = "Modification du pseudo impossible."
        super().__init__(message)


class AccountDeletionError(Exception):
    """Raised for errors while changing password."""

    def __init__(self, pseudo: str | None = None) -> None:
        """Itilialize an AccountDeletionError."""
        super().__init__(f"Impossible de supprimer le compte : {pseudo}")


class UserAlreadyExistsError(Exception):
    """Raised when attempting to create a user with an existing pseudo.

    :param pseudo: pseudo that already exists
    """

    def __init__(self, pseudo: str) -> None:
        """Initialize UserAlreadyExistsError.

        :param pseudo: pseudo that already exists
        :return: None
        """
        super().__init__(f"pseudo {pseudo} already exists")


class MailAlreadyExistsError(Exception):
    """Raised when attempting to create a user with an existing email.

    :param mail: email that already exists
    """

    def __init__(self, mail: str) -> None:
        """Initialize MailAlreadyExistsError.

        :param mail: email that already exists
        :return: None
        """
        super().__init__(f"Email {mail} already exists")


class InvalidPasswordError(ServiceError):
    """Exception levée quand le mot de passe ne respecte pas les critères."""

    def __init__(self, errors: list[str]) -> None:
        """Initialise l'exception avec la liste des erreurs.

        Parameters
        ----------
        errors : list[str]
            Liste des erreurs de validation du mot de passe

        """
        self.errors = errors
        message = "Le mot de passe ne respecte pas les critères de sécurité"
        super().__init__(message)


class UserNotFoundError(Exception):
    """Raised when a user is not found.

    :param id_utilisateur: ID of the user (optional)
    :param pseudo: pseudo of the user (optional)
    """

    def __init__(self, message: str) -> None:
        """Initialize UserNotFoundError.

        :param id_utilisateur: ID of the user (optional)
        :param pseudo: pseudo of the user (optional)
        :return: None
        """
        if message is None:
            message = "Utilisateur introuvable"
        super().__init__(message)


class AuthError(Exception):
    """Raised for authentication errors."""

    def __init__(self) -> None:
        """Initialize AuthError.

        :return: None
        """
        super().__init__("Could not validate credentials")


class EmptyFieldError(Exception):
    """Raised when a required field is empty.

    :param field: name of the empty field
    """

    def __init__(self, field: str) -> None:
        """Initialize EmptyFieldError.

        :param field: name of the empty field
        :return: None
        """
        super().__init__(f"Le champ '{field}' ne peut pas être vide")
        self.field = field


class StockError(ServiceError):
    """Exception levée pour les erreurs liées au stock."""


class IngredientNotFoundError(Exception):
    """Exception levée quand un ingrédient n'est pas trouvé."""

    def __init__(self, message: str) -> None:
        """Initialize IngredientNotFoundError."""
        if message is None:
            message = "Ingrédient introuvable."
        super().__init__(message)


class InvalidQuantityError(StockError):
    """Exception levée quand la quantité est invalide."""

    def __init__(self, message: str) -> None:
        """Initialize InvalidQuantityError."""
        if message is None:
            message = "Quantité non valide"
        super().__init__(message)


class InsufficientQuantityError(StockError):
    """Exception levée quand la quantité à retirer est supérieure à la quantité
    disponible.
    """

    def __init__(self, quantite_demandee: float, quantite_disponible: float) -> None:
        """Initialize InsufficientQuantityError."""
        self.quantite_demandee = quantite_demandee
        self.quantite_disponible = quantite_disponible
        super().__init__(
            f"Quantité insuffisante : vous essayez de retirer {quantite_demandee}, "
            f"mais seulement {quantite_disponible} disponible",
        )


class AvisError(ServiceError):
    """Exception de base pour les erreurs liées aux avis."""


class AvisNotFoundError(AvisError):
    """Exception levée quand un avis n'est pas trouvé."""

    def __init__(self, id_utilisateur: int, nom_cocktail: str) -> None:
        """Initialize AvisNotFoundError."""
        super().__init__(
            f"Aucun avis de l'utilisateur {id_utilisateur} pour le cocktail"
            f"'{nom_cocktail}'",
        )


class InvalidAvisError(AvisError):
    """Exception levée quand les données d'un avis sont invalides."""

    def __init__(self, message) -> None:
        """Initialise InvalidAvisError."""
        if message is None:
            message = "Avis invalide."
        super().__init__(message)


class AccessDeniedError(Exception):
    """Exception levée quand l'accès est refusé."""

    def __init__(self, message: str) -> None:
        """Itilialize AccessDeniedError."""
        if message is None:
            message = "Accès refusé !"
        super().__init__(message)


class AccessAlreadyExistsError(Exception):
    """Exception levée quand un accès existe déjà."""

    def __init__(self, message: str) -> None:
        """Itilialize SelfAccessError."""
        if message is None:
            message = "Accès déjà existant !"
        super().__init__(message)


class AccessNotFoundError(Exception):
    """Exception levée quand un accès n'existe pas."""

    def __init__(self, message: str) -> None:
        """Itilialize AccessNotFoundError."""
        if message is None:
            message = "Accès non trouvé !"
        super().__init__(message)


class SelfAccessError(Exception):
    """Exception levée quand un utilisateur essaie de se donner accès à lui-même."""

    def __init__(self, message: str) -> None:
        """Itilialize SelfAccessError."""
        if message is None:
            message = "Accès donné à soit même !"
        super().__init__(message)


class CocktailNotFoundError(Exception):
    """Exception levée quand un cocktail n'est pas trouvé."""

    def __init__(self, message: str) -> None:
        """Initialize CocktailNotFoundError."""
        if message is None:
            message = "Cocktail introuvable."

        super().__init__(message)


class CocktailSearchError(Exception):
    """Erreur indiquant un problème dans la recherche du cocktail
    par l'utilsateur.
    """

    def __init__(self, message: str | None = None) -> None:
        """Initialize CocktailSearchError."""
        if message is None:
            message = "Problème dans la recherche du cocktail."

        super().__init__(message)


class PermissionDeniedError(Exception):
    """Erreur indiquant que l'utilisateur n'a pas les permissions nécessaires."""

    def __init__(self, message: str | None = None) -> None:
        """Initialize PermissionDeniedError.

        :param message: Error message (optional)
        :return: None
        """
        if message is None:
            message = "L'utilisateur n'est pas le propriétaire du cocktail."
        super().__init__(message)
        # pour avoir une vrai Exception python avec le message personnalisé


class InvalidBirthDateError(Exception):
    """Erreur indiquant que la date de naissance de l'utilisateur est invalide."""

    def __init__(self, message: str | None = None) -> None:
        """Initialize InvalidBirthdayError."""
        super().__init__(message)


class UniteNotFoundError(Exception):
    """Exception levée quand une unité n'est pas trouvée."""

    def __init__(self, abbreviation: str) -> None:
        """Initialize UniteNotFoundError."""
        message = f"Unité '{abbreviation}' non trouvée"
        super().__init__(message)
        self.abbreviation = abbreviation


class CocktailNotTestedError(Exception):
    """Exception levée quand un cocktail n'est pas dans les cocktails testés."""

    def __init__(self, nom_cocktail: str) -> None:
        """Initialize CocktailNotTestedError."""
        message = f"Le cocktail '{nom_cocktail}' n'est pas dans vos cocktails testés!"
        super().__init__(message)


class InstructionError(Exception):
    """Exception levée quand il y a un problème concernant les instructions."""

    def __init__(self, message: str) -> None:
        """Initialize InstructionError."""
        if message is None:
            message = "Erreur dans l'instruction du cocktail."
        super().__init__(message)


class OneIngredientError:
    """Exception levée quand il y a un problème d'ingredients dans la création
    d'un cocktail privé.
    """

    def __init__(self, message: str) -> None:
        """Initialize InstructOneIngredientErrorionError."""
        if message is None:
            message = "Erreur dans la création du cocktail privé."
        super().__init__(message)


class CocktailDupeError(Exception):
    """Exception levée quand un cocktail exoste déjà dans la base de
    données.
    """

    def __init__(self, message: str) -> None:
        """Itilialize CocktailDupeError."""
        if message is None:
            message = "Ce nom de cocktail existe déjà !"
        super().__init__(message)
