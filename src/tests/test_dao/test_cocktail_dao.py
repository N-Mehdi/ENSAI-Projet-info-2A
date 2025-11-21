"""Tests d'intégration pour CocktailDAO."""

import pytest

from src.business_object.cocktail import Cocktail
from src.dao.cocktail_dao import CocktailDAO


class TestCocktailDAOIntegration:
    """Tests d'intégration pour CocktailDAO."""

    # ========== Tests pour rechercher_cocktail_par_nom ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_rechercher_cocktail_par_nom_existant(
        db_connection,
    ) -> None:
        """Teste la recherche d'un cocktail existant par nom."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES (
                    'Mojito', 'Cocktail', 'Highball', TRUE, 'mojito.jpg'
                )
            """,
            )
            db_connection.commit()

        dao = CocktailDAO()

        # WHEN
        result = dao.rechercher_cocktail_par_nom("mojito")

        # THEN
        if result is None:
            raise AssertionError(message="Le cocktail devrait être trouvé")
        if not isinstance(result, Cocktail):
            raise TypeError(
                message=f"Le résultat devrait être un Cocktail, obtenu: {type(result)}",
            )
        if result.nom != "Mojito":
            raise AssertionError(
                message=f"Le nom devrait être 'Mojito', obtenu: {result.nom}",
            )
        if result.categorie != "Cocktail":
            raise AssertionError(
                message=f"La catégorie devrait être 'Cocktail', "
                f"obtenu: {result.categorie}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_rechercher_cocktail_par_nom_title_case(
        db_connection,
    ) -> None:
        """Teste que la recherche utilise title case."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES (
                    'Pina Colada', 'Cocktail', 'Hurricane', TRUE, 'img.jpg'
                )
            """,
            )
            db_connection.commit()

        dao = CocktailDAO()

        # WHEN
        result = dao.rechercher_cocktail_par_nom("PINA COLADA")

        # THEN
        if result is None:
            raise AssertionError(message="Le cocktail devrait être trouvé")
        if result.nom != "Pina Colada":
            raise AssertionError(
                message=f"Le nom devrait être 'Pina Colada', obtenu: {result.nom}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_rechercher_cocktail_par_nom_inexistant() -> None:
        """Teste la recherche d'un cocktail inexistant."""
        # GIVEN
        dao = CocktailDAO()

        # WHEN
        result = dao.rechercher_cocktail_par_nom("Cocktail Inexistant")

        # THEN
        if result is not None:
            raise AssertionError(
                message=f"Le résultat devrait être None, obtenu: {result}",
            )

    # ========== Tests pour rechercher_cocktail_par_sequence_debut ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_rechercher_cocktail_par_sequence_debut_multiple(
        db_connection,
    ) -> None:
        """Teste la recherche par séquence avec plusieurs résultats."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES
                    ('Mojito', 'Cocktail', 'Highball', TRUE, 'img.jpg'),
                    ('Margarita', 'Cocktail', 'Coupe', TRUE, 'img.jpg'),
                    ('Manhattan', 'Cocktail', 'Coupe', TRUE, 'img.jpg')
            """,
            )
            db_connection.commit()

        dao = CocktailDAO()

        # WHEN
        result = dao.rechercher_cocktail_par_sequence_debut("Ma", 10)

        # THEN
        nb_cocktail = 2
        if len(result) != nb_cocktail:
            raise AssertionError(
                message=f"2 cocktails attendus, obtenu: {len(result)}",
            )
        # Vérifier l'ordre alphabétique
        noms = [c.nom for c in result]
        if noms != ["Manhattan", "Margarita"]:
            raise AssertionError(
                message=f"L'ordre devrait être alphabétique, obtenu: {noms}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_rechercher_cocktail_par_sequence_debut_case_insensitive(
        db_connection,
    ) -> None:
        """Teste que la recherche est insensible à la casse."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Mojito', 'Cocktail', 'Highball', TRUE, 'img.jpg')
            """,
            )
            db_connection.commit()

        dao = CocktailDAO()

        # WHEN
        result = dao.rechercher_cocktail_par_sequence_debut("mo", 10)

        # THEN
        if len(result) != 1:
            raise AssertionError(
                message=f"1 cocktail attendu, obtenu: {len(result)}",
            )
        if result[0].nom != "Mojito":
            raise AssertionError(
                message=f"Le nom devrait être 'Mojito', obtenu: {result[0].nom}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_rechercher_cocktail_par_sequence_debut_limite(
        db_connection,
    ) -> None:
        """Teste que la limite de résultats est respectée."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES
                    ('Apple Martini', 'Cocktail', 'Coupe', TRUE, 'img.jpg'),
                    ('Aviation', 'Cocktail', 'Coupe', TRUE, 'img.jpg'),
                    ('Americano', 'Cocktail', 'Verre', TRUE, 'img.jpg')
            """,
            )
            db_connection.commit()

        dao = CocktailDAO()

        # WHEN
        result = dao.rechercher_cocktail_par_sequence_debut("A", 2)

        # THEN
        nb_cocktail = 2
        if len(result) != nb_cocktail:
            raise AssertionError(
                message=f"2 cocktails attendus (limite), obtenu: {len(result)}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_rechercher_cocktail_par_sequence_debut_aucun_resultat() -> None:
        """Teste la recherche sans résultat."""
        # GIVEN
        dao = CocktailDAO()

        # WHEN
        result = dao.rechercher_cocktail_par_sequence_debut("Xyz", 10)

        # THEN
        if len(result) != 0:
            raise AssertionError(
                message=f"0 cocktails attendus, obtenu: {len(result)}",
            )

    # ========== Tests pour get_cocktail_id_by_name ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_cocktail_id_by_name_existant(
        db_connection,
    ) -> None:
        """Teste la récupération de l'ID d'un cocktail existant."""
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

        dao = CocktailDAO()

        # WHEN
        result = dao.get_cocktail_id_by_name("Mojito")

        # THEN
        if result != cocktail_id:
            raise AssertionError(
                message=f"L'ID devrait être {cocktail_id}, obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_cocktail_id_by_name_case_insensitive(
        db_connection,
    ) -> None:
        """Teste que la recherche est insensible à la casse."""
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

        dao = CocktailDAO()

        # WHEN
        result = dao.get_cocktail_id_by_name("MOJITO")

        # THEN
        if result != cocktail_id:
            raise AssertionError(
                message=f"L'ID devrait être {cocktail_id}, obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_cocktail_id_by_name_with_spaces(
        db_connection,
    ) -> None:
        """Teste que la recherche ignore les espaces superflus."""
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

        dao = CocktailDAO()

        # WHEN
        result = dao.get_cocktail_id_by_name("  Mojito  ")

        # THEN
        if result != cocktail_id:
            raise AssertionError(
                message=f"L'ID devrait être {cocktail_id}, obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_cocktail_id_by_name_inexistant() -> None:
        """Teste la récupération de l'ID d'un cocktail inexistant."""
        # GIVEN
        dao = CocktailDAO()

        # WHEN
        result = dao.get_cocktail_id_by_name("Cocktail Inexistant")

        # THEN
        if result is not None:
            raise AssertionError(
                message=f"Le résultat devrait être None, obtenu: {result}",
            )

    # ========== Tests pour get_tous_cocktails_avec_ingredients ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_tous_cocktails_avec_ingredients_sans_ingredients(
        db_connection,
    ) -> None:
        """Teste la récupération d'un cocktail sans ingrédients."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Empty Cocktail', 'Test', 'Verre', FALSE, 'img.jpg')
            """,
            )
            db_connection.commit()

        dao = CocktailDAO()

        # WHEN
        result = dao.get_tous_cocktails_avec_ingredients()

        # THEN
        if len(result) == 0:
            raise AssertionError(
                message="Au moins un résultat attendu",
            )
        # Trouver le cocktail dans les résultats
        empty_cocktail = [r for r in result if r["nom"] == "Empty Cocktail"]
        if len(empty_cocktail) == 0:
            raise AssertionError(
                message="Le cocktail 'Empty Cocktail' devrait être présent",
            )
        if empty_cocktail[0]["id_ingredient"] is not None:
            raise AssertionError(
                message="id_ingredient devrait être None pour un "
                "cocktail sans ingrédients",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_tous_cocktails_avec_ingredients_avec_ingredients(
        db_connection,
    ) -> None:
        """Teste la récupération d'un cocktail avec ingrédients."""
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
                INSERT INTO cocktail_ingredient (
                    id_cocktail, id_ingredient, qte, unite
                )
                VALUES (%s, %s, 50, 'ml'), (%s, %s, 10, 'feuilles')
            """,
                (cocktail_id, rhum_id, cocktail_id, menthe_id),
            )
            db_connection.commit()

        dao = CocktailDAO()

        # WHEN
        result = dao.get_tous_cocktails_avec_ingredients()

        # THEN
        nb_ligne = 2
        mojito_rows = [r for r in result if r["nom"] == "Mojito"]
        if len(mojito_rows) != nb_ligne:
            raise AssertionError(
                message=f"2 lignes attendues pour Mojito, obtenu: {len(mojito_rows)}",
            )
        # Vérifier les ingrédients
        ingredient_ids = [r["id_ingredient"] for r in mojito_rows]
        if rhum_id not in ingredient_ids:
            raise AssertionError(
                message="Le Rhum devrait être dans les ingrédients",
            )
        if menthe_id not in ingredient_ids:
            raise AssertionError(
                message="La Menthe devrait être dans les ingrédients",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_tous_cocktails_avec_ingredients_multiple_cocktails(
        db_connection,
    ) -> None:
        """Teste la récupération de plusieurs cocktails."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES
                    ('Mojito', 'Cocktail', 'Highball', TRUE, 'img.jpg'),
                    ('Margarita', 'Cocktail', 'Coupe', TRUE, 'img.jpg')
            """,
            )
            db_connection.commit()

        dao = CocktailDAO()

        # WHEN
        result = dao.get_tous_cocktails_avec_ingredients()

        # THEN
        nb_res = 2
        if len(result) < nb_res:
            raise AssertionError(
                message=f"Au moins 2 résultats attendus, obtenu: {len(result)}",
            )
        noms = {r["nom"] for r in result}
        if "Mojito" not in noms:
            raise AssertionError(
                message="Mojito devrait être dans les résultats",
            )
        if "Margarita" not in noms:
            raise AssertionError(
                message="Margarita devrait être dans les résultats",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_tous_cocktails_avec_ingredients_ordre(
        db_connection,
    ) -> None:
        """Teste l'ordre des résultats par id_cocktail."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES
                    ('Cocktail A', 'Test', 'Verre', TRUE, 'img.jpg'),
                    ('Cocktail B', 'Test', 'Verre', TRUE, 'img.jpg')
                RETURNING id_cocktail
            """,
            )
            db_connection.commit()

        dao = CocktailDAO()

        # WHEN
        result = dao.get_tous_cocktails_avec_ingredients()

        # THEN
        ids = [r["id_cocktail"] for r in result]
        # Vérifier que les IDs sont dans l'ordre croissant
        if ids != sorted(ids):
            raise AssertionError(
                message=f"Les IDs devraient être triés, obtenu: {ids}",
            )

    # ========== Tests pour get_cocktails_quasi_realisables ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_cocktails_quasi_realisables_sans_stock(
        db_connection,
    ) -> None:
        """Teste la récupération quand l'utilisateur n'a pas de stock."""
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
                VALUES ('Mojito', 'Cocktail', 'Highball', TRUE, 'img.jpg')
                RETURNING id_cocktail
            """,
            )
            cocktail_id = cursor.fetchone()["id_cocktail"]

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
                INSERT INTO cocktail_ingredient (
                    id_cocktail, id_ingredient, qte, unite
                )
                VALUES (%s, %s, 50, 'ml')
            """,
                (cocktail_id, ingredient_id),
            )
            db_connection.commit()

        dao = CocktailDAO()

        # WHEN
        result = dao.get_cocktails_quasi_realisables(user_id)

        # THEN
        if len(result) == 0:
            raise AssertionError(
                message="Au moins un résultat attendu",
            )
        mojito_rows = [r for r in result if r["nom"] == "Mojito"]
        if len(mojito_rows) == 0:
            raise AssertionError(
                message="Le Mojito devrait être dans les résultats",
            )
        if mojito_rows[0]["quantite_stock"] is not None:
            raise AssertionError(
                message="quantite_stock devrait être None sans stock",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_cocktails_quasi_realisables_avec_stock(
        db_connection,
    ) -> None:
        """Teste la récupération avec stock disponible."""
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
                VALUES ('Mojito', 'Cocktail', 'Highball', TRUE, 'img.jpg')
                RETURNING id_cocktail
            """,
            )
            cocktail_id = cursor.fetchone()["id_cocktail"]

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
                INSERT INTO cocktail_ingredient (
                    id_cocktail, id_ingredient, qte, unite
                )
                VALUES (%s, %s, 50, 'ml')
            """,
                (cocktail_id, ingredient_id),
            )

            cursor.execute(
                """
                INSERT INTO stock (
                    id_utilisateur, id_ingredient, quantite, id_unite
                )
                VALUES (%s, %s, 100, %s)
            """,
                (user_id, ingredient_id, unite_id),
            )
            db_connection.commit()

        dao = CocktailDAO()

        # WHEN
        result = dao.get_cocktails_quasi_realisables(user_id)

        # THEN
        mojito_rows = [r for r in result if r["nom"] == "Mojito"]
        if len(mojito_rows) == 0:
            raise AssertionError(
                message="Le Mojito devrait être dans les résultats",
            )
        if mojito_rows[0]["quantite_stock"] is None:
            raise AssertionError(
                message="quantite_stock ne devrait pas être None",
            )
        qte = 100.0
        if float(mojito_rows[0]["quantite_stock"]) != qte:
            raise AssertionError(
                message=f"quantite_stock devrait être 100, "
                f"obtenu: {mojito_rows[0]['quantite_stock']}",
            )
        if mojito_rows[0]["unite_stock"] != "ml":
            raise AssertionError(
                message=f"unite_stock devrait être 'ml', "
                f"obtenu: {mojito_rows[0]['unite_stock']}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_cocktails_quasi_realisables_multiple_ingredients(
        db_connection,
    ) -> None:
        """Teste avec un cocktail ayant plusieurs ingrédients."""
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
                VALUES ('Mojito', 'Cocktail', 'Highball', TRUE, 'img.jpg')
                RETURNING id_cocktail
            """,
            )
            cocktail_id = cursor.fetchone()["id_cocktail"]

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
                INSERT INTO cocktail_ingredient (
                    id_cocktail, id_ingredient, qte, unite
                )
                VALUES (%s, %s, 50, 'ml'), (%s, %s, 10, 'feuilles')
            """,
                (cocktail_id, rhum_id, cocktail_id, menthe_id),
            )
            db_connection.commit()

        dao = CocktailDAO()

        # WHEN
        result = dao.get_cocktails_quasi_realisables(user_id)

        # THEN
        nb_ligne = 2
        mojito_rows = [r for r in result if r["nom"] == "Mojito"]
        if len(mojito_rows) != nb_ligne:
            raise AssertionError(
                message=f"2 lignes attendues pour Mojito, obtenu: {len(mojito_rows)}",
            )
        ingredient_noms = [r["nom_ingredient"] for r in mojito_rows]
        if "Rhum" not in ingredient_noms:
            raise AssertionError(
                message="Rhum devrait être dans les ingrédients",
            )
        if "Menthe" not in ingredient_noms:
            raise AssertionError(
                message="Menthe devrait être dans les ingrédients",
            )
