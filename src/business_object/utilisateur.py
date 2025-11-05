"""utilisateur.py
Ce module définit un utilisateur.
"""


class Utilisateur:
    """Classe représentant un Utilisateur.

    Attributs
    ---------
    id_utilisateur : int
        identifiant unique de l'utilisateur
    pseudo : str
        pseudo de l'utilisateur
    mail : str
        adresse mail du joueur
    mdp : str
        mot de passe de l'utilisateur
    date_naissance : str
        date de naissance de l'utilisateur
    """

    def __init__(
        self,
        pseudo: str,
        mail: str,
        date_naissance: str,
        mot_de_passe: str | None = None,
        id_utilisateur: int | None = None,
    ):
        """Constructeur."""
        self.id_utilisateur = id_utilisateur
        self.pseudo = pseudo
        self.mail = mail
        self.date_naissance = date_naissance
        self.mot_de_passe = mot_de_passe

    def __str__(self) -> str:
        """Afficher les informations de l'utilisateur."""
        return f"Utilisateur({self.pseudo}, {self.date_naissance})"

    def as_list(self) -> list[str]:
        """Retourne pseudo, mail et date_naissance de l'utilsateur dans une liste."""
        return [self.pseudo, self.mail, self.date_naissance]
