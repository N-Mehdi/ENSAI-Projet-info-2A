"""doc."""

from src.business_object.cocktail import Cocktail
from src.dao.cocktail_utilisateur_dao import CocktailUtilisateurDAO
from src.utils.log_decorator import log


class CocktailUtilisateurService:
    """Service pour gérer les cocktails testés d'un utilisateur."""

    def __init__(self) -> None:
        """Initialise un CocktailUtilisateurService."""
        self.dao = CocktailUtilisateurDAO()

    # ----------------- cocktails testés -----------------

    @log
    def get_cocktails_testes(self, id_utilisateur: int) -> list[Cocktail]:
        """Récupère tous les cocktails testés par un utilisateur."""
        return self.dao.get_teste(id_utilisateur)

    @log
    def ajouter_cocktail_teste(self, id_utilisateur: int, nom_cocktail: str) -> dict:
        """Ajoute un cocktail aux cocktails testés par son nom."""
        return self.dao.ajouter_cocktail_teste(id_utilisateur, nom_cocktail)

    @log
    def retirer_cocktail_teste(self, id_utilisateur: int, nom_cocktail: str) -> dict:
        """Retire un cocktail des cocktails testés par son nom."""
        return self.dao.retirer_cocktail_teste(id_utilisateur, nom_cocktail)
