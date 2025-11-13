from src.dao.ingredient_dao import IngredientDao


class IngredientService:
    """Service pour gérer les informations d'alcool des ingrédients"""

    def __init__(self):
        self.dao = IngredientDao()

    def check_if_alcoholic(self, ingredient_id: int) -> dict:
        """Vérifie si un ingrédient contient de l'alcool

        Args:
            ingredient_id: L'ID de l'ingrédient

        Returns:
            Dictionnaire avec le statut de l'alcool

        Raises:
            ValueError: Si l'ingrédient n'existe pas

        """
        is_alcoholic = self.dao.is_alcoholic(ingredient_id)

        if is_alcoholic is None:
            raise ValueError(f"Ingrédient avec l'ID {ingredient_id} introuvable")

        return {
            "ingredient_id": ingredient_id,
            "is_alcoholic": is_alcoholic,
            "message": "Cet ingrédient contient de l'alcool" if is_alcoholic else "Cet ingrédient ne contient pas d'alcool",
        }

    def check_if_alcoholic_by_name(self, ingredient_name: str) -> dict:
        """Vérifie si un ingrédient contient de l'alcool en utilisant son nom

        Args:
            ingredient_name: Le nom de l'ingrédient

        Returns:
            Dictionnaire avec le statut de l'alcool

        Raises:
            ValueError: Si l'ingrédient n'existe pas

        """
        is_alcoholic = self.dao.is_alcoholic_by_name(ingredient_name)

        if is_alcoholic is None:
            raise ValueError(f"Ingrédient '{ingredient_name}' introuvable")

        return {
            "ingredient_name": ingredient_name,
            "is_alcoholic": is_alcoholic,
            "message": "Cet ingrédient contient de l'alcool" if is_alcoholic else "Cet ingrédient ne contient pas d'alcool",
        }
