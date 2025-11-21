"""Tests d'intégration pour ListeCourseDAO."""

import pytest

from src.dao.liste_course_dao import ListeCourseDAO


class TestListeCourseDAOIntegration:
    """Tests d'intégration pour ListeCourseDAO."""

    # ========== Tests pour get_liste_course ==========

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_liste_course_vide(db_connection) -> None:
        """Teste la récupération d'une liste de course vide."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('testuser', 'test@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]
            db_connection.commit()

        dao = ListeCourseDAO()

        # WHEN
        result = dao.get_liste_course(user_id)

        # THEN
        if len(result) != 0:
            raise AssertionError(
                message=f"La liste devrait être vide, obtenu: {len(result)} items",
            )
        if not isinstance(result, list):
            raise TypeError(
                message=f"Le résultat devrait être une liste, obtenu: {type(result)}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_liste_course_avec_items(db_connection) -> None:
        """Teste la récupération d'une liste avec des items."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('testuser', 'test@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute(
                """
                INSERT INTO ingredient (nom, alcool)
                VALUES ('Rhum', TRUE), ('Menthe', FALSE)
                RETURNING id_ingredient
            """,
            )
            ingredients = cursor.fetchall()
            rhum_id = ingredients[0]["id_ingredient"]
            menthe_id = ingredients[1]["id_ingredient"]

            cursor.execute(
                """
                INSERT INTO unite (nom, abbreviation, type_unite)
                VALUES ('millilitre', 'ml', 'liquide')
                RETURNING id_unite
            """,
            )
            unite_id = cursor.fetchone()["id_unite"]

            cursor.execute(
                """
                INSERT INTO liste_course (
                    id_utilisateur, id_ingredient, quantite, id_unite, effectue
                )
                VALUES
                    (%s, %s, 50.0, %s, FALSE),
                    (%s, %s, 10.0, %s, TRUE)
            """,
                (user_id, rhum_id, unite_id, user_id, menthe_id, unite_id),
            )
            db_connection.commit()

        dao = ListeCourseDAO()

        # WHEN
        result = dao.get_liste_course(user_id)

        # THEN
        nb_item = 2
        if len(result) != nb_item:
            raise AssertionError(
                message=f"2 items attendus, obtenu: {len(result)}",
            )

        # Vérifier l'ordre : effectue = FALSE d'abord
        if result[0]["effectue"] is not False:
            raise AssertionError(
                message="Le premier item devrait avoir effectue = FALSE",
            )
        if result[1]["effectue"] is not True:
            raise AssertionError(
                message="Le deuxième item devrait avoir effectue = TRUE",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_liste_course_ordre_alphabetique(db_connection) -> None:
        """Teste que les items sont triés alphabétiquement."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('testuser', 'test@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute(
                """
                INSERT INTO ingredient (nom, alcool)
                VALUES ('Vodka', TRUE), ('Gin', TRUE), ('Rhum', TRUE)
                RETURNING id_ingredient
            """,
            )
            ingredients = cursor.fetchall()

            cursor.execute(
                """
                INSERT INTO unite (nom, abbreviation, type_unite)
                VALUES ('millilitre', 'ml', 'liquide')
                RETURNING id_unite
            """,
            )
            unite_id = cursor.fetchone()["id_unite"]

            for ing in ingredients:
                cursor.execute(
                    """
                    INSERT INTO liste_course (
                        id_utilisateur, id_ingredient, quantite,
                        id_unite, effectue
                    )
                    VALUES (%s, %s, 50.0, %s, FALSE)
                """,
                    (user_id, ing["id_ingredient"], unite_id),
                )
            db_connection.commit()

        dao = ListeCourseDAO()

        # WHEN
        result = dao.get_liste_course(user_id)

        # THEN
        noms = [r["nom_ingredient"] for r in result]
        noms_tries = sorted(noms)
        if noms != noms_tries:
            raise AssertionError(
                message=f"Les noms devraient être triés alphabétiquement, "
                f"obtenu: {noms}, attendu: {noms_tries}",
            )

    # ========== Tests pour add_to_liste_course ==========

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_add_to_liste_course_nouvel_item(db_connection) -> None:
        """Teste l'ajout d'un nouvel item à la liste."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('testuser', 'test@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute(
                """
                INSERT INTO ingredient (nom, alcool)
                VALUES ('Rhum', TRUE)
                RETURNING id_ingredient
            """,
            )
            ingredient_id = cursor.fetchone()["id_ingredient"]

            cursor.execute(
                """
                INSERT INTO unite (nom, abbreviation, type_unite)
                VALUES ('millilitre', 'ml', 'liquide')
                RETURNING id_unite
            """,
            )
            unite_id = cursor.fetchone()["id_unite"]
            db_connection.commit()

        dao = ListeCourseDAO()

        # WHEN
        result = dao.add_to_liste_course(
            id_utilisateur=user_id,
            id_ingredient=ingredient_id,
            quantite=50.0,
            id_unite=unite_id,
        )

        # THEN
        if result is None:
            raise AssertionError(
                message="Le résultat ne devrait pas être None",
            )
        if result["id_ingredient"] != ingredient_id:
            raise AssertionError(
                message=f"L'ingredient_id devrait être {ingredient_id}, "
                f"obtenu: {result['id_ingredient']}",
            )
        qte = 50.0
        if float(result["quantite"]) != qte:
            raise AssertionError(
                message=f"La quantité devrait être 50.0, obtenu: {result['quantite']}",
            )
        if result["effectue"] is not False:
            raise AssertionError(
                message="effectue devrait être False pour un nouvel item",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_add_to_liste_course_meme_unite_cumul(db_connection) -> None:
        """Teste l'ajout avec la même unité (cumul)."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('testuser', 'test@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute(
                """
                INSERT INTO ingredient (nom, alcool)
                VALUES ('Rhum', TRUE)
                RETURNING id_ingredient
            """,
            )
            ingredient_id = cursor.fetchone()["id_ingredient"]

            cursor.execute(
                """
                INSERT INTO unite (nom, abbreviation, type_unite)
                VALUES ('millilitre', 'ml', 'liquide')
                RETURNING id_unite
            """,
            )
            unite_id = cursor.fetchone()["id_unite"]

            # Ajouter un item initial
            cursor.execute(
                """
                INSERT INTO liste_course (
                    id_utilisateur, id_ingredient, quantite, id_unite, effectue
                )
                VALUES (%s, %s, 100.0, %s, FALSE)
            """,
                (user_id, ingredient_id, unite_id),
            )
            db_connection.commit()

        dao = ListeCourseDAO()

        # WHEN - Ajouter 50ml à un item existant de 100ml
        result = dao.add_to_liste_course(
            id_utilisateur=user_id,
            id_ingredient=ingredient_id,
            quantite=50.0,
            id_unite=unite_id,
        )

        # THEN - Devrait être 150ml
        qte = 150.0
        if float(result["quantite"]) != qte:
            raise AssertionError(
                message=f"La quantité devrait être 150.0 (100+50), "
                f"obtenu: {result['quantite']}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_add_to_liste_course_unite_differente_remplace(
        db_connection,
    ) -> None:
        """Teste l'ajout avec une unité différente (remplacement)."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('testuser', 'test@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute(
                """
                INSERT INTO ingredient (nom, alcool)
                VALUES ('Sucre', FALSE)
                RETURNING id_ingredient
            """,
            )
            ingredient_id = cursor.fetchone()["id_ingredient"]

            cursor.execute(
                """
                INSERT INTO unite (nom, abbreviation, type_unite)
                VALUES
                    ('gramme', 'g', 'poids'),
                    ('kilogramme', 'kg', 'poids')
                RETURNING id_unite
            """,
            )
            unites = cursor.fetchall()
            unite_g_id = unites[0]["id_unite"]
            unite_kg_id = unites[1]["id_unite"]

            # Ajouter un item initial en grammes
            cursor.execute(
                """
                INSERT INTO liste_course (
                    id_utilisateur, id_ingredient, quantite, id_unite, effectue
                )
                VALUES (%s, %s, 100.0, %s, FALSE)
            """,
                (user_id, ingredient_id, unite_g_id),
            )
            db_connection.commit()

        dao = ListeCourseDAO()

        # WHEN - Ajouter en kg (type différent de liquide)
        result = dao.add_to_liste_course(
            id_utilisateur=user_id,
            id_ingredient=ingredient_id,
            quantite=2.0,
            id_unite=unite_kg_id,
        )

        # THEN - Devrait remplacer (pas de conversion pour non-liquides)
        qte = 2.0
        if float(result["quantite"]) != qte:
            raise AssertionError(
                message=f"La quantité devrait être remplacée à 2.0, "
                f"obtenu: {result['quantite']}",
            )
        if result["id_unite"] != unite_kg_id:
            raise AssertionError(
                message=f"L'unité devrait être changée à {unite_kg_id}, "
                f"obtenu: {result['id_unite']}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_add_to_liste_course_remet_effectue_a_false(
        db_connection,
    ) -> None:
        """Teste que l'ajout remet effectue à False."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('testuser', 'test@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute(
                """
                INSERT INTO ingredient (nom, alcool)
                VALUES ('Rhum', TRUE)
                RETURNING id_ingredient
            """,
            )
            ingredient_id = cursor.fetchone()["id_ingredient"]

            cursor.execute(
                """
                INSERT INTO unite (nom, abbreviation, type_unite)
                VALUES ('millilitre', 'ml', 'liquide')
                RETURNING id_unite
            """,
            )
            unite_id = cursor.fetchone()["id_unite"]

            # Ajouter un item marqué comme effectué
            cursor.execute(
                """
                INSERT INTO liste_course (
                    id_utilisateur, id_ingredient, quantite, id_unite, effectue
                )
                VALUES (%s, %s, 100.0, %s, TRUE)
            """,
                (user_id, ingredient_id, unite_id),
            )
            db_connection.commit()

        dao = ListeCourseDAO()

        # WHEN
        result = dao.add_to_liste_course(
            id_utilisateur=user_id,
            id_ingredient=ingredient_id,
            quantite=50.0,
            id_unite=unite_id,
        )

        # THEN
        if result["effectue"] is not False:
            raise AssertionError(
                message="effectue devrait être remis à False après ajout",
            )

    # ========== Tests pour get_liste_course_item ==========

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_liste_course_item_existant(db_connection) -> None:
        """Teste la récupération d'un item existant."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('testuser', 'test@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute(
                """
                INSERT INTO ingredient (nom, alcool)
                VALUES ('Rhum', TRUE)
                RETURNING id_ingredient
            """,
            )
            ingredient_id = cursor.fetchone()["id_ingredient"]

            cursor.execute(
                """
                INSERT INTO unite (nom, abbreviation, type_unite)
                VALUES ('millilitre', 'ml', 'liquide')
                RETURNING id_unite
            """,
            )
            unite_id = cursor.fetchone()["id_unite"]

            cursor.execute(
                """
                INSERT INTO liste_course (
                    id_utilisateur, id_ingredient, quantite, id_unite, effectue
                )
                VALUES (%s, %s, 100.0, %s, FALSE)
            """,
                (user_id, ingredient_id, unite_id),
            )
            db_connection.commit()

        dao = ListeCourseDAO()

        # WHEN
        result = dao.get_liste_course_item(user_id, ingredient_id)

        # THEN
        if result is None:
            raise AssertionError(
                message="L'item devrait être trouvé",
            )
        qte = 100.0
        if float(result["quantite"]) != qte:
            raise AssertionError(
                message=f"La quantité devrait être 100.0, obtenu: {result['quantite']}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_liste_course_item_inexistant(db_connection) -> None:
        """Teste la récupération d'un item inexistant."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('testuser', 'test@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]
            db_connection.commit()

        dao = ListeCourseDAO()

        # WHEN
        result = dao.get_liste_course_item(user_id, 99999)

        # THEN
        if result is not None:
            raise AssertionError(
                message=f"Le résultat devrait être None, obtenu: {result}",
            )

    # ========== Tests pour remove_from_liste_course ==========

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_remove_from_liste_course_reussi(db_connection) -> None:
        """Teste la suppression d'un item existant."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('testuser', 'test@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute(
                """
                INSERT INTO ingredient (nom, alcool)
                VALUES ('Rhum', TRUE)
                RETURNING id_ingredient
            """,
            )
            ingredient_id = cursor.fetchone()["id_ingredient"]

            cursor.execute(
                """
                INSERT INTO unite (nom, abbreviation, type_unite)
                VALUES ('millilitre', 'ml', 'liquide')
                RETURNING id_unite
            """,
            )
            unite_id = cursor.fetchone()["id_unite"]

            cursor.execute(
                """
                INSERT INTO liste_course (
                    id_utilisateur, id_ingredient, quantite, id_unite, effectue
                )
                VALUES (%s, %s, 100.0, %s, FALSE)
            """,
                (user_id, ingredient_id, unite_id),
            )
            db_connection.commit()

        dao = ListeCourseDAO()

        # WHEN
        result = dao.remove_from_liste_course(user_id, ingredient_id)

        # THEN
        if result is not True:
            raise AssertionError(
                message=f"La suppression devrait réussir, obtenu: {result}",
            )

        # Vérifier que l'item n'existe plus
        item = dao.get_liste_course_item(user_id, ingredient_id)
        if item is not None:
            raise AssertionError(
                message="L'item ne devrait plus exister",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_remove_from_liste_course_inexistant(db_connection) -> None:
        """Teste la suppression d'un item inexistant."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('testuser', 'test@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]
            db_connection.commit()

        dao = ListeCourseDAO()

        # WHEN
        result = dao.remove_from_liste_course(user_id, 99999)

        # THEN
        if result is not False:
            raise AssertionError(
                message=f"La suppression devrait retourner False, obtenu: {result}",
            )

    # ========== Tests pour clear_liste_course ==========

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_clear_liste_course_avec_items(db_connection) -> None:
        """Teste le vidage d'une liste avec des items."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('testuser', 'test@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute(
                """
                INSERT INTO ingredient (nom, alcool)
                VALUES ('Rhum', TRUE), ('Vodka', TRUE), ('Gin', TRUE)
                RETURNING id_ingredient
            """,
            )
            ingredients = cursor.fetchall()

            cursor.execute(
                """
                INSERT INTO unite (nom, abbreviation, type_unite)
                VALUES ('millilitre', 'ml', 'liquide')
                RETURNING id_unite
            """,
            )
            unite_id = cursor.fetchone()["id_unite"]

            for ing in ingredients:
                cursor.execute(
                    """
                    INSERT INTO liste_course (
                        id_utilisateur, id_ingredient, quantite,
                        id_unite, effectue
                    )
                    VALUES (%s, %s, 50.0, %s, FALSE)
                """,
                    (user_id, ing["id_ingredient"], unite_id),
                )
            db_connection.commit()

        dao = ListeCourseDAO()

        # WHEN
        result = dao.clear_liste_course(user_id)

        # THEN
        nb_item = 3
        if result != nb_item:
            raise AssertionError(
                message=f"3 items devraient être supprimés, obtenu: {result}",
            )

        # Vérifier que la liste est vide
        liste = dao.get_liste_course(user_id)
        if len(liste) != 0:
            raise AssertionError(
                message=f"La liste devrait être vide, obtenu: {len(liste)} items",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_clear_liste_course_deja_vide(db_connection) -> None:
        """Teste le vidage d'une liste déjà vide."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('testuser', 'test@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]
            db_connection.commit()

        dao = ListeCourseDAO()

        # WHEN
        result = dao.clear_liste_course(user_id)

        # THEN
        if result != 0:
            raise AssertionError(
                message=f"0 items devraient être supprimés, obtenu: {result}",
            )

    # ========== Tests pour toggle_effectue ==========

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_toggle_effectue_false_vers_true(db_connection) -> None:
        """Teste le toggle de False vers True."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('testuser', 'test@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute(
                """
                INSERT INTO ingredient (nom, alcool)
                VALUES ('Rhum', TRUE)
                RETURNING id_ingredient
            """,
            )
            ingredient_id = cursor.fetchone()["id_ingredient"]

            cursor.execute(
                """
                INSERT INTO unite (nom, abbreviation, type_unite)
                VALUES ('millilitre', 'ml', 'liquide')
                RETURNING id_unite
            """,
            )
            unite_id = cursor.fetchone()["id_unite"]

            cursor.execute(
                """
                INSERT INTO liste_course (
                    id_utilisateur, id_ingredient, quantite, id_unite, effectue
                )
                VALUES (%s, %s, 100.0, %s, FALSE)
            """,
                (user_id, ingredient_id, unite_id),
            )
            db_connection.commit()

        dao = ListeCourseDAO()

        # WHEN
        result = dao.toggle_effectue(user_id, ingredient_id)

        # THEN
        if result is not True:
            raise AssertionError(
                message=f"Le statut devrait être True, obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_toggle_effectue_true_vers_false(db_connection) -> None:
        """Teste le toggle de True vers False."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('testuser', 'test@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute(
                """
                INSERT INTO ingredient (nom, alcool)
                VALUES ('Rhum', TRUE)
                RETURNING id_ingredient
            """,
            )
            ingredient_id = cursor.fetchone()["id_ingredient"]

            cursor.execute(
                """
                INSERT INTO unite (nom, abbreviation, type_unite)
                VALUES ('millilitre', 'ml', 'liquide')
                RETURNING id_unite
            """,
            )
            unite_id = cursor.fetchone()["id_unite"]

            cursor.execute(
                """
                INSERT INTO liste_course (
                    id_utilisateur, id_ingredient, quantite, id_unite, effectue
                )
                VALUES (%s, %s, 100.0, %s, TRUE)
            """,
                (user_id, ingredient_id, unite_id),
            )
            db_connection.commit()

        dao = ListeCourseDAO()

        # WHEN
        result = dao.toggle_effectue(user_id, ingredient_id)

        # THEN
        if result is not False:
            raise AssertionError(
                message=f"Le statut devrait être False, obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_toggle_effectue_plusieurs_fois(db_connection) -> None:
        """Teste plusieurs toggles successifs."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('testuser', 'test@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]

            cursor.execute(
                """
                INSERT INTO ingredient (nom, alcool)
                VALUES ('Rhum', TRUE)
                RETURNING id_ingredient
            """,
            )
            ingredient_id = cursor.fetchone()["id_ingredient"]

            cursor.execute(
                """
                INSERT INTO unite (nom, abbreviation, type_unite)
                VALUES ('millilitre', 'ml', 'liquide')
                RETURNING id_unite
            """,
            )
            unite_id = cursor.fetchone()["id_unite"]

            cursor.execute(
                """
                INSERT INTO liste_course (
                    id_utilisateur, id_ingredient, quantite, id_unite, effectue
                )
                VALUES (%s, %s, 100.0, %s, FALSE)
            """,
                (user_id, ingredient_id, unite_id),
            )
            db_connection.commit()

        dao = ListeCourseDAO()

        # WHEN
        result_1 = dao.toggle_effectue(user_id, ingredient_id)
        result_2 = dao.toggle_effectue(user_id, ingredient_id)
        result_3 = dao.toggle_effectue(user_id, ingredient_id)

        # THEN
        if result_1 is not True:
            raise AssertionError(
                message=f"Le 1er toggle devrait donner True, obtenu: {result_1}",
            )
        if result_2 is not False:
            raise AssertionError(
                message=f"Le 2e toggle devrait donner False, obtenu: {result_2}",
            )
        if result_3 is not True:
            raise AssertionError(
                message=f"Le 3e toggle devrait donner True, obtenu: {result_3}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_toggle_effectue_item_inexistant(db_connection) -> None:
        """Teste le toggle sur un item inexistant."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO utilisateur (
                    pseudo, mail, mot_de_passe, date_naissance
                )
                VALUES ('testuser', 'test@example.com', 'pass', '1990-01-01')
                RETURNING id_utilisateur
            """,
            )
            user_id = cursor.fetchone()["id_utilisateur"]
            db_connection.commit()

        dao = ListeCourseDAO()

        # WHEN
        result = dao.toggle_effectue(user_id, 99999)

        # THEN
        if result is not False:
            raise AssertionError(
                message=f"Le résultat devrait être False pour un item "
                f"inexistant, obtenu: {result}",
            )
