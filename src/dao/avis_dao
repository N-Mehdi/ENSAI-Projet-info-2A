import logging

from business_object.utilisateur import Utilisateur
from dao.db_connection import DBConnection
from utils.log_decorator import log
from utils.singleton import Singleton

class AvisDAO(metaclass = Singleton):
    """classe contenant les méthodes d'appel à la BDD pour les avis"""
    @log
    def listage(nom_cocktail):
        "faire jointure avis cocktail et "


def rechercher_avis(cocktail):
    """fait la jointure entre AVIS et Cocktail pour récupérer le nom, puis renvoie une liste des avis des cocktailsavec ce nom
    donc renvoie une liste de liste [note,commentaire]"""
    with DBconnection().connection as connection :
        with connection.cursor() as cursor:
            cursor.execute:
            "SELECT avis.note,"           
            "avis.commentaire,"
            "avis.nom_users"
            "FROM  Avis avis"
            "LEFT JOIN cocktail"
            "using(id_cocktail)"