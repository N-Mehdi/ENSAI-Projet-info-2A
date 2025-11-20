from src.dao.ingredient_dao import IngredientDAO
from src.service.ingredient_service import IngredientService

x = IngredientDAO()

print(x.search_by_name("vodka"))

y = IngredientService()

sugg = y.get_by_name_with_suggestions(nom="Vodka")
print(", ".join(ing["nom"] for ing in sugg[:3]))
