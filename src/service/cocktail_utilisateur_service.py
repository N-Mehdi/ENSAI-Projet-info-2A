"""Couche service pour les opérations sur les cocktails testés par un utilisateur."""

from src.business_object.cocktail import Cocktail
from src.dao.cocktail_utilisateur_dao import CocktailUtilisateurDAO
from src.utils.log_decorator import log


class CocktailUtilisateurService:
    """Service pour gérer les cocktails testés d'un utilisateur."""

    def __init__(self) -> None:
        """Initialise un CocktailUtilisateurService."""
        self.dao = CocktailUtilisateurDAO()

    @log
    def get_cocktails_testes(self, id_utilisateur: int) -> list[Cocktail]:
        """Récupère tous les cocktails testés par un utilisateur.

        Parameters
        ----------
        id_utilisateur : int
            L'identifiant de l'utilisateur

        Returns
        -------
        list[Cocktail]
            Liste des cocktails marqués comme testés par l'utilisateur

        Raises
        ------
        DAOError
            En cas d'erreur de base de données

        """
        return self.dao.get_teste(id_utilisateur)

    @log
    def ajouter_cocktail_teste(self, id_utilisateur: int, nom_cocktail: str) -> dict:
        """Ajoute un cocktail aux cocktails testés par son nom.

        Crée un avis avec teste=TRUE si l'avis n'existe pas encore.
        Si l'avis existe déjà, met à jour le champ teste.

        Parameters
        ----------
        id_utilisateur : int
            L'identifiant de l'utilisateur
        nom_cocktail : str
            Le nom du cocktail à marquer comme testé

        Returns
        -------
        dict
            Dictionnaire contenant :
            - nom_cocktail : str
            - id_cocktail : int
            - teste : bool (True)
            - deja_teste : bool (True si déjà testé avant, False sinon)

        Raises
        ------
        CocktailNotFoundError
            Si le cocktail n'existe pas
        DAOError
            En cas d'erreur de base de données

        """
        return self.dao.ajouter_cocktail_teste(id_utilisateur, nom_cocktail)

    @log
    def retirer_cocktail_teste(self, id_utilisateur: int, nom_cocktail: str) -> dict:
        """Retire un cocktail des cocktails testés par son nom.

        Parameters
        ----------
        id_utilisateur : int
            L'identifiant de l'utilisateur
        nom_cocktail : str
            Le nom du cocktail à retirer des testés

        Returns
        -------
        dict
            Dictionnaire contenant :
            - nom_cocktail : str
            - id_cocktail : int
            - teste : bool (False)

        Raises
        ------
        CocktailNotFoundError
            Si le cocktail n'existe pas
        CocktailNotTestedError
            Si le cocktail n'était pas marqué comme testé
        DAOError
            En cas d'erreur de base de données

        """
        return self.dao.retirer_cocktail_teste(id_utilisateur, nom_cocktail)
