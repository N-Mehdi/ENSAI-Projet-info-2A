from src.dao.cocktail_dao import CocktailDao


class CocktailService:
    """Service pour la logique cocktail."""

    def __init__(self, cocktail_dao: CocktailDao) -> None:
        """Initialise un CocktailService."""
        self.cocktail_dao = cocktail_dao

    def rechercher_cocktail_par_nom(self, nom: str):
        """Recherche un cocktail par son nom.

        Parameters
        ----------
        nom : str
            Nom du cocktail à rechercher.

        Raises
        ------
        ValueError
            Si le nom est vide ou None.
        LookupError
            Si aucun cocktail n'est trouvé pour le nom donné.

        Returns
        -------
        cocktail : Cocktail
            L'objet Cocktail correspondant au nom fourni.

        """
        if not nom:
            raise ValueError("Le nom du cocktail doit être fourni.")

        cocktail = self.cocktail_dao.rechercher_cocktail_par_nom(nom)

        if cocktail is None:
            raise LookupError(f"Aucun cocktail trouvé pour le nom '{nom}'")

        return cocktail

    def rechercher_cocktail_par_premiere_lettre(self, lettre: str) -> list:
        """Doc"""
        if not lettre or len(lettre) != 1:
            raise ValueError("Une seule lettre doit être fournie pour la recherche.")

        cocktails = self.cocktail_dao.rechercher_cocktail_par_premiere_lettre(lettre)

        if not cocktails:
            raise LookupError(
                f"Aucun cocktail trouvé pour la lettre '{lettre.upper()}'",
            )

        return cocktails
