"""doc."""

from src.business_object.cocktail import Cocktail
from src.dao.cocktail_utilisateur_dao import CocktailUtilisateurDao
from src.utils.log_decorator import log


class CocktailUtilisateurService:
    """Service pour gérer les cocktails testés d'un utilisateur."""

    def __init__(self):
        self.dao = CocktailUtilisateurDao()

    # ----------------- cocktails testés -----------------

    @log
    def get_cocktails_testes(self, id_utilisateur: int) -> list[Cocktail]:
        """Récupère tous les cocktails testés par un utilisateur."""
        return self.dao.get_teste(id_utilisateur)

    # Dans cocktail_utilisateur_service.py

    @log
    def ajouter_cocktail_teste(self, id_utilisateur: int, nom_cocktail: str) -> dict:
        """Ajoute un cocktail aux cocktails testés par son nom."""
        return self.dao.ajouter_cocktail_teste(id_utilisateur, nom_cocktail)

    @log
    def retirer_cocktail_teste(self, id_utilisateur: int, nom_cocktail: str) -> dict:
        """Retire un cocktail des cocktails testés par son nom."""
        return self.dao.retirer_cocktail_teste(id_utilisateur, nom_cocktail)

    # ----------- cocktails privés -----------

    '''@log
    def get_cocktails_prives(self, id_utilisateur: int) -> list[Cocktail]:
        """Récupère tous les cocktails privés d'un utilisateur."""
        return self.dao.get_prive(id_utilisateur)

    @log
    def creer_cocktail_prive(self, id_utilisateur: int, cocktail: Cocktail) -> int:
        """Crée un nouveau cocktail privé pour un utilisateur."""
        return self.dao.insert_cocktail_prive(id_utilisateur, cocktail)

    @log
    def get_ingredients_cocktail(self, id_cocktail: int) -> dict:
        """Récupère les ingrédients d'un cocktail."""
        return self.dao.get_cocktail_ingredient(id_cocktail)

    @log
    def modifier_quantite_ingredient(
        self,
        id_utilisateur: int,
        id_cocktail: int,
        id_ingredient: int,
        quantite: float,
    ) -> None:
        """Modifie la quantité d'un ingrédient dans un cocktail privé."""
        self.dao.update_cocktail_prive_modif_ingredient(
            id_utilisateur,
            id_cocktail,
            id_ingredient,
            quantite,
        )

    @log
    def ajouter_ingredient(
        self,
        id_utilisateur: int,
        id_cocktail: int,
        id_ingredient: int,
        quantite: float,
    ) -> None:
        """Ajoute un ingrédient à un cocktail privé."""
        self.dao.update_cocktail_prive_ajout_ingredient(
            id_utilisateur,
            id_cocktail,
            id_ingredient,
            quantite,
        )

    @log
    def supprimer_ingredient(
        self,
        id_utilisateur: int,
        id_cocktail: int,
        id_ingredient: int,
    ) -> None:
        """Supprime un ingrédient d'un cocktail privé."""
        self.dao.update_cocktail_prive_supprimer_ingredient(
            id_utilisateur,
            id_cocktail,
            id_ingredient,
            None,
        )

    @log
    def supprimer_cocktail_prive(self, id_utilisateur: int, id_cocktail: int) -> None:
        """Supprime un cocktail privé d'un utilisateur."""
        self.dao.delete_cocktail_prive(id_utilisateur, id_cocktail)'''


'''''from src.dao.cocktail_dao import CocktailDao
from src.dao.cocktail_utilisateur_dao import CocktailUtilisateurDao
from src.business_object.cocktail import cocktail
from src.business_object.utilisateur import utilisateur


class Cocktailutilisateurservice:
    """Service gérant les cocktails favoris, privés et testés des utilisateurs."""

    # -------------------- FAVORIS --------------------

    def ajouter_cocktail_favori(self, id_utilisateur: int, id_cocktail: int) -> bool:
        """Ajoute un cocktail (par son ID) aux favoris de l'utilisateur."""
        self._cocktails_favoris.setdefault(id_utilisateur, [])
        if id_cocktail not in self._cocktails_favoris[id_utilisateur]:
            self._cocktails_favoris[id_utilisateur].append(id_cocktail)
            return True
        return False

    def retirer_cocktail_favori(self, id_utilisateur: int, id_cocktail: int) -> bool:
        """Retire un cocktail (par son ID) des favoris de l'utilisateur."""
        if id_utilisateur in self._cocktails_favoris:
            if id_cocktail in self._cocktails_favoris[id_utilisateur]:
                self._cocktails_favoris[id_utilisateur].remove(id_cocktail)
                return True
        return False

    def lister_cocktails_favoris(self, id_utilisateur: int) -> list[int]:
        """Retourne la liste des IDs de cocktails favoris de l'utilisateur."""
        return self._cocktails_favoris.get(id_utilisateur, [])

        # -------------------- PRIVÉS --------------------

    def ajouter_cocktail_prive(self, id_utilisateur: int, id_cocktail: int) -> bool:
        """Ajoute un cocktail privé à un utilisateur."""
        self._cocktails_prives.setdefault(id_utilisateur, [])
        if id_cocktail not in self._cocktails_prives[id_utilisateur]:
            self._cocktails_prives[id_utilisateur].append(id_cocktail)
            return True
        return False

    def retirer_cocktail_prive(self, id_utilisateur: int, id_cocktail: int) -> bool:
        """Retire un cocktail privé d’un utilisateur."""
        if id_utilisateur in self.cocktails_prives:
            if id_cocktail in self.cocktails_prives[id_utilisateur]:
                self._cocktails_prives[id_utilisateur].remove(id_cocktail)
                return True
        return False

    def lister_cocktails_prives(self, id_utilisateur: int) -> list[int]:
        """Retourne la liste des IDs de cocktails privés d’un utilisateur."""
        return self._cocktails_prives.get(id_utilisateur, [])

        # -------------------- TESTÉS --------------------

    def ajouter_cocktail_teste(self, id_utilisateur: int, id_cocktail: int) -> bool:
        """Ajoute un cocktail testé à un utilisateur."""
        self._cocktails_testes.setdefault(id_utilisateur, [])
        if id_cocktail not in self._cocktails_testes[id_utilisateur]:
            self._cocktails_testes[id_utilisateur].append(id_cocktail)
            return True
        return False

    def retirer_cocktail_teste(self, id_utilisateur: int, id_cocktail: int) -> bool:
        """Retire un cocktail testé d’un utilisateur."""
        if id_utilisateur in self._cocktails_testes:
            if id_cocktail in self._cocktails_testes[id_utilisateur]:
                self._cocktails_testes[id_utilisateur].remove(id_cocktail)
                return True
        return False

    def lister_cocktails_testes(self, id_utilisateur: int) -> list[int]:
        """Retourne la liste des IDs de cocktails testés d’un utilisateur."""
        return self._cocktails_testes.get(id_utilisateur, [])''' ""
