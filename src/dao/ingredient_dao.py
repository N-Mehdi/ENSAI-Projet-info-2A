from src.business_object.Ingredient import Ingredient
from src.service.stock_course_service import stock_course_service
from src.service.ingredient_service import ingredient_service



class IngredrientDao(metaclass=Singleton):
    """Classe contenant les méthodes agissant sur les Ingrédients de la base
    de données.
    """

    @log
    def rechercher_ingredient_par_nom(self, nom) -> ingredient:
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT *                       "
                    "FROM ingredient                  "
                    "WHERE nom = %(nom)s            ",
                    {"nom": nom},
                )
                res = cursor.fetchone()
        Ingredient = None
        if res:
            ingredient = ingredient(
                id_ingredient=res["id_ingredient"],
                nom=res["nom"],
                categorie=res["categorie"],
                verre=res["verre"],
                alcool=res["alcool"],
                image=res["image"],
            )
        return ingredient

    @log
    def rechercher_ingredient_par_premiere_lettre(self, lettre) -> list[ingredient]:
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT *                       "
                    "FROM ingredient                  "
                    "WHERE nom LIKE %(lettre)s      ",
                    {"lettre": lettre.upper() + "%"},
                )
                res = cursor.fetchall()

        liste_ingredients = []
        if res:
            for raw_ingredient in res:
                ingredient = ingredient(
                    id_ingredient=raw_ingredient["id_ingredient"],
                    nom=raw_ingredient["nom"],
                    categorie=raw_ingredient["categorie"],
                    verre=raw_ingredient["verre"],
                    alcool=raw_ingredient["alcool"],
                    image=raw_ingredient["image"],
                )
                liste_ingredients.append(ingredient)
        return liste_ingredients

    def rechercher_ingredient_aleatoire():
        pass