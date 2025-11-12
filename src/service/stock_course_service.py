from src.dao.ingredient_dao import IngredientDao
from src.dao.stock_course_dao import StockCourseDao
from src.models.stock import Stock, StockItem
from src.utils.exceptions import IngredientNotFoundError, InsufficientQuantityError, InvalidQuantityError, ServiceError
from src.utils.text_utils import normalize_ingredient_name


class StockCourseService:
    """Service pour gérer le stock des utilisateurs."""

    def __init__(self):
        self.stock_dao = StockCourseDao()
        self.ingredient_dao = IngredientDao()

    def _get_ingredient_by_name(self, nom_ingredient: str) -> dict:
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
        # Normaliser le nom
        nom_normalized = normalize_ingredient_name(nom_ingredient)

        # Chercher l'ingrédient
        ingredient = self.ingredient_dao.get_by_name(nom_normalized)

        if not ingredient:
            # Chercher des suggestions
            suggestions_data = self.ingredient_dao.search_by_name(nom_normalized, limit=5)
            suggestions = [s["nom"] for s in suggestions_data]
            raise IngredientNotFoundError(nom_normalized, suggestions)

        return ingredient

    def add_or_update_ingredient_by_name(
        self,
        id_utilisateur: int,
        nom_ingredient: str,
        quantite: float,
        id_unite: int,
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
        id_unite : int
            ID de l'unité

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
        ServiceError
            Si erreur lors de l'ajout

        """
        # Validation quantité
        if quantite <= 0:
            raise InvalidQuantityError(quantite)

        # Récupérer l'ingrédient (lève exception si non trouvé)
        ingredient = self._get_ingredient_by_name(nom_ingredient)

        # Ajouter au stock en utilisant l'ID
        try:
            success = self.stock_dao.update_or_create_stock_item(
                id_utilisateur=id_utilisateur,
                id_ingredient=ingredient["id_ingredient"],
                quantite=quantite,
                id_unite=id_unite,
            )

            if not success:
                raise ServiceError("Impossible d'ajouter l'ingrédient au stock")

            return f"Ingrédient '{ingredient['nom']}' ajouté/mis à jour avec succès"

        except (InvalidQuantityError, IngredientNotFoundError):
            raise
        except Exception as e:
            raise ServiceError(f"Erreur lors de l'ajout au stock : {e}")

    def get_user_stock(
        self,
        id_utilisateur: int,
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
            # Le DAO retourne des dictionnaires
            rows = self.stock_dao.get_stock(
                id_utilisateur=id_utilisateur,
                only_available=only_available,
            )

            # Conversion en modèles Pydantic dans le Service
            items = [
                StockItem(
                    id_ingredient=row["id_ingredient"],
                    nom_ingredient=row["nom_ingredient"],
                    quantite=float(row["quantite"]),  # ← Conversion Decimal → float
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
            raise ServiceError(f"Erreur lors de la récupération du stock : {e}")

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
        # Récupérer l'ingrédient (lève exception si non trouvé)
        ingredient = self._get_ingredient_by_name(nom_ingredient)

        try:
            # Le DAO retourne un dictionnaire
            row = self.stock_dao.get_stock_item(
                id_utilisateur=id_utilisateur,
                id_ingredient=ingredient["id_ingredient"],
            )

            if not row:
                return None

            # Conversion en modèle Pydantic dans le Service
            return StockItem(
                id_ingredient=row["id_ingredient"],
                nom_ingredient=row["nom_ingredient"],
                quantite=float(row["quantite"]),  # ← Conversion Decimal → float
                id_unite=row["id_unite"],
                code_unite=row["code_unite"],
                nom_unite_complet=row["nom_unite_complet"],
            )
        except Exception as e:
            raise ServiceError(f"Erreur lors de la récupération de l'ingrédient : {e}")

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
        # Validation de la quantité
        if quantite <= 0:
            raise InvalidQuantityError(quantite)

        # Récupérer l'ingrédient (lève exception si non trouvé)
        ingredient = self._get_ingredient_by_name(nom_ingredient)

        try:
            result = self.stock_dao.decrement_stock_item(
                id_utilisateur=id_utilisateur,
                id_ingredient=ingredient["id_ingredient"],
                quantite=quantite,
            )

            if result["supprime"]:
                return f"Ingrédient '{ingredient['nom']}' retiré complètement du stock (quantité épuisée)"
            return f"{quantite} retiré(s) de '{ingredient['nom']}'. Nouvelle quantité : {result['nouvelle_quantite']}"

        except ValueError as e:
            # Capturer les erreurs de quantité insuffisante ou ingrédient non trouvé
            error_msg = str(e)
            if "Impossible de retirer" in error_msg:
                # Extraire les quantités du message d'erreur
                # Format: "Impossible de retirer X (quantité disponible : Y)"
                import re

                match = re.search(r"retirer ([\d.]+).*disponible : ([\d.]+)", error_msg)
                if match:
                    quantite_demandee = float(match.group(1))
                    quantite_disponible = float(match.group(2))
                    raise InsufficientQuantityError(quantite_demandee, quantite_disponible)

            if "non trouvé dans le stock" in error_msg:
                raise ServiceError(f"L'ingrédient '{ingredient['nom']}' n'est pas dans votre stock")

            raise ServiceError(error_msg)

        except (InvalidQuantityError, IngredientNotFoundError, InsufficientQuantityError):
            raise
        except Exception as e:
            raise ServiceError(f"Erreur lors du retrait : {e}")

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
        # Récupérer l'ingrédient (lève exception si non trouvé)
        ingredient = self._get_ingredient_by_name(nom_ingredient)

        try:
            success = self.stock_dao.delete_stock_item(
                id_utilisateur=id_utilisateur,
                id_ingredient=ingredient["id_ingredient"],
            )

            if not success:
                raise ServiceError(f"L'ingrédient '{ingredient['nom']}' n'est pas dans votre stock")

            return f"Ingrédient '{ingredient['nom']}' supprimé complètement du stock"

        except ServiceError:
            raise
        except Exception as e:
            raise ServiceError(f"Erreur lors de la suppression : {e}")

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
            raise ServiceError(f"Erreur lors de la récupération du stock complet : {e}")
