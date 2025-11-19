"""Ce module définit la classe AccesDAO, responsable des opérations CRUD
sur la table acces dans la base de données.
"""

from typing import Any

from dao.db_connection import DBConnection
from src.utils.singleton import Singleton


class AccesDAO(metaclass=Singleton):
    """DAO pour gérer les accès aux cocktails privés."""

    @staticmethod
    def get_user_id_by_pseudo(pseudo: str) -> int | None:
        """Récupère l'identifiant d'un utilisateur par son pseudo.

        La recherche est insensible à la casse et ignore les espaces superflus.

        Parameters
        ----------
        pseudo : str
            Le pseudo de l'utilisateur à rechercher

        Returns
        -------
        int | None
            L'identifiant de l'utilisateur si trouvé, None sinon

        Raises
        ------
        DAOError
            En cas d'erreur de base de données

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT id_utilisateur
                    FROM utilisateur
                    WHERE LOWER(TRIM(pseudo)) = LOWER(TRIM(%(pseudo)s))
                    """,
                {"pseudo": pseudo},
            )
            result = cursor.fetchone()
            return result["id_utilisateur"] if result else None

    @staticmethod
    def grant_access(owner_id: int, user_id: int) -> bool:
        """Donne l'accès à un utilisateur pour voir les cocktails privés du propriétaire.

        Crée une ligne d'accès (is_owner=false, has_access=true) pour chaque
        cocktail privé du propriétaire auquel l'utilisateur n'a pas encore accès.

        Parameters
        ----------
        owner_id : int
            L'identifiant du propriétaire des cocktails privés
        user_id : int
            L'identifiant de l'utilisateur à qui donner l'accès

        Returns
        -------
        bool
            True si au moins un accès a été créé, False si aucun cocktail privé
            n'existe ou si tous les accès existaient déjà

        Raises
        ------
        DAOError
            En cas d'erreur de base de données

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            # Récupérer tous les cocktails privés du propriétaire
            cursor.execute(
                """
                    SELECT id_cocktail
                    FROM acces
                    WHERE id_utilisateur = %(owner_id)s
                    AND is_owner = true
                    """,
                {"owner_id": owner_id},
            )
            private_cocktails = cursor.fetchall()

            if not private_cocktails:
                return False

            # Pour chaque cocktail privé, créer un accès pour l'utilisateur
            created = False
            for cocktail in private_cocktails:
                # Vérifier si l'accès existe déjà
                cursor.execute(
                    """
                        SELECT 1
                        FROM acces
                        WHERE id_utilisateur = %(user_id)s
                        AND id_cocktail = %(cocktail_id)s
                        """,
                    {"user_id": user_id, "cocktail_id": cocktail["id_cocktail"]},
                )

                if not cursor.fetchone():
                    # Créer l'accès : l'utilisateur reçoit une ligne avec is_owner=false
                    cursor.execute(
                        """
                            INSERT INTO acces (id_utilisateur, id_cocktail, is_owner, has_access)
                            VALUES (%(user_id)s, %(cocktail_id)s, false, true)
                            """,
                        {"user_id": user_id, "cocktail_id": cocktail["id_cocktail"]},
                    )
                    created = True

            connection.commit()
            return created

    @staticmethod
    def revoke_access(owner_id: int, user_id: int) -> bool:
        """Retire l'accès d'un utilisateur à tous les cocktails privés du propriétaire.

        Supprime toutes les lignes d'accès de l'utilisateur aux cocktails
        du propriétaire (où is_owner=false).

        Parameters
        ----------
        owner_id : int
            L'identifiant du propriétaire des cocktails privés
        user_id : int
            L'identifiant de l'utilisateur à qui retirer l'accès

        Returns
        -------
        bool
            True si au moins un accès a été retiré, False si aucun cocktail privé
            n'existe ou si l'utilisateur n'avait aucun accès

        Raises
        ------
        DAOError
            En cas d'erreur de base de données

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            # Récupérer tous les cocktails privés du propriétaire
            cursor.execute(
                """
                    SELECT id_cocktail
                    FROM acces
                    WHERE id_utilisateur = %(owner_id)s
                    AND is_owner = true
                    """,
                {"owner_id": owner_id},
            )
            private_cocktails = cursor.fetchall()

            if not private_cocktails:
                return False

            # Supprimer tous les accès de cet utilisateur à ces cocktails
            cocktail_ids = [c["id_cocktail"] for c in private_cocktails]
            cursor.execute(
                """
                    DELETE FROM acces
                    WHERE id_utilisateur = %(user_id)s
                    AND id_cocktail = ANY(%(cocktail_ids)s)
                    AND is_owner = false
                    """,
                {"user_id": user_id, "cocktail_ids": cocktail_ids},
            )
            connection.commit()
            return cursor.rowcount > 0

    @staticmethod
    def has_access(owner_id: int, viewer_id: int) -> bool:
        """Vérifie si un utilisateur a accès aux cocktails privés d'un propriétaire.

        Le propriétaire a toujours accès à ses propres cocktails.

        Parameters
        ----------
        owner_id : int
            L'identifiant du propriétaire des cocktails privés
        viewer_id : int
            L'identifiant de l'utilisateur dont on vérifie l'accès

        Returns
        -------
        bool
            True si l'utilisateur a accès aux cocktails privés, False sinon

        Raises
        ------
        DAOError
            En cas d'erreur de base de données

        """
        # Le propriétaire a toujours accès à ses propres cocktails
        if owner_id == viewer_id:
            return True

        with DBConnection().connection as connection, connection.cursor() as cursor:
            # Vérifier si l'utilisateur a au moins une ligne d'accès aux cocktails du propriétaire
            cursor.execute(
                """
                    SELECT 1
                    FROM acces a1
                    WHERE a1.id_utilisateur = %(viewer_id)s
                    AND a1.has_access = true
                    AND a1.is_owner = false
                    AND EXISTS (
                        SELECT 1
                        FROM acces a2
                        WHERE a2.id_cocktail = a1.id_cocktail
                        AND a2.id_utilisateur = %(owner_id)s
                        AND a2.is_owner = true
                    )
                    LIMIT 1
                    """,
                {"owner_id": owner_id, "viewer_id": viewer_id},
            )
            return cursor.fetchone() is not None

    @staticmethod
    def get_users_with_access(owner_id: int) -> list[str]:
        """Récupère la liste des pseudos des utilisateurs ayant accès aux cocktails privés.

        Parameters
        ----------
        owner_id : int
            L'identifiant du propriétaire des cocktails privés

        Returns
        -------
        list[str]
            Liste des pseudos des utilisateurs ayant accès, triée par ordre alphabétique

        Raises
        ------
        DAOError
            En cas d'erreur de base de données

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            # Trouver tous les utilisateurs qui ont des lignes d'accès aux cocktails du propriétaire
            cursor.execute(
                """
                    SELECT DISTINCT u.pseudo
                    FROM acces a1
                    JOIN utilisateur u ON a1.id_utilisateur = u.id_utilisateur
                    WHERE a1.has_access = true
                    AND a1.is_owner = false
                    AND EXISTS (
                        SELECT 1
                        FROM acces a2
                        WHERE a2.id_cocktail = a1.id_cocktail
                        AND a2.id_utilisateur = %(owner_id)s
                        AND a2.is_owner = true
                    )
                    ORDER BY u.pseudo
                    """,
                {"owner_id": owner_id},
            )
            results = cursor.fetchall()
            return [row["pseudo"] for row in results]

    @staticmethod
    def get_private_cocktails(owner_id: int) -> list[dict[str, Any]]:
        """Récupère la liste des cocktails privés d'un utilisateur avec leurs ingrédients.

        Parameters
        ----------
        owner_id : int
            L'identifiant du propriétaire des cocktails privés

        Returns
        -------
        list[dict[str, Any]]
            Liste de dictionnaires contenant pour chaque cocktail :
            - id_cocktail : int
            - nom_cocktail : str
            - ingredients : list[dict] avec nom_ingredient, quantite, unite

        Raises
        ------
        DAOError
            En cas d'erreur de base de données

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT c.id_cocktail, c.nom
                    FROM cocktail c
                    JOIN acces a ON c.id_cocktail = a.id_cocktail
                    WHERE a.id_utilisateur = %(owner_id)s
                    AND a.is_owner = true
                    ORDER BY c.nom
                    """,
                {"owner_id": owner_id},
            )
            cocktails = cursor.fetchall()

            # Pour chaque cocktail, récupérer les ingrédients
            result = []
            for cocktail in cocktails:
                cursor.execute(
                    """
                        SELECT i.nom, ci.qte, ci.unite
                        FROM cocktail_ingredient ci
                        JOIN ingredient i ON ci.id_ingredient = i.id_ingredient
                        WHERE ci.id_cocktail = %(cocktail_id)s
                        ORDER BY i.nom
                        """,
                    {"cocktail_id": cocktail["id_cocktail"]},
                )
                ingredients = cursor.fetchall()

                result.append(
                    {
                        "id_cocktail": cocktail["id_cocktail"],
                        "nom_cocktail": cocktail["nom"],
                        "ingredients": [
                            {
                                "nom_ingredient": ing["nom"],
                                "quantite": float(ing["qte"]) if ing["qte"] else None,
                                "unite": ing["unite"],
                            }
                            for ing in ingredients
                        ],
                    },
                )

            return result

    @staticmethod
    def add_cocktail_to_private_list(owner_id: int, cocktail_id: int) -> bool:
        """Ajoute un cocktail à la liste privée d'un utilisateur.

        Crée une ligne d'accès avec is_owner=true et has_access=true.

        Parameters
        ----------
        owner_id : int
            L'identifiant de l'utilisateur propriétaire
        cocktail_id : int
            L'identifiant du cocktail à ajouter

        Returns
        -------
        bool
            True si le cocktail a été ajouté, False s'il existait déjà dans la liste

        Raises
        ------
        DAOError
            En cas d'erreur de base de données

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            # Vérifier si le cocktail existe déjà dans la liste privée
            cursor.execute(
                """
                    SELECT 1
                    FROM acces
                    WHERE id_utilisateur = %(owner_id)s
                    AND id_cocktail = %(cocktail_id)s
                    AND is_owner = true
                    """,
                {"owner_id": owner_id, "cocktail_id": cocktail_id},
            )

            if cursor.fetchone():
                return False

            # Ajouter le cocktail à la liste privée
            cursor.execute(
                """
                    INSERT INTO acces (id_utilisateur, id_cocktail, is_owner, has_access)
                    VALUES (%(owner_id)s, %(cocktail_id)s, true, true)
                    """,
                {"owner_id": owner_id, "cocktail_id": cocktail_id},
            )
            connection.commit()
            return True

    @staticmethod
    def remove_cocktail_from_private_list(owner_id: int, cocktail_id: int) -> bool:
        """Retire un cocktail de la liste privée d'un utilisateur.

        Supprime la ligne d'accès où is_owner=true.

        Parameters
        ----------
        owner_id : int
            L'identifiant de l'utilisateur propriétaire
        cocktail_id : int
            L'identifiant du cocktail à retirer

        Returns
        -------
        bool
            True si le cocktail a été retiré, False s'il n'existait pas dans la liste

        Raises
        ------
        DAOError
            En cas d'erreur de base de données

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                    DELETE FROM acces
                    WHERE id_utilisateur = %(owner_id)s
                    AND id_cocktail = %(cocktail_id)s
                    AND is_owner = true
                    """,
                {"owner_id": owner_id, "cocktail_id": cocktail_id},
            )
            connection.commit()
            return cursor.rowcount > 0

    @staticmethod
    def is_cocktail_in_private_list(owner_id: int, cocktail_id: int) -> bool:
        """Vérifie si un cocktail est dans la liste privée d'un utilisateur.

        Parameters
        ----------
        owner_id : int
            L'identifiant de l'utilisateur propriétaire
        cocktail_id : int
            L'identifiant du cocktail à vérifier

        Returns
        -------
        bool
            True si le cocktail est dans la liste privée, False sinon

        Raises
        ------
        DAOError
            En cas d'erreur de base de données

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT 1
                    FROM acces
                    WHERE id_utilisateur = %(owner_id)s
                    AND id_cocktail = %(cocktail_id)s
                    AND is_owner = true
                    """,
                {"owner_id": owner_id, "cocktail_id": cocktail_id},
            )
            return cursor.fetchone() is not None
