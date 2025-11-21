"""Tests d'intégration pour AccesDAO."""

import pytest

from src.dao.acces_dao import AccesDAO


class TestAccesDAOIntegration:
    """Tests d'intégration pour AccesDAO."""

    # ========== Tests pour get_user_id_by_pseudo ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_user_id_by_pseudo_existant(
        db_connection,
    ) -> None:
        """Teste la récupération de l'ID d'un utilisateur existant."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('alice', 'alice@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """)
            user_id = cursor.fetchone()["id_utilisateur"]
            db_connection.commit()

        dao = AccesDAO()

        # WHEN
        result = dao.get_user_id_by_pseudo("alice")

        # THEN
        if result != user_id:
            raise AssertionError(
                message=f"L'ID devrait être {user_id}, obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_user_id_by_pseudo_case_insensitive(
        db_connection,
    ) -> None:
        """Teste que la recherche est insensible à la casse."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('Alice', 'alice@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """)
            user_id = cursor.fetchone()["id_utilisateur"]
            db_connection.commit()

        dao = AccesDAO()

        # WHEN
        result = dao.get_user_id_by_pseudo("ALICE")

        # THEN
        if result != user_id:
            raise AssertionError(
                message=f"L'ID devrait être {user_id}, obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_user_id_by_pseudo_with_spaces(
        db_connection,
    ) -> None:
        """Teste que la recherche ignore les espaces superflus."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('bob', 'bob@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """)
            user_id = cursor.fetchone()["id_utilisateur"]
            db_connection.commit()

        dao = AccesDAO()

        # WHEN
        result = dao.get_user_id_by_pseudo("  bob  ")

        # THEN
        if result != user_id:
            raise AssertionError(
                message=f"L'ID devrait être {user_id}, obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_user_id_by_pseudo_inexistant() -> None:
        """Teste la recherche d'un utilisateur inexistant."""
        # GIVEN
        dao = AccesDAO()

        # WHEN
        result = dao.get_user_id_by_pseudo("inexistant")

        # THEN
        if result is not None:
            raise AssertionError(
                message=f"Le résultat devrait être None, obtenu: {result}",
            )

    # ========== Tests pour add_cocktail_to_private_list ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_add_cocktail_to_private_list_success(
        db_connection,
    ) -> None:
        """Teste l'ajout d'un cocktail à la liste privée."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('owner', 'owner@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """)
            owner_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Mojito', 'Cocktail', 'Highball', TRUE, 'image.jpg')
                RETURNING id_cocktail
            """)
            cocktail_id = cursor.fetchone()["id_cocktail"]
            db_connection.commit()

        dao = AccesDAO()

        # WHEN
        result = dao.add_cocktail_to_private_list(owner_id, cocktail_id)

        # THEN
        if result is not True:
            raise AssertionError(
                message=f"L'ajout devrait réussir, obtenu: {result}",
            )

        # Vérifier que l'accès a été créé
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT is_owner, has_access
                FROM acces
                WHERE id_utilisateur = %s AND id_cocktail = %s
            """,
                (owner_id, cocktail_id),
            )
            row = cursor.fetchone()

            if row is None:
                raise AssertionError(message="L'accès devrait exister")
            if row["is_owner"] is not True:
                raise AssertionError(message="is_owner devrait être True")
            if row["has_access"] is not True:
                raise AssertionError(message="has_access devrait être True")

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_add_cocktail_to_private_list_deja_existant(
        db_connection,
    ) -> None:
        """Teste l'ajout d'un cocktail déjà dans la liste."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('owner', 'owner@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """)
            owner_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Mojito', 'Cocktail', 'Highball', TRUE, 'image.jpg')
                RETURNING id_cocktail
            """)
            cocktail_id = cursor.fetchone()["id_cocktail"]

            # Ajouter déjà le cocktail
            cursor.execute(
                """
                INSERT INTO acces (id_utilisateur, id_cocktail, is_owner, has_access)
                VALUES (%s, %s, TRUE, TRUE)
            """,
                (owner_id, cocktail_id),
            )
            db_connection.commit()

        dao = AccesDAO()

        # WHEN
        result = dao.add_cocktail_to_private_list(owner_id, cocktail_id)

        # THEN
        if result is not False:
            raise AssertionError(
                message=f"L'ajout devrait retourner False (déjà existant), obtenu:"
                f"{result}",
            )

    # ========== Tests pour is_cocktail_in_private_list ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_is_cocktail_in_private_list_true(db_connection) -> None:
        """Teste la vérification d'un cocktail dans la liste."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('owner', 'owner@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """)
            owner_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Mojito', 'Cocktail', 'Highball', TRUE, 'image.jpg')
                RETURNING id_cocktail
            """)
            cocktail_id = cursor.fetchone()["id_cocktail"]

            cursor.execute(
                """
                INSERT INTO acces (id_utilisateur, id_cocktail, is_owner, has_access)
                VALUES (%s, %s, TRUE, TRUE)
            """,
                (owner_id, cocktail_id),
            )
            db_connection.commit()

        dao = AccesDAO()

        # WHEN
        result = dao.is_cocktail_in_private_list(owner_id, cocktail_id)

        # THEN
        if result is not True:
            raise AssertionError(
                message=f"Le cocktail devrait être dans la liste, obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_is_cocktail_in_private_list_false(db_connection) -> None:
        """Teste la vérification d'un cocktail absent de la liste."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('owner', 'owner@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """)
            owner_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Mojito', 'Cocktail', 'Highball', TRUE, 'image.jpg')
                RETURNING id_cocktail
            """)
            cocktail_id = cursor.fetchone()["id_cocktail"]
            db_connection.commit()

        dao = AccesDAO()

        # WHEN
        result = dao.is_cocktail_in_private_list(owner_id, cocktail_id)

        # THEN
        if result is not False:
            raise AssertionError(
                message=f"Le cocktail ne devrait pas être dans la liste, obtenu:"
                f"{result}",
            )

    # ========== Tests pour remove_cocktail_from_private_list ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_remove_cocktail_from_private_list_success(
        db_connection,
    ) -> None:
        """Teste le retrait d'un cocktail de la liste privée."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('owner', 'owner@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """)
            owner_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Mojito', 'Cocktail', 'Highball', TRUE, 'image.jpg')
                RETURNING id_cocktail
            """)
            cocktail_id = cursor.fetchone()["id_cocktail"]

            cursor.execute(
                """
                INSERT INTO acces (id_utilisateur, id_cocktail, is_owner, has_access)
                VALUES (%s, %s, TRUE, TRUE)
            """,
                (owner_id, cocktail_id),
            )
            db_connection.commit()

        dao = AccesDAO()

        # WHEN
        result = dao.remove_cocktail_from_private_list(owner_id, cocktail_id)

        # THEN
        if result is not True:
            raise AssertionError(
                message=f"Le retrait devrait réussir, obtenu: {result}",
            )

        # Vérifier que l'accès a été supprimé
        if dao.is_cocktail_in_private_list(owner_id, cocktail_id):
            raise AssertionError(
                message="Le cocktail ne devrait plus être dans la liste",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_remove_cocktail_from_private_list_inexistant(
        db_connection,
    ) -> None:
        """Teste le retrait d'un cocktail absent de la liste."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('owner', 'owner@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """)
            owner_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Mojito', 'Cocktail', 'Highball', TRUE, 'image.jpg')
                RETURNING id_cocktail
            """)
            cocktail_id = cursor.fetchone()["id_cocktail"]
            db_connection.commit()

        dao = AccesDAO()

        # WHEN
        result = dao.remove_cocktail_from_private_list(owner_id, cocktail_id)

        # THEN
        if result is not False:
            raise AssertionError(
                message=f"Le retrait devrait retourner False, obtenu: {result}",
            )

    # ========== Tests pour grant_access ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_grant_access_success(db_connection) -> None:
        """Teste l'octroi d'accès à un utilisateur."""
        # GIVEN
        with db_connection.cursor() as cursor:
            # Créer le propriétaire
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('owner', 'owner@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """)
            owner_id = cursor.fetchone()["id_utilisateur"]

            # Créer l'utilisateur
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('user', 'user@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """)
            user_id = cursor.fetchone()["id_utilisateur"]

            # Créer un cocktail privé
            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Private Mojito', 'Cocktail', 'Highball', TRUE, 'image.jpg')
                RETURNING id_cocktail
            """)
            cocktail_id = cursor.fetchone()["id_cocktail"]

            # Marquer comme privé pour le propriétaire
            cursor.execute(
                """
                INSERT INTO acces (id_utilisateur, id_cocktail, is_owner, has_access)
                VALUES (%s, %s, TRUE, TRUE)
            """,
                (owner_id, cocktail_id),
            )
            db_connection.commit()

        dao = AccesDAO()

        # WHEN
        result = dao.grant_access(owner_id, user_id)

        # THEN
        if result is not True:
            raise AssertionError(
                message=f"L'octroi d'accès devrait réussir, obtenu: {result}",
            )

        # Vérifier que l'accès a été créé
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT is_owner, has_access
                FROM acces
                WHERE id_utilisateur = %s AND id_cocktail = %s
            """,
                (user_id, cocktail_id),
            )
            row = cursor.fetchone()

            if row is None:
                raise AssertionError(message="L'accès devrait exister")
            if row["is_owner"] is not False:
                raise AssertionError(message="is_owner devrait être False")
            if row["has_access"] is not True:
                raise AssertionError(message="has_access devrait être True")

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_grant_access_no_private_cocktails(db_connection) -> None:
        """Teste l'octroi d'accès quand il n'y a pas de cocktails privés."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES
                    ('owner', 'owner@example.com', 'pass', '1990-01-01'),
                    ('user', 'user@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """)
            results = cursor.fetchall()
            owner_id = results[0]["id_utilisateur"]
            user_id = results[1]["id_utilisateur"]
            db_connection.commit()

        dao = AccesDAO()

        # WHEN
        result = dao.grant_access(owner_id, user_id)

        # THEN
        if result is not False:
            raise AssertionError(
                message=f"L'octroi devrait retourner False (pas de cocktails), obtenu:"
                f"{result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_grant_access_already_exists(db_connection) -> None:
        """Teste l'octroi d'accès quand l'accès existe déjà."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('owner', 'owner@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """)
            owner_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('user', 'user@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """)
            user_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Private Mojito', 'Cocktail', 'Highball', TRUE, 'image.jpg')
                RETURNING id_cocktail
            """)
            cocktail_id = cursor.fetchone()["id_cocktail"]

            # Owner et accès utilisateur déjà existant
            cursor.execute(
                """
                INSERT INTO acces (id_utilisateur, id_cocktail, is_owner, has_access)
                VALUES
                    (%s, %s, TRUE, TRUE),
                    (%s, %s, FALSE, TRUE)
            """,
                (owner_id, cocktail_id, user_id, cocktail_id),
            )
            db_connection.commit()

        dao = AccesDAO()

        # WHEN
        result = dao.grant_access(owner_id, user_id)

        # THEN
        if result is not False:
            raise AssertionError(
                message=f"L'octroi devrait retourner False (déjà existant), obtenu:"
                f"{result}",
            )

    # ========== Tests pour revoke_access ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_revoke_access_success(db_connection) -> None:
        """Teste le retrait d'accès à un utilisateur."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('owner', 'owner@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """)
            owner_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('user', 'user@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """)
            user_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Private Mojito', 'Cocktail', 'Highball', TRUE, 'image.jpg')
                RETURNING id_cocktail
            """)
            cocktail_id = cursor.fetchone()["id_cocktail"]

            cursor.execute(
                """
                INSERT INTO acces (id_utilisateur, id_cocktail, is_owner, has_access)
                VALUES
                    (%s, %s, TRUE, TRUE),
                    (%s, %s, FALSE, TRUE)
            """,
                (owner_id, cocktail_id, user_id, cocktail_id),
            )
            db_connection.commit()

        dao = AccesDAO()

        # WHEN
        result = dao.revoke_access(owner_id, user_id)

        # THEN
        if result is not True:
            raise AssertionError(
                message=f"Le retrait devrait réussir, obtenu: {result}",
            )

        # Vérifier que l'accès a été supprimé
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1
                FROM acces
                WHERE id_utilisateur = %s AND id_cocktail = %s AND is_owner = FALSE
            """,
                (user_id, cocktail_id),
            )

            if cursor.fetchone() is not None:
                raise AssertionError(message="L'accès ne devrait plus exister")

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_revoke_access_no_private_cocktails(
        db_connection,
    ) -> None:
        """Teste le retrait d'accès quand il n'y a pas de cocktails privés."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES
                    ('owner', 'owner@example.com', 'pass', '1990-01-01'),
                    ('user', 'user@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """)
            results = cursor.fetchall()
            owner_id = results[0]["id_utilisateur"]
            user_id = results[1]["id_utilisateur"]
            db_connection.commit()

        dao = AccesDAO()

        # WHEN
        result = dao.revoke_access(owner_id, user_id)

        # THEN
        if result is not False:
            raise AssertionError(
                message=f"Le retrait devrait retourner False, obtenu: {result}",
            )

    # ========== Tests pour has_access ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_has_access_owner_himself(db_connection) -> None:
        """Teste que le propriétaire a toujours accès à ses propres cocktails."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('owner', 'owner@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """)
            owner_id = cursor.fetchone()["id_utilisateur"]
            db_connection.commit()

        dao = AccesDAO()

        # WHEN
        result = dao.has_access(owner_id, owner_id)

        # THEN
        if result is not True:
            raise AssertionError(
                message=f"Le propriétaire devrait avoir accès, obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_has_access_user_with_access(db_connection) -> None:
        """Teste qu'un utilisateur avec accès peut voir les cocktails."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('owner', 'owner@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """)
            owner_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('user', 'user@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """)
            user_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Private Mojito', 'Cocktail', 'Highball', TRUE, 'image.jpg')
                RETURNING id_cocktail
            """)
            cocktail_id = cursor.fetchone()["id_cocktail"]

            cursor.execute(
                """
                INSERT INTO acces (id_utilisateur, id_cocktail, is_owner, has_access)
                VALUES
                    (%s, %s, TRUE, TRUE),
                    (%s, %s, FALSE, TRUE)
            """,
                (owner_id, cocktail_id, user_id, cocktail_id),
            )
            db_connection.commit()

        dao = AccesDAO()

        # WHEN
        result = dao.has_access(owner_id, user_id)

        # THEN
        if result is not True:
            raise AssertionError(
                message=f"L'utilisateur devrait avoir accès, obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_has_access_user_without_access(db_connection) -> None:
        """Teste qu'un utilisateur sans accès ne peut pas voir les cocktails."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES
                    ('owner', 'owner@example.com', 'pass', '1990-01-01'),
                    ('user', 'user@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """)
            results = cursor.fetchall()
            owner_id = results[0]["id_utilisateur"]
            user_id = results[1]["id_utilisateur"]
            db_connection.commit()

        dao = AccesDAO()

        # WHEN
        result = dao.has_access(owner_id, user_id)

        # THEN
        if result is not False:
            raise AssertionError(
                message=f"L'utilisateur ne devrait pas avoir accès, obtenu: {result}",
            )

    # ========== Tests pour get_users_with_access ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_users_with_access_empty(db_connection) -> None:
        """Teste la récupération quand aucun utilisateur n'a accès."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('owner', 'owner@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """)
            owner_id = cursor.fetchone()["id_utilisateur"]
            db_connection.commit()

        dao = AccesDAO()

        # WHEN
        result = dao.get_users_with_access(owner_id)

        # THEN
        if len(result) != 0:
            raise AssertionError(
                message=f"La liste devrait être vide, obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_users_with_access_multiple_users(
        db_connection,
    ) -> None:
        """Teste la récupération de plusieurs utilisateurs avec accès."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('owner', 'owner@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """)
            owner_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES
                    ('alice', 'alice@example.com', 'pass', '1990-01-01'),
                    ('bob', 'bob@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """)
            users = cursor.fetchall()
            alice_id = users[0]["id_utilisateur"]
            bob_id = users[1]["id_utilisateur"]

            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Private Mojito', 'Cocktail', 'Highball', TRUE, 'image.jpg')
                RETURNING id_cocktail
            """)
            cocktail_id = cursor.fetchone()["id_cocktail"]

            cursor.execute(
                """
                INSERT INTO acces (id_utilisateur, id_cocktail, is_owner, has_access)
                VALUES
                    (%s, %s, TRUE, TRUE),
                    (%s, %s, FALSE, TRUE),
                    (%s, %s, FALSE, TRUE)
            """,
                (owner_id, cocktail_id, alice_id, cocktail_id, bob_id, cocktail_id),
            )
            db_connection.commit()

        dao = AccesDAO()

        # WHEN
        result = dao.get_users_with_access(owner_id)

        # THEN
        nb_user = 2
        if len(result) != nb_user:
            raise AssertionError(
                message=f"2 utilisateurs attendus, obtenu: {len(result)}",
            )
        if "alice" not in result:
            raise AssertionError(
                message=f"'alice' devrait être dans la liste: {result}",
            )
        if "bob" not in result:
            raise AssertionError(
                message=f"'bob' devrait être dans la liste: {result}",
            )
        # Vérifier l'ordre alphabétique
        if result != ["alice", "bob"]:
            raise AssertionError(
                message=f"La liste devrait être triée alphabétiquement: {result}",
            )

    # ========== Tests pour get_private_cocktails ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_private_cocktails_empty(db_connection) -> None:
        """Teste la récupération quand il n'y a pas de cocktails privés."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('owner', 'owner@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """)
            owner_id = cursor.fetchone()["id_utilisateur"]
            db_connection.commit()

        dao = AccesDAO()

        # WHEN
        result = dao.get_private_cocktails(owner_id)

        # THEN
        if len(result) != 0:
            raise AssertionError(
                message=f"La liste devrait être vide, obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_private_cocktails_with_ingredients(
        db_connection,
    ) -> None:
        """Teste la récupération de cocktails privés avec ingrédients."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('owner', 'owner@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """)
            owner_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('My Mojito', 'Cocktail', 'Highball', TRUE, 'image.jpg')
                RETURNING id_cocktail
            """)
            cocktail_id = cursor.fetchone()["id_cocktail"]

            cursor.execute("""
                INSERT INTO ingredient (nom, alcool)
                VALUES ('Rhum', TRUE), ('Menthe', FALSE)
                RETURNING id_ingredient
            """)
            ingredients = cursor.fetchall()
            rhum_id = ingredients[0]["id_ingredient"]
            menthe_id = ingredients[1]["id_ingredient"]

            cursor.execute(
                """
                INSERT INTO cocktail_ingredient (id_cocktail, id_ingredient, qte, unite)
                VALUES (%s, %s, 50, 'ml'), (%s, %s, 10, 'feuilles')
            """,
                (cocktail_id, rhum_id, cocktail_id, menthe_id),
            )

            cursor.execute(
                """
                INSERT INTO acces (id_utilisateur, id_cocktail, is_owner, has_access)
                VALUES (%s, %s, TRUE, TRUE)
            """,
                (owner_id, cocktail_id),
            )
            db_connection.commit()

        dao = AccesDAO()

        # WHEN
        result = dao.get_private_cocktails(owner_id)

        # THEN
        if len(result) != 1:
            raise AssertionError(
                message=f"1 cocktail attendu, obtenu: {len(result)}",
            )

        cocktail = result[0]
        if cocktail["nom_cocktail"] != "My Mojito":
            raise AssertionError(
                message=f"Le nom devrait être 'My Mojito', obtenu:"
                f"{cocktail['nom_cocktail']}",
            )
        nb_ing = 2
        if len(cocktail["ingredients"]) != nb_ing:
            raise AssertionError(
                message=f"2 ingrédients attendus, obtenu:"
                f"{len(cocktail['ingredients'])}",
            )
