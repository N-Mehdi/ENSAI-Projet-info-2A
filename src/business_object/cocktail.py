"""cocktail.py
Ce module définit un cocktail.
"""


class Cocktail:
    """Classe représentant un Cocktail.

    Attributs
    ---------
    id_cocktail : int
        identifiant unique du cocktail
    nom : str
        nom du cocktail
    categorie : str
        catégorie du cocktail
    verre : str
        type de verre
    alcool : bool
        indique si le cocktail contient de l'alcool
    image : str
        image du cocktail
    """

    def __init__(
        self,
        id_cocktail: int,
        nom: str,
        categorie: str,
        verre: str,
        alcool: bool,
        image: str,
    ):
        """Constructeur."""
        self.id_cocktail = id_cocktail
        self.nom = nom
        self.categorie = categorie
        self.verre = verre
        self.alcool = alcool
        self.image = image

    def __str__(self) -> str:
        """Afficher les informations du cocktail."""
        return f"Cocktail({self.nom}, {self.categorie})"
