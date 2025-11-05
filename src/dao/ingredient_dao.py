from src.business_object.Ingredient import Ingredient
from src.service.stock_course_service import stock_course_service
from src.service.ingredient_service import ingredient_service

class IngredientDao(metaclass=Singleton):
    """Classe contenant les méthodes agissant sur les Ingrédients de la base de données."""

    @log
    def rechercher_ingredient_par_nom(self, nom: str) -> Ingredient | None:
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id_ingredient, nom, alcool
                    FROM ingredient
                    WHERE nom = %(nom)s
                    """,
                    {"nom": nom},
                )
                res = cursor.fetchone()

        if res:
            return Ingredient(
                id_ingredient=res["id_ingredient"],
                nom=res["nom"],
                ingredient_alcool=res["alcool"],
            )
        return None

    @log
    def rechercher_ingredient_par_premiere_lettre(self, lettre: str) -> list[Ingredient]:
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id_ingredient, nom, alcool
                    FROM ingredient
                    WHERE UPPER(nom) LIKE %(lettre)s
                    """,
                    {"lettre": lettre.upper() + "%"},
                )
                res = cursor.fetchall()

        liste_ingredients = []
        for row in res:
            liste_ingredients.append(
                Ingredient(
                    id_ingredient=row["id_ingredient"],
                    nom=row["nom"],
                    ingredient_alcool=row["alcool"],
                )
            )
        return liste_ingredients



    def est_alcoolise(ingredient: Ingredient) -> bool:
        """
        Détermine si un ingrédient est alcoolisé.

        Paramètres
        ----------
        ingredient : Ingredient
            L'objet Ingredient à vérifier.

        Retour
        ------
        bool
            True si l'ingrédient est alcoolisé, False sinon.
        """
        if not isinstance(ingredient, Ingredient):
            raise TypeError("L'argument doit être une instance de la classe Ingredient.")
        
        return ingredient.ingredient_alcool






from src.business_object.Ingredient import Ingredient
from src.utils.db_connection import DBConnection  # à adapter à ton projet
from src.utils.singleton import Singleton  # idem
from src.utils.logger import log  # idem


class IngredientDao(metaclass=Singleton):
    """Classe contenant les méthodes agissant sur les ingrédients de la base de données."""

    @log
    def rechercher_ingredient_par_nom(self, nom: str) -> Ingredient | None:
        """
        Recherche un ingrédient par son nom exact.

        Paramètres
        ----------
        nom : str
            Nom de l'ingrédient à rechercher.

        Retour
        ------
        Ingredient | None
            L'objet Ingredient trouvé, ou None si aucun résultat.
        """
        with DBConnection().connection as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT id_ingredient, nom, alcool
                    FROM ingredient
                    WHERE nom = %(nom)s
                    """,
                    {"nom": nom},
                )
                res = cursor.fetchone()

        if res:
            return Ingredient(
                id_ingredient=res["id_ingredient"],
                nom=res["nom"],
                ingredient_alcool=res["alcool"],
            )
        return None

    @log
    def rechercher_ingredient_par_premiere_lettre(self, lettre: str) -> list[Ingredient]:
        """
        Recherche tous les ingrédients dont le nom commence par une certaine lettre.

        Paramètres
        ----------
        lettre : str
            La première lettre du nom à filtrer.

        Retour
        ------
        list[Ingredient]
            Liste des ingrédients correspondants.
        """
        with DBConnection().connection as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT id_ingredient, nom, alcool
                    FROM ingredient
                    WHERE UPPER(nom) LIKE %(lettre)s
                    """,
                    {"lettre": lettre.upper() + "%"},
                )
                res = cursor.fetchall()

        liste_ingredients = []
        for row in res:
            liste_ingredients.append(
                Ingredient(
                    id_ingredient=row["id_ingredient"],
                    nom=row["nom"],
                    ingredient_alcool=row["alcool"],
                )
            )
        return liste_ingredients
