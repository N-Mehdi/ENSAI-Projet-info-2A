"""Couche service pour les opérations d'accès aux cocktails privés."""

from src.business_object.cocktail import Cocktail
from src.dao.acces_dao import AccesDAO
from src.dao.cocktail_dao import CocktailDAO
from src.models.acces import (
    AccessList,
    AccessResponse,
    CocktailIngredient,
    PrivateCocktailDetail,
    PrivateCocktailsList,
)
from src.models.cocktail import CocktailAvecInstructions
from src.service.cocktail_service import CocktailService
from src.utils.exceptions import (
    AccessAlreadyExistsError,
    AccessDeniedError,
    AccessNotFoundError,
    CocktailNotFoundError,
    SelfAccessError,
    UserNotFoundError,
)


class AccesService:
    """Service pour gérer les accès aux cocktails privés."""

    def __init__(self) -> None:
        """Initialise un AccesService."""
        self.dao = AccesDAO()
        self.dao_cocktail = CocktailDAO()

    def grant_access_to_user(
        self,
        owner_pseudo: str,
        user_pseudo: str,
    ) -> AccessResponse:
        """Donne l'accès à un utilisateur pour voir les cocktails privés du
        propriétaire.

        Parameters
        ----------
        owner_pseudo : str
            Le pseudo du propriétaire des cocktails privés
        user_pseudo : str
            Le pseudo de l'utilisateur à qui donner l'accès

        Returns
        -------
        AccessResponse
            Objet contenant le succès de l'opération et les détails de l'accès accordé

        Raises
        ------
        UserNotFoundError
            Si le propriétaire ou l'utilisateur n'existe pas
        SelfAccessError
            Si l'utilisateur tente de se donner accès à lui-même
        AccessAlreadyExistsError
            Si l'utilisateur a déjà accès aux cocktails du propriétaire
        DAOError
            En cas d'erreur de base de données

        """
        owner_id = self.dao.get_user_id_by_pseudo(owner_pseudo)
        if owner_id is None:
            raise UserNotFoundError(
                message=f"Utilisateur propriétaire '{owner_pseudo}' introuvable",
            )

        user_id = self.dao.get_user_id_by_pseudo(user_pseudo)
        if user_id is None:
            raise UserNotFoundError(message=f"Utilisateur '{user_pseudo}' introuvable")

        if owner_id == user_id:
            raise SelfAccessError(
                message="Vous ne pouvez pas vous donner accès à vous-même",
            )

        created = self.dao.grant_access(owner_id, user_id)

        if not created:
            raise AccessAlreadyExistsError(
                message=f"L'utilisateur '{user_pseudo}' a déjà accès aux cocktails de"
                f"'{owner_pseudo}'",
            )

        return AccessResponse(
            success=True,
            message=f"Accès accordé à '{user_pseudo}' pour voir vos cocktails privés",
            owner_pseudo=owner_pseudo,
            user_pseudo=user_pseudo,
        )

    def revoke_access_from_user(
        self,
        owner_pseudo: str,
        user_pseudo: str,
    ) -> AccessResponse:
        """Retire l'accès d'un utilisateur aux cocktails privés du propriétaire.

        Parameters
        ----------
        owner_pseudo : str
            Le pseudo du propriétaire des cocktails privés
        user_pseudo : str
            Le pseudo de l'utilisateur à qui retirer l'accès

        Returns
        -------
        AccessResponse
            Objet contenant le succès de l'opération et les détails de l'accès retiré

        Raises
        ------
        UserNotFoundError
            Si le propriétaire ou l'utilisateur n'existe pas
        AccessNotFoundError
            Si l'utilisateur n'a pas d'accès aux cocktails du propriétaire
        DAOError
            En cas d'erreur de base de données

        """
        owner_id = self.dao.get_user_id_by_pseudo(owner_pseudo)
        if owner_id is None:
            raise UserNotFoundError(
                message=f"Utilisateur propriétaire '{owner_pseudo}' introuvable",
            )

        user_id = self.dao.get_user_id_by_pseudo(user_pseudo)
        if user_id is None:
            raise UserNotFoundError(message=f"Utilisateur '{user_pseudo}' introuvable")

        removed = self.dao.revoke_access(owner_id, user_id)

        if not removed:
            raise AccessNotFoundError(
                message=f"L'utilisateur '{user_pseudo}' n'a pas d'accès aux cocktails"
                f"de'{owner_pseudo}'",
            )

        return AccessResponse(
            success=True,
            message=f"Accès retiré à '{user_pseudo}'",
            owner_pseudo=owner_pseudo,
            user_pseudo=user_pseudo,
        )

    def get_users_with_access(self, owner_pseudo: str) -> AccessList:
        """Récupère la liste des utilisateurs ayant accès aux cocktails privés.

        Parameters
        ----------
        owner_pseudo : str
            Le pseudo du propriétaire des cocktails privés

        Returns
        -------
        AccessList
            Objet contenant la liste des pseudos avec accès et le total

        Raises
        ------
        UserNotFoundError
            Si le propriétaire n'existe pas
        DAOError
            En cas d'erreur de base de données

        """
        owner_id = self.dao.get_user_id_by_pseudo(owner_pseudo)
        if owner_id is None:
            raise UserNotFoundError(message=f"Utilisateur '{owner_pseudo}' introuvable")

        users = self.dao.get_users_with_access(owner_id)

        return AccessList(
            owner_pseudo=owner_pseudo,
            users_with_access=users,
            total_users=len(users),
        )

    def view_private_cocktails(
        self,
        owner_pseudo: str,
        viewer_pseudo: str,
    ) -> PrivateCocktailsList:
        """Permet à un utilisateur de voir les cocktails privés d'un autre utilisateur.

        Parameters
        ----------
        owner_pseudo : str
            Le pseudo du propriétaire des cocktails privés
        viewer_pseudo : str
            Le pseudo de l'utilisateur qui souhaite voir les cocktails

        Returns
        -------
        PrivateCocktailsList
            Liste des cocktails privés avec leurs ingrédients

        Raises
        ------
        UserNotFoundError
            Si le propriétaire ou le visiteur n'existe pas
        AccessDeniedError
            Si le visiteur n'a pas accès aux cocktails privés
        DAOError
            En cas d'erreur de base de données

        """
        owner_id = self.dao.get_user_id_by_pseudo(owner_pseudo)
        if owner_id is None:
            raise UserNotFoundError(message=f"Utilisateur '{owner_pseudo}' introuvable")

        viewer_id = self.dao.get_user_id_by_pseudo(viewer_pseudo)
        if viewer_id is None:
            raise UserNotFoundError(
                message=f"Utilisateur '{viewer_pseudo}' introuvable",
            )

        if not self.dao.has_access(owner_id, viewer_id):
            raise AccessDeniedError(
                message="Vous n'avez pas accès aux cocktails privés de"
                f"'{owner_pseudo}'",
            )

        cocktails_data = self.dao.get_private_cocktails(owner_id)

        cocktails = [
            PrivateCocktailDetail(
                id_cocktail=c["id_cocktail"],
                nom_cocktail=c["nom_cocktail"],
                ingredients=[CocktailIngredient(**ing) for ing in c["ingredients"]],
            )
            for c in cocktails_data
        ]

        return PrivateCocktailsList(
            owner_pseudo=owner_pseudo,
            cocktails=cocktails,
            total_cocktails=len(cocktails),
        )

    def get_my_private_cocktails(self, owner_pseudo: str) -> PrivateCocktailsList:
        """Récupère ses propres cocktails privés.

        Parameters
        ----------
        owner_pseudo : str
            Le pseudo du propriétaire

        Returns
        -------
        PrivateCocktailsList
            Liste des cocktails privés du propriétaire avec leurs ingrédients

        Raises
        ------
        UserNotFoundError
            Si le propriétaire n'existe pas
        DAOError
            En cas d'erreur de base de données

        """
        return self.view_private_cocktails(owner_pseudo, owner_pseudo)

    def add_cocktail_to_private_list(
        self,
        owner_pseudo: str,
        cocktail_id: int,
    ) -> AccessResponse:
        """Ajoute un cocktail à la liste privée par son identifiant.

        Parameters
        ----------
        owner_pseudo : str
            Le pseudo du propriétaire
        cocktail_id : int
            L'identifiant du cocktail à ajouter

        Returns
        -------
        AccessResponse
            Objet contenant le succès de l'opération et un message de confirmation

        Raises
        ------
        UserNotFoundError
            Si le propriétaire n'existe pas
        AccessAlreadyExistsError
            Si le cocktail est déjà dans la liste privée
        DAOError
            En cas d'erreur de base de données

        """
        owner_id = self.dao.get_user_id_by_pseudo(owner_pseudo)
        if owner_id is None:
            raise UserNotFoundError(message=f"Utilisateur '{owner_pseudo}' introuvable")

        added = self.dao.add_cocktail_to_private_list(owner_id, cocktail_id)

        if not added:
            raise AccessAlreadyExistsError(
                message=f"Le cocktail (ID: {cocktail_id}) est déjà dans votre liste"
                "privée",
            )

        return AccessResponse(
            success=True,
            message=f"Cocktail (ID: {cocktail_id}) ajouté à votre liste privée",
            owner_pseudo=owner_pseudo,
        )

    def add_cocktail_to_private_list_by_name(
        self,
        owner_pseudo: str,
        cocktail_name: str,
    ) -> AccessResponse:
        """Ajoute un cocktail à la liste privée par son nom.

        Parameters
        ----------
        owner_pseudo : str
            Le pseudo du propriétaire
        cocktail_name : str
            Le nom du cocktail à ajouter

        Returns
        -------
        AccessResponse
            Objet contenant le succès de l'opération et un message de confirmation

        Raises
        ------
        UserNotFoundError
            Si le propriétaire n'existe pas
        CocktailNotFoundError
            Si le cocktail n'existe pas
        AccessAlreadyExistsError
            Si le cocktail est déjà dans la liste privée
        DAOError
            En cas d'erreur de base de données

        """
        owner_id = self.dao.get_user_id_by_pseudo(owner_pseudo)
        if owner_id is None:
            raise UserNotFoundError(message=f"Utilisateur '{owner_pseudo}' introuvable")

        cocktail_id = self.dao_cocktail.get_cocktail_id_by_name(cocktail_name)
        if cocktail_id is None:
            raise CocktailNotFoundError(
                message=f"Cocktail '{cocktail_name}' non trouvé.",
            )

        added = self.dao.add_cocktail_to_private_list(owner_id, cocktail_id)

        if not added:
            raise AccessAlreadyExistsError(
                message=f"Le cocktail '{cocktail_name}' est déjà dans votre liste"
                "privée",
            )

        return AccessResponse(
            success=True,
            message=f"Cocktail '{cocktail_name}' ajouté à votre liste privée",
            owner_pseudo=owner_pseudo,
        )

    def remove_cocktail_from_private_list(
        self,
        owner_pseudo: str,
        cocktail_id: int,
    ) -> AccessResponse:
        """Retire un cocktail de la liste privée par son identifiant.

        Parameters
        ----------
        owner_pseudo : str
            Le pseudo du propriétaire
        cocktail_id : int
            L'identifiant du cocktail à retirer

        Returns
        -------
        AccessResponse
            Objet contenant le succès de l'opération et un message de confirmation

        Raises
        ------
        UserNotFoundError
            Si le propriétaire n'existe pas
        AccessNotFoundError
            Si le cocktail n'est pas dans la liste privée
        DAOError
            En cas d'erreur de base de données

        """
        owner_id = self.dao.get_user_id_by_pseudo(owner_pseudo)
        if owner_id is None:
            raise UserNotFoundError(message=f"Utilisateur '{owner_pseudo}' introuvable")

        removed = self.dao.remove_cocktail_from_private_list(owner_id, cocktail_id)

        if not removed:
            raise AccessNotFoundError(
                message=f"Le cocktail (ID: {cocktail_id}) n'est pas dans votre liste"
                "privée",
            )

        return AccessResponse(
            success=True,
            message=f"Cocktail (ID: {cocktail_id}) retiré de votre liste privée",
            owner_pseudo=owner_pseudo,
        )

    def remove_cocktail_from_private_list_by_name(
        self,
        owner_pseudo: str,
        cocktail_name: str,
    ) -> AccessResponse:
        """Retire un cocktail de la liste privée par son nom.

        Parameters
        ----------
        owner_pseudo : str
            Le pseudo du propriétaire
        cocktail_name : str
            Le nom du cocktail à retirer

        Returns
        -------
        AccessResponse
            Objet contenant le succès de l'opération et un message de confirmation

        Raises
        ------
        UserNotFoundError
            Si le propriétaire n'existe pas
        CocktailNotFoundError
            Si le cocktail n'existe pas
        AccessNotFoundError
            Si le cocktail n'est pas dans la liste privée
        DAOError
            En cas d'erreur de base de données

        """
        owner_id = self.dao.get_user_id_by_pseudo(owner_pseudo)
        if owner_id is None:
            raise UserNotFoundError(message=f"Utilisateur '{owner_pseudo}' introuvable")

        cocktail_id = self.dao_cocktail.get_cocktail_id_by_name(cocktail_name)
        if cocktail_id is None:
            raise CocktailNotFoundError(
                message=f"Cocktail '{cocktail_name}' non trouvé.",
            )

        removed = self.dao.remove_cocktail_from_private_list(owner_id, cocktail_id)

        if not removed:
            raise AccessNotFoundError(
                message=f"Le cocktail '{cocktail_name}' n'est pas dans votre liste"
                "privée",
            )

        return AccessResponse(
            success=True,
            message=f"Cocktail '{cocktail_name}' retiré de votre liste privée",
            owner_pseudo=owner_pseudo,
        )

    def creer_cocktail_prive(
        self,
        pseudo: str,
        nom: str,
        categorie: str,
        verre: str,
        alcool: bool,
        image: str,
        instructions: str | None = None,
    ) -> CocktailAvecInstructions:
        """Crée un nouveau cocktail privé pour un utilisateur.

        Le cocktail est automatiquement ajouté avec is_owner=TRUE dans la table acces.

        Parameters
        ----------
        pseudo : str
            Le pseudo de l'utilisateur propriétaire
        nom : str
            Nom du cocktail
        categorie : str
            Catégorie du cocktail
        verre : str
            Type de verre
        alcool : bool
            Contient de l'alcool
        image : str
            URL de l'image
        instructions : str | None, optional
            Instructions de préparation

        Returns
        -------
        CocktailAvecInstructions
            Le cocktail créé avec ses instructions

        Raises
        ------
        UserNotFoundError
            Si l'utilisateur n'existe pas
        DAOError
            En cas d'erreur de base de données

        """
        # Récupérer l'ID de l'utilisateur
        user_id = self.dao.get_user_id_by_pseudo(pseudo)
        if user_id is None:
            raise UserNotFoundError(message=f"Utilisateur '{pseudo}' introuvable")

        # Créer l'objet Cocktail
        cocktail = Cocktail(
            id_cocktail=None,
            nom=nom,
            categorie=categorie,
            verre=verre,
            alcool=alcool,
            image=image,
        )

        # Utiliser CocktailService pour ajouter le cocktail avec instructions
        cocktail_service = CocktailService()
        id_cocktail = cocktail_service.ajouter_cocktail_complet(
            cocktail=cocktail,
            instructions=instructions,
        )

        # Créer la relation d'accès (propriétaire)
        self.dao.create_owner_access(user_id, id_cocktail)

        return CocktailAvecInstructions(
            id_cocktail=id_cocktail,
            nom=nom,
            categorie=categorie,
            verre=verre,
            alcool=alcool,
            image=image,
            instructions=instructions,
        )

    def supprimer_cocktail_prive(
        self,
        pseudo: str,
        id_cocktail: int,
    ) -> AccessResponse:
        """Supprime un cocktail privé dont l'utilisateur est propriétaire.

        Supprime également tous les accès associés (CASCADE) et les instructions.

        Parameters
        ----------
        pseudo : str
            Le pseudo du propriétaire
        id_cocktail : int
            L'identifiant du cocktail à supprimer

        Returns
        -------
        AccessResponse
            Message de confirmation

        Raises
        ------
        UserNotFoundError
            Si l'utilisateur n'existe pas
        PermissionDeniedError
            Si l'utilisateur n'est pas le propriétaire
        DAOError
            En cas d'erreur de base de données

        """
        # Récupérer l'ID de l'utilisateur
        user_id = self.dao.get_user_id_by_pseudo(pseudo)
        if user_id is None:
            raise UserNotFoundError(message=f"Utilisateur '{pseudo}' introuvable")

        # Vérifier que l'utilisateur est propriétaire
        if not self.dao.is_owner(user_id, id_cocktail):
            raise PermissionDeniedError(
                message=f"Vous n'êtes pas le propriétaire du cocktail (ID: {id_cocktail})",
            )

        # Supprimer le cocktail (les accès seront supprimés en CASCADE)
        self.dao_cocktail.supprimer_cocktail(id_cocktail)

        return AccessResponse(
            success=True,
            message=f"Cocktail (ID: {id_cocktail}) supprimé avec succès",
            owner_pseudo=pseudo,
        )
