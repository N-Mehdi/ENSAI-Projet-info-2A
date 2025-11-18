"""doc."""

from src.business_object.cocktail import Cocktail
from src.dao.cocktail_dao import CocktailDAO
from src.dao.stock_course_dao import StockCourseDAO
from src.utils.conversion_unite import UnitConverter
from src.utils.exceptions import DAOError, EmptyFieldError, ServiceError


class CocktailService:
    """Service pour la logique cocktail."""

    def __init__(self, cocktail_dao: CocktailDAO) -> None:
        """Initialise un CocktailService."""
        self.cocktail_dao = cocktail_dao
        self.stock_dao = StockCourseDAO()

    def rechercher_cocktail_par_nom(self, nom: str) -> Cocktail:
        """Recherche un cocktail par son nom.

        Parameters
        ----------
        nom : str
            Nom du cocktail à rechercher.

        Raises
        ------
        TypeError
            Si le nom n'est pas une chaîne de caractères.
        ValueError
            Si le nom est vide ou None.
        LookupError
            Si aucun cocktail n'est trouvé pour le nom donné.

        Returns
        -------
        cocktail : Cocktail
            L'objet Cocktail correspondant au nom fourni.

        """
        if not nom:
            raise EmptyFieldError(nom)

        if not isinstance(nom, str):
            raise TypeError(message="Le nom du cocktail doit être une chaîne de caractères.")

        cocktail = self.cocktail_dao.rechercher_cocktail_par_nom(nom)

        if cocktail is None:
            raise LookupError(message=f"Aucun cocktail trouvé pour le nom '{nom}'")

        return cocktail

    def rechercher_cocktail_par_sequence_debut(
        self,
        sequence: str,
        max_resultats: int = 10,
    ) -> list:
        """Recherche les cocktails dont le nom commence par une séquence donnée.

        Parameters
        ----------
        sequence : str
            Sequence par laquelle commence le nom du cocktail.
        max_resultats : int
            Le nombre maximal de cocktails à retourner (triés par ordre alaphabétique)

        Raises
        ------
        TypeError
            Si séquence n'est pas une chaîne de caractères.
            Si max_resultats n'est pas un entier.
        ValueError
            Si la séquence est vide ou None.
            Si le nombre max_resultats n'est pas supérieur ou égal à 1.
        LookupError
            Si aucun cocktail n'est trouvé pour le nom donné.

        Returns
        -------
        cocktails : list[Cocktail]
            Liste de cocktails commençant par la séquence fournie.

        """
        if not sequence:
            raise EmptyFieldError(sequence)

        if not isinstance(sequence, str):
            raise TypeError(message="L'argument 'sequence' doit être une chaîne de caractères.")

        if not isinstance(max_resultats, int):
            raise TypeError(message="L'argument 'max_resultats' doit être un entier.")

        if max_resultats < 1:
            raise ValueError(message="L'argument 'max_resultats' doit être supérieur ou égal à 1.")

        cocktails = self.cocktail_dao.rechercher_cocktail_par_sequence_debut(
            sequence,
            max_resultats,
        )

        if not cocktails:
            raise LookupError(
                message=f"Aucun cocktail trouvé pour la séquence '{sequence}'",
            )

        return cocktails

    def get_cocktails_realisables(self, id_utilisateur: int) -> dict:
        """Récupère les cocktails réalisables avec le stock actuel.

        Compare le stock de l'utilisateur avec les ingrédients requis.
        Utilise UnitConverter pour normaliser les unités avant comparaison.

        Parameters
        ----------
        id_utilisateur : int
            ID de l'utilisateur

        Returns
        -------
        dict
            Format: {
                "cocktails_realisables": [...],
                "nombre_cocktails": int
            }

        Raises
        ------
        ServiceError
            En cas d'erreur de récupération

        """
        try:
            # Étape 1 : Récupérer le stock de l'utilisateur
            stock_rows = self.stock_dao.get_stock(id_utilisateur, only_available=True)

            # Étape 2 : Normaliser le stock (conversion en ml ou g)
            stock_normalise = {}
            for row in stock_rows:
                id_ingredient = row["id_ingredient"]
                quantite = float(row["quantite"])
                code_unite = row["code_unite"]

                if not code_unite:
                    # Pas d'unité définie, garder tel quel
                    stock_normalise[id_ingredient] = quantite
                    continue

                # Déterminer le type d'unité via UnitConverter
                if UnitConverter.is_liquid_unit(code_unite):
                    quantite_normalisee = UnitConverter.convert_to_ml(quantite, code_unite)
                elif UnitConverter.is_solid_unit(code_unite):
                    quantite_normalisee = UnitConverter.convert_to_g(quantite, code_unite)
                else:
                    # Unité spéciale ou inconnue
                    quantite_normalisee = quantite

                if quantite_normalisee is not None:
                    stock_normalise[id_ingredient] = quantite_normalisee

            # Étape 3 : Récupérer tous les cocktails avec leurs ingrédients
            cocktails_rows = self.cocktail_dao.get_tous_cocktails_avec_ingredients()

            # Étape 4 : Grouper par cocktail et vérifier la disponibilité
            cocktails_dict = {}
            for row in cocktails_rows:
                id_cocktail = row["id_cocktail"]

                # Initialiser le cocktail s'il n'existe pas encore
                if id_cocktail not in cocktails_dict:
                    cocktails_dict[id_cocktail] = {
                        "info": {
                            "id_cocktail": id_cocktail,
                            "nom": row["nom"],
                            "categorie": row["categorie"],
                            "verre": row["verre"],
                            "alcool": row["alcool"],
                            "image": row["image"],
                        },
                        "realisable": True,
                    }

                # Si le cocktail a des ingrédients requis
                if row["id_ingredient"]:
                    id_ingredient = row["id_ingredient"]
                    qte_requise = float(row["qte"]) if row["qte"] else 0
                    unite_requise = row["unite"]

                    # Convertir la quantité requise
                    if unite_requise:
                        if UnitConverter.is_liquid_unit(unite_requise):
                            qte_requise_normalisee = UnitConverter.convert_to_ml(qte_requise, unite_requise)
                        elif UnitConverter.is_solid_unit(unite_requise):
                            qte_requise_normalisee = UnitConverter.convert_to_g(qte_requise, unite_requise)
                        else:
                            # Unité spéciale
                            qte_requise_normalisee = qte_requise
                    else:
                        qte_requise_normalisee = qte_requise

                    # Vérifier la disponibilité dans le stock
                    if id_ingredient not in stock_normalise:
                        # Ingrédient manquant dans le stock
                        cocktails_dict[id_cocktail]["realisable"] = False
                        # Vérifier la quantité
                    if stock_normalise[id_ingredient] < qte_requise_normalisee and qte_requise_normalisee is not None:
                        cocktails_dict[id_cocktail]["realisable"] = False

            # Étape 5 : Filtrer et formater les cocktails réalisables
            cocktails_realisables = [data["info"] for data in cocktails_dict.values() if data["realisable"]]

            return {
                "cocktails_realisables": cocktails_realisables,
                "nombre_cocktails": len(cocktails_realisables),
            }

        except DAOError as e:
            raise ServiceError(message=f"Erreur lors de la récupération des cocktails réalisables : {e}") from e
        except Exception as e:
            raise ServiceError(message=f"Erreur inattendue : {e}") from e

    def get_cocktails_quasi_realisables(
        self,
        id_utilisateur: int,
        max_ingredients_manquants: int = 3,
    ) -> dict:
        """Récupère les cocktails réalisables avec peu d'ingrédients manquants.

        Utilise UnitConverter pour gérer les conversions d'unités côté Python.

        Parameters
        ----------
        id_utilisateur : int
            ID de l'utilisateur
        max_ingredients_manquants : int
            Nombre maximum d'ingrédients manquants (défaut: 3)

        Returns
        -------
        dict
            Format: {
                "cocktails_quasi_realisables": [...],
                "nombre_cocktails": int,
                "max_ingredients_manquants": int
            }

        Raises
        ------
        ServiceError
            En cas d'erreur de récupération

        """
        try:
            rows = self.cocktail_dao.get_cocktails_quasi_realisables(id_utilisateur)
            cocktails_dict = self._build_cocktails_dict(rows)
            cocktails_quasi_realisables = self._filter_and_format_cocktails(
                cocktails_dict,
                max_ingredients_manquants,
            )

            return {
                "cocktails_quasi_realisables": cocktails_quasi_realisables,
                "nombre_cocktails": len(cocktails_quasi_realisables),
                "max_ingredients_manquants": max_ingredients_manquants,
            }

        except DAOError as e:
            raise ServiceError(message=f"Erreur lors de la récupération des cocktails quasi-réalisables : {e}") from e
        except Exception as e:
            raise ServiceError(message=f"Erreur inattendue : {e}") from e

    def _build_cocktails_dict(self, rows: list[dict]) -> dict:
        """Construit le dictionnaire des cocktails avec leurs ingrédients."""
        cocktails_dict = {}

        for row in rows:
            id_cocktail = row["id_cocktail"]

            # Initialiser le cocktail
            if id_cocktail not in cocktails_dict:
                cocktails_dict[id_cocktail] = {
                    "info": {
                        "id_cocktail": id_cocktail,
                        "nom": row["nom"],
                        "categorie": row["categorie"],
                        "verre": row["verre"],
                        "alcool": row["alcool"],
                        "image": row["image"],
                    },
                    "ingredients_manquants": [],
                    "total_ingredients": 0,
                }

            # Traiter l'ingrédient
            if row["id_ingredient"]:
                cocktails_dict[id_cocktail]["total_ingredients"] += 1

                if not self._is_ingredient_available(row):
                    cocktails_dict[id_cocktail]["ingredients_manquants"].append(row["nom_ingredient"])

        return cocktails_dict

    def _is_ingredient_available(self, row: dict) -> bool:
        """Vérifie si un ingrédient est disponible en quantité suffisante."""
        quantite_requise = float(row["quantite_requise"]) if row["quantite_requise"] else 0
        unite_requise = row["unite_requise"]
        quantite_stock = float(row["quantite_stock"]) if row["quantite_stock"] else None
        unite_stock = row["unite_stock"]

        # Pas de stock
        if quantite_stock is None:
            return False

        # Pas d'unité définie
        if not unite_requise or not unite_stock:
            return quantite_stock >= quantite_requise

        # Normaliser les unités
        unite_requise_norm = UnitConverter.normalize_unit(unite_requise)
        unite_stock_norm = UnitConverter.normalize_unit(unite_stock)

        # Même unité
        if unite_requise_norm == unite_stock_norm:
            return quantite_stock >= quantite_requise

        # Unités liquides
        if UnitConverter.is_liquid_unit(unite_requise) and UnitConverter.is_liquid_unit(unite_stock):
            return self._compare_liquid_quantities(quantite_requise, unite_requise, quantite_stock, unite_stock)

        # Unités solides
        if UnitConverter.is_solid_unit(unite_requise) and UnitConverter.is_solid_unit(unite_stock):
            return self._compare_solid_quantities(quantite_requise, unite_requise, quantite_stock, unite_stock)

        # Types incompatibles
        return False

    def _compare_liquid_quantities(
        self,
        quantite_requise: float,
        unite_requise: str,
        quantite_stock: float,
        unite_stock: str,
    ) -> bool:
        """Compare deux quantités de liquides en les convertissant en ml."""
        ml_requis = UnitConverter.convert_to_ml(quantite_requise, unite_requise)
        ml_stock = UnitConverter.convert_to_ml(quantite_stock, unite_stock)

        if ml_requis is not None and ml_stock is not None:
            return ml_stock >= ml_requis

        return False

    def _compare_solid_quantities(
        self,
        quantite_requise: float,
        unite_requise: str,
        quantite_stock: float,
        unite_stock: str,
    ) -> bool:
        """Compare deux quantités de solides en les convertissant en g."""
        g_requis = UnitConverter.convert_to_g(quantite_requise, unite_requise)
        g_stock = UnitConverter.convert_to_g(quantite_stock, unite_stock)

        if g_requis is not None and g_stock is not None:
            return g_stock >= g_requis

        return False

    def _filter_and_format_cocktails(
        self,
        cocktails_dict: dict,
        max_ingredients_manquants: int,
    ) -> list[dict]:
        """Filtre et formate les cocktails selon le nombre d'ingrédients manquants."""
        cocktails_quasi_realisables = []

        for data in cocktails_dict.values():
            nb_manquants = len(data["ingredients_manquants"])
            nb_total = data["total_ingredients"]

            # Filtrer selon le nombre d'ingrédients manquants
            if 0 < nb_manquants <= max_ingredients_manquants and nb_total > 0:
                pourcentage = round(100.0 * (nb_total - nb_manquants) / nb_total, 2)

                cocktails_quasi_realisables.append(
                    {
                        **data["info"],
                        "ingredients_manquants": data["ingredients_manquants"],
                        "nombre_ingredients_manquants": nb_manquants,
                        "nombre_ingredients_total": nb_total,
                        "pourcentage_possession": pourcentage,
                    },
                )

        # Trier
        cocktails_quasi_realisables.sort(
            key=lambda x: (
                x["nombre_ingredients_manquants"],
                -x["pourcentage_possession"],
                x["nom"],
            ),
        )

        return cocktails_quasi_realisables
