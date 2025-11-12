'''"""stock.py
Ce module définit le stock d'un utilisateur.
"""


class Stock:
    """Classe représentant le stock d'un utilisateur.

    Attributs
    ---------
    id_stock : int
        identifiant unique du stock d'un utilisateur
    nom : str
        nom du stock utilisateur
    """

    def __init__(self, id_stock, nom):
        """Constructeur."""
        self.id_stock = id_stock
        self.nom = nom'''