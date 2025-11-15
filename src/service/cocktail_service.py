"""doc."""
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
        TypeError
            Si le nom n'est pas une chaîne de caractères.
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

        if not isinstance(nom, str):
            raise TypeError("Le nom du cocktail doit être une chaîne de caractères.")

        cocktail = self.cocktail_dao.rechercher_cocktail_par_nom(nom)

        if cocktail is None:
            raise LookupError(f"Aucun cocktail trouvé pour le nom '{nom}'")

        return cocktail

    def rechercher_cocktail_par_sequence_debut(
        self,
        sequence: str,
        max_resultats: int = 10,
    ) -> list:
        """Recherche les cocktails dont le nom commence par une séquence donnée.

        Parameters
        ----------
        sequence : str
            Sequence par laquelle commence le nom du cocktail.
        max_resultats : int
            Le nombre maximal de cocktails à retourner (triés par ordre alaphabétique)

        Raises
        ------
        TypeError
            Si séquence n'est pas une chaîne de caractères.
            Si max_resultats n'est pas un entier.
        ValueError
            Si la séquence est vide ou None.
            Si le nombre max_resultats n'est pas supérieur ou égal à 1.
        LookupError
            Si aucun cocktail n'est trouvé pour le nom donné.

        Returns
        -------
        cocktails : list[Cocktail]
            Liste de cocktails commençant par la séquence fournie.

        """
        if not sequence:
            raise ValueError("La séquence doit être fournie.")

        if not isinstance(sequence, str):
            raise TypeError("L'argument 'sequence' doit être une chaîne de caractères.")

        if not isinstance(max_resultats, int):
            raise TypeError("L'argument 'max_resultats' doit être un entier.")

        if max_resultats < 1:
            raise ValueError("L'argument 'max_resultats' doit être supérieur ou égal à 1.")

        cocktails = self.cocktail_dao.rechercher_cocktail_par_sequence_debut(
            sequence,
            max_resultats,
        )

        if not cocktails:
            raise LookupError(
                f"Aucun cocktail trouvé pour la séquence '{sequence}'",
            )

        return cocktails
