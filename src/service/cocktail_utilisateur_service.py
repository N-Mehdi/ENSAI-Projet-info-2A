from src.dao.cocktail_dao import CocktailDao
from src.dao.cocktail_utilisateur_dao import CocktailUtilisateurDao
from src.business_object.cocktail import cocktail
from src.business_object.utilisateur import utilisateur


class cocktail_utilisateur_service:
   """Service gérant les cocktails favoris, privés et testés des utilisateurs."""

    def __init__(self):
        # Dictionnaires de stockage temporaire :
        # chaque utilisateur a une liste d'IDs de cocktails.
        self._cocktails_favoris = {}  # {id_utilisateur: [id_cocktail]}
        self._cocktails_prives = {}   # {id_utilisateur: [id_cocktail]}
        self._cocktails_testes = {}   # {id_utilisateur: [id_cocktail]}

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
        if id_utilisateur in self._cocktails_prives:
            if id_cocktail in self._cocktails_prives[id_utilisateur]:
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
        return self._cocktails_testes.get(id_utilisateur, [])