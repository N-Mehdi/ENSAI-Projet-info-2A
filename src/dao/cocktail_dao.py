"""cocktail_dao.py
Classe DAO du business object Cocktail.
"""

from src.business_object.cocktail import Cocktail
from src.dao.db_connection import DBConnection
from src.utils.log_decorator import log
from src.utils.singleton import Singleton


class CocktailDao(metaclass=Singleton):
    """Classe contenant les méthodes agissant sur les cocktails de la base
    de données.
    """

    @log
    def rechercher_cocktail_par_nom(self, nom) -> Cocktail:
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT *                       "
                    "FROM cocktail                  "
                    "WHERE nom = %(nom)s            ",
                    {"nom": nom},
                )
                res = cursor.fetchone()
        cocktail = None
        if res:
            cocktail = Cocktail(
                id_cocktail=res["id_cocktail"],
                nom=res["nom"],
                categorie=res["categorie"],
                verre=res["verre"],
                alcool=res["alcool"],
                image=res["image"],
            )
        return cocktail

    @log
    def rechercher_cocktail_par_premiere_lettre(self, lettre) -> list[Cocktail]:
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT *                       "
                    "FROM cocktail                  "
                    "WHERE nom LIKE %(lettre)s      ",
                    {"lettre": lettre.upper() + "%"},
                )
                res = cursor.fetchall()

        liste_cocktails = []
        if res:
            for raw_cocktail in res:
                cocktail = Cocktail(
                    id_cocktail=raw_cocktail["id_cocktail"],
                    nom=raw_cocktail["nom"],
                    categorie=raw_cocktail["categorie"],
                    verre=raw_cocktail["verre"],
                    alcool=raw_cocktail["alcool"],
                    image=raw_cocktail["image"],
                )
                liste_cocktails.append(cocktail)
        return liste_cocktails

    def rechercher_cocktail_aleatoire():
        pass


y = CocktailDao()
x = y.rechercher_cocktail_par_nom("Margarita")
z = y.rechercher_cocktail_par_premiere_lettre("M")
print(x, z)
# il faut ajouter la méthode __repr__() dans la BO cocktail pour que le print(z) n'affiche plus des noms de cocktails codés
