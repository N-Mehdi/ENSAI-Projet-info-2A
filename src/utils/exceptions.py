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


class UserAlreadyExistsError(Exception):
    """Raised when attempting to create a user with an existing username or email."""

    def __init__(self, field: str, value: str) -> None:
        """Initialize UserAlreadyExistsError.

        Args:
            field: Le champ qui existe déjà ('pseudo' ou 'mail')
            value: La valeur qui existe déjà

        """
        if field == "pseudo":
            super().__init__(f"Le pseudo '{value}' est déjà utilisé")
        elif field == "mail":
            super().__init__(f"L'email '{value}' est déjà utilisé")
        else:
            super().__init__(f"Le champ {field} avec la valeur '{value}' existe déjà")


class UserNotFoundError(Exception):
    """Raised when a user is not found.

    :param user_id: ID of the user (optional)
    :param username: Username of the user (optional)
    """

    def __init__(self, user_id: int | None = None, username: str | None = None) -> None:
        """Initialize UserNotFoundError.

        :param user_id: ID of the user (optional)
        :param username: Username of the user (optional)
        :return: None
        """
        if user_id:
            msg = f"No user found for id={user_id}"
        elif username:
            msg = f"No user found for username='{username}'"
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



