"""Tests d'intégration pour AvisDAO."""

import pytest

from src.dao.avis_dao import AvisDAO


class TestAvisDAOIntegration:
    """Tests d'intégration pour AvisDAO."""

    # ========== Tests pour create_or_update_avis ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_create_avis_success(
        db_connection,
    ) -> None:
        """Teste la création d'un nouvel avis."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('alice', 'alice@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute(
                """
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES (
                    'Mojito', 'Cocktail', 'Highball', TRUE, 'image.jpg'
                )
                RETURNING id_cocktail
            """,
            )
            cocktail_id = cursor.fetchone()["id_cocktail"]
            db_connection.commit()

        dao = AvisDAO()

        # WHEN
        result = dao.create_or_update_avis(
            id_utilisateur=user_id,
            id_cocktail=cocktail_id,
            note="8.5",
            commentaire="Excellent cocktail!",
        )

        # THEN
        if result is None:
            raise AssertionError(message="L'avis devrait être créé")
        if result["id_utilisateur"] != user_id:
            raise AssertionError(
                message=f"user_id devrait être {user_id}, "
                f"obtenu: {result['id_utilisateur']}",
            )
        if result["id_cocktail"] != cocktail_id:
            raise AssertionError(
                message=f"cocktail_id devrait être {cocktail_id}, "
                f"obtenu: {result['id_cocktail']}",
            )
        note = 8.5
        if float(result["note"]) != note:
            raise AssertionError(
                message=f"note devrait être 8.5, obtenu: {result['note']}",
            )
        if result["commentaire"] != "Excellent cocktail!":
            raise AssertionError(
                message=f"commentaire incorrect: {result['commentaire']}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_update_avis_existing(
        db_connection,
    ) -> None:
        """Teste la mise à jour d'un avis existant."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('bob', 'bob@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute(
                """
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES (
                    'Margarita', 'Cocktail', 'Coupe', TRUE, 'image.jpg'
                )
                RETURNING id_cocktail
            """,
            )
            cocktail_id = cursor.fetchone()["id_cocktail"]

            cursor.execute(
                """
                INSERT INTO avis (
                    id_utilisateur, id_cocktail, note,
                    commentaire, favoris
                )
                VALUES (%s, %s, 7.0, 'Pas mal', FALSE)
            """,
                (user_id, cocktail_id),
            )
            db_connection.commit()

        dao = AvisDAO()

        # WHEN
        result = dao.create_or_update_avis(
            id_utilisateur=user_id,
            id_cocktail=cocktail_id,
            note="9.0",
            commentaire="Finalement excellent!",
        )

        # THEN
        note = 9.0
        if float(result["note"]) != note:
            raise AssertionError(
                message=f"note devrait être 9.0, obtenu: {result['note']}",
            )
        if result["commentaire"] != "Finalement excellent!":
            raise AssertionError(
                message=f"commentaire incorrect: {result['commentaire']}",
            )

    # ========== Tests pour get_avis_by_user_and_cocktail ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_avis_by_user_and_cocktail_existant(
        db_connection,
    ) -> None:
        """Teste la récupération d'un avis spécifique existant."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('charlie', 'charlie@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute(
                """
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Daiquiri', 'Cocktail', 'Coupe', TRUE, 'image.jpg')
                RETURNING id_cocktail
            """,
            )
            cocktail_id = cursor.fetchone()["id_cocktail"]

            cursor.execute(
                """
                INSERT INTO avis (
                    id_utilisateur, id_cocktail, note,
                    commentaire, favoris
                )
                VALUES (%s, %s, 8.0, 'Super!', TRUE)
            """,
                (user_id, cocktail_id),
            )
            db_connection.commit()

        dao = AvisDAO()

        # WHEN
        result = dao.get_avis_by_user_and_cocktail(user_id, cocktail_id)

        # THEN
        if result is None:
            raise AssertionError(message="L'avis devrait être trouvé")
        if result["pseudo_utilisateur"] != "charlie":
            raise AssertionError(
                message=f"pseudo devrait être 'charlie', "
                f"obtenu: {result['pseudo_utilisateur']}",
            )
        if result["nom_cocktail"] != "Daiquiri":
            raise AssertionError(
                message=f"nom_cocktail devrait être 'Daiquiri', "
                f"obtenu: {result['nom_cocktail']}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_avis_by_user_and_cocktail_inexistant(
        db_connection,
    ) -> None:
        """Teste la récupération d'un avis inexistant."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('dave', 'dave@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute(
                """
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Pina Colada', 'Cocktail', 'Verre', TRUE, 'img.jpg')
                RETURNING id_cocktail
            """,
            )
            cocktail_id = cursor.fetchone()["id_cocktail"]
            db_connection.commit()

        dao = AvisDAO()

        # WHEN
        result = dao.get_avis_by_user_and_cocktail(user_id, cocktail_id)

        # THEN
        if result is not None:
            raise AssertionError(
                message=f"Le résultat devrait être None, obtenu: {result}",
            )

    # ========== Tests pour get_avis_by_cocktail ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_avis_by_cocktail_multiple(
        db_connection,
    ) -> None:
        """Teste la récupération de plusieurs avis pour un cocktail."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES
                    ('alice', 'alice@example.com', 'pass', '1990-01-01'),
                    ('bob', 'bob@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            users = cursor.fetchall()
            alice_id = users[0]["id_utilisateur"]
            bob_id = users[1]["id_utilisateur"]

            cursor.execute(
                """
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Mojito', 'Cocktail', 'Highball', TRUE, 'img.jpg')
                RETURNING id_cocktail
            """,
            )
            cocktail_id = cursor.fetchone()["id_cocktail"]

            cursor.execute(
                """
                INSERT INTO avis (
                    id_utilisateur, id_cocktail, note,
                    commentaire, favoris
                )
                VALUES
                    (%s, %s, 8.0, 'Très bon!', FALSE),
                    (%s, %s, 9.0, 'Excellent!', TRUE)
            """,
                (alice_id, cocktail_id, bob_id, cocktail_id),
            )
            db_connection.commit()

        dao = AvisDAO()

        # WHEN
        result = dao.get_avis_by_cocktail(cocktail_id)

        # THEN
        nb_avis = 2
        if len(result) != nb_avis:
            raise AssertionError(
                message=f"2 avis attendus, obtenu: {len(result)}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_avis_by_cocktail_empty(
        db_connection,
    ) -> None:
        """Teste la récupération quand il n'y a pas d'avis."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Mojito', 'Cocktail', 'Highball', TRUE, 'img.jpg')
                RETURNING id_cocktail
            """,
            )
            cocktail_id = cursor.fetchone()["id_cocktail"]
            db_connection.commit()

        dao = AvisDAO()

        # WHEN
        result = dao.get_avis_by_cocktail(cocktail_id)

        # THEN
        if len(result) != 0:
            raise AssertionError(
                message=f"0 avis attendus, obtenu: {len(result)}",
            )

    # ========== Tests pour get_avis_by_user ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_avis_by_user_multiple(
        db_connection,
    ) -> None:
        """Teste la récupération de plusieurs avis d'un utilisateur."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('eve', 'eve@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute(
                """
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES
                    ('Mojito', 'Cocktail', 'Highball', TRUE, 'img.jpg'),
                    ('Margarita', 'Cocktail', 'Coupe', TRUE, 'img.jpg')
                RETURNING id_cocktail
            """,
            )
            cocktails = cursor.fetchall()
            mojito_id = cocktails[0]["id_cocktail"]
            margarita_id = cocktails[1]["id_cocktail"]

            cursor.execute(
                """
                INSERT INTO avis (
                    id_utilisateur, id_cocktail, note,
                    commentaire, favoris
                )
                VALUES
                    (%s, %s, 8.0, 'Bon', FALSE),
                    (%s, %s, 9.0, 'Excellent', TRUE)
            """,
                (user_id, mojito_id, user_id, margarita_id),
            )
            db_connection.commit()

        dao = AvisDAO()

        # WHEN
        result = dao.get_avis_by_user(user_id)

        # THEN
        nb_avis = 2
        if len(result) != nb_avis:
            raise AssertionError(
                message=f"2 avis attendus, obtenu: {len(result)}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_avis_by_user_empty(
        db_connection,
    ) -> None:
        """Teste la récupération quand l'utilisateur n'a pas d'avis."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('frank', 'frank@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]
            db_connection.commit()

        dao = AvisDAO()

        # WHEN
        result = dao.get_avis_by_user(user_id)

        # THEN
        if len(result) != 0:
            raise AssertionError(
                message=f"0 avis attendus, obtenu: {len(result)}",
            )

    # ========== Tests pour delete_avis ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_delete_avis_success(
        db_connection,
    ) -> None:
        """Teste la suppression d'un avis existant."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('grace', 'grace@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute(
                """
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Mojito', 'Cocktail', 'Highball', TRUE, 'img.jpg')
                RETURNING id_cocktail
            """,
            )
            cocktail_id = cursor.fetchone()["id_cocktail"]

            cursor.execute(
                """
                INSERT INTO avis (
                    id_utilisateur, id_cocktail, note,
                    commentaire, favoris
                )
                VALUES (%s, %s, 7.0, 'Correct', FALSE)
            """,
                (user_id, cocktail_id),
            )
            db_connection.commit()

        dao = AvisDAO()

        # WHEN
        result = dao.delete_avis(user_id, cocktail_id)

        # THEN
        if result is not True:
            raise AssertionError(
                message=f"La suppression devrait réussir, obtenu: {result}",
            )

        # Vérifier que l'avis n'existe plus
        avis = dao.get_avis_by_user_and_cocktail(user_id, cocktail_id)
        if avis is not None:
            raise AssertionError(
                message="L'avis ne devrait plus exister",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_delete_avis_inexistant(
        db_connection,
    ) -> None:
        """Teste la suppression d'un avis inexistant."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('henry', 'henry@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute(
                """
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Mojito', 'Cocktail', 'Highball', TRUE, 'img.jpg')
                RETURNING id_cocktail
            """,
            )
            cocktail_id = cursor.fetchone()["id_cocktail"]
            db_connection.commit()

        dao = AvisDAO()

        # WHEN
        result = dao.delete_avis(user_id, cocktail_id)

        # THEN
        if result is not False:
            raise AssertionError(
                message=f"La suppression devrait retourner False, obtenu: {result}",
            )

    # ========== Tests pour get_avis_summary ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_avis_summary_with_avis(
        db_connection,
    ) -> None:
        """Teste le résumé avec plusieurs avis."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES
                    ('alice', 'alice@example.com', 'pass', '1990-01-01'),
                    ('bob', 'bob@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            users = cursor.fetchall()
            alice_id = users[0]["id_utilisateur"]
            bob_id = users[1]["id_utilisateur"]

            cursor.execute(
                """
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Mojito', 'Cocktail', 'Highball', TRUE, 'img.jpg')
                RETURNING id_cocktail
            """,
            )
            cocktail_id = cursor.fetchone()["id_cocktail"]

            cursor.execute(
                """
                INSERT INTO avis (
                    id_utilisateur, id_cocktail, note,
                    commentaire, favoris
                )
                VALUES
                    (%s, %s, 8.0, 'Bon', TRUE),
                    (%s, %s, 10.0, 'Excellent', FALSE)
            """,
                (alice_id, cocktail_id, bob_id, cocktail_id),
            )
            db_connection.commit()

        dao = AvisDAO()

        # WHEN
        result = dao.get_avis_summary(cocktail_id)

        # THEN
        nb_avis = 2
        if result is None:
            raise AssertionError(message="Le résumé devrait exister")
        if result["nombre_avis"] != nb_avis:
            raise AssertionError(
                message=f"nombre_avis devrait être 2, obtenu: {result['nombre_avis']}",
            )
        note_moy = 9.0
        if result["note_moyenne"] != note_moy:
            raise AssertionError(
                message=f"note_moyenne devrait être 9.0, "
                f"obtenu: {result['note_moyenne']}",
            )
        if result["nombre_favoris"] != 1:
            raise AssertionError(
                message=f"nombre_favoris devrait être 1, "
                f"obtenu: {result['nombre_favoris']}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_avis_summary_no_avis(
        db_connection,
    ) -> None:
        """Teste le résumé sans avis."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Mojito', 'Cocktail', 'Highball', TRUE, 'img.jpg')
                RETURNING id_cocktail
            """,
            )
            cocktail_id = cursor.fetchone()["id_cocktail"]
        dao = AvisDAO()

        # WHEN
        result = dao.get_avis_summary(cocktail_id)

        # THEN
        if result is None:
            raise AssertionError(message="Le résumé devrait exister")
        if result["nombre_avis"] != 0:
            raise AssertionError(
                message=f"nombre_avis devrait être 0, obtenu: {result['nombre_avis']}",
            )
        if result["note_moyenne"] is not None:
            raise AssertionError(
                message=f"note_moyenne devrait être None, "
                f"obtenu: {result['note_moyenne']}",
            )

    # ========== Tests pour get_favoris_by_user ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_favoris_by_user_multiple(
        db_connection,
    ) -> None:
        """Teste la récupération de plusieurs favoris."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('iris', 'iris@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute(
                """
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES
                    ('Mojito', 'Cocktail', 'Highball', TRUE, 'img.jpg'),
                    ('Margarita', 'Cocktail', 'Coupe', TRUE, 'img.jpg'),
                    ('Daiquiri', 'Cocktail', 'Coupe', TRUE, 'img.jpg')
                RETURNING id_cocktail
            """,
            )
            cocktails = cursor.fetchall()
            mojito_id = cocktails[0]["id_cocktail"]
            margarita_id = cocktails[1]["id_cocktail"]
            daiquiri_id = cocktails[2]["id_cocktail"]

            cursor.execute(
                """
                INSERT INTO avis (
                    id_utilisateur, id_cocktail, note,
                    commentaire, favoris
                )
                VALUES
                    (%s, %s, 8.0, 'Bon', TRUE),
                    (%s, %s, 9.0, 'Excellent', FALSE),
                    (%s, %s, 7.0, 'Correct', TRUE)
            """,
                (
                    user_id,
                    mojito_id,
                    user_id,
                    margarita_id,
                    user_id,
                    daiquiri_id,
                ),
            )
            db_connection.commit()

        dao = AvisDAO()

        # WHEN
        result = dao.get_favoris_by_user(user_id)

        # THEN
        nb_fav = 2
        if len(result) != nb_fav:
            raise AssertionError(
                message=f"2 favoris attendus, obtenu: {len(result)}",
            )
        for avis in result:
            if avis["favoris"] is not True:
                raise AssertionError(
                    message="Tous les résultats devraient être des favoris",
                )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_favoris_by_user_empty(
        db_connection,
    ) -> None:
        """Teste la récupération quand il n'y a pas de favoris."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('jack', 'jack@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]
            db_connection.commit()

        dao = AvisDAO()

        # WHEN
        result = dao.get_favoris_by_user(user_id)

        # THEN
        if len(result) != 0:
            raise AssertionError(
                message=f"0 favoris attendus, obtenu: {len(result)}",
            )

    # ========== Tests pour add_favoris ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_add_favoris_nouveau(
        db_connection,
    ) -> None:
        """Teste l'ajout d'un nouveau favori."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('kate', 'kate@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute(
                """
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Mojito', 'Cocktail', 'Highball', TRUE, 'img.jpg')
                RETURNING id_cocktail
            """,
            )
            cocktail_id = cursor.fetchone()["id_cocktail"]
            db_connection.commit()

        dao = AvisDAO()

        # WHEN
        result = dao.add_favoris(user_id, cocktail_id)

        # THEN
        if result["favoris"] is not True:
            raise AssertionError(
                message=f"favoris devrait être True, obtenu: {result}",
            )
        if result["deja_en_favoris"] is not False:
            raise AssertionError(
                message=f"deja_en_favoris devrait être False, obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_add_favoris_deja_existant(
        db_connection,
    ) -> None:
        """Teste l'ajout d'un favori déjà existant."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('leo', 'leo@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute(
                """
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Mojito', 'Cocktail', 'Highball', TRUE, 'img.jpg')
                RETURNING id_cocktail
            """,
            )
            cocktail_id = cursor.fetchone()["id_cocktail"]

            cursor.execute(
                """
                INSERT INTO avis (
                    id_utilisateur, id_cocktail, note,
                    commentaire, favoris
                )
                VALUES (%s, %s, 8.0, 'Bon', TRUE)
            """,
                (user_id, cocktail_id),
            )
            db_connection.commit()

        dao = AvisDAO()

        # WHEN
        result = dao.add_favoris(user_id, cocktail_id)

        # THEN
        if result["deja_en_favoris"] is not True:
            raise AssertionError(
                message=f"deja_en_favoris devrait être True, obtenu: {result}",
            )

    # ========== Tests pour remove_favoris ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_remove_favoris_success(
        db_connection,
    ) -> None:
        """Teste le retrait d'un favori existant."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('mike', 'mike@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute(
                """
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Mojito', 'Cocktail', 'Highball', TRUE, 'img.jpg')
                RETURNING id_cocktail
            """,
            )
            cocktail_id = cursor.fetchone()["id_cocktail"]

            cursor.execute(
                """
                INSERT INTO avis (
                    id_utilisateur, id_cocktail, note,
                    commentaire, favoris
                )
                VALUES (%s, %s, 8.0, 'Bon', TRUE)
            """,
                (user_id, cocktail_id),
            )
            db_connection.commit()

        dao = AvisDAO()

        # WHEN
        result = dao.remove_favoris(user_id, cocktail_id)

        # THEN
        if result is not True:
            raise AssertionError(
                message=f"Le retrait devrait réussir, obtenu: {result}",
            )

        # Vérifier que ce n'est plus un favori
        avis = dao.get_avis_by_user_and_cocktail(user_id, cocktail_id)
        if avis["favoris"] is not False:
            raise AssertionError(
                message="favoris devrait être False après le retrait",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_remove_favoris_non_favori(
        db_connection,
    ) -> None:
        """Teste le retrait d'un favori qui n'est pas en favoris."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('nina', 'nina@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute(
                """
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Mojito', 'Cocktail', 'Highball', TRUE, 'img.jpg')
                RETURNING id_cocktail
            """,
            )
            cocktail_id = cursor.fetchone()["id_cocktail"]

            cursor.execute(
                """
                INSERT INTO avis (
                    id_utilisateur, id_cocktail, note,
                    commentaire, favoris
                )
                VALUES (%s, %s, 8.0, 'Bon', FALSE)
            """,
                (user_id, cocktail_id),
            )
            db_connection.commit()

        dao = AvisDAO()

        # WHEN
        result = dao.remove_favoris(user_id, cocktail_id)

        # THEN
        if result is not False:
            raise AssertionError(
                message=f"Le retrait devrait retourner False, obtenu: {result}",
            )
