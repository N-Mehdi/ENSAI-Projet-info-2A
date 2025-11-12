from src.dao.ingredient_dao import IngredientDao
from src.dao.liste_course_dao import ListeCourseDao
from src.dao.stock_course_dao import StockCourseDao
from src.models.liste_course import ListeCourse, ListeCourseItem
from src.utils.conversion_unite import UnitConverter
from src.utils.exceptions import ServiceError


class ListeCourseService:
    """Service pour gérer la liste de course des utilisateurs."""

    def __init__(self):
        self.liste_course_dao = ListeCourseDao()
        self.stock_dao = StockCourseDao()
        self.ingredient_dao = IngredientDao()

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
        id_unite: int,
    ) -> str:
        """Ajoute un ingrédient à la liste de course."""
        # Utiliser la méthode du DAO qui gère les suggestions
        ingredient = self.ingredient_dao.get_by_name_with_suggestions(nom_ingredient)

        try:
            self.liste_course_dao.add_to_liste_course(
                id_utilisateur=id_utilisateur,
                id_ingredient=ingredient["id_ingredient"],
                quantite=quantite,
                id_unite=id_unite,
            )

            return f"Ingrédient '{ingredient['nom']}' ajouté à la liste de course"

        except Exception as e:
            raise ServiceError(f"Erreur lors de l'ajout à la liste de course : {e}")

    def remove_from_liste_course_and_add_to_stock(
        self,
        id_utilisateur: int,
        nom_ingredient: str,
    ) -> str:
        """Retire un ingrédient de la liste de course et l'ajoute au stock."""
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
            type_unite_liste = liste_item["type_unite"]
            code_unite_liste = liste_item["code_unite"]

            # Vérifier si l'ingrédient existe déjà dans le stock
            stock_item = self.stock_dao.get_stock_item(
                id_utilisateur=id_utilisateur,
                id_ingredient=ingredient["id_ingredient"],
            )

            if stock_item:
                # L'ingrédient existe dans le stock
                quantite_stock = float(stock_item["quantite"])
                id_unite_stock = stock_item["id_unite"]

                if id_unite_liste == id_unite_stock:
                    # Même unité → additionner
                    nouvelle_quantite = quantite_stock + quantite_liste

                    self.stock_dao.update_stock_quantity(
                        id_utilisateur=id_utilisateur,
                        id_ingredient=ingredient["id_ingredient"],
                        quantite=nouvelle_quantite,
                    )
                elif type_unite_liste == "liquide":
                    # Unités liquides différentes → convertir et additionner
                    # Utiliser la méthode du DAO au lieu d'une requête directe
                    stock_unite_info = self.stock_dao.get_unite_info(id_unite_stock)
                    code_unite_stock = stock_unite_info["abbreviation"] if stock_unite_info else None

                    if code_unite_stock:
                        ml_stock = UnitConverter.convert_to_ml(quantite_stock, code_unite_stock)
                        ml_liste = UnitConverter.convert_to_ml(quantite_liste, code_unite_liste)

                        if ml_stock and ml_liste:
                            total_ml = ml_stock + ml_liste
                            facteur = UnitConverter.LIQUID_TO_ML.get(code_unite_stock.lower(), 1)
                            nouvelle_quantite = total_ml / facteur

                            self.stock_dao.update_stock_quantity(
                                id_utilisateur=id_utilisateur,
                                id_ingredient=ingredient["id_ingredient"],
                                quantite=nouvelle_quantite,
                            )
                        else:
                            # Conversion impossible → additionner quand même
                            nouvelle_quantite = quantite_stock + quantite_liste
                            self.stock_dao.update_stock_quantity(
                                id_utilisateur=id_utilisateur,
                                id_ingredient=ingredient["id_ingredient"],
                                quantite=nouvelle_quantite,
                            )
                    else:
                        # Pas d'info sur l'unité → additionner quand même
                        nouvelle_quantite = quantite_stock + quantite_liste
                        self.stock_dao.update_stock_quantity(
                            id_utilisateur=id_utilisateur,
                            id_ingredient=ingredient["id_ingredient"],
                            quantite=nouvelle_quantite,
                        )
                else:
                    # Types différents → additionner quand même (warning implicite)
                    nouvelle_quantite = quantite_stock + quantite_liste
                    self.stock_dao.update_stock_quantity(
                        id_utilisateur=id_utilisateur,
                        id_ingredient=ingredient["id_ingredient"],
                        quantite=nouvelle_quantite,
                    )
            else:
                # L'ingrédient n'existe pas dans le stock → créer
                self.stock_dao.add_stock_item(
                    id_utilisateur=id_utilisateur,
                    id_ingredient=ingredient["id_ingredient"],
                    quantite=quantite_liste,
                    id_unite=id_unite_liste,
                )

            # Supprimer de la liste de course
            self.liste_course_dao.remove_from_liste_course(
                id_utilisateur=id_utilisateur,
                id_ingredient=ingredient["id_ingredient"],
            )

            return f"Ingrédient '{ingredient['nom']}' retiré de la liste de course et ajouté au stock ({quantite_liste})"

        except ServiceError:
            raise
        except Exception as e:
            raise ServiceError(f"Erreur lors du transfert vers le stock : {e}")

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
