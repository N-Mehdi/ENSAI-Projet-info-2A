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
