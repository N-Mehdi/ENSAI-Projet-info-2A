"""Couche service pour les opérations sur les cocktails."""

from src.business_object.cocktail import Cocktail
from src.dao.cocktail_dao import CocktailDAO
from src.dao.instruction_dao import InstructionDAO
from src.dao.stock_dao import StockDAO
from src.utils.conversion_unite import UnitConverter
from src.utils.exceptions import (
    CocktailSearchError,
    DAOError,
    EmptyFieldError,
    ServiceError,
)


class CocktailService:
    """Service pour la logique cocktail."""

    def __init__(self, cocktail_dao: CocktailDAO) -> None:
        """Initialise un CocktailService."""
        self.cocktail_dao = cocktail_dao
        self.stock_dao = StockDAO()
        self.instruction_dao = InstructionDAO()

    def rechercher_cocktail_par_nom(self, nom: str) -> Cocktail:
        """Recherche un cocktail par son nom.

        Parameters
        ----------
        nom : str
            Nom du cocktail à rechercher.

        Raises
        ------
        CocktailSearchError
            Si le nom n'est pas une chaîne de caractères.
        CocktailSearchError
            Si le nom est vide ou None.
        CocktailSearchError
            Si aucun cocktail n'est trouvé pour le nom donné.

        Returns
        -------
        cocktail : Cocktail
            L'objet Cocktail correspondant au nom fourni.

        """
        if not nom:
            raise EmptyFieldError(nom)

        if not isinstance(nom, str):
            raise CocktailSearchError(
                message="Le nom du cocktail doit être une chaîne de caractères.",
            )

        cocktail = self.cocktail_dao.rechercher_cocktail_par_nom(nom)

        if cocktail is None:
            raise CocktailSearchError(
                message=f"Aucun cocktail trouvé pour le nom '{nom}'",
            )
        instructions = self.instruction_dao.get_instruction(cocktail.id_cocktail)

        return cocktail, instructions

    def rechercher_cocktail_par_sequence_debut(
        self,
        sequence: str,
        max_resultats: int = 10,
    ) -> list[tuple[Cocktail, str | None]]:
        """Recherche les cocktails dont le nom commence par une séquence donnée.

        Parameters
        ----------
        sequence : str
            Sequence par laquelle commence le nom du cocktail.
        max_resultats : int
            Le nombre maximal de cocktails à retourner (triés par ordre alaphabétique)

        Raises
        ------
        CocktailSearchError
            Si séquence n'est pas une chaîne de caractères.
            Si max_resultats n'est pas un entier.
        CocktailSearchError
            Si la séquence est vide ou None.
            Si le nombre max_resultats n'est pas supérieur ou égal à 1.
        CocktailSearchError
            Si aucun cocktail n'est trouvé pour le nom donné.

        Returns
        -------
        cocktails : list[Cocktail]
            Liste de cocktails commençant par la séquence fournie.

        """
        if not sequence:
            raise EmptyFieldError(sequence)

        if not isinstance(sequence, str):
            raise CocktailSearchError(
                message="L'argument 'sequence' doit être une chaîne de caractères.",
            )

        if not isinstance(max_resultats, int):
            raise CocktailSearchError(
                message="L'argument 'max_resultats' doit être un entier.",
            )

        if max_resultats < 1:
            raise CocktailSearchError(
                message="L'argument 'max_resultats' doit être supérieur ou égal à 1.",
            )

        cocktails = self.cocktail_dao.rechercher_cocktail_par_sequence_debut(
            sequence,
            max_resultats,
        )

        if not cocktails:
            raise CocktailSearchError(
                message=f"Aucun cocktail trouvé pour la séquence '{sequence}'",
            )

        cocktails_avec_instructions = []
        for cocktail in cocktails:
            instructions = self.instruction_dao.get_instruction(cocktail.id_cocktail)
            cocktails_avec_instructions.append((cocktail, instructions))

        return cocktails_avec_instructions

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
            stock_normalise = self._normaliser_stock(id_utilisateur)
            cocktails_dict = self._construire_cocktails_avec_disponibilite(
                stock_normalise,
            )
            cocktails_realisables = self._filtrer_cocktails_realisables(cocktails_dict)

            return {
                "cocktails_realisables": cocktails_realisables,
                "nombre_cocktails": len(cocktails_realisables),
            }

        except DAOError as e:
            raise ServiceError(
                message=f"Erreur lors de la récupération des cocktails "
                f"réalisables : {e}",
            ) from e
        except Exception as e:
            raise ServiceError(message=f"Erreur inattendue : {e}") from e

    def _normaliser_stock(self, id_utilisateur: int) -> dict[int, float]:
        """Normalise le stock de l'utilisateur en convertissant les unités.

        Parameters
        ----------
        id_utilisateur : int
            ID de l'utilisateur

        Returns
        -------
        dict[int, float]
            Dictionnaire {id_ingredient: quantite_normalisee}

        """
        stock_rows = self.stock_dao.get_stock(id_utilisateur, only_available=True)
        stock_normalise = {}

        for row in stock_rows:
            id_ingredient = row["id_ingredient"]
            quantite = float(row["quantite"])
            code_unite = row["code_unite"]

            quantite_normalisee = self._convertir_quantite(quantite, code_unite)
            if quantite_normalisee is not None:
                stock_normalise[id_ingredient] = quantite_normalisee

        return stock_normalise

    @staticmethod
    def _convertir_quantite(quantite: float, unite: str | None) -> float | None:
        """Convertit une quantité vers son unité normalisée (ml ou g).

        Parameters
        ----------
        quantite : float
            Quantité à convertir
        unite : str | None
            Unité de la quantité

        Returns
        -------
        float | None
            Quantité convertie ou None si conversion impossible

        """
        if not unite:
            return quantite

        if UnitConverter.is_liquid_unit(unite):
            return UnitConverter.convert_to_ml(quantite, unite)

        if UnitConverter.is_solid_unit(unite):
            return UnitConverter.convert_to_g(quantite, unite)

        # Unité spéciale ou inconnue
        return quantite

    def _construire_cocktails_avec_disponibilite(
        self,
        stock_normalise: dict[int, float],
    ) -> dict:
        """Construit un dictionnaire des cocktails avec leur disponibilité.

        Parameters
        ----------
        stock_normalise : dict[int, float]
            Stock normalisé de l'utilisateur

        Returns
        -------
        dict
            Dictionnaire des cocktails avec leurs informations et disponibilité

        """
        cocktails_rows = self.cocktail_dao.get_tous_cocktails_avec_ingredients()
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

            # Vérifier la disponibilité de l'ingrédient
            if row["id_ingredient"]:
                est_disponible = self._verifier_ingredient_disponible(
                    row,
                    stock_normalise,
                )
                if not est_disponible:
                    cocktails_dict[id_cocktail]["realisable"] = False

        return cocktails_dict

    def _verifier_ingredient_disponible(
        self,
        row: dict,
        stock_normalise: dict[int, float],
    ) -> bool:
        """Vérifie si un ingrédient est disponible en quantité suffisante.

        Parameters
        ----------
        row : dict
            Ligne contenant les informations de l'ingrédient requis
        stock_normalise : dict[int, float]
            Stock normalisé de l'utilisateur

        Returns
        -------
        bool
            True si l'ingrédient est disponible, False sinon

        """
        id_ingredient = row["id_ingredient"]
        qte_requise = float(row["qte"]) if row["qte"] else 0
        unite_requise = row["unite"]

        # Convertir la quantité requise
        qte_requise_normalisee = self._convertir_quantite(qte_requise, unite_requise)

        # Vérifier la disponibilité dans le stock
        if id_ingredient not in stock_normalise:
            return False

        if qte_requise_normalisee is None:
            return True

        return stock_normalise[id_ingredient] >= qte_requise_normalisee

    @staticmethod
    def _filtrer_cocktails_realisables(cocktails_dict: dict) -> list[dict]:
        """Filtre et retourne uniquement les cocktails réalisables.

        Parameters
        ----------
        cocktails_dict : dict
            Dictionnaire des cocktails avec leur disponibilité

        Returns
        -------
        list[dict]
            Liste des cocktails réalisables

        """
        return [data["info"] for data in cocktails_dict.values() if data["realisable"]]

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
            cocktails_dict = self.build_cocktails_dict(rows)
            cocktails_quasi_realisables = self.filter_and_format_cocktails(
                cocktails_dict,
                max_ingredients_manquants,
            )

            return {
                "cocktails_quasi_realisables": cocktails_quasi_realisables,
                "nombre_cocktails": len(cocktails_quasi_realisables),
                "max_ingredients_manquants": max_ingredients_manquants,
            }

        except DAOError as e:
            raise ServiceError(
                message=(
                    f"Erreur lors de la récupération des cocktails quasi-réalisables :"
                    f"{e}",
                ),
            ) from e
        except Exception as e:
            raise ServiceError(message=f"Erreur inattendue : {e}") from e

    def build_cocktails_dict(self, rows: list[dict]) -> dict:
        """Construit le dictionnaire des cocktails avec leurs ingrédients.

        Pour chaque cocktail, initialise sa structure avec les informations de base
        et compte les ingrédients manquants en vérifiant la disponibilité en stock.

        Parameters
        ----------
        rows : list[dict]
            Liste des lignes de résultats de la base de données contenant
            les cocktails et leurs ingrédients

        Returns
        -------
        dict
            Dictionnaire avec id_cocktail comme clé et pour chaque cocktail :
            - info : dict avec id_cocktail, nom, categorie, verre, alcool, image
            - ingredients_manquants : list[str] des noms d'ingrédients manquants
            - total_ingredients : int nombre total d'ingrédients du cocktail

        """
        cocktails_dict = {}

        for row in rows:
            id_cocktail = row["id_cocktail"]

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

            if row["id_ingredient"]:
                cocktails_dict[id_cocktail]["total_ingredients"] += 1

                if not self.is_ingredient_available(row):
                    cocktails_dict[id_cocktail]["ingredients_manquants"].append(
                        row["nom_ingredient"],
                    )

        return cocktails_dict

    def is_ingredient_available(self, row: dict) -> bool:
        """Vérifie si un ingrédient est disponible en quantité suffisante dans le stock.

        Compare la quantité requise avec la quantité en stock en gérant les
        conversions d'unités pour les liquides (ml) et solides (g).

        Parameters
        ----------
        row : dict
            Ligne contenant les informations de l'ingrédient :
            quantite_requise, unite_requise, quantite_stock, unite_stock, nom_ingredient

        Returns
        -------
        bool
            True si l'ingrédient est disponible en quantité suffisante, False sinon

        """
        quantite_requise = (
            float(row["quantite_requise"]) if row["quantite_requise"] else 0
        )
        unite_requise = row["unite_requise"]
        quantite_stock = float(row["quantite_stock"]) if row["quantite_stock"] else None
        unite_stock = row["unite_stock"]

        if quantite_stock is None:
            return False

        if not unite_requise or not unite_stock:
            return quantite_stock >= quantite_requise

        # Normaliser les unités
        unite_requise_norm = UnitConverter.normalize_unit(unite_requise)
        unite_stock_norm = UnitConverter.normalize_unit(unite_stock)

        if unite_requise_norm == unite_stock_norm:
            return quantite_stock >= quantite_requise

        # Unités liquides
        if UnitConverter.is_liquid_unit(unite_requise) and UnitConverter.is_liquid_unit(
            unite_stock,
        ):
            return self.compare_liquid_quantities(
                quantite_requise,
                unite_requise,
                quantite_stock,
                unite_stock,
            )

        # Unités solides
        if UnitConverter.is_solid_unit(unite_requise) and UnitConverter.is_solid_unit(
            unite_stock,
        ):
            return self.compare_solid_quantities(
                quantite_requise,
                unite_requise,
                quantite_stock,
                unite_stock,
            )

        # Types incompatibles
        return False

    @staticmethod
    def compare_liquid_quantities(
        quantite_requise: float,
        unite_requise: str,
        quantite_stock: float,
        unite_stock: str,
    ) -> bool:
        """Compare deux quantités de liquides en les convertissant en ml.

        Parameters
        ----------
        quantite_requise : float
            La quantité requise
        unite_requise : str
            L'unité de la quantité requise
        quantite_stock : float
            La quantité en stock
        unite_stock : str
            L'unité de la quantité en stock

        Returns
        -------
        bool
            True si le stock est suffisant (ml_stock >= ml_requis), False sinon

        """
        ml_requis = UnitConverter.convert_to_ml(quantite_requise, unite_requise)
        ml_stock = UnitConverter.convert_to_ml(quantite_stock, unite_stock)

        if ml_requis is not None and ml_stock is not None:
            return ml_stock >= ml_requis

        return False

    @staticmethod
    def compare_solid_quantities(
        quantite_requise: float,
        unite_requise: str,
        quantite_stock: float,
        unite_stock: str,
    ) -> bool:
        """Compare deux quantités de solides en les convertissant en grammes.

        Parameters
        ----------
        quantite_requise : float
            La quantité requise
        unite_requise : str
            L'unité de la quantité requise
        quantite_stock : float
            La quantité en stock
        unite_stock : str
            L'unité de la quantité en stock

        Returns
        -------
        bool
            True si le stock est suffisant (g_stock >= g_requis), False sinon

        """
        g_requis = UnitConverter.convert_to_g(quantite_requise, unite_requise)
        g_stock = UnitConverter.convert_to_g(quantite_stock, unite_stock)

        if g_requis is not None and g_stock is not None:
            return g_stock >= g_requis

        return False

    @staticmethod
    def filter_and_format_cocktails(
        cocktails_dict: dict,
        max_ingredients_manquants: int,
    ) -> list[dict]:
        """Filtre et formate les cocktails selon le nombre d'ingrédients manquants.

        Sélectionne les cocktails ayant entre 1 et max_ingredients_manquants ingrédients
        manquants, calcule le pourcentage de possession et trie les résultats.

        Parameters
        ----------
        cocktails_dict : dict
            Dictionnaire des cocktails construit par _build_cocktails_dict
        max_ingredients_manquants : int
            Nombre maximum d'ingrédients manquants autorisés

        Returns
        -------
        list[dict]
            Liste des cocktails quasi-réalisables, triée par :
            1. Nombre d'ingrédients manquants (croissant)
            2. Pourcentage de possession (décroissant)
            3. Nom (alphabétique)
            Chaque dictionnaire contient : toutes les infos du cocktail,
            ingredients_manquants, nombre_ingredients_manquants,
            nombre_ingredients_total, pourcentage_possession

        """
        cocktails_quasi_realisables = []

        for data in cocktails_dict.values():
            nb_manquants = len(data["ingredients_manquants"])
            nb_total = data["total_ingredients"]

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

        cocktails_quasi_realisables.sort(
            key=lambda x: (
                x["nombre_ingredients_manquants"],
                -x["pourcentage_possession"],
                x["nom"],
            ),
        )

        return cocktails_quasi_realisables

    def get_instruction(self, nom_cocktail: str) -> str | None:
        """Récupère les instructions de préparation d'un cocktail."""
        id_cocktail = self.cocktail_dao.get_cocktail_id_by_name(nom_cocktail)
        if id_cocktail is None:
            return None
        return self.instruction_dao.get_instruction(id_cocktail)

    def ajouter_cocktail_complet(
        self,
        cocktail: Cocktail,
        instructions: str | None = None,
        langue: str = "en",
    ) -> int:
        """Ajoute un cocktail avec ses instructions dans la base de données.

        Cette méthode effectue une transaction complète :
        1. Ajoute le cocktail
        2. Si des instructions sont fournies, les ajoute

        Parameters
        ----------
        cocktail : Cocktail
            L'objet Cocktail à ajouter
        instructions : str | None, optional
            Le texte des instructions (par défaut: None)
        langue : str, optional
            La langue des instructions (par défaut: "en")

        Returns
        -------
        int
            L'identifiant du cocktail créé

        Raises
        ------
        CocktailServiceError
            En cas d'erreur lors de l'ajout du cocktail ou des instructions

        Examples
        --------
        >>> service = CocktailService()
        >>> cocktail = Cocktail(
        ...     id_cocktail=None,
        ...     nom="Mojito Maison",
        ...     categorie="Cocktail",
        ...     verre="Highball glass",
        ...     alcool=True,
        ...     image="mojito.jpg"
        ... )
        >>> instructions = "Muddle mint leaves with sugar and lime juice..."
        >>> id_cocktail = service.ajouter_cocktail_complet(cocktail, instructions)

        """
        try:
            # 1. Ajouter le cocktail
            id_cocktail = self.cocktail_dao.ajouter_cocktail(cocktail)

            # 2. Ajouter les instructions si fournies

        except Exception as e:
            raise DAOError(
                message=f"Erreur lors de l'ajout du cocktail complet : {e}",
            ) from e

        if instructions:
            self.instruction_dao.ajouter_instruction(
                id_cocktail=id_cocktail,
                texte=instructions,
                langue=langue,
            )

        return id_cocktail

    def ajouter_cocktail(self, cocktail: Cocktail) -> int:
        """Ajoute uniquement un cocktail sans instructions.

        Parameters
        ----------
        cocktail : Cocktail
            L'objet Cocktail à ajouter

        Returns
        -------
        int
            L'identifiant du cocktail créé

        Raises
        ------
        CocktailServiceError
            En cas d'erreur lors de l'ajout du cocktail

        """
        try:
            return self.cocktail_dao.ajouter_cocktail(cocktail)
        except Exception as e:
            raise DAOError(
                message=f"Erreur lors de l'ajout du cocktail : {e}",
            ) from e

    def ajouter_instruction(
        self,
        id_cocktail: int,
        texte: str,
        langue: str = "en",
    ) -> bool:
        """Ajoute une instruction pour un cocktail existant.

        Parameters
        ----------
        id_cocktail : int
            L'identifiant du cocktail
        texte : str
            Le texte de l'instruction
        langue : str, optional
            La langue de l'instruction (par défaut: "en")

        Returns
        -------
        bool
            True si l'ajout a réussi

        Raises
        ------
        CocktailServiceError
            En cas d'erreur lors de l'ajout de l'instruction

        """
        try:
            return self.instruction_dao.ajouter_instruction(
                id_cocktail=id_cocktail,
                texte=texte,
                langue=langue,
            )
        except Exception as e:
            raise DAOError(
                message=f"Erreur lors de l'ajout de l'instruction : {e}",
            ) from e
