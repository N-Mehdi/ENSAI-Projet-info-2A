"""Couche service pour les opérations sur les ingrédients."""

from src.dao.ingredient_dao import IngredientDAO
from src.utils.exceptions import IngredientNotFoundError, ServiceError
from src.utils.log_decorator import log
from src.utils.text_utils import normalize_ingredient_name


class IngredientService:
    """Service pour gérer les informations d'alcool des ingrédients."""

    def __init__(self) -> None:
        """Initialise un IngredientService."""
        self.dao = IngredientDAO()

    def check_if_alcoholic(self, ingredient_id: int) -> dict:
        """Vérifie si un ingrédient contient de l'alcool par son identifiant.

        Parameters
        ----------
        ingredient_id : int
            L'identifiant de l'ingrédient à vérifier

        Returns
        -------
        dict
            Dictionnaire contenant :
            - ingredient_id : int
            - is_alcoholic : bool
            - message : str (message descriptif)

        Raises
        ------
        IngredientNotFoundError
            Si l'ingrédient n'existe pas

        """
        is_alcoholic = self.dao.is_alcoholic(ingredient_id)

        if is_alcoholic is None:
            raise IngredientNotFoundError(
                message=f"Ingrédient avec l'ID {ingredient_id} introuvable",
            )

        return {
            "ingredient_id": ingredient_id,
            "is_alcoholic": is_alcoholic,
            "message": "Cet ingrédient contient de l'alcool"
            if is_alcoholic
            else "Cet ingrédient ne contient pas d'alcool",
        }

    def check_if_alcoholic_by_name(self, ingredient_name: str) -> dict:
        """Vérifie si un ingrédient contient de l'alcool par son nom.

        Parameters
        ----------
        ingredient_name : str
            Le nom de l'ingrédient à vérifier

        Returns
        -------
        dict
            Dictionnaire contenant :
            - ingredient_name : str
            - is_alcoholic : bool
            - message : str (message descriptif)

        Raises
        ------
        IngredientNotFoundError
            Si l'ingrédient n'existe pas

        """
        is_alcoholic = self.dao.is_alcoholic_by_name(ingredient_name)

        if is_alcoholic is None:
            raise IngredientNotFoundError(
                message=f"Ingrédient '{ingredient_name}' introuvable",
            )

        return {
            "ingredient_name": ingredient_name,
            "is_alcoholic": is_alcoholic,
            "message": "Cet ingrédient contient de l'alcool"
            if is_alcoholic
            else "Cet ingrédient ne contient pas d'alcool",
        }

    @log
    def get_by_name_with_suggestions(self, nom: str) -> dict:
        """Cherche un ingrédient par son nom exact.
        Si non trouvé, lève une exception avec des suggestions.

        Parameters
        ----------
        nom : str
            Nom de l'ingrédient (sera normalisé au format Title Case)

        Returns
        -------
        dict
            L'ingrédient trouvé

        Raises
        ------
        IngredientNotFoundError
            Si l'ingrédient n'existe pas (avec suggestions)

        """
        # Normaliser le nom
        nom_normalized = normalize_ingredient_name(nom)

        ingredient = self.dao.get_by_name(nom_normalized)

        if not ingredient:
            suggestions_data = self.dao.search_by_name(
                nom=nom_normalized,
                limit=5,
            )
            suggestions = [ing["nom"] for ing in suggestions_data]

            if len(suggestions_data) == 0:
                raise IngredientNotFoundError(
                    message=f"Ingrédient '{nom_normalized}' non trouvé.",
                )

            raise IngredientNotFoundError(
                message=f"Ingrédient '{nom_normalized}' non trouvé. "
                f"Vouliez-vous dire : {', '.join(suggestions[:3])} ?",
            )

        return ingredient

    def get_or_create_ingredient(self, nom: str, *, alcool: bool = False) -> dict:
        """Récupère ou crée un ingrédient.

        Normalise le nom de l'ingrédient avant la recherche/création
        pour éviter les doublons.

        Parameters
        ----------
        nom : str
            Nom de l'ingrédient
        alcool : bool
            Indique si l'ingrédient contient de l'alcool

        Returns
        -------
        dict
            Ingrédient avec id_ingredient, nom, alcool

        Raises
        ------
        ServiceError
            En cas d'erreur

        """
        try:
            nom_normalise = normalize_ingredient_name(nom)
            id_ingredient = self.dao.get_or_create_ingredient(
                nom_normalise,
                alcool=alcool,
            )

        except Exception as e:
            raise ServiceError(
                message=f"Erreur lors de la récupération/création de l'ingrédient: {e}",
            ) from e
        return {
            "id_ingredient": id_ingredient,
            "nom": nom_normalise,
            "alcool": alcool,
        }

    def create_ingredient(self, nom: str, *, alcool: bool = False) -> dict:
        """Crée un nouvel ingrédient s'il n'existe pas déjà.

        Parameters
        ----------
        nom : str
            Nom de l'ingrédient
        alcool : bool
            Indique si l'ingrédient contient de l'alcool

        Returns
        -------
        dict
            Ingrédient créé ou existant

        """
        return self.get_or_create_ingredient(nom, alcool=alcool)
