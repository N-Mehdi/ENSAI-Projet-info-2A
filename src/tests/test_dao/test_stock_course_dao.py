"""Tests d'intégration pour StockCourseDAO."""

import pytest

from src.dao.stock_course_dao import StockCourseDAO
from src.utils.exceptions import (
    IngredientNotFoundError,
    InvalidQuantityError,
)


class TestStockCourseDAOIntegration:
    """Tests d'intégration pour StockCourseDAO."""

    # ========== Tests pour update_or_create_stock_item ==========

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_update_or_create_nouveau_stock(db_connection) -> None:
        """Teste la création d'un nouvel item de stock."""
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

        dao = StockCourseDAO()

        # WHEN
        result = dao.update_or_create_stock_item(
            id_utilisateur=user_id,
            id_ingredient=ingredient_id,
            quantite=50.0,
            id_unite=unite_id,
        )

        # THEN
        if result is not True:
            raise AssertionError(
                message=f"La création devrait réussir, obtenu: {result}",
            )

        # Vérifier que l'item a été créé
        stock_item = dao.get_stock_item(user_id, ingredient_id)
        if stock_item is None:
            raise AssertionError(
                message="L'item de stock devrait être créé",
            )
        qte = 50.0
        if float(stock_item["quantite"]) != qte:
            raise AssertionError(
                message=f"La quantité devrait être 50.0, "
                f"obtenu: {stock_item['quantite']}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_update_or_create_cumul_quantite(db_connection) -> None:
        """Teste la mise à jour avec cumul de quantité."""
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

            # Créer un stock initial de 100
            cursor.execute(
                """
                INSERT INTO stock (
                    id_utilisateur, id_ingredient, quantite, id_unite
                )
                VALUES (%s, %s, 100.0, %s)
            """,
                (user_id, ingredient_id, unite_id),
            )
            db_connection.commit()

        dao = StockCourseDAO()

        # WHEN - Ajouter 50 à un stock de 100
        result = dao.update_or_create_stock_item(
            id_utilisateur=user_id,
            id_ingredient=ingredient_id,
            quantite=50.0,
            id_unite=unite_id,
        )

        # THEN
        if result is not True:
            raise AssertionError(
                message=f"La mise à jour devrait réussir, obtenu: {result}",
            )

        # Vérifier le cumul : 100 + 50 = 150
        stock_item = dao.get_stock_item(user_id, ingredient_id)
        qte = 150.0
        if float(stock_item["quantite"]) != qte:
            raise AssertionError(
                message=f"La quantité devrait être 150.0 (100+50), "
                f"obtenu: {stock_item['quantite']}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_update_or_create_change_unite(db_connection) -> None:
        """Teste que l'unité est mise à jour lors du cumul."""
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
            unite_ml_id = cursor.fetchone()["id_unite"]

            cursor.execute(
                """
                INSERT INTO unite (nom, abbreviation, type_unite)
                VALUES ('centilitre', 'cl', 'liquide')
                RETURNING id_unite
            """,
            )
            unite_cl_id = cursor.fetchone()["id_unite"]

            cursor.execute(
                """
                INSERT INTO stock (
                    id_utilisateur, id_ingredient, quantite, id_unite
                )
                VALUES (%s, %s, 100.0, %s)
            """,
                (user_id, ingredient_id, unite_ml_id),
            )
            db_connection.commit()

        dao = StockCourseDAO()

        # WHEN - Ajouter avec une nouvelle unité
        result = dao.update_or_create_stock_item(
            id_utilisateur=user_id,
            id_ingredient=ingredient_id,
            quantite=50.0,
            id_unite=unite_cl_id,
        )

        # THEN
        if result is not True:
            raise AssertionError(
                message=f"La mise à jour devrait réussir, obtenu: {result}",
            )

        # Vérifier que l'unité a changé
        stock_item = dao.get_stock_item(user_id, ingredient_id)
        if stock_item["id_unite"] != unite_cl_id:
            raise AssertionError(
                message=f"L'unité devrait être {unite_cl_id}, "
                f"obtenu: {stock_item['id_unite']}",
            )

    # ========== Tests pour get_stock ==========

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_stock_disponible(db_connection) -> None:
        """Teste la récupération du stock avec quantité > 0."""
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
                INSERT INTO stock (
                    id_utilisateur, id_ingredient, quantite, id_unite
                )
                VALUES (%s, %s, 100.0, %s)
            """,
                (user_id, ingredient_id, unite_id),
            )
            db_connection.commit()

        dao = StockCourseDAO()

        # WHEN
        result = dao.get_stock(user_id, only_available=True)

        # THEN
        if len(result) != 1:
            raise AssertionError(
                message=f"1 item attendu, obtenu: {len(result)}",
            )
        if result[0]["id_ingredient"] != ingredient_id:
            raise AssertionError(
                message=f"L'ingredient_id devrait être {ingredient_id}, "
                f"obtenu: {result[0]['id_ingredient']}",
            )
        qte = 100.0
        if float(result[0]["quantite"]) != qte:
            raise AssertionError(
                message=f"La quantité devrait être 100.0, "
                f"obtenu: {result[0]['quantite']}",
            )
        if result[0]["nom_ingredient"] != "Rhum":
            raise AssertionError(
                message=f"Le nom devrait être 'Rhum', "
                f"obtenu: {result[0]['nom_ingredient']}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_stock_exclut_quantite_zero(db_connection) -> None:
        """Teste que les items avec quantité 0 ne sont pas retournés."""
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
                VALUES ('Rhum', TRUE), ('Vodka', TRUE)
                RETURNING id_ingredient
            """,
            )
            ingredients = cursor.fetchall()
            rhum_id = ingredients[0]["id_ingredient"]
            vodka_id = ingredients[1]["id_ingredient"]

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
                INSERT INTO stock (
                    id_utilisateur, id_ingredient, quantite, id_unite
                )
                VALUES (%s, %s, 100.0, %s), (%s, %s, 0.0, %s)
            """,
                (user_id, rhum_id, unite_id, user_id, vodka_id, unite_id),
            )
            db_connection.commit()

        dao = StockCourseDAO()

        # WHEN
        result = dao.get_stock(user_id, only_available=True)

        # THEN
        if len(result) != 1:
            raise AssertionError(
                message=f"1 item attendu (Vodka exclu), obtenu: {len(result)}",
            )

        ingredient_ids = [r["id_ingredient"] for r in result]
        if vodka_id in ingredient_ids:
            raise AssertionError(
                message="La Vodka (quantité 0) ne devrait pas être retournée",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_stock_tous_ingredients(db_connection) -> None:
        """Teste la récupération de tous les items (y compris quantité 0)."""
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
                VALUES ('Rhum', TRUE), ('Vodka', TRUE)
                RETURNING id_ingredient
            """,
            )
            ingredients = cursor.fetchall()
            rhum_id = ingredients[0]["id_ingredient"]
            vodka_id = ingredients[1]["id_ingredient"]

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
                INSERT INTO stock (
                    id_utilisateur, id_ingredient, quantite, id_unite
                )
                VALUES (%s, %s, 100.0, %s), (%s, %s, 0.0, %s)
            """,
                (user_id, rhum_id, unite_id, user_id, vodka_id, unite_id),
            )
            db_connection.commit()

        dao = StockCourseDAO()

        # WHEN
        result = dao.get_stock(user_id, only_available=False)

        # THEN
        nb_item = 2
        if len(result) != nb_item:
            raise AssertionError(
                message=f"2 items attendus, obtenu: {len(result)}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_stock_vide(db_connection) -> None:
        """Teste avec un utilisateur sans stock."""
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

        dao = StockCourseDAO()

        # WHEN
        result = dao.get_stock(user_id, only_available=True)

        # THEN
        if len(result) != 0:
            raise AssertionError(
                message=f"0 items attendus, obtenu: {len(result)}",
            )
        if not isinstance(result, list):
            raise TypeError(
                message=f"Le résultat devrait être une liste, obtenu: {type(result)}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_stock_ordre_alphabetique(db_connection) -> None:
        """Teste que les résultats sont triés par nom d'ingrédient."""
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
                    INSERT INTO stock (
                        id_utilisateur, id_ingredient, quantite, id_unite
                    )
                    VALUES (%s, %s, 50.0, %s)
                """,
                    (user_id, ing["id_ingredient"], unite_id),
                )
            db_connection.commit()

        dao = StockCourseDAO()

        # WHEN
        result = dao.get_stock(user_id, only_available=True)

        # THEN
        noms = [r["nom_ingredient"] for r in result]
        noms_tries = sorted(noms)
        if noms != noms_tries:
            raise AssertionError(
                message=f"Les noms devraient être triés alphabétiquement, "
                f"obtenu: {noms}, attendu: {noms_tries}",
            )

    # ========== Tests pour get_stock_item ==========

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_stock_item_existant(db_connection) -> None:
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
                INSERT INTO stock (
                    id_utilisateur, id_ingredient, quantite, id_unite
                )
                VALUES (%s, %s, 100.0, %s)
            """,
                (user_id, ingredient_id, unite_id),
            )
            db_connection.commit()

        dao = StockCourseDAO()

        # WHEN
        result = dao.get_stock_item(user_id, ingredient_id)

        # THEN
        if result is None:
            raise AssertionError(
                message="L'item devrait être trouvé",
            )
        if result["id_ingredient"] != ingredient_id:
            raise AssertionError(
                message=f"L'ingredient_id devrait être {ingredient_id}, "
                f"obtenu: {result['id_ingredient']}",
            )
        qte = 100.0
        if float(result["quantite"]) != qte:
            raise AssertionError(
                message=f"La quantité devrait être 100.0, obtenu: {result['quantite']}",
            )
        if result["nom_ingredient"] != "Rhum":
            raise AssertionError(
                message=f"Le nom devrait être 'Rhum', "
                f"obtenu: {result['nom_ingredient']}",
            )
        if result["code_unite"] != "ml":
            raise AssertionError(
                message=f"Le code_unite devrait être 'ml', "
                f"obtenu: {result['code_unite']}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_stock_item_inexistant(db_connection) -> None:
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

        dao = StockCourseDAO()

        # WHEN
        result = dao.get_stock_item(user_id, 99999)

        # THEN
        if result is not None:
            raise AssertionError(
                message=f"Le résultat devrait être None, obtenu: {result}",
            )

    # ========== Tests pour decrement_stock_item ==========

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_decrement_stock_item_normal(db_connection) -> None:
        """Teste un décrément normal."""
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
                INSERT INTO stock (
                    id_utilisateur, id_ingredient, quantite, id_unite
                )
                VALUES (%s, %s, 100.0, %s)
            """,
                (user_id, ingredient_id, unite_id),
            )
            db_connection.commit()

        dao = StockCourseDAO()

        # WHEN
        result = dao.decrement_stock_item(
            id_utilisateur=user_id,
            id_ingredient=ingredient_id,
            quantite=30.0,
        )

        # THEN
        qte = 70.0
        if result["nouvelle_quantite"] != qte:
            raise AssertionError(
                message=f"La nouvelle quantité devrait être 70.0, "
                f"obtenu: {result['nouvelle_quantite']}",
            )
        if result["supprime"] is not False:
            raise AssertionError(
                message=f"supprime devrait être False, obtenu: {result['supprime']}",
            )

        # Vérifier en base
        stock_item = dao.get_stock_item(user_id, ingredient_id)
        qte = 70.0
        if float(stock_item["quantite"]) != qte:
            raise AssertionError(
                message=f"La quantité en base devrait être 70.0, "
                f"obtenu: {stock_item['quantite']}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_decrement_stock_item_jusqu_a_zero(db_connection) -> None:
        """Teste un décrément jusqu'à zéro (suppression)."""
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
                INSERT INTO stock (
                    id_utilisateur, id_ingredient, quantite, id_unite
                )
                VALUES (%s, %s, 100.0, %s)
            """,
                (user_id, ingredient_id, unite_id),
            )
            db_connection.commit()

        dao = StockCourseDAO()

        # WHEN
        result = dao.decrement_stock_item(
            id_utilisateur=user_id,
            id_ingredient=ingredient_id,
            quantite=100.0,
        )

        # THEN
        if result["nouvelle_quantite"] != 0.0:
            raise AssertionError(
                message=f"La nouvelle quantité devrait être 0.0, "
                f"obtenu: {result['nouvelle_quantite']}",
            )
        if result["supprime"] is not True:
            raise AssertionError(
                message=f"supprime devrait être True, obtenu: {result['supprime']}",
            )

        # Vérifier que l'item a été supprimé
        stock_item = dao.get_stock_item(user_id, ingredient_id)
        if stock_item is not None:
            raise AssertionError(
                message="L'item devrait être supprimé de la base",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_decrement_stock_item_presque_zero(db_connection) -> None:
        """Teste un décrément qui laisse une quantité très petite."""
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
                INSERT INTO stock (
                    id_utilisateur, id_ingredient, quantite, id_unite
                )
                VALUES (%s, %s, 100.0, %s)
            """,
                (user_id, ingredient_id, unite_id),
            )
            db_connection.commit()

        dao = StockCourseDAO()

        # WHEN
        result = dao.decrement_stock_item(
            id_utilisateur=user_id,
            id_ingredient=ingredient_id,
            quantite=99.99999,
        )

        # THEN - Devrait être considéré comme 0 et supprimé (tolérance)
        if result["nouvelle_quantite"] != 0.0:
            raise AssertionError(
                message=f"La nouvelle quantité devrait être 0.0 (tolérance), "
                f"obtenu: {result['nouvelle_quantite']}",
            )
        if result["supprime"] is not True:
            raise AssertionError(
                message=f"supprime devrait être True (tolérance), "
                f"obtenu: {result['supprime']}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_decrement_stock_item_quantite_superieure(
        db_connection,
    ) -> None:
        """Teste un décrément avec quantité supérieure au stock."""
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
                INSERT INTO stock (
                    id_utilisateur, id_ingredient, quantite, id_unite
                )
                VALUES (%s, %s, 100.0, %s)
            """,
                (user_id, ingredient_id, unite_id),
            )
            db_connection.commit()

        dao = StockCourseDAO()

        # WHEN / THEN
        with pytest.raises(InvalidQuantityError) as exc_info:
            dao.decrement_stock_item(
                id_utilisateur=user_id,
                id_ingredient=ingredient_id,
                quantite=150.0,
            )

        error_message = str(exc_info.value)
        if "150" not in error_message:
            raise AssertionError(
                message=f"L'erreur devrait mentionner '150': {error_message}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_decrement_stock_item_ingredient_inexistant(
        db_connection,
    ) -> None:
        """Teste un décrément sur un ingrédient inexistant."""
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

        dao = StockCourseDAO()

        # WHEN / THEN
        with pytest.raises(IngredientNotFoundError):
            dao.decrement_stock_item(
                id_utilisateur=user_id,
                id_ingredient=99999,
                quantite=10.0,
            )

    # ========== Tests pour delete_stock_item ==========

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_delete_stock_item_reussi(db_connection) -> None:
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
                INSERT INTO stock (
                    id_utilisateur, id_ingredient, quantite, id_unite
                )
                VALUES (%s, %s, 100.0, %s)
            """,
                (user_id, ingredient_id, unite_id),
            )
            db_connection.commit()

        dao = StockCourseDAO()

        # WHEN
        result = dao.delete_stock_item(user_id, ingredient_id)

        # THEN
        if result is not True:
            raise AssertionError(
                message=f"La suppression devrait réussir, obtenu: {result}",
            )

        # Vérifier que l'item a été supprimé
        stock_item = dao.get_stock_item(user_id, ingredient_id)
        if stock_item is not None:
            raise AssertionError(
                message="L'item ne devrait plus exister",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_delete_stock_item_inexistant(db_connection) -> None:
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

        dao = StockCourseDAO()

        # WHEN
        result = dao.delete_stock_item(user_id, 99999)

        # THEN
        if result is not False:
            raise AssertionError(
                message=f"La suppression devrait retourner False, obtenu: {result}",
            )

    # ========== Tests pour get_full_stock ==========

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_full_stock_tous_ingredients(db_connection) -> None:
        """Teste la récupération de tous les ingrédients avec stock."""
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

            # Créer plusieurs ingrédients
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

            # Ajouter seulement le Rhum au stock
            cursor.execute(
                """
                INSERT INTO stock (
                    id_utilisateur, id_ingredient, quantite, id_unite
                )
                VALUES (%s, %s, 100.0, %s)
            """,
                (user_id, ingredients[0]["id_ingredient"], unite_id),
            )
            db_connection.commit()

        dao = StockCourseDAO()

        # WHEN
        result = dao.get_full_stock(user_id)

        # THEN
        nb_item = 3
        if len(result) != nb_item:
            raise AssertionError(
                message=f"3 ingrédients attendus, obtenu: {len(result)}",
            )

        # Vérifier que le Rhum a une quantité
        rhum = [r for r in result if r["nom_ingredient"] == "Rhum"]
        if len(rhum) == 0:
            raise AssertionError(
                message="Le Rhum devrait être dans les résultats",
            )
        qte = 100.0
        if float(rhum[0]["quantite"]) != qte:
            raise AssertionError(
                message=f"Le Rhum devrait avoir une quantité de 100.0, "
                f"obtenu: {rhum[0]['quantite']}",
            )

        # Vérifier que Vodka et Gin ont quantité = 0
        vodka = [r for r in result if r["nom_ingredient"] == "Vodka"]
        if len(vodka) == 0:
            raise AssertionError(
                message="La Vodka devrait être dans les résultats",
            )
        if float(vodka[0]["quantite"]) != 0.0:
            raise AssertionError(
                message=f"La Vodka devrait avoir une quantité de 0.0, "
                f"obtenu: {vodka[0]['quantite']}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_full_stock_ordre_alphabetique(db_connection) -> None:
        """Teste que les résultats sont triés alphabétiquement."""
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
            """,
            )
            db_connection.commit()

        dao = StockCourseDAO()

        # WHEN
        result = dao.get_full_stock(user_id)

        # THEN
        noms = [r["nom_ingredient"] for r in result]
        noms_tries = sorted(noms)
        if noms != noms_tries:
            raise AssertionError(
                message=f"Les noms devraient être triés alphabétiquement, "
                f"obtenu: {noms}, attendu: {noms_tries}",
            )

    # ========== Tests pour get_unite_info ==========

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_unite_info_existante(db_connection) -> None:
        """Teste la récupération d'une unité existante."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO unite (nom, abbreviation, type_unite)
                VALUES ('millilitre', 'ml', 'liquide')
                RETURNING id_unite
            """,
            )
            unite_id = cursor.fetchone()["id_unite"]
            db_connection.commit()

        dao = StockCourseDAO()

        # WHEN
        result = dao.get_unite_info(unite_id)

        # THEN
        if result is None:
            raise AssertionError(
                message="L'unité devrait être trouvée",
            )
        if result["abbreviation"] != "ml":
            raise AssertionError(
                message=f"L'abréviation devrait être 'ml', "
                f"obtenu: {result['abbreviation']}",
            )
        if result["type_unite"] != "liquide":
            raise AssertionError(
                message=f"Le type devrait être 'liquide', "
                f"obtenu: {result['type_unite']}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_unite_info_inexistante() -> None:
        """Teste la récupération d'une unité inexistante."""
        # GIVEN
        dao = StockCourseDAO()

        # WHEN
        result = dao.get_unite_info(99999)

        # THEN
        if result is not None:
            raise AssertionError(
                message=f"Le résultat devrait être None, obtenu: {result}",
            )

    # ========== Tests pour get_unite_id_by_abbreviation ==========

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_unite_id_by_abbreviation_existante(
        db_connection,
    ) -> None:
        """Teste la récupération par abréviation existante."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO unite (nom, abbreviation, type_unite)
                VALUES ('millilitre', 'ml', 'liquide')
                RETURNING id_unite
            """,
            )
            unite_id = cursor.fetchone()["id_unite"]
            db_connection.commit()

        dao = StockCourseDAO()

        # WHEN
        result = dao.get_unite_id_by_abbreviation("ml")

        # THEN
        if result != unite_id:
            raise AssertionError(
                message=f"L'ID devrait être {unite_id}, obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_unite_id_by_abbreviation_case_insensitive(
        db_connection,
    ) -> None:
        """Teste que la recherche est insensible à la casse."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO unite (nom, abbreviation, type_unite)
                VALUES ('millilitre', 'ml', 'liquide')
                RETURNING id_unite
            """,
            )
            unite_id = cursor.fetchone()["id_unite"]
            db_connection.commit()

        dao = StockCourseDAO()

        # WHEN
        result = dao.get_unite_id_by_abbreviation("ML")

        # THEN
        if result != unite_id:
            raise AssertionError(
                message=f"L'ID devrait être {unite_id}, obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_unite_id_by_abbreviation_inexistante() -> None:
        """Teste avec une abréviation inexistante."""
        # GIVEN
        dao = StockCourseDAO()

        # WHEN
        result = dao.get_unite_id_by_abbreviation("xyz")

        # THEN
        if result is not None:
            raise AssertionError(
                message=f"Le résultat devrait être None, obtenu: {result}",
            )

    # ========== Tests pour set_stock_item ==========

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_set_stock_item_nouveau(db_connection) -> None:
        """Teste la définition d'un nouveau stock."""
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

        dao = StockCourseDAO()

        # WHEN
        result = dao.set_stock_item(
            id_utilisateur=user_id,
            id_ingredient=ingredient_id,
            quantite=75.0,
            id_unite=unite_id,
        )

        # THEN
        if result is not True:
            raise AssertionError(
                message=f"La définition devrait réussir, obtenu: {result}",
            )

        # Vérifier la quantité
        stock_item = dao.get_stock_item(user_id, ingredient_id)
        qte = 75.0
        if float(stock_item["quantite"]) != qte:
            raise AssertionError(
                message=f"La quantité devrait être 75.0, "
                f"obtenu: {stock_item['quantite']}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_set_stock_item_remplace_existant(db_connection) -> None:
        """Teste que set remplace (au lieu de cumuler)."""
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

            # Créer un stock initial de 100
            cursor.execute(
                """
                INSERT INTO stock (
                    id_utilisateur, id_ingredient, quantite, id_unite
                )
                VALUES (%s, %s, 100.0, %s)
            """,
                (user_id, ingredient_id, unite_id),
            )
            db_connection.commit()

        dao = StockCourseDAO()

        # WHEN - Set à 50 (devrait remplacer, pas cumuler)
        result = dao.set_stock_item(
            id_utilisateur=user_id,
            id_ingredient=ingredient_id,
            quantite=50.0,
            id_unite=unite_id,
        )

        # THEN
        if result is not True:
            raise AssertionError(
                message=f"La définition devrait réussir, obtenu: {result}",
            )

        # Vérifier que c'est 50 (pas 150)
        stock_item = dao.get_stock_item(user_id, ingredient_id)
        qte = 50.0
        if float(stock_item["quantite"]) != qte:
            raise AssertionError(
                message=f"La quantité devrait être 50.0 (remplacée, pas cumulée), "
                f"obtenu: {stock_item['quantite']}",
            )
