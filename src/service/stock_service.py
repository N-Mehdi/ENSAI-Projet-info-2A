"""Couche service pour les opérations de stock."""

import re

from src.dao.ingredient_dao import IngredientDAO
from src.dao.stock_dao import StockDAO
from src.models.stock import Stock, StockItem
from src.utils.exceptions import (
    DAOError,
    IngredientNotFoundError,
    InsufficientQuantityError,
    InvalidQuantityError,
    ServiceError,
    UniteNotFoundError,
)
from src.utils.text_utils import normalize_ingredient_name


class StockService:
    """Service pour gérer le stock des utilisateurs."""

    def __init__(self) -> None:
        """Initialise un StockService."""
        self.stock_dao = StockDAO()
        self.ingredient_dao = IngredientDAO()

    def get_ingredient_by_name(self, nom_ingredient: str) -> dict:
        """Méthode privée pour récupérer un ingrédient par son nom.
        Lève une exception avec suggestions si non trouvé.

        Parameters
        ----------
        nom_ingredient : str
            Nom de l'ingrédient (sera normalisé)

        Returns
        -------
        dict
            L'ingrédient trouvé

        Raises
        ------
        IngredientNotFoundError
            Si l'ingrédient n'existe pas

        """
        nom_normalized = normalize_ingredient_name(nom_ingredient)

        ingredient = self.ingredient_dao.get_by_name(nom_normalized)

        if not ingredient:
            suggestions_data = self.ingredient_dao.search_by_name(
                nom_normalized,
                limit=5,
            )
            suggestions = [s["nom"] for s in suggestions_data]
            raise IngredientNotFoundError(
                message=f"Ingrédient{nom_normalized} introuvable. "
                f"Vouliez-vous dire {','.join(suggestions[:3])} ?",
            )

        return ingredient

    def add_or_update_ingredient_by_name(
        self,
        id_utilisateur: int,
        nom_ingredient: str,
        quantite: float,
        abbreviation_unite: str,
    ) -> str:
        """Ajoute ou met à jour un ingrédient dans le stock en utilisant son nom.

        Parameters
        ----------
        id_utilisateur : int
            ID de l'utilisateur
        nom_ingredient : str
            Nom de l'ingrédient (sera normalisé automatiquement)
        quantite : float
            Quantité (doit être > 0)
        abbreviation_unite : str
            Abréviation de l'unité (ex: 'ml', 'cl', 'g', 'kg')

        Returns
        -------
        str
            Message de confirmation

        Raises
        ------
        InvalidQuantityError
            Si la quantité est <= 0
        IngredientNotFoundError
            Si l'ingrédient n'existe pas (avec suggestions)
        UniteNotFoundError
            Si l'unité n'existe pas
        ServiceError
            Si erreur lors de l'ajout

        """
        if quantite <= 0:
            raise InvalidQuantityError(
                message=f"Quantité invalide : {quantite}.La quantité doit être > 0",
            )

        ingredient = self.get_ingredient_by_name(nom_ingredient)

        try:
            id_unite = self.stock_dao.get_unite_id_by_abbreviation(abbreviation_unite)

            if id_unite is None:
                raise UniteNotFoundError(abbreviation_unite)

        except DAOError as e:
            raise ServiceError from e

        try:
            success = self.stock_dao.update_or_create_stock_item(
                id_utilisateur=id_utilisateur,
                id_ingredient=ingredient["id_ingredient"],
                quantite=quantite,
                id_unite=id_unite,
            )

        except (InvalidQuantityError, IngredientNotFoundError, UniteNotFoundError):
            raise
        except Exception as e:
            raise ServiceError(message=f"Erreur lors de l'ajout au stock : {e}") from e
        if not success:
            raise ServiceError(message="Impossible d'ajouter l'ingrédient au stock")

        return (
            f"Ingrédient '{ingredient['nom']}' ajouté/mis à jour avec succès "
            f"({quantite} {abbreviation_unite})"
        )

    def get_user_stock(
        self,
        id_utilisateur: int,
        *,
        only_available: bool = True,
    ) -> Stock:
        """Récupère le stock d'un utilisateur.

        Parameters
        ----------
        id_utilisateur : int
            ID de l'utilisateur
        only_available : bool, optional
            Si True, retourne seulement les ingrédients disponibles

        Returns
        -------
        Stock
            Le stock de l'utilisateur.

        """
        try:
            rows = self.stock_dao.get_stock(
                id_utilisateur=id_utilisateur,
                only_available=only_available,
            )

            items = [
                StockItem(
                    id_ingredient=row["id_ingredient"],
                    nom_ingredient=row["nom_ingredient"],
                    quantite=float(row["quantite"]),
                    id_unite=row["id_unite"],
                    code_unite=row["code_unite"],
                    nom_unite_complet=row["nom_unite_complet"],
                )
                for row in rows
            ]

            return Stock(
                id_utilisateur=id_utilisateur,
                items=items,
            )
        except Exception as e:
            raise ServiceError(
                message=f"Erreur lors de la récupération du stock : {e}",
            ) from e

    def get_ingredient_from_stock_by_name(
        self,
        id_utilisateur: int,
        nom_ingredient: str,
    ) -> StockItem | None:
        """Récupère un ingrédient spécifique du stock en utilisant son nom.

        Parameters
        ----------
        id_utilisateur : int
            ID de l'utilisateur
        nom_ingredient : str
            Nom de l'ingrédient (sera normalisé)

        Returns
        -------
        StockItem | None
            L'ingrédient s'il existe dans le stock, None sinon

        Raises
        ------
        IngredientNotFoundError
            Si l'ingrédient n'existe pas dans la base de données

        """
        ingredient = self.get_ingredient_by_name(nom_ingredient)

        try:
            row = self.stock_dao.get_stock_item(
                id_utilisateur=id_utilisateur,
                id_ingredient=ingredient["id_ingredient"],
            )

            if not row:
                return None

            return StockItem(
                id_ingredient=row["id_ingredient"],
                nom_ingredient=row["nom_ingredient"],
                quantite=float(row["quantite"]),
                id_unite=row["id_unite"],
                code_unite=row["code_unite"],
                nom_unite_complet=row["nom_unite_complet"],
            )
        except Exception as e:
            raise ServiceError(
                message=f"Erreur lors de la récupération de l'ingrédient : {e}",
            ) from e

    def remove_ingredient_by_name(
        self,
        id_utilisateur: int,
        nom_ingredient: str,
        quantite: float,
    ) -> str:
        """Retire une quantité d'un ingrédient du stock en utilisant son nom.

        Parameters
        ----------
        id_utilisateur : int
            ID de l'utilisateur
        nom_ingredient : str
            Nom de l'ingrédient (sera normalisé)
        quantite : float
            Quantité à retirer (doit être > 0)

        Returns
        -------
        str
            Message de confirmation

        Raises
        ------
        InvalidQuantityError
            Si la quantité est <= 0
        IngredientNotFoundError
            Si l'ingrédient n'existe pas dans la base de données
        InsufficientQuantityError
            Si la quantité à retirer est supérieure à la quantité disponible
        ServiceError
            Si l'ingrédient n'est pas dans le stock ou erreur lors de la suppression

        """
        if quantite <= 0:
            raise InvalidQuantityError(
                message=f"Quantité invalide : {quantite}. La quantité doit être > 0",
            )

        ingredient = self.get_ingredient_by_name(nom_ingredient)

        try:
            result = self.stock_dao.decrement_stock_item(
                id_utilisateur=id_utilisateur,
                id_ingredient=ingredient["id_ingredient"],
                quantite=quantite,
            )

            if result["supprime"]:
                return (
                    f"Ingrédient '{ingredient['nom']}' retiré complètement du stock"
                    f"(quantité épuisée)"
                )
            return (
                f"{quantite} retiré(s) de '{ingredient['nom']}'. Nouvelle quantité :"
                f"{result['nouvelle_quantite']}"
            )

        except ValueError as e:
            error_msg = str(e)
            if "Impossible de retirer" in error_msg:
                match = re.search(r"retirer ([\d.]+).*disponible : ([\d.]+)", error_msg)
                if match:
                    quantite_demandee = float(match.group(1))
                    quantite_disponible = float(match.group(2))
                    raise InsufficientQuantityError(
                        quantite_demandee,
                        quantite_disponible,
                    ) from e

            if "non trouvé dans le stock" in error_msg:
                raise ServiceError(
                    message=f"L'ingrédient '{ingredient['nom']}' n'est pas dans"
                    "votre stock",
                ) from e

            raise ServiceError(error_msg) from e

        except (
            InvalidQuantityError,
            IngredientNotFoundError,
            InsufficientQuantityError,
        ):
            raise
        except Exception as e:
            raise ServiceError(message=f"Erreur lors du retrait : {e}") from e

    def delete_ingredient_by_name(
        self,
        id_utilisateur: int,
        nom_ingredient: str,
    ) -> str:
        """Supprime complètement un ingrédient du stock (quelle que soit la quantité).

        Cette méthode supprime l'ingrédient entièrement.
        Utilisez remove_ingredient_by_name() pour retirer une quantité spécifique.

        Parameters
        ----------
        id_utilisateur : int
            ID de l'utilisateur
        nom_ingredient : str
            Nom de l'ingrédient (sera normalisé)

        Returns
        -------
        str
            Message de confirmation

        Raises
        ------
        IngredientNotFoundError
            Si l'ingrédient n'existe pas dans la base de données
        ServiceError
            Si l'ingrédient n'est pas dans le stock ou erreur lors de la suppression

        """
        ingredient = self.get_ingredient_by_name(nom_ingredient)

        try:
            success = self.stock_dao.delete_stock_item(
                id_utilisateur=id_utilisateur,
                id_ingredient=ingredient["id_ingredient"],
            )

        except ServiceError:
            raise
        except Exception as e:
            raise ServiceError(message=f"Erreur lors de la suppression : {e}") from e
        if not success:
            raise ServiceError(
                message=(
                    f"L'ingrédient '{ingredient['nom']}' n'est pas dans votrestock",
                ),
            )

        return f"Ingrédient '{ingredient['nom']}' supprimé complètement du stock"

    def get_full_stock_list(self, id_utilisateur: int) -> list[dict]:
        """Récupère TOUS les ingrédients avec leur quantité.

        Parameters
        ----------
        id_utilisateur : int
            ID de l'utilisateur

        Returns
        -------
        list[dict]
            Liste complète des ingrédients (quantité = 0 si pas dans stock)

        """
        try:
            return self.stock_dao.get_full_stock(id_utilisateur)
        except Exception as e:
            raise ServiceError(
                message=f"Erreur lors de la récupération du stock complet : {e}",
            ) from e
