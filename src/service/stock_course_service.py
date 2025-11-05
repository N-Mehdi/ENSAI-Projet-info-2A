"""stock_course_service.py
Class service du business object Stock.
"""

import logging

from business_object.stock import Stock
from business_object.utilisateur import Utilisateur
from dao.stock_course_dao import (
    delete_ingredient_liste_course,
    delete_ingredient_stock,
    get_liste_course,
    get_stock,
    update_ingredient_stock,
    updtate_liste_course,
)
from utils.log_decorator import log


class Stock_course_service:
    """Classe contenant la logique métier liée au stock et à la liste de courses
    d'un utilisateur.
    """

    @staticmethod
    @log
    def get_stock(stock: Stock) -> Stock:
        """Récupère les informations du stock en base de données pour un objet
         Stock donné.

        Parameters
        ----------
        stock : Stock
            Objet de la classe Stock, dont l'id_stock sera utilisé pour interroger
             la base.

        Returns
        -------
        Stock
            L'objet Stock complété avec les informations de la base, ou None si
             introuvable.

        """
        try:
            res = get_stock(stock)
            if not res:
                logging.info("Aucun stock trouvé pour cet id_stock.")
                return None

            stock.ingredients = [(r[0], r[1], r[2]) for r in res]
            return stock

        except Exception as e:
            logging.exception("Erreur dans get_stock : %s", e)
            return None

    @staticmethod
    @log
    def modifier_quantite_ingredient(
        id_ingredient: int,
        quantite: float,
        id_unite: int,
    ) -> bool:
        """Méthode qui permet de modifier la quantité d'un ingrédient dans le stock.

        Parameters
        ----------
        id_ingredient : int
            Identifiant unique de l'ingrédient.
        quantite : float
            Nouvelle quantité de l'ingrédient.
        id_unite : int
            Identifiant unique de l'unité de mesure.

        Returns
        -------
        updated : bool
            Indique si la mise à jour a bien été effectuée.

        """
        try:
            return update_ingredient_stock(id_ingredient, quantite, id_unite)
        except Exception as e:
            logging.exception("Erreur dans modifier_stock : %s", e)
            return False

    @staticmethod
    @log
    def retirer_du_stock(
        id_ingredient: int,
        quantite: float,
        id_unite: int,
    ) -> bool:
        """Méthode qui permet de retirer une certaine quantité d'un
         ingrédient du stock.

        Parameters
        ----------
        id_ingredient : int
            Identifiant unique de l'ingrédient.
        quantite : float
            Quantité à retirer.
        id_unite : int
            Identifiant unique de l'unité de mesure.

        Returns
        -------
        updated : bool
            Indique si la suppression a bien été effectuée.

        """
        try:
            return delete_ingredient_stock(id_ingredient, quantite, id_unite)
        except Exception as e:
            logging.exception("Erreur dans retirer_du_stock : %s", e)
            return False

    @staticmethod
    @log
    def get_liste_course_utilisateur(utilisateur: Utilisateur):
        """Méthode qui permet de récupérer la liste de courses d'un utilisateur.

        Parameters
        ----------
        utilisateur : Utilisateur
            Objet représentant l'utilisateur.

        Returns
        -------
        liste_course : list
            Liste de tuples (id_ingredient, quantite, id_unite) représentant la liste de courses.

        """
        try:
            res = get_liste_course(utilisateur)
            if res is None:
                logging.info(
                    "Aucune liste de courses trouvée pour cet utilisateur.",
                )
                return None
            return res

        except Exception as e:
            logging.exception("Erreur dans get_liste_course_utilisateur : %s", e)
            return None

    @staticmethod
    @log
    def modifier_liste_course(
        id_ingredient: int,
        quantite: float,
        id_unite: int,
    ) -> bool:
        """Méthode qui permet de modifier la liste de courses.

        Parameters
        ----------
        id_ingredient : int
            Identifiant unique de l'ingrédient.
        quantite : float
            Nouvelle quantité.
        id_unite : int
            Identifiant unique de l'unité de mesure.

        Returns
        -------
        updated : bool
            Indique si la modification a bien été effectuée.

        """
        try:
            return updtate_liste_course(id_ingredient, quantite, id_unite)
        except Exception as e:
            logging.exception("Erreur dans modifier_liste_course : %s", e)
            return False

    @staticmethod
    @log
    def retirer_de_liste_course(
        id_ingredient: int,
        quantite: float,
        id_unite: int,
    ) -> bool:
        """Méthode qui permet de retirer un ingrédient de la liste de courses.

        Parameters
        ----------
        id_ingredient : int
            Identifiant unique de l'ingrédient.
        quantite : float
            Quantité à retirer.
        id_unite : int
            Identifiant unique de l'unité de mesure.

        Returns
        -------
        updated : bool
            Indique si la suppression a bien été effectuée.

        """
        try:
            return delete_ingredient_liste_course(
                id_ingredient,
                quantite,
                id_unite,
            )
        except Exception as e:
            logging.exception("Erreur dans retirer_de_liste_course : %s", e)
            return False
