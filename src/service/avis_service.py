"""Couche service pour les opérations sur les avis."""

from src.dao.avis_dao import AvisDAO
from src.dao.cocktail_dao import CocktailDAO
from src.models.avis import AvisResponse, AvisSummary
from src.utils.exceptions import (
    AvisNotFoundError,
    CocktailNotFoundError,
    InvalidAvisError,
    ServiceError,
)
from src.utils.text_utils import normalize_ingredient_name


class AvisService:
    """Service pour gérer les avis sur les cocktails."""

    def __init__(self) -> None:
        """Initialise un AvisService."""
        self.avis_dao = AvisDAO()
        self.cocktail_dao = CocktailDAO()

    def _get_cocktail_by_name(self, nom_cocktail: str) -> dict:
        """Récupère un cocktail par son nom.

        Parameters
        ----------
        nom_cocktail : str
            Nom du cocktail (sera normalisé en Title Case)

        Returns
        -------
        dict
            Dictionnaire avec les infos du cocktail

        Raises
        ------
        IngredientNotFoundError
            Si le cocktail n'existe pas (avec suggestions)

        """
        # Normaliser le nom
        nom_normalized = normalize_ingredient_name(nom_cocktail)

        cocktail = self.cocktail_dao.rechercher_cocktail_par_nom(nom_normalized)

        if not cocktail:
            # Chercher des suggestions avec la méthode par séquence
            suggestions_cocktails = self.cocktail_dao.rechercher_cocktail_par_sequence_debut(
                sequence=nom_normalized[:3],  # Premiers caractères
                max_resultats=5,
            )
            suggestions = [c.nom for c in suggestions_cocktails]

            raise CocktailNotFoundError(nom_normalized, suggestions)

        return {
            "id_cocktail": cocktail.id_cocktail,
            "nom": cocktail.nom,
            "categorie": cocktail.categorie,
            "verre": cocktail.verre,
            "alcool": cocktail.alcool,
            "image": cocktail.image,
        }

    def create_or_update_avis(
        self,
        id_utilisateur: int,
        nom_cocktail: str,
        note: int | None,
        commentaire: str | None,
    ) -> str:
        """Crée ou met à jour un avis.

        Parameters
        ----------
        id_utilisateur : int
            ID de l'utilisateur
        nom_cocktail : str
            Nom du cocktail
        note : int | None
            Note entre 0 et 10
        commentaire : str | None
            Commentaire

        Returns
        -------
        str
            Message de confirmation

        """
        # Validation : au moins note OU commentaire
        if note is None and commentaire is None:
            raise InvalidAvisError

        cocktail = self._get_cocktail_by_name(nom_cocktail)

        try:
            # Créer ou mettre à jour
            self.avis_dao.create_or_update_avis(
                id_utilisateur=id_utilisateur,
                id_cocktail=cocktail["id_cocktail"],
                note=note,
                commentaire=commentaire,
            )

            return f"Avis ajouté/modifié avec succès pour '{cocktail['nom']}'"

        except Exception as e:
            raise ServiceError from e

    def get_avis_cocktail(self, nom_cocktail: str) -> list[AvisResponse]:
        """Récupère tous les avis d'un cocktail par son nom.

        Parameters
        ----------
        nom_cocktail : str
            Le nom du cocktail

        Returns
        -------
        list[AvisResponse]
            Liste des avis du cocktail, triés par date de création décroissante

        Raises
        ------
        CocktailNotFoundError
            Si le cocktail n'existe pas
        ServiceError
            En cas d'erreur lors de la récupération des avis

        """
        cocktail = self._get_cocktail_by_name(nom_cocktail)

        try:
            rows = self.avis_dao.get_avis_by_cocktail(cocktail["id_cocktail"])

            return [
                AvisResponse(
                    id_utilisateur=row["id_utilisateur"],
                    pseudo_utilisateur=row["pseudo_utilisateur"],
                    id_cocktail=row["id_cocktail"],
                    nom_cocktail=row["nom_cocktail"],
                    note=row["note"],
                    commentaire=row["commentaire"],
                    favoris=row["favoris"],
                    date_creation=row["date_creation"],
                    date_modification=row["date_modification"],
                )
                for row in rows
            ]
        except Exception as e:
            raise ServiceError(message=f"Erreur lors de la récupération des avis : {e}") from e

    def get_mes_avis_simple(self, id_utilisateur: int, pseudo: str) -> dict:
        """Récupère tous les avis d'un utilisateur (format simplifié).

        Parameters
        ----------
        id_utilisateur : int
            ID de l'utilisateur
        pseudo : str
            Pseudo de l'utilisateur (depuis le token)

        Returns
        -------
        dict
            Format : {"pseudo_utilisateur": "...", "avis": [...]}

        """
        try:
            rows = self.avis_dao.get_avis_by_user(id_utilisateur)
        except Exception as e:
            raise ServiceError(message=f"Erreur lors de la récupération des avis : {e}") from e

            avis = [
                {
                    "nom_cocktail": row["nom_cocktail"],
                    "note": row["note"],
                    "commentaire": row["commentaire"],
                }
                for row in rows
            ]

            return {
                "pseudo_utilisateur": pseudo,
                "avis": avis,
            }

    def delete_avis(self, id_utilisateur: int, nom_cocktail: str) -> str:
        """Supprime l'avis d'un utilisateur sur un cocktail.

        Parameters
        ----------
        id_utilisateur : int
            L'identifiant de l'utilisateur
        nom_cocktail : str
            Le nom du cocktail

        Returns
        -------
        str
            Message de confirmation de la suppression

        Raises
        ------
        CocktailNotFoundError
            Si le cocktail n'existe pas
        AvisNotFoundError
            Si l'avis n'existe pas

        """
        cocktail = self._get_cocktail_by_name(nom_cocktail)

        try:
            success = self.avis_dao.delete_avis(
                id_utilisateur=id_utilisateur,
                id_cocktail=cocktail["id_cocktail"],
            )

        except Exception as e:
            raise AvisNotFoundError(id_utilisateur=id_utilisateur, nom_cocktail=nom_cocktail) from e
        if not success:
            raise AvisNotFoundError(id_utilisateur, cocktail["nom"])

        return f"Avis supprimé avec succès pour '{cocktail['nom']}'"

    def add_favoris(self, id_utilisateur: int, nom_cocktail: str) -> dict:
        """Ajoute un cocktail aux favoris.

        Parameters
        ----------
        id_utilisateur : int
            ID de l'utilisateur
        nom_cocktail : str
            Nom du cocktail

        Returns
        -------
        dict
            Message de confirmation avec statut

        """
        cocktail = self._get_cocktail_by_name(nom_cocktail)

        try:
            result = self.avis_dao.add_favoris(
                id_utilisateur=id_utilisateur,
                id_cocktail=cocktail["id_cocktail"],
            )

            if result["deja_en_favoris"]:
                message = f"Cocktail '{cocktail['nom']}' est déjà dans vos favoris"
            else:
                message = f"Cocktail '{cocktail['nom']}' ajouté aux favoris"

            return {
                "favoris": True,
                "deja_en_favoris": result["deja_en_favoris"],
                "message": message,
            }

        except Exception as e:
            raise ServiceError(message=f"Erreur lors de l'ajout aux favoris : {e}") from e

    def remove_favoris(self, id_utilisateur: int, nom_cocktail: str) -> str:
        """Retire un cocktail des favoris d'un utilisateur.

        Parameters
        ----------
        id_utilisateur : int
            L'identifiant de l'utilisateur
        nom_cocktail : str
            Le nom du cocktail

        Returns
        -------
        str
            Message de confirmation du retrait des favoris

        Raises
        ------
        CocktailNotFoundError
            Si le cocktail n'existe pas
        AvisNotFoundError
            Si le cocktail n'était pas en favoris
        ServiceError
            En cas d'erreur lors du retrait des favoris

        """
        cocktail = self._get_cocktail_by_name(nom_cocktail)

        try:
            success = self.avis_dao.remove_favoris(
                id_utilisateur=id_utilisateur,
                id_cocktail=cocktail["id_cocktail"],
            )

        except AvisNotFoundError:
            raise
        except Exception as e:
            raise ServiceError(message=f"Erreur lors du retrait des favoris : {e}") from e
        if not success:
            raise AvisNotFoundError(id_utilisateur, cocktail["nom"])

        return f"Cocktail '{cocktail['nom']}' retiré des favoris"

    def get_mes_favoris_simple(self, id_utilisateur: int, pseudo: str) -> dict:
        """Récupère les cocktails favoris d'un utilisateur (format simplifié).

        Parameters
        ----------
        id_utilisateur : int
            ID de l'utilisateur
        pseudo : str
            Pseudo de l'utilisateur (depuis le token)

        Returns
        -------
        dict
            Format : {"pseudo_utilisateur": "...", "cocktails_favoris": [...]}

        """
        try:
            rows = self.avis_dao.get_favoris_by_user(id_utilisateur)

            # Extraire uniquement les noms des cocktails
            cocktails_favoris = [row["nom_cocktail"] for row in rows]

        except Exception as e:
            raise ServiceError(message=f"Erreur lors de la récupération des favoris : {e}") from e
        return {
            "pseudo_utilisateur": pseudo,
            "cocktails_favoris": cocktails_favoris,
        }

    def get_avis_summary(self, nom_cocktail: str) -> AvisSummary:
        """Récupère un résumé statistique des avis pour un cocktail.

        Parameters
        ----------
        nom_cocktail : str
            Le nom du cocktail

        Returns
        -------
        AvisSummary
            Objet contenant les statistiques : id_cocktail, nom_cocktail,
            nombre_avis, note_moyenne, nombre_favoris

        Raises
        ------
        CocktailNotFoundError
            Si le cocktail n'existe pas
        ServiceError
            En cas d'erreur lors de la récupération du résumé

        """
        cocktail = self._get_cocktail_by_name(nom_cocktail)

        try:
            result = self.avis_dao.get_avis_summary(cocktail["id_cocktail"])

        except Exception as e:
            raise ServiceError(message=f"Erreur lors de la récupération du résumé : {e}") from e
        if not result:
            raise ServiceError(message=f"Impossible de récupérer le résumé pour '{cocktail['nom']}'")

        return AvisSummary(**result)
