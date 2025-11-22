"""Tests d'intégration pour IngredientDAO."""

import pytest

from src.dao.ingredient_dao import IngredientDAO
from src.utils.exceptions import DAOError


def check_pg_trgm_available(db_connection) -> bool:
    """Vérifie si l'extension pg_trgm est disponible."""
    try:
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1 FROM pg_extension WHERE extname = 'pg_trgm'
            """,
            )
            return cursor.fetchone() is not None
    except Exception as e:
        raise DAOError from e
    return False


class TestIngredientDAOIntegration:
    """Tests d'intégration pour IngredientDAO."""

    # ========== Tests pour get_all_ingredients ==========

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_all_ingredients_vide() -> None:
        """Teste la récupération de tous les ingrédients (base vide)."""
        # GIVEN
        dao = IngredientDAO()

        # WHEN
        result = dao.get_all_ingredients()

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
    def test_get_all_ingredients_avec_donnees(db_connection) -> None:
        """Teste la récupération de tous les ingrédients avec des données."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ingredient (nom, alcool)
                VALUES ('Rhum', TRUE), ('Vodka', TRUE), ('Menthe', FALSE)
            """,
            )
            db_connection.commit()

        dao = IngredientDAO()

        # WHEN
        result = dao.get_all_ingredients()

        # THEN
        nb_ing = 3
        if len(result) != nb_ing:
            raise AssertionError(
                message=f"3 ingrédients attendus, obtenu: {len(result)}",
            )

        noms = [r["nom"] for r in result]
        if "Rhum" not in noms:
            raise AssertionError(
                message="'Rhum' devrait être dans les résultats",
            )
        if "Vodka" not in noms:
            raise AssertionError(
                message="'Vodka' devrait être dans les résultats",
            )
        if "Menthe" not in noms:
            raise AssertionError(
                message="'Menthe' devrait être dans les résultats",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_all_ingredients_ordre_alphabetique(db_connection) -> None:
        """Teste que les ingrédients sont triés alphabétiquement."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ingredient (nom, alcool)
                VALUES ('Vodka', TRUE), ('Gin', TRUE), ('Rhum', TRUE)
            """,
            )
            db_connection.commit()

        dao = IngredientDAO()

        # WHEN
        result = dao.get_all_ingredients()

        # THEN
        noms = [r["nom"] for r in result]
        noms_tries = sorted(noms)
        if noms != noms_tries:
            raise AssertionError(
                message=f"Les noms devraient être triés alphabétiquement, "
                f"obtenu: {noms}, attendu: {noms_tries}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_all_ingredients_contient_id_et_nom(db_connection) -> None:
        """Teste que chaque ingrédient contient id_ingredient et nom."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ingredient (nom, alcool)
                VALUES ('Rhum', TRUE)
            """,
            )
            db_connection.commit()

        dao = IngredientDAO()

        # WHEN
        result = dao.get_all_ingredients()

        # THEN
        for ingredient in result:
            if "id_ingredient" not in ingredient:
                raise AssertionError(
                    message="Chaque ingrédient devrait avoir 'id_ingredient'",
                )
            if "nom" not in ingredient:
                raise AssertionError(
                    message="Chaque ingrédient devrait avoir 'nom'",
                )

    # ========== Tests pour get_by_name ==========

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_by_name_existant(db_connection) -> None:
        """Teste la recherche d'un ingrédient existant par nom exact."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ingredient (nom, alcool)
                VALUES ('Rhum', TRUE)
                RETURNING id_ingredient
            """,
            )
            ingredient_id = cursor.fetchone()["id_ingredient"]
            db_connection.commit()

        dao = IngredientDAO()

        # WHEN
        result = dao.get_by_name("Rhum")

        # THEN
        if result is None:
            raise AssertionError(
                message="L'ingrédient devrait être trouvé",
            )
        if result["id_ingredient"] != ingredient_id:
            raise AssertionError(
                message=f"L'id devrait être {ingredient_id}, "
                f"obtenu: {result['id_ingredient']}",
            )
        if result["nom"] != "Rhum":
            raise AssertionError(
                message=f"Le nom devrait être 'Rhum', obtenu: {result['nom']}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_by_name_inexistant() -> None:
        """Teste la recherche d'un ingrédient inexistant."""
        # GIVEN
        dao = IngredientDAO()

        # WHEN
        result = dao.get_by_name("Ingrédient Inexistant")

        # THEN
        if result is not None:
            raise AssertionError(
                message=f"Le résultat devrait être None, obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_by_name_case_insensitive(db_connection) -> None:
        """Teste que la recherche est insensible à la casse."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ingredient (nom, alcool)
                VALUES ('Rhum', TRUE) -- Casse initiale 'Rhum'
            """,
            )
            db_connection.commit()

        dao = IngredientDAO()

        # WHEN
        result = dao.get_by_name("rhum")

        if result is None:
            raise AssertionError(
                message="La recherche devrait être insensible à la casse, l'ingrédient "
                "n'a pas été trouvé.",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_by_name_avec_espaces(db_connection) -> None:
        """Teste la recherche avec un nom contenant des espaces."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ingredient (nom, alcool)
                VALUES ('Jus D''Orange', FALSE)
                RETURNING id_ingredient
            """,
            )
            ingredient_id = cursor.fetchone()["id_ingredient"]
            db_connection.commit()

        dao = IngredientDAO()

        # WHEN
        result = dao.get_by_name("Jus D'Orange")

        # THEN
        if result is None:
            raise AssertionError(
                message="L'ingrédient devrait être trouvé",
            )
        if result["id_ingredient"] != ingredient_id:
            raise AssertionError(
                message=f"L'id devrait être {ingredient_id}, "
                f"obtenu: {result['id_ingredient']}",
            )

    # ========== Tests pour search_by_name ==========

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_search_by_name_resultats_multiples(db_connection) -> None:
        """Teste la recherche avec plusieurs résultats."""
        # GIVEN
        if not check_pg_trgm_available(db_connection):
            pytest.skip("Extension pg_trgm non disponible")

        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ingredient (nom, alcool)
                VALUES
                    ('Rhum Blanc', TRUE),
                    ('Rhum Ambré', TRUE),
                    ('Rhum Vieux', TRUE)
            """,
            )
            db_connection.commit()

        dao = IngredientDAO()

        # WHEN
        result = dao.search_by_name("Rhum", limit=10)

        # THEN
        if len(result) == 0:
            raise AssertionError(
                message="Des résultats devraient être trouvés",
            )

        # Vérifier que tous contiennent "Rhum"
        for ingredient in result:
            if "Rhum" not in ingredient["nom"]:
                raise AssertionError(
                    message=f"'{ingredient['nom']}' devrait contenir 'Rhum'",
                )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_search_by_name_limite_respectee(db_connection) -> None:
        """Teste que la limite de résultats est respectée."""
        # GIVEN
        if not check_pg_trgm_available(db_connection):
            pytest.skip("Extension pg_trgm non disponible")

        with db_connection.cursor() as cursor:
            # Créer 10 ingrédients avec "Rhum"
            for i in range(10):
                cursor.execute(
                    """
                    INSERT INTO ingredient (nom, alcool)
                    VALUES (%s, TRUE)
                """,
                    (f"Rhum Type {i}",),
                )
            db_connection.commit()

        dao = IngredientDAO()

        # WHEN - Limiter à 5 résultats
        result = dao.search_by_name("Rhum", limit=5)

        # THEN
        max_res = 5
        if len(result) > max_res:
            raise AssertionError(
                message=f"Maximum 5 résultats attendus, obtenu: {len(result)}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_search_by_name_aucun_resultat(db_connection) -> None:
        """Teste la recherche sans résultat."""
        # GIVEN
        if not check_pg_trgm_available(db_connection):
            pytest.skip("Extension pg_trgm non disponible")

        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ingredient (nom, alcool)
                VALUES ('Rhum', TRUE)
            """,
            )
            db_connection.commit()

        dao = IngredientDAO()

        # WHEN
        result = dao.search_by_name("Xylophonetqrst", limit=10)

        # THEN
        if len(result) != 0:
            raise AssertionError(
                message=f"Aucun résultat attendu, obtenu: {len(result)}",
            )
        if not isinstance(result, list):
            raise TypeError(
                message=f"Le résultat devrait être une liste, obtenu: {type(result)}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_search_by_name_similarite(db_connection) -> None:
        """Teste que la recherche utilise la similarité."""
        # GIVEN
        if not check_pg_trgm_available(db_connection):
            pytest.skip("Extension pg_trgm non disponible")

        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ingredient (nom, alcool)
                VALUES ('Rhum', TRUE), ('Rum', TRUE)
            """,
            )
            db_connection.commit()

        dao = IngredientDAO()

        # WHEN - Rechercher "Rhum" (devrait trouver "Rhum" et "Rum")
        result = dao.search_by_name("Rhum", limit=10)

        # THEN
        if len(result) == 0:
            raise AssertionError(
                message="Des résultats devraient être trouvés",
            )

    # ========== Tests pour is_alcoholic ==========

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_is_alcoholic_ingredient_alcoolise(db_connection) -> None:
        """Teste la vérification pour un ingrédient alcoolisé."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ingredient (nom, alcool)
                VALUES ('Rhum', TRUE)
                RETURNING id_ingredient
            """,
            )
            ingredient_id = cursor.fetchone()["id_ingredient"]
            db_connection.commit()

        dao = IngredientDAO()

        # WHEN
        result = dao.is_alcoholic(ingredient_id)

        # THEN
        if result is not True:
            raise AssertionError(
                message=f"Le résultat devrait être True, obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_is_alcoholic_ingredient_non_alcoolise(db_connection) -> None:
        """Teste la vérification pour un ingrédient non alcoolisé."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ingredient (nom, alcool)
                VALUES ('Menthe', FALSE)
                RETURNING id_ingredient
            """,
            )
            ingredient_id = cursor.fetchone()["id_ingredient"]
            db_connection.commit()

        dao = IngredientDAO()

        # WHEN
        result = dao.is_alcoholic(ingredient_id)

        # THEN
        if result is not False:
            raise AssertionError(
                message=f"Le résultat devrait être False, obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_is_alcoholic_ingredient_inexistant() -> None:
        """Teste la vérification pour un ingrédient inexistant."""
        # GIVEN
        dao = IngredientDAO()

        # WHEN
        result = dao.is_alcoholic(99999)

        # THEN
        if result is not None:
            raise AssertionError(
                message=f"Le résultat devrait être None, obtenu: {result}",
            )

    # ========== Tests pour is_alcoholic_by_name ==========

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_is_alcoholic_by_name_alcoolise(db_connection) -> None:
        """Teste la vérification par nom pour un ingrédient alcoolisé."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ingredient (nom, alcool)
                VALUES ('Rhum', TRUE)
            """,
            )
            db_connection.commit()

        dao = IngredientDAO()

        # WHEN
        result = dao.is_alcoholic_by_name("Rhum")

        # THEN
        if result is not True:
            raise AssertionError(
                message=f"Le résultat devrait être True, obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_is_alcoholic_by_name_non_alcoolise(db_connection) -> None:
        """Teste la vérification par nom pour un ingrédient non alcoolisé."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ingredient (nom, alcool)
                VALUES ('Menthe', FALSE)
            """,
            )
            db_connection.commit()

        dao = IngredientDAO()

        # WHEN
        result = dao.is_alcoholic_by_name("Menthe")

        # THEN
        if result is not False:
            raise AssertionError(
                message=f"Le résultat devrait être False, obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_is_alcoholic_by_name_case_insensitive(db_connection) -> None:
        """Teste que la recherche est insensible à la casse."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ingredient (nom, alcool)
                VALUES ('Rhum', TRUE)
            """,
            )
            db_connection.commit()

        dao = IngredientDAO()

        # WHEN
        result = dao.is_alcoholic_by_name("RHUM")

        # THEN
        if result is not True:
            raise AssertionError(
                message=f"Le résultat devrait être True (case insensitive), "
                f"obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_is_alcoholic_by_name_avec_espaces(db_connection) -> None:
        """Teste que les espaces superflus sont ignorés."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ingredient (nom, alcool)
                VALUES ('Rhum', TRUE)
            """,
            )
            db_connection.commit()

        dao = IngredientDAO()

        # WHEN
        result = dao.is_alcoholic_by_name("  Rhum  ")

        # THEN
        if result is not True:
            raise AssertionError(
                message=f"Le résultat devrait être True (espaces ignorés), "
                f"obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_is_alcoholic_by_name_inexistant() -> None:
        """Teste la vérification pour un ingrédient inexistant."""
        # GIVEN
        dao = IngredientDAO()

        # WHEN
        result = dao.is_alcoholic_by_name("Ingrédient Inexistant")

        # THEN
        if result is not None:
            raise AssertionError(
                message=f"Le résultat devrait être None, obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_is_alcoholic_by_name_casse_mixte(db_connection) -> None:
        """Teste avec une casse mixte."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ingredient (nom, alcool)
                VALUES ('Rhum', TRUE)
            """,
            )
            db_connection.commit()

        dao = IngredientDAO()

        # WHEN
        result = dao.is_alcoholic_by_name("rHuM")

        # THEN
        if result is not True:
            raise AssertionError(
                message=f"Le résultat devrait être True (casse mixte), "
                f"obtenu: {result}",
            )
