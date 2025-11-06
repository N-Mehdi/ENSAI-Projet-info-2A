from src.business_object.ingredient import Ingredient
from src.utils.db_connection import DBConnection  # à adapter à ton projet
from src.utils.logger import log  # idem
from src.utils.singleton import Singleton  # idem


class IngredientDao(metaclass=Singleton):
    """Classe contenant les méthodes agissant sur les ingrédients de la base de données."""

    @log
    def rechercher_ingredient_par_nom(self, nom: str) -> Ingredient | None:
        """Recherche un ingrédient par son nom exact.
        ----------
        nom : str
            Nom de l'ingrédient à rechercher.
        Retour
        ------
        Ingredient | None
            L'objet Ingredient trouvé, ou None si aucun résultat.
        """
        with DBConnection().connection as connection, connection.cursor(dictionary=True) as cursor:
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
        """Recherche tous les ingrédients dont le nom commence par une certaine lettre.

        Paramètres
        ----------
        lettre : str
            La première lettre du nom à filtrer.

        Retour
        ------
        list[Ingredient]
            Liste des ingrédients correspondants.
        """
        with DBConnection().connection as connection, connection.cursor(dictionary=True) as cursor:
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
                ),
            )
        return liste_ingredients
