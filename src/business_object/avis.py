"""Ce module définit un avis."""


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
        *,
        favoris: bool = False,
        teste: bool = False,
    ) -> None:
        """Constructeur de la classe Avis."""
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
        return f"Avis(Utilisateur {self.id_utilisateur},Cocktail {self.id_cocktail},{note_str}) {fav_str} {test_str}".strip()

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
