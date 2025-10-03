class Avis:
    """Classe représentant un Avis.

    Attributs
    ---------
    id_cocktail ; int
    id_utilisateur : int
        id de l'utilisateur qui a posté l'élément
    Note : num
        Note laissée par l'utilisateur qui a posté l'avis
    commentaire : chr
        commentaire laissé par l'utilisateur
    est_favori : bool
        Booléen vérifiant si l'utilisateur a mis le cocktail dans ses favoris
    """


def __init__(
    self,
    id_user: str,
    id_cocktail: str,
    Note: num | None = None,
    Commentaire: str | None = None,
    est_favoris: bool
) -> Utilisateur:
    """Constructeur."""
    self.id_user = id_user
    self.id_cocktail = id_cocktail
    self.Note = Note
    self.Commentaire = Commentaire
    self.est_favoris = est_favoris


def __str__(self) -> str:
    """Afficher les informations de l'avis."""
    return f"Utilisateur({self.pseudo}, {self.date_naissance})"


def as_list(self) -> list[str]:
    """Retourne les pseudo, note et commentaire dans une Matrice."""


    
    """return [self.pseudo, self.mail, self.date_naissance]"""