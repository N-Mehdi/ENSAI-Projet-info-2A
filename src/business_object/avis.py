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
    favoris : bool
        Booléen indiquant si l'utilisateur a mis le cocktail dans ses favoris
    teste : bool
        Booléen indiquant si l'utilisateur a testé le cocktail
    """


def __init__(
    self,
    id_utilisateur: str,
    id_cocktail: str,
    note: int | None = None,
    commentaire: str | None = None,
    favoris: bool | None = False,
    teste: bool | None = False
):
    """Constructeur."""
    self.id_utilisateur = id_utilisateur
    self.id_cocktail = id_cocktail
    self.note = note
    self.commentaire = commentaire
    self.favoris = favoris
    self.teste = teste


def __str__(self) -> str:
    """Afficher les informations de l'avis."""
    return f"Utilisateur({self.id_utilisateur}, {self.date_naissance})"


def as_list(self) -> list[str]:
    """Retourne les pseudo, note et commentaire dans une Matrice."""
    return [self.id_utilisateur, self.mail, self.date_naissance]