"""doc."""

"""Tests d'intégration pour UniteDAO."""

import pytest

from src.dao.unite_dao import UniteDAO


class TestUniteDAOIntegration:
    """Tests d'intégration pour UniteDAO."""

    # ========== Tests pour get_or_create_unit ==========

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_or_create_unit_creation_nouvelle_unite() -> None:
        """Teste la création d'une nouvelle unité."""
        # GIVEN
        dao = UniteDAO()

        # WHEN
        result = dao.get_or_create_unit("millilitre")

        # THEN
        if not isinstance(result, int):
            raise TypeError(
                message=f"Le résultat devrait être un int, obtenu: {type(result)}",
            )
        if result <= 0:
            raise AssertionError(
                message=f"L'ID devrait être > 0, obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_or_create_unit_recupere_unite_existante(
        db_connection,
    ) -> None:
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
            unite_id_existant = cursor.fetchone()["id_unite"]
            db_connection.commit()

        dao = UniteDAO()

        # WHEN
        result = dao.get_or_create_unit("millilitre")

        # THEN
        if result != unite_id_existant:
            raise AssertionError(
                message=f"L'ID devrait être {unite_id_existant} (existant), "
                f"obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_or_create_unit_case_insensitive(db_connection) -> None:
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
            unite_id_existant = cursor.fetchone()["id_unite"]
            db_connection.commit()

        dao = UniteDAO()

        # WHEN - Rechercher en majuscules
        result = dao.get_or_create_unit("MILLILITRE")

        # THEN
        if result != unite_id_existant:
            raise AssertionError(
                message=f"L'ID devrait être {unite_id_existant} "
                f"(recherche insensible à la casse), obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_or_create_unit_casse_mixte(db_connection) -> None:
        """Teste avec une casse mixte."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO unite (nom, abbreviation, type_unite)
                VALUES ('millilitre', 'ml', 'liquide')
                RETURNING id_unite
            """,
            )
            unite_id_existant = cursor.fetchone()["id_unite"]
            db_connection.commit()

        dao = UniteDAO()

        # WHEN - Rechercher avec casse mixte
        result = dao.get_or_create_unit("MilliLitre")

        # THEN
        if result != unite_id_existant:
            raise AssertionError(
                message=f"L'ID devrait être {unite_id_existant} "
                f"(casse mixte), obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_or_create_unit_unites_differentes(db_connection) -> None:
        """Teste la création de plusieurs unités différentes."""
        # GIVEN
        dao = UniteDAO()

        # WHEN
        id_ml = dao.get_or_create_unit("ml")
        id_cl = dao.get_or_create_unit("cl")
        id_l = dao.get_or_create_unit("l")

        # THEN
        if id_ml == id_cl:
            raise AssertionError(
                message="Les IDs de 'ml' et 'cl' devraient être différents",
            )
        if id_ml == id_l:
            raise AssertionError(
                message="Les IDs de 'ml' et 'l' devraient être différents",
            )
        if id_cl == id_l:
            raise AssertionError(
                message="Les IDs de 'cl' et 'l' devraient être différents",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_or_create_unit_appels_multiples_meme_unite() -> None:
        """Teste que plusieurs appels pour la même unité retournent le même ID."""
        # GIVEN
        dao = UniteDAO()

        # WHEN
        id_1 = dao.get_or_create_unit("gramme")
        id_2 = dao.get_or_create_unit("gramme")
        id_3 = dao.get_or_create_unit("GRAMME")

        # THEN
        if id_1 != id_2:
            raise AssertionError(
                message=f"Les appels successifs devraient retourner le même ID, "
                f"obtenu: {id_1} et {id_2}",
            )
        if id_1 != id_3:
            raise AssertionError(
                message=f"La recherche insensible à la casse devrait retourner "
                f"le même ID, obtenu: {id_1} et {id_3}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_or_create_unit_unite_avec_espaces() -> None:
        """Teste la création d'une unité avec des espaces."""
        # GIVEN
        dao = UniteDAO()

        # WHEN
        result = dao.get_or_create_unit("once liquide")

        # THEN
        if not isinstance(result, int):
            raise TypeError(
                message=f"Le résultat devrait être un int, obtenu: {type(result)}",
            )
        if result <= 0:
            raise AssertionError(
                message=f"L'ID devrait être > 0, obtenu: {result}",
            )

    # ========== Tests pour get_unit_name_by_id ==========

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_unit_name_by_id_unite_existante(db_connection) -> None:
        """Teste la récupération du nom d'une unité existante."""
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

        dao = UniteDAO()

        # WHEN
        result = dao.get_unit_name_by_id(unite_id)

        # THEN
        if result is None:
            raise AssertionError(
                message="Le nom de l'unité devrait être trouvé",
            )
        if result != "millilitre":
            raise AssertionError(
                message=f"Le nom devrait être 'millilitre', obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_unit_name_by_id_unite_inexistante() -> None:
        """Teste la récupération du nom d'une unité inexistante."""
        # GIVEN
        dao = UniteDAO()

        # WHEN
        result = dao.get_unit_name_by_id(99999)

        # THEN
        if result is not None:
            raise AssertionError(
                message=f"Le résultat devrait être None, obtenu: {result}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_unit_name_by_id_plusieurs_unites(db_connection) -> None:
        """Teste la récupération de noms de plusieurs unités."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO unite (nom, abbreviation, type_unite)
                VALUES 
                    ('millilitre', 'ml', 'liquide'),
                    ('gramme', 'g', 'poids'),
                    ('once', 'oz', 'poids')
                RETURNING id_unite, nom
            """,
            )
            unites = cursor.fetchall()
            db_connection.commit()

        dao = UniteDAO()

        # WHEN & THEN
        for unite in unites:
            result = dao.get_unit_name_by_id(unite["id_unite"])
            if result != unite["nom"]:
                raise AssertionError(
                    message=f"Le nom devrait être '{unite['nom']}', obtenu: {result}",
                )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_unit_name_by_id_avec_caracteres_speciaux(
        db_connection,
    ) -> None:
        """Teste avec un nom d'unité contenant des caractères spéciaux."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO unite (nom, abbreviation, type_unite)
                VALUES ('degré celsius', '°C', 'temperature')
                RETURNING id_unite
            """,
            )
            unite_id = cursor.fetchone()["id_unite"]
            db_connection.commit()

        dao = UniteDAO()

        # WHEN
        result = dao.get_unit_name_by_id(unite_id)

        # THEN
        if result != "degré celsius":
            raise AssertionError(
                message=f"Le nom devrait être 'degré celsius', obtenu: {result}",
            )

    # ========== Tests d'intégration entre les deux méthodes ==========

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_integration_create_puis_get_name() -> None:
        """Teste la création puis la récupération du nom."""
        # GIVEN
        dao = UniteDAO()

        # WHEN
        id_unite = dao.get_or_create_unit("kilogramme")
        nom = dao.get_unit_name_by_id(id_unite)

        # THEN
        if nom != "kilogramme":
            raise AssertionError(
                message=f"Le nom devrait être 'kilogramme', obtenu: {nom}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_integration_cycle_complet_plusieurs_unites() -> None:
        """Teste un cycle complet avec plusieurs unités."""
        # GIVEN
        dao = UniteDAO()
        unites_a_creer = ["ml", "cl", "dl", "l"]

        # WHEN - Créer toutes les unités
        ids_crees = {}
        for unite in unites_a_creer:
            id_unite = dao.get_or_create_unit(unite)
            ids_crees[unite] = id_unite

        # THEN - Vérifier qu'on peut récupérer tous les noms
        for unite, id_attendu in ids_crees.items():
            nom_recupere = dao.get_unit_name_by_id(id_attendu)
            if nom_recupere != unite:
                raise AssertionError(
                    message=f"Le nom devrait être '{unite}', obtenu: {nom_recupere}",
                )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_integration_get_or_create_idempotence() -> None:
        """Teste l'idempotence de get_or_create_unit."""
        # GIVEN
        dao = UniteDAO()

        # WHEN - Créer la même unité plusieurs fois
        id_1 = dao.get_or_create_unit("pincée")
        nom_1 = dao.get_unit_name_by_id(id_1)

        id_2 = dao.get_or_create_unit("pincée")
        nom_2 = dao.get_unit_name_by_id(id_2)

        id_3 = dao.get_or_create_unit("PINCÉE")
        nom_3 = dao.get_unit_name_by_id(id_3)

        # THEN
        if id_1 != id_2 or id_2 != id_3:
            raise AssertionError(
                message=f"Les IDs devraient être identiques, "
                f"obtenu: {id_1}, {id_2}, {id_3}",
            )
        if nom_1 != nom_2 or nom_2 != nom_3:
            raise AssertionError(
                message=f"Les noms devraient être identiques, "
                f"obtenu: {nom_1}, {nom_2}, {nom_3}",
            )
