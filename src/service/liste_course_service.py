"""doc."""

from src.dao.ingredient_dao import IngredientDAO
from src.dao.liste_course_dao import ListeCourseDAO
from src.dao.stock_course_dao import StockCourseDAO
from src.models.liste_course import ListeCourse, ListeCourseItem
from src.utils.conversion_unite import UnitConverter
from src.utils.exceptions import ServiceError, UniteNotFoundError


class ListeCourseService:
    """Service pour gérer la liste de course des utilisateurs."""

    def __init__(self) -> None:
        """Initialise un ListeCourseService."""
        self.liste_course_dao = ListeCourseDAO()
        self.stock_dao = StockCourseDAO()
        self.ingredient_dao = IngredientDAO()

    def get_liste_course(self, id_utilisateur: int) -> ListeCourse:
        """Récupère la liste de course d'un utilisateur."""
        try:
            rows = self.liste_course_dao.get_liste_course(id_utilisateur)

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

            return ListeCourse(
                id_utilisateur=id_utilisateur,
                items=items,
                nombre_items=len(items),
                nombre_effectues=nombre_effectues,
            )
        except Exception as e:
            raise ServiceError(f"Erreur lors de la récupération de la liste de course : {e}")

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
        # Utiliser la méthode du DAO qui gère les suggestions
        ingredient = self.ingredient_dao.get_by_name_with_suggestions(nom_ingredient)

        # Récupérer l'ID de l'unité via son abréviation
        try:
            stock_dao = StockCourseDAO()
            id_unite = stock_dao.get_unite_id_by_abbreviation(abbreviation_unite)

            if id_unite is None:
                raise UniteNotFoundError(abbreviation_unite)

        except UniteNotFoundError:
            raise
        except Exception as e:
            raise ServiceError(f"Erreur lors de la récupération de l'unité : {e}") from e

        try:
            self.liste_course_dao.add_to_liste_course(
                id_utilisateur=id_utilisateur,
                id_ingredient=ingredient["id_ingredient"],
                quantite=quantite,
                id_unite=id_unite,
            )

            return f"Ingrédient '{ingredient['nom']}' ajouté à la liste de course ({quantite} {abbreviation_unite})"

        except Exception as e:
            raise ServiceError(f"Erreur lors de l'ajout à la liste de course : {e}") from e

    def remove_from_liste_course_and_add_to_stock(
        self,
        id_utilisateur: int,
        nom_ingredient: str,
    ) -> str:
        """Retire un ingrédient de la liste de course et l'ajoute au stock.

        Gère intelligemment les conversions d'unités :
        - Même unité → additionne directement
        - Unités liquides différentes → convertit en ml puis additionne
        - Unités solides différentes → convertit en g puis additionne
        - Types incompatibles → remplace par la nouvelle quantité
        """
        ingredient = self.ingredient_dao.get_by_name_with_suggestions(nom_ingredient)

        try:
            # Récupérer l'item de la liste de course
            liste_item = self.liste_course_dao.get_liste_course_item(
                id_utilisateur=id_utilisateur,
                id_ingredient=ingredient["id_ingredient"],
            )

            if not liste_item:
                raise ServiceError(
                    f"L'ingrédient '{ingredient['nom']}' n'est pas dans votre liste de course",
                )

            quantite_liste = float(liste_item["quantite"])
            id_unite_liste = liste_item["id_unite"]
            code_unite_liste = liste_item["code_unite"]

            # Vérifier si l'ingrédient existe déjà dans le stock
            stock_item = self.stock_dao.get_stock_item(
                id_utilisateur=id_utilisateur,
                id_ingredient=ingredient["id_ingredient"],
            )

            # ✅ Initialiser les variables par défaut
            nouvelle_quantite = quantite_liste
            id_unite_finale = id_unite_liste

            if stock_item:
                # L'ingrédient existe dans le stock
                quantite_stock = float(stock_item["quantite"])
                id_unite_stock = stock_item["id_unite"]

                # Récupérer l'info de l'unité du stock
                stock_unite_info = self.stock_dao.get_unite_info(id_unite_stock)
                code_unite_stock = stock_unite_info["abbreviation"] if stock_unite_info else None

                if id_unite_liste == id_unite_stock:
                    # Même unité → additionner directement
                    nouvelle_quantite = quantite_stock + quantite_liste
                    id_unite_finale = id_unite_liste

                elif code_unite_stock and code_unite_liste:
                    # Déterminer le type d'unité
                    is_liquid_liste = UnitConverter.is_liquid_unit(code_unite_liste)
                    is_liquid_stock = UnitConverter.is_liquid_unit(code_unite_stock)
                    is_solid_liste = UnitConverter.is_solid_unit(code_unite_liste)
                    is_solid_stock = UnitConverter.is_solid_unit(code_unite_stock)

                    if is_liquid_liste and is_liquid_stock:
                        # Les deux sont liquides → convertir en ml
                        ml_stock = UnitConverter.convert_to_ml(quantite_stock, code_unite_stock)
                        ml_liste = UnitConverter.convert_to_ml(quantite_liste, code_unite_liste)

                        if ml_stock is not None and ml_liste is not None:
                            total_ml = ml_stock + ml_liste

                            # Convertir le total dans l'unité du stock
                            facteur_stock = UnitConverter.LIQUID_TO_ML.get(code_unite_stock.lower(), 1)
                            nouvelle_quantite = total_ml / facteur_stock
                            id_unite_finale = id_unite_stock

                    elif is_solid_liste and is_solid_stock:
                        # Les deux sont solides → convertir en g
                        g_stock = UnitConverter.convert_to_g(quantite_stock, code_unite_stock)
                        g_liste = UnitConverter.convert_to_g(quantite_liste, code_unite_liste)

                        if g_stock is not None and g_liste is not None:
                            total_g = g_stock + g_liste

                            # Convertir le total dans l'unité du stock
                            facteur_stock = UnitConverter.SOLID_TO_G.get(code_unite_stock.lower(), 1)
                            nouvelle_quantite = total_g / facteur_stock
                            id_unite_finale = id_unite_stock

            # ✅ Créer ou mettre à jour le stock (REMPLACE toujours avec set_stock_item)
            self.stock_dao.set_stock_item(
                id_utilisateur=id_utilisateur,
                id_ingredient=ingredient["id_ingredient"],
                quantite=nouvelle_quantite,
                id_unite=id_unite_finale,
            )

            # Supprimer de la liste de course
            self.liste_course_dao.remove_from_liste_course(
                id_utilisateur=id_utilisateur,
                id_ingredient=ingredient["id_ingredient"],
            )

            # Récupérer l'unité finale pour le message
            unite_info = self.stock_dao.get_unite_info(id_unite_finale)
            code_unite_final = unite_info["abbreviation"] if unite_info else ""

            return f"Ingrédient '{ingredient['nom']}' retiré de la liste de course et ajouté au stock ({nouvelle_quantite} {code_unite_final})"

        except ServiceError:
            raise
        except Exception as e:
            raise ServiceError(f"Erreur lors du transfert vers le stock : {e}") from e

    def remove_from_liste_course(
        self,
        id_utilisateur: int,
        nom_ingredient: str,
    ) -> str:
        """Retire un ingrédient de la liste de course SANS l'ajouter au stock."""
        # Utiliser la méthode du DAO
        ingredient = self.ingredient_dao.get_by_name_with_suggestions(nom_ingredient)

        try:
            success = self.liste_course_dao.remove_from_liste_course(
                id_utilisateur=id_utilisateur,
                id_ingredient=ingredient["id_ingredient"],
            )

            if not success:
                raise ServiceError(
                    f"L'ingrédient '{ingredient['nom']}' n'est pas dans votre liste de course",
                )

            return f"Ingrédient '{ingredient['nom']}' retiré de la liste de course"

        except ServiceError:
            raise
        except Exception as e:
            raise ServiceError(f"Erreur lors du retrait de la liste de course : {e}")

    def clear_liste_course(self, id_utilisateur: int) -> str:
        """Vide complètement la liste de course."""
        try:
            count = self.liste_course_dao.clear_liste_course(id_utilisateur)

            if count == 0:
                return "La liste de course est déjà vide"

            return f"Liste de course vidée ({count} ingrédient{'s' if count > 1 else ''} supprimé{'s' if count > 1 else ''})"

        except Exception as e:
            raise ServiceError(f"Erreur lors du vidage de la liste de course : {e}")

    def toggle_effectue(
        self,
        id_utilisateur: int,
        nom_ingredient: str,
    ) -> dict:
        """Toggle le statut 'effectué' d'un item de la liste de course."""
        # Utiliser la méthode du DAO
        ingredient = self.ingredient_dao.get_by_name_with_suggestions(nom_ingredient)

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
            raise ServiceError(f"Erreur lors de la modification du statut : {e}")
