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
    """Raised when attempting to create a user with an existing username.

    :param username: Username that already exists
    """

    def __init__(self, pseudo: str) -> None:
        """Initialize UserAlreadyExistsError.

        :param username: Username that already exists
        :return: None
        """
        super().__init__(f"Username {pseudo} already exists")
