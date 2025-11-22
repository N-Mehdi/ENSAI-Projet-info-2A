"""Couche service pour les opérations sur les listes de course."""

from src.dao.ingredient_dao import IngredientDAO
from src.dao.liste_course_dao import ListeCourseDAO
from src.dao.stock_dao import StockDAO
from src.dao.utilisateur_dao import UtilisateurDAO
from src.models.liste_course import ListeCourseItem
from src.service.ingredient_service import IngredientService
from src.service.utilisateur_service import UtilisateurService
from src.utils.conversion_unite import UnitConverter
from src.utils.exceptions import (
    IngredientNotFoundError,
    ServiceError,
    UniteNotFoundError,
)


class ListeCourseService:
    """Service pour gérer la liste de course des utilisateurs."""

    def __init__(self) -> None:
        """Initialise un ListeCourseService."""
        self.liste_course_dao = ListeCourseDAO()
        self.stock_dao = StockDAO()
        self.ingredient_dao = IngredientDAO()
        self.ingredient_svc = IngredientService()
        utilisateur_dao = UtilisateurDAO()
        self.utilisateur_svc = UtilisateurService(utilisateur_dao)

    def get_liste_course(self, id_utilisateur: int) -> dict:
        """Récupère la liste de course complète d'un utilisateur.

        Parameters
        ----------
        id_utilisateur : int
            L'identifiant de l'utilisateur

        Returns
        -------
        ListeCourse
            Objet contenant :
            - id_utilisateur : int
            - items : list[ListeCourseItem]
            - nombre_items : int (nombre total d'items)
            - nombre_effectues : int (nombre d'items cochés)

        Raises
        ------
        ServiceError
            En cas d'erreur lors de la récupération de la liste de course

        """
        try:
            rows = self.liste_course_dao.get_liste_course(id_utilisateur)
            pseudo = self.utilisateur_svc.read(id_utilisateur=id_utilisateur).pseudo
            items = [
                ListeCourseItem(
                    id_ingredient=row["id_ingredient"],
                    nom_ingredient=row["nom_ingredient"],
                    quantite=float(row["quantite"]),
                    effectue=row["effectue"],
                    id_unite=row["id_unite"],
                    code_unite=row["code_unite"],
                    nom_unite_complet=row["nom_unite_complet"],
                )
                for row in rows
            ]

            nombre_effectues = sum(1 for item in items if item.effectue)

            return {
                "pseudo": pseudo,
                "items": items,
                "nombre_items": len(items),
                "nombre_effectues": nombre_effectues,
            }
        except Exception as e:
            raise ServiceError(
                message=f"Erreur lors de la récupération de la liste de course : {e}",
            ) from e

    def add_to_liste_course(
        self,
        id_utilisateur: int,
        nom_ingredient: str,
        quantite: float,
        abbreviation_unite: str,
    ) -> str:
        """Ajoute un ingrédient à la liste de course.

        Parameters
        ----------
        id_utilisateur : int
            ID de l'utilisateur
        nom_ingredient : str
            Nom de l'ingrédient
        quantite : float
            Quantité
        abbreviation_unite : str
            Abréviation de l'unité (ex: 'ml', 'cl', 'g', 'kg')

        Returns
        -------
        str
            Message de confirmation

        Raises
        ------
        IngredientNotFoundError
            Si l'ingrédient n'existe pas
        UniteNotFoundError
            Si l'unité n'existe pas
        ServiceError
            En cas d'erreur

        """
        ingredient = self.ingredient_svc.get_by_name_with_suggestions(nom_ingredient)

        try:
            id_unite = self.stock_dao.get_unite_id_by_abbreviation(abbreviation_unite)

        except IngredientNotFoundError as e:
            raise IngredientNotFoundError(message="L'ingrédient n'existe pas") from e
        except ServiceError as e:
            raise ServiceError(
                message=f"Erreur lors de la récupération del'unité : {e}",
            ) from e

        if id_unite is None:
            raise UniteNotFoundError(abbreviation_unite)

        try:
            self.liste_course_dao.add_to_liste_course(
                id_utilisateur=id_utilisateur,
                id_ingredient=ingredient["id_ingredient"],
                quantite=quantite,
                id_unite=id_unite,
            )

        except Exception as e:
            raise ServiceError(
                message=f"Erreur lors de l'ajout à la liste de course : {e}",
            ) from e
        return (
            f"Ingrédient '{ingredient['nom']}' ajouté à la liste de course "
            f"({quantite} {abbreviation_unite})"
        )

    def remove_from_liste_course_and_add_to_stock(
        self,
        id_utilisateur: int,
        nom_ingredient: str,
    ) -> str:
        """Retire un ingrédient de la liste de course et l'ajoute au stock.

        Gère intelligemment les conversions d'unités lors de l'ajout au stock :
        - Même unité : additionne directement les quantités
        - Unités liquides différentes : convertit en ml, additionne et reconvertit
        - Unités solides différentes : convertit en g, additionne et reconvertit
        - Types incompatibles : remplace par la nouvelle quantité

        Parameters
        ----------
        id_utilisateur : int
            L'identifiant de l'utilisateur
        nom_ingredient : str
            Le nom de l'ingrédient à transférer

        Returns
        -------
        str
            Message de confirmation avec la quantité et l'unité finale

        Raises
        ------
        IngredientNotFoundError
            Si l'ingrédient n'existe pas
        ServiceError
            Si l'ingrédient n'est pas dans la liste de course ou en cas d'erreur
            lors du transfert

        """
        ingredient = self.ingredient_svc.get_by_name_with_suggestions(nom_ingredient)
        liste_item = self._recuperer_liste_item(id_utilisateur, ingredient)
        stock_item = self._recuperer_stock_item(id_utilisateur, ingredient)

        nouvelle_quantite, id_unite_finale = self._calculer_nouvelle_quantite(
            liste_item,
            stock_item,
        )

        self._transferer_vers_stock(
            id_utilisateur,
            ingredient["id_ingredient"],
            nouvelle_quantite,
            id_unite_finale,
        )

        return self._generer_message_confirmation(
            ingredient["nom"],
            nouvelle_quantite,
            id_unite_finale,
        )

    def _recuperer_liste_item(self, id_utilisateur: int, ingredient: dict) -> dict:
        """Récupère l'item de la liste de course.

        Parameters
        ----------
        id_utilisateur : int
            L'identifiant de l'utilisateur
        ingredient : dict
            Informations de l'ingrédient

        Returns
        -------
        dict
            Item de la liste de course

        Raises
        ------
        ServiceError
            Si l'item n'existe pas ou erreur de récupération

        """
        try:
            liste_item = self.liste_course_dao.get_liste_course_item(
                id_utilisateur=id_utilisateur,
                id_ingredient=ingredient["id_ingredient"],
            )
        except Exception as e:
            raise ServiceError(
                message=f"Erreur lors de la récupération de la liste de course : {e}",
            ) from e

        if not liste_item:
            raise ServiceError(
                message=f"L'ingrédient '{ingredient['nom']}' n'est pas dans votre "
                "liste de course",
            )

        return liste_item

    def _recuperer_stock_item(
        self,
        id_utilisateur: int,
        ingredient: dict,
    ) -> dict | None:
        """Récupère l'item du stock s'il existe.

        Parameters
        ----------
        id_utilisateur : int
            L'identifiant de l'utilisateur
        ingredient : dict
            Informations de l'ingrédient

        Returns
        -------
        dict | None
            Item du stock ou None s'il n'existe pas

        Raises
        ------
        ServiceError
            En cas d'erreur de récupération

        """
        try:
            return self.stock_dao.get_stock_item(
                id_utilisateur=id_utilisateur,
                id_ingredient=ingredient["id_ingredient"],
            )
        except Exception as e:
            raise ServiceError(
                message=f"Erreur lors de la récupération du stock : {e}",
            ) from e

    def _calculer_nouvelle_quantite(
        self,
        liste_item: dict,
        stock_item: dict | None,
    ) -> tuple[float, int]:
        """Trouve la nouvelle quantité en gérant les conversions d'unités.

        Parameters
        ----------
        liste_item : dict
            Item de la liste de course
        stock_item : dict | None
            Item du stock existant ou None

        Returns
        -------
        tuple[float, int]
            (nouvelle_quantite, id_unite_finale)

        """
        quantite_liste = float(liste_item["quantite"])
        id_unite_liste = liste_item["id_unite"]

        if not stock_item:
            return quantite_liste, id_unite_liste

        return self._fusionner_quantites(liste_item, stock_item)

    def _fusionner_quantites(
        self,
        liste_item: dict,
        stock_item: dict,
    ) -> tuple[float, int]:
        """Fusionne les quantités du stock et de la liste de course.

        Parameters
        ----------
        liste_item : dict
            Item de la liste de course
        stock_item : dict
            Item du stock existant

        Returns
        -------
        tuple[float, int]
            (nouvelle_quantite, id_unite_finale)

        """
        quantite_liste = float(liste_item["quantite"])
        id_unite_liste = liste_item["id_unite"]
        code_unite_liste = liste_item["code_unite"]

        quantite_stock = float(stock_item["quantite"])
        id_unite_stock = stock_item["id_unite"]

        # Même unité : addition directe
        if id_unite_liste == id_unite_stock:
            return quantite_stock + quantite_liste, id_unite_liste

        # Unités différentes : conversion nécessaire
        stock_unite_info = self.stock_dao.get_unite_info(id_unite_stock)
        code_unite_stock = (
            stock_unite_info["abbreviation"] if stock_unite_info else None
        )

        if not (code_unite_stock and code_unite_liste):
            return quantite_liste, id_unite_liste

        return self._convertir_et_additionner(
            quantite_liste,
            code_unite_liste,
            quantite_stock,
            code_unite_stock,
            id_unite_stock,
            id_unite_liste,
        )

    # ruff: noqa: PLR0913
    # ruff: noqa: PLR0917
    def _convertir_et_additionner(
        self,
        quantite_liste: float,
        code_unite_liste: str,
        quantite_stock: float,
        code_unite_stock: str,
        id_unite_stock: int,
        id_unite_liste: int,
    ) -> tuple[float, int]:
        """Convertit et additionne les quantités selon leur type.

        Parameters
        ----------
        quantite_liste : float
            Quantité de la liste de course
        code_unite_liste : str
            Code unité de la liste
        quantite_stock : float
            Quantité du stock
        code_unite_stock : str
            Code unité du stock
        id_unite_stock : int
            ID unité du stock
        id_unite_liste : int
            ID unité de la liste

        Returns
        -------
        tuple[float, int]
            (nouvelle_quantite, id_unite_finale)

        """
        # Vérifier si les deux unités sont liquides
        if UnitConverter.is_liquid_unit(
            code_unite_liste,
        ) and UnitConverter.is_liquid_unit(code_unite_stock):
            return self._additionner_liquides(
                quantite_liste,
                code_unite_liste,
                quantite_stock,
                code_unite_stock,
                id_unite_stock,
            )

        # Vérifier si les deux unités sont solides
        if UnitConverter.is_solid_unit(
            code_unite_liste,
        ) and UnitConverter.is_solid_unit(code_unite_stock):
            return self._additionner_solides(
                quantite_liste,
                code_unite_liste,
                quantite_stock,
                code_unite_stock,
                id_unite_stock,
            )

        # Types incompatibles : garder la quantité de la liste
        return quantite_liste, id_unite_liste

    @staticmethod
    def _additionner_liquides(
        quantite_liste: float,
        code_unite_liste: str,
        quantite_stock: float,
        code_unite_stock: str,
        id_unite_stock: int,
    ) -> tuple[float, int]:
        """Additionne deux quantités liquides avec conversion.

        Parameters
        ----------
        quantite_liste : float
            Quantité de la liste de course
        code_unite_liste : str
            Code unité de la liste
        quantite_stock : float
            Quantité du stock
        code_unite_stock : str
            Code unité du stock
        id_unite_stock : int
            ID unité du stock

        Returns
        -------
        tuple[float, int]
            (nouvelle_quantite, id_unite_finale)

        """
        ml_stock = UnitConverter.convert_to_ml(quantite_stock, code_unite_stock)
        ml_liste = UnitConverter.convert_to_ml(quantite_liste, code_unite_liste)

        if ml_stock is None or ml_liste is None:
            return quantite_liste, id_unite_stock

        total_ml = ml_stock + ml_liste
        facteur_stock = UnitConverter.LIQUID_TO_ML.get(code_unite_stock.lower(), 1)
        nouvelle_quantite = total_ml / facteur_stock

        return nouvelle_quantite, id_unite_stock

    @staticmethod
    def _additionner_solides(
        quantite_liste: float,
        code_unite_liste: str,
        quantite_stock: float,
        code_unite_stock: str,
        id_unite_stock: int,
    ) -> tuple[float, int]:
        """Additionne deux quantités solides avec conversion.

        Parameters
        ----------
        quantite_liste : float
            Quantité de la liste de course
        code_unite_liste : str
            Code unité de la liste
        quantite_stock : float
            Quantité du stock
        code_unite_stock : str
            Code unité du stock
        id_unite_stock : int
            ID unité du stock

        Returns
        -------
        tuple[float, int]
            (nouvelle_quantite, id_unite_finale)

        """
        g_stock = UnitConverter.convert_to_g(quantite_stock, code_unite_stock)
        g_liste = UnitConverter.convert_to_g(quantite_liste, code_unite_liste)

        if g_stock is None or g_liste is None:
            return quantite_liste, id_unite_stock

        total_g = g_stock + g_liste
        facteur_stock = UnitConverter.SOLID_TO_G.get(code_unite_stock.lower(), 1)
        nouvelle_quantite = total_g / facteur_stock

        return nouvelle_quantite, id_unite_stock

    def _transferer_vers_stock(
        self,
        id_utilisateur: int,
        id_ingredient: int,
        nouvelle_quantite: float,
        id_unite_finale: int,
    ) -> None:
        """Transfère l'ingrédient de la liste de course vers le stock.

        Parameters
        ----------
        id_utilisateur : int
            L'identifiant de l'utilisateur
        id_ingredient : int
            L'identifiant de l'ingrédient
        nouvelle_quantite : float
            La nouvelle quantité
        id_unite_finale : int
            L'identifiant de l'unité finale

        Raises
        ------
        ServiceError
            En cas d'erreur lors du transfert

        """
        try:
            self.stock_dao.set_stock_item(
                id_utilisateur=id_utilisateur,
                id_ingredient=id_ingredient,
                quantite=nouvelle_quantite,
                id_unite=id_unite_finale,
            )

            self.liste_course_dao.remove_from_liste_course(
                id_utilisateur=id_utilisateur,
                id_ingredient=id_ingredient,
            )
        except Exception as e:
            raise ServiceError(
                message=f"Erreur lors du transfert vers le stock : {e}",
            ) from e

    def _generer_message_confirmation(
        self,
        nom_ingredient: str,
        nouvelle_quantite: float,
        id_unite_finale: int,
    ) -> str:
        """Génère le message de confirmation.

        Parameters
        ----------
        nom_ingredient : str
            Nom de l'ingrédient
        nouvelle_quantite : float
            La nouvelle quantité
        id_unite_finale : int
            L'identifiant de l'unité finale

        Returns
        -------
        str
            Message de confirmation

        """
        unite_info = self.stock_dao.get_unite_info(id_unite_finale)
        code_unite_final = unite_info["abbreviation"] if unite_info else ""

        return (
            f"Ingrédient '{nom_ingredient}' retiré de la liste de course "
            f"et ajouté au stock ({nouvelle_quantite} {code_unite_final})"
        )

    def remove_from_liste_course(
        self,
        id_utilisateur: int,
        nom_ingredient: str,
    ) -> str:
        """Retirer un ingrédient de la liste de course d'un utilisateur.

        Parameters
        ----------
        id_utilisateur : int
            Identifiant unique de l'utilisateur dont on souhaite modifier
            la liste de course.
        nom_ingredient : str
            Nom de l'ingrédient à retirer.

        Returns
        -------
        str
        Message confirmant que l'ingrédient a été retiré de la liste de course.

        Raises
        ------
        IngredientNotFoundError
        Si l'ingrédient n'existe pas (avec suggestions)
        ServiceError
        Si l'ingrédient n'est pas présent dans la liste de course ou en cas d'erreur
        lors de l'accès à la base de données.

        """
        ingredient = self.ingredient_svc.get_by_name_with_suggestions(nom_ingredient)

        try:
            success = self.liste_course_dao.remove_from_liste_course(
                id_utilisateur=id_utilisateur,
                id_ingredient=ingredient["id_ingredient"],
            )

        except ServiceError:
            raise
        except Exception as e:
            raise ServiceError(
                message=f"Erreur lors du retrait de la liste de course : {e}",
            ) from e

        if not success:
            raise ServiceError(
                message=f"L'ingrédient '{ingredient['nom']}' n'est pas dans votre"
                "liste de course",
            )

        return f"Ingrédient '{ingredient['nom']}' retiré de la liste de course"

    def clear_liste_course(self, id_utilisateur: int) -> str:
        """Vider complètement la liste de course d'un utilisateur.

        Parameters
        ----------
        id_utilisateur : int
            Identifiant unique de l'utilisateur dont la liste de course sera vidée.

        Returns
        -------
        str
            Message confirmant le vidage de la liste, avec le nombre d'ingrédients
            supprimés
            ou indiquant que la liste était déjà vide.

        Raises
        ------
        ServiceError
            En cas d'erreur lors de l'accès ou de la modification de la base de données.

        """
        try:
            count = self.liste_course_dao.clear_liste_course(id_utilisateur)

            if count == 0:
                return "La liste de course est déjà vide"

        except Exception as e:
            raise ServiceError(
                message=f"Erreur lors du vidage de la liste de course : {e}",
            ) from e

        return (
            f"Liste de course vidée ({count} ingrédient{'s' if count > 1 else ''}"
            f"supprimé{'s' if count > 1 else ''})"
        )

    def toggle_effectue(
        self,
        id_utilisateur: int,
        nom_ingredient: str,
    ) -> dict:
        """Bascule le statut 'effectué' d'un item de la liste de course.

        Change l'état de coché à décoché ou inversement.

        Parameters
        ----------
        id_utilisateur : int
            L'identifiant de l'utilisateur
        nom_ingredient : str
            Le nom de l'ingrédient dont on change le statut

        Returns
        -------
        dict
            Dictionnaire contenant :
            - effectue : bool (nouveau statut)
            - message : str (message de confirmation)

        Raises
        ------
        IngredientNotFoundError
            Si l'ingrédient n'existe pas
        ServiceError
            En cas d'erreur lors de la modification du statut

        """
        ingredient = self.ingredient_svc.get_by_name_with_suggestions(nom_ingredient)

        try:
            effectue = self.liste_course_dao.toggle_effectue(
                id_utilisateur=id_utilisateur,
                id_ingredient=ingredient["id_ingredient"],
            )

            status = "coché" if effectue else "décoché"

            return {
                "effectue": effectue,
                "message": f"Ingrédient '{ingredient['nom']}' {status}",
            }

        except Exception as e:
            raise ServiceError(
                message=f"Erreur lors de la modification du statut : {e}",
            ) from e
