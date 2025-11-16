"""doc."""

from fastapi import APIRouter, HTTPException, status

from src.api.deps import CurrentUser
from src.dao.utilisateur_dao import UtilisateurDao
from src.models.utilisateurs import DateInscriptionResponse, UserChangePassword, UserDelete, UserUpdatePseudo
from src.service.utilisateur_service import UtilisateurService
from src.utils.exceptions import (
    AuthError,
    DAOError,
    EmptyFieldError,
    ServiceError,
    UserAlreadyExistsError,
    UserNotFoundError,
)

router = APIRouter(prefix="/compte", tags=["Compte"])

service = UtilisateurService(utilisateur_dao=UtilisateurDao())


@router.put(
    "/pseudo",
    status_code=status.HTTP_200_OK,
    summary="Changer le pseudo",
    response_description="Pseudo modifié avec succès",
    responses={
        200: {
            "description": "Pseudo modifié avec succès",
            "content": {
                "application/json": {
                    "example": "Pseudo modifié avec succès.",
                },
            },
        },
        400: {
            "description": "Données invalides",
            "content": {
                "application/json": {
                    "examples": {
                        "empty_field": {
                            "summary": "Champ vide",
                            "value": {"detail": "Le champ 'nouveau_pseudo' ne peut pas être vide"},
                        },
                        "same_pseudo": {
                            "summary": "Pseudos identiques",
                            "value": {"detail": "Le nouveau pseudo doit être différent de l'ancien"},
                        },
                        "pseudo_exists": {
                            "summary": "Pseudo déjà utilisé",
                            "value": {"detail": "Username already registered"},
                        },
                    },
                },
            },
        },
        401: {
            "description": "Non authentifié",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"},
                },
            },
        },
        404: {
            "description": "Utilisateur non trouvé",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"},
                },
            },
        },
        500: {
            "description": "Erreur serveur",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not update pseudo."},
                },
            },
        },
    },
    tags=["Compte"],
)
def changer_pseudo(
    donnees: UserUpdatePseudo,
    _current_user: CurrentUser,
) -> str:
    """Changer le pseudo de l'utilisateur connecté.

    L'utilisateur fournit uniquement son nouveau pseudo.
    Son identité actuelle est automatiquement récupérée via son token d'authentification.

    **Note** : Le nouveau pseudo doit être différent de l'ancien et ne pas déjà exister.

    **Exemple d'utilisation** :
    - URL : PUT /compte/pseudo
    - Body : {"nouveau_pseudo": "alice456"}
    - Headers : Authorization: Bearer <votre_token>
    """
    try:
        return service.changer_pseudo(donnees.ancien_pseudo, donnees.nouveau_pseudo)
    except EmptyFieldError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from None
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from None
    except UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        ) from None
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from None
    except DAOError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update pseudo.",
        ) from None


@router.put(
    "/mot-de-passe",
    status_code=status.HTTP_200_OK,
    summary="Changer le mot de passe",
    response_description="Mot de passe modifié avec succès",
    responses={
        200: {
            "description": "Mot de passe modifié avec succès",
            "content": {
                "application/json": {
                    "example": "Mot de passe modifié avec succès.",
                },
            },
        },
        400: {
            "description": "Données invalides",
            "content": {
                "application/json": {
                    "examples": {
                        "empty_field": {
                            "summary": "Champ vide",
                            "value": {"detail": "Le champ 'pseudo' ne peut pas être vide"},
                        },
                        "same_password": {
                            "summary": "Mots de passe identiques",
                            "value": {"detail": "Le nouveau mot de passe doit être différent de l'ancien"},
                        },
                    },
                },
            },
        },
        401: {
            "description": "Mot de passe actuel incorrect",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid credentials"},
                },
            },
        },
        404: {
            "description": "Utilisateur non trouvé",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"},
                },
            },
        },
        500: {
            "description": "Erreur serveur",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not update password."},
                },
            },
        },
    },
    tags=["Compte"],
)
def changer_mot_de_passe(donnees: UserChangePassword, _current_user: CurrentUser) -> str:
    """Changer le mot de passe d'un utilisateur.

    L'utilisateur doit fournir :
    - Son pseudo
    - Son mot de passe actuel (pour vérification)
    - Son nouveau mot de passe

    **Sécurité** :
    - Le mot de passe actuel est vérifié avant le changement
    - Le nouveau mot de passe doit être différent de l'ancien
    - Le nouveau mot de passe est automatiquement haché
    """
    try:
        return service.changer_mot_de_passe(donnees)
    except EmptyFieldError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from None
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from None
    except AuthError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        ) from None
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from None
    except DAOError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update password.",
        ) from None


@router.get(
    "/date-inscription",
    status_code=status.HTTP_200_OK,
    summary="Obtenir la date d'inscription",
    response_description="Date d'inscription récupérée avec succès",
    response_model=DateInscriptionResponse,
    responses={
        200: {
            "description": "Date d'inscription récupérée avec succès",
            "content": {
                "application/json": {
                    "example": {
                        "pseudo": "alice123",
                        "date_inscription": "2024-01-15",
                    },
                },
            },
        },
        401: {
            "description": "Non authentifié",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"},
                },
            },
        },
        404: {
            "description": "Utilisateur non trouvé",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"},
                },
            },
        },
        500: {
            "description": "Erreur serveur",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not retrieve registration date."},
                },
            },
        },
    },
    tags=["Compte"],
)
def obtenir_date_inscription(
    current_user: CurrentUser,
) -> DateInscriptionResponse:
    """Obtenir la date d'inscription de l'utilisateur connecté.

    Retourne la date à laquelle l'utilisateur a créé son compte.

    **Exemple de réponse** :
    ```json
    {
        "pseudo": "alice123",
        "date_inscription": "2024-01-15"
    }
    ```
    """
    try:
        return service.obtenir_date_inscription(current_user.pseudo)
    except EmptyFieldError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from None
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from None
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from None
    except DAOError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve registration date.",
        ) from None


@router.delete(
    "/supprimer",
    status_code=status.HTTP_200_OK,
    summary="Supprimer un compte utilisateur",
    response_description="Compte supprimé avec succès",
    responses={
        200: {
            "description": "Compte supprimé avec succès",
            "content": {
                "application/json": {
                    "example": "Compte supprimé avec succès.",
                },
            },
        },
        400: {
            "description": "Champ vide",
            "content": {
                "application/json": {
                    "example": {"detail": "Le champ 'pseudo' ne peut pas être vide"},
                },
            },
        },
        401: {
            "description": "Mot de passe incorrect",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid credentials"},
                },
            },
        },
        404: {
            "description": "Utilisateur non trouvé",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"},
                },
            },
        },
        500: {
            "description": "Erreur serveur",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not delete user."},
                },
            },
        },
    },
    tags=["Compte"],
)
def supprimer_compte(donnees: UserDelete, _current_user: CurrentUser) -> str:
    """Supprimer un compte utilisateur après authentification.

    L'utilisateur doit fournir son pseudo et mot de passe pour confirmer
    la suppression de son compte. Cette action est irréversible.

    **Sécurité** : Le mot de passe est vérifié avant la suppression pour
    empêcher les suppressions non autorisées.
    """
    try:
        return service.supprimer_compte(donnees)
    except EmptyFieldError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from None
    except AuthError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        ) from None
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from None
    except DAOError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete user.",
        ) from None
