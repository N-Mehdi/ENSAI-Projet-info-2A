"""doc."""


class Unite:
    """Classe représentant une unité de mesure.

    Attributs
    ---------
    id_unité : int
        identifiant unique d'une inité de mesure
    nom : str
        nom de l'unité (exemple : "Litre")
    abbreviation : str
        abbreviation/notation de l'unité de mesure (exemple : "L")
    type_unite : str
        type de grandeur mesurée (exemple : "volume")
    """

    def __init__(self, id_unite, nom, abbreviation, type_unite) -> None:
        """Constructeur."""
        self.id_unite = id_unite
        self.nom = nom
        self.abbreviation = abbreviation
        self.type = type_unite
