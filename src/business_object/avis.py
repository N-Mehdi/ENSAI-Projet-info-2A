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
    


    def __init__(
        self,
        id_utilisateur: str,
        id_cocktail: str,
        note: int | None = None,
        commentaire: str | None = None,
        favoris: bool | None = False,
        teste: bool | None = False
    ):
        """
        """Constructeur."""
  """      self.id_utilisateur = id_utilisateur
        self.id_cocktail = id_cocktail
        self.note = note
        self.commentaire = commentaire
        self.favoris = favoris
        self.teste = teste


    def __str__(self) -> str:
        Afficher les informations de l'avis.
        return f"Utilisateur({self.id_utilisateur}, {self.date_naissance})"


    def as_list(self) -> list[str]:
        Retourne les pseudo, note et commentaire dans une Matrice.
        return [self.id_utilisateur, self.mail, self.date_naissance]

avis.py
Ce module définit un avis laissé par un utilisateur sur un cocktail.
"""

class Avis:
    """Classe représentant un avis.

    Attributs
    ---------
    id_utilisateur : int
        Identifiant de l'utilisateur ayant posté l'avis.
    id_cocktail : int
        Identifiant du cocktail concerné.
    note : int | None
        Note laissée par l'utilisateur (ex : sur 5).
    commentaire : str | None
        Commentaire facultatif de l'utilisateur.
    favoris : bool
        True si l'utilisateur a mis le cocktail en favori.
    teste : bool
        True si l'utilisateur a testé le cocktail.
    """

    def __init__(
        self,
        id_utilisateur: int,
        id_cocktail: int,
        note: int | None = None,
        commentaire: str | None = None,
        favoris: bool = False,
        teste: bool = False,
    ):
        """Constructeur."""
        self.id_utilisateur = id_utilisateur
        self.id_cocktail = id_cocktail
        self.note = note
        self.commentaire = commentaire
        self.favoris = favoris
        self.teste = teste

    def __str__(self) -> str:
        """Retourne une représentation lisible de l'avis."""
        note_str = f"Note : {self.note}" if self.note is not None else "Aucune note"
        fav_str = "Favori" if self.favoris else ""
        test_str = "Testé" if self.teste else ""
        return f"Avis(Utilisateur {self.id_utilisateur}, Cocktail {self.id_cocktail}, {note_str}) {fav_str} {test_str}".strip()

    def as_list(self) -> list[str]:
        """Retourne les informations de l'avis sous forme de liste."""
        return [
            str(self.id_utilisateur),
            str(self.id_cocktail),
            str(self.note) if self.note is not None else "",
            self.commentaire or "",
            str(self.favoris),
            str(self.teste),
        ]