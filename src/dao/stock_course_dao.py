"""stock_course_dao.py
Class dao du business object Stock.
"""

from dao.db_connection import DBConnection
from utils.log_decorator import log


class Stock_course_dao:
    """Classe contenant les méthodes agissants sur le stock d'un utilisateur."""


@log
def get_stock(
    stock,
):  # pb : id_stock = id utilisateur??
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
    with DBConnection().connection as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                VALUES (stock.id_stock)
                RETURNING (id_ingredient,quantite,id_unite);
                """,
            )
            res = cursor.fetchone()
    return res


@log
def update_ingredient_stock(id_ingredient, quantite, id_unite):
    # rien n'est fait encore
    """Méthode qui permet de modifier la quantité d'un ingredient dans le stock.

    Parameters
    ----------
    id_ingredient : int
        Identifiant unique de l'ingrédient
    quantite : float
        Nouvelle quantité de l'ingrédient
    id_unité : int
        Identifiant unique de l'unité de mesure

    Returns
    -------
    created : bool
        renvoie si la quantité a bien était modifiée et vaut la grandeur souhaitée

    """
    try:
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                INSERT INTO utilisateur(quantite)
                VALUES (%(pseudo)s, %(mail)s, %(mdp)s, %(date_naissance)s)
                RETURNING ;
                """,
                    {
                        "quantite": quantite,
                    },
                )
            res = cursor.fetchone()
    except Exception as e:
        logging.info(e)
    created = False
    if res:
        utilisateur.id_utilisateur = res["id_utilisateur"]
        created = True

    return created
