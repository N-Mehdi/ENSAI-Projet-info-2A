"""return [self.pseudo, self.mail, self.date_naissance]"""

class Ingredient:
    """Classe représentant un ingrédient.

    Attributs
    ----------
    id_ingredient : int
        Identifiant unique de l'ingrédient.
    nom : str | None
        Nom de l'ingrédient.
    ingredient_alcool : bool
        True si l'ingrédient est alcoolisé, False sinon.
    """

    def __init__(self, id_ingredient: int, nom: str | None = None, ingredient_alcool: bool = False):
        """Constructeur de la classe Ingredient."""
        self.id_ingredient = id_ingredient
        self.nom = nom
        self.ingredient_alcool = ingredient_alcool

    def __str__(self) -> str:
        """Retourne une représentation lisible de l'ingrédient."""
        alcool_status = "alcoolisé" if self.ingredient_alcool else "non alcoolisé"
        return f"Ingredient({self.nom}, {alcool_status})"

    def as_list(self) -> list[str]:
        """Retourne les attributs principaux sous forme de liste de chaînes."""
        return [str(self.id_ingredient), self.nom or "", str(self.ingredient_alcool)]
