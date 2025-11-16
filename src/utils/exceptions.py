"""Classe pour les exceptions."""


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
    """doc."""

    def __init__(self, message: str | None = None) -> None:
        """Initialize ServiceError.

        :param message: Error message (optional)
        :return: None
        """
        if message is None:
            message = "Something went wrong in the Service."
        super().__init__(message)


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


class UserNotFoundError(Exception):
    """Raised when a user is not found.

    :param id_utilisateur: ID of the user (optional)
    :param pseudo: pseudo of the user (optional)
    """

    def __init__(self, id_utilisateur: int | None = None, pseudo: str | None = None) -> None:
        """Initialize UserNotFoundError.

        :param id_utilisateur: ID of the user (optional)
        :param pseudo: pseudo of the user (optional)
        :return: None
        """
        if id_utilisateur:
            msg = f"No user found for id={id_utilisateur}"
        elif pseudo:
            msg = f"No user found for pseudo='{pseudo}'"
        else:
            msg = "No user found"
        super().__init__(msg)


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

    def __init__(self, nom_ingredient: str, suggestions: list[str]) -> None:
        """Initialize IngredientNotFoundError."""
        self.nom_ingredient = nom_ingredient
        self.suggestions = suggestions or []

        message = f"Ingrédient '{nom_ingredient}' non trouvé."
        if self.suggestions:
            message += f" Vouliez-vous dire : {', '.join(self.suggestions[:3])} ?"

        super().__init__(message)


class InvalidQuantityError(StockError):
    """Exception levée quand la quantité est invalide."""

    def __init__(self, quantite: float) -> None:
        """Initialize InvalidQuantityError."""
        super().__init__(f"Quantité invalide : {quantite}. La quantité doit être > 0")


class InsufficientQuantityError(StockError):
    """Exception levée quand la quantité à retirer est supérieure à la quantité disponible."""

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
            f"Aucun avis de l'utilisateur {id_utilisateur} pour le cocktail '{nom_cocktail}'",
        )


class InvalidAvisError(AvisError):
    """Exception levée quand les données d'un avis sont invalides."""

    def __init__(self) -> None:
        """Initialise InvalidAvisError."""
        super().__init__(
            "Au moins la note ou le commentaire doit être renseigné",
        )


class AccessDeniedError(Exception):
    """Exception levée quand l'accès est refusé."""


class AccessAlreadyExistsError(Exception):
    """Exception levée quand un accès existe déjà."""


class AccessNotFoundError(Exception):
    """Exception levée quand un accès n'existe pas."""


class SelfAccessError(Exception):
    """Exception levée quand un utilisateur essaie de se donner accès à lui-même."""


class CocktailNotFoundError(Exception):
    """Exception levée quand un cocktail n'est pas trouvé."""

    def __init__(self, nom_cocktail: str, suggestions: list[str] | None = None) -> None:
        """Initialize CocktailNotFoundError."""
        self.nom_cocktail = nom_cocktail
        self.suggestions = suggestions or []

        message = f"Cocktail '{nom_cocktail}' non trouvé."
        if self.suggestions:
            message += f" Vouliez-vous dire : {', '.join(self.suggestions[:3])} ?"

        super().__init__(message)


class InvalidBirthDateError(ServiceError):
    """Date de naissance invalide."""


class UniteNotFoundError(Exception):
    """Exception levée quand une unité n'est pas trouvée."""

    def __init__(self, abbreviation: str) -> None:
        """Initialize UniteNotFoundError."""
        msg = f"Unité '{abbreviation}' non trouvée"
        super().__init__(msg)
        self.abbreviation = abbreviation
