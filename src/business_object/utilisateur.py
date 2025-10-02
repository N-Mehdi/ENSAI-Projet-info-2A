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
    mdp: str | None = None,
    id_joueur: id | None = None,
) -> Utilisateur:
    """Constructeur."""
    self.id_joueur = id_joueur
    self.pseudo = pseudo
    self.mail = mail
    self.date_naissance = date_naissance
    self.mdp = mdp


def __str__(self) -> str:
    """Afficher les informations de l'utilisateur."""
    return f"Utilisateur({self.pseudo}, {self.date_naissance})"


def as_list(self) -> list[str]:
    """Retourne pseudo, mail et date_naissance de l'utilsateur dans une liste."""
    return [self.pseudo, self.mail, self.date_naissance]
