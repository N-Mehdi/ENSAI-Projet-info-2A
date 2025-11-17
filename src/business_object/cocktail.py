"""Ce module définit un cocktail."""


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
        *,
        alcool: bool,
        image: str,
    ) -> None:
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

    def __repr__(self) -> str:
        """Représentation du cocktail."""
        return (
            f"Cocktail("
            f"id_cocktail={self.id_cocktail!r}, "
            f"nom={self.nom!r}, "
            f"categorie={self.categorie!r}, "
            f"verre={self.verre!r}, "
            f"alcool={self.alcool!r}, "
            f"image={self.image!r})"
        )

    def __eq__(self, other) -> bool:
        """Vérifie l'égalité entre deux objets Cocktail."""
        if not isinstance(other, Cocktail):
            return NotImplemented

        return (
            self.id_cocktail == other.id_cocktail
            and self.nom == other.nom
            and self.categorie == other.categorie
            and self.verre == other.verre
            and self.alcool == other.alcool
            and self.image == other.image
        )
