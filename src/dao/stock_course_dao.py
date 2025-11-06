"""stock_course_dao.py
Class dao du business object Stock.
"""

import logging

from business_object.stock import Stock
from dao.db_connection import DBConnection
from utils.log_decorator import log


class Stock_course_dao:
    """Classe contenant les méthodes agissants sur le stock d'un utilisateur."""

    @log
    def get_stock(stock) -> Stock:  # pb : id_stock = id utilisateur??
        # et parametre on pourrait ptetre mettre direct id_stock
        """Méthode qui permet de renvoyer le stock d'un utilisateur.

        Parameters
        ----------
        stock : Objet de la classe Stock

        Returns
        -------
        stock : Stock
            Un objet de la classe Stock représetant le stock de l'utilisateur

        """
        res = None
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT id_ingredient, quantite, id_unite
                    FROM stock
                    WHERE id_stock = %(id_stock)s;
                    """,
                {"id_stock": stock.id_stock},
            )
            res = cursor.fetchone()
        return res

    @log
    def update_ingredient_stock(id_ingredient, quantite, id_unite) -> bool:
        """Méthode qui permet de modifier la quantité d'un ingredient dans le stock.

        Parameters
        ----------
        id_ingredient : int
            Identifiant unique de l'ingrédient
        quantite : float
            Nouvelle quantité de l'ingrédient
        id_unite : int
            Identifiant unique de l'unité de mesure

        Returns
        -------
        created : bool
            renvoie si la quantité a bien était modifiée et vaut la grandeur souhaitée

        """
        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    """
                        UPDATE stock
                        SET quantite = %(quantite)s, id_unite = %(id_unite)s
                        WHERE id_ingredient = %(id_ingredient)s
                        RETURNING id_ingredient;
                        """,
                    {
                        "quantite": quantite,
                        "id_unite": id_unite,
                        "id_ingredient": id_ingredient,
                    },
                )
                res = cursor.fetchone()
                if res:
                    updated = True
        except Exception as e:
            logging.info(e)

        return updated

    @log
    def delete_ingredient_stock(id_ingredient, quantite, id_unite) -> bool:
        """Méthode qui permet de supprimer une certaine quantité d'un ingredient dans
        le stock.

        Parameters
        ----------
        id_ingredient : int
            Identifiant unique de l'ingrédient
        quantite : float
            Nouvelle quantité de l'ingrédient
        id_unite : int
            Identifiant unique de l'unité de mesure

        Returns
        -------
        created : bool
            renvoie si la quantité a bien était modifiée et vaut la grandeur souhaitée

        """
        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    """
                        UPDATE stock
                        SET quantite = quantite - %(quantite)s, id_unite = %(id_unite)s
                        WHERE id_ingredient = %(id_ingredient)s
                        RETURNING id_ingredient;
                        """,
                    {
                        "quantite": quantite,
                        "id_unite": id_unite,
                        "id_ingredient": id_ingredient,
                    },
                )
                res = cursor.fetchone()
                if res:
                    updated = True
        except Exception as e:
            logging.info(e)

        return updated

    @log
    def get_liste_course(utilisateur):
        """Méthode qui permet de renvoyer la liste de course d'un utilisateur.

        Parameters
        ----------
        utilisateur : Utilisateur
        objet de classe utilisateur

        Returns
        -------
        liste de course : ?
            La liste de course de l'utilisateur

        """
        res = None
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT id_ingredient, quantite, id_unite
                    FROM liste_course
                    WHERE id_utilisateur = %(id_utilisateur)s;
                    """,
                {"id_utilisateur": utilisateur.id_utilisateur},
            )
            res = cursor.fetchone()
        return res

    @log
    def updtate_liste_course(id_ingredient, quantite, id_unite) -> bool:
        """Méthode qui permet de modifier la quantité d'un ingredient dans la liste de
        course.

        Parameters
        ----------
        id_ingredient : int
            Identifiant unique de l'ingrédient
        quantite : float
            Nouvelle quantité de l'ingrédient
        id_unite : int
            Identifiant unique de l'unité de mesure

        Returns
        -------
        created : bool
            renvoie si la quantité a bien était modifiée et vaut la grandeur souhaitée

        """
        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    """
                        UPDATE liste_course
                        SET quantite = %(quantite)s, id_unite = %(id_unite)s
                        WHERE id_ingredient = %(id_ingredient)s
                        RETURNING id_ingredient;
                        """,
                    {
                        "quantite": quantite,
                        "id_unite": id_unite,
                        "id_ingredient": id_ingredient,
                    },
                )
                res = cursor.fetchone()
                if res:
                    updated = True
        except Exception as e:
            logging.info(e)

        return updated

    @log
    def delete_ingredient_liste_course(id_ingredient, quantite, id_unite) -> bool:
        """Méthode qui permet de supprimer une certaine quantité d'un ingredient dans
        la liste de course.

        Parameters
        ----------
        id_ingredient : int
            Identifiant unique de l'ingrédient
        quantite : float
            Nouvelle quantité de l'ingrédient
        id_unite : int
            Identifiant unique de l'unité de mesure

        Returns
        -------
        created : bool
            renvoie si la quantité a bien était modifiée et vaut la grandeur souhaitée

        """
        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    """
                        UPDATE stock
                        SET quantite = quantite - %(quantite)s, id_unite = %(id_unite)s
                        WHERE id_ingredient = %(id_ingredient)s
                        RETURNING id_ingredient;
                        """,
                    {
                        "quantite": quantite,
                        "id_unite": id_unite,
                        "id_ingredient": id_ingredient,
                    },
                )
                res = cursor.fetchone()
                if res:
                    updated = True
        except Exception as e:
            logging.info(e)

        return updated
