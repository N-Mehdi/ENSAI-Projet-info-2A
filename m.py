from src.dao.cocktail_dao import CocktailDao
from src.models.utilisateurs import UserLogin
from src.utils.securite import hacher_mot_de_passe, verifier_mot_de_passe


dao = CocktailDao()

x = dao.rechercher_cocktail_par_sequence_debut("M", 3)

print(x, len(x))