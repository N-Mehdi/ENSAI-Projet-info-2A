class Ingredient:
    """Classe représentant un Ingredient.

    Attributs
    ---------
    id_ingredient ; int
   
        id de l'ingrédient
    Note : num
        Note laissée par l'utilisateur qui a posté l'Ingredient
    nom_ingredient : chr
        nom de l'ingrédient
    alcool_ingredient : bool
        Booléen vérifiant si l'ingrédient est alcoolisé
    """


def __init__(
    self,
    id_ingredient: str,
    nom_ingredient: chr | None = None,
    alcool_ingredient: bool
) -> Utilisateur:

"""Constructeur."""

self.id_ingredient = id_ingredient
self.nom_ingredient = nom_ingredient
self.alcool_ingredient = alcool_ingredient


def __str__(self) -> str:
    """Afficher les informations de l'ingrédient."""
    return f"Ingredient({self.nom_ingredient}, {self.})"


def as_list(self) -> list[str]:
    """Retourne les pseudo, note et nom_ingredient dans une Matrice."""


   
    """return [self.pseudo, self.mail, self.date_naissance]"""
