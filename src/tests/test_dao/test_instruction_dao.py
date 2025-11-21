"""Tests d'intégration pour InstructionDAO."""

import pytest

from src.dao.instruction_dao import InstructionDAO


class TestInstructionDAOAjout:
    """Tests pour l'ajout d'instructions."""

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_ajouter_instruction_success(db_connection) -> None:
        """Teste l'ajout d'une instruction pour un cocktail."""
        # GIVEN
        # Créer d'abord un cocktail
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Margarita', 'Cocktail', 'Margarita glass', TRUE, 'marg.jpg')
                RETURNING id_cocktail
            """)
            id_cocktail = cursor.fetchone()["id_cocktail"]
            db_connection.commit()

        dao = InstructionDAO()
        texte_instruction = "Rub the rim of the glass with lime. Shake with ice."
        langue = "en"

        # WHEN
        result = dao.ajouter_instruction(id_cocktail, texte_instruction, langue)

        # THEN
        if result is not True:
            raise AssertionError(
                message=f"Le résultat devrait être True, obtenu: {result}",
            )

        # Vérifier que l'instruction est bien en base
        with db_connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM instruction WHERE id_cocktail = %s AND langue = %s",
                (id_cocktail, langue),
            )
            row = cursor.fetchone()

            if row is None:
                raise AssertionError(
                    message="L'instruction devrait être en base",
                )

            if row["texte"] != texte_instruction:
                raise AssertionError(
                    message=f"Texte devrait être '{texte_instruction}', obtenu: "
                    f"{row['texte']}",
                )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_ajouter_instruction_langue_francais(db_connection) -> None:
        """Teste l'ajout d'une instruction en français."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Cosmopolitan', 'Cocktail', 'Cocktail glass', TRUE, 'cosmo.jpg')
                RETURNING id_cocktail
            """)
            id_cocktail = cursor.fetchone()["id_cocktail"]
            db_connection.commit()

        dao = InstructionDAO()
        texte_instruction = "Frotter le bord du verre avec du citron."
        langue = "fr"

        # WHEN
        result = dao.ajouter_instruction(id_cocktail, texte_instruction, langue)

        # THEN
        if result is not True:
            raise AssertionError(
                message=f"Le résultat devrait être True, obtenu: {result}",
            )

        with db_connection.cursor() as cursor:
            cursor.execute(
                "SELECT langue, texte FROM instruction WHERE id_cocktail = %s",
                (id_cocktail,),
            )
            row = cursor.fetchone()

            if row["langue"] != "fr":
                raise AssertionError(
                    message=f"Langue devrait être 'fr', obtenu: {row['langue']}",
                )

            if row["texte"] != texte_instruction:
                raise AssertionError(
                    message=f"Texte devrait être '{texte_instruction}', obtenu: "
                    f"{row['texte']}",
                )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_ajouter_instruction_cocktail_inexistant() -> None:
        """Teste l'ajout d'une instruction pour un cocktail inexistant."""
        # GIVEN
        dao = InstructionDAO()
        id_cocktail_inexistant = 999999
        texte_instruction = "Test instruction"

        # WHEN / THEN
        with pytest.raises(Exception):
            dao.ajouter_instruction(id_cocktail_inexistant, texte_instruction)
