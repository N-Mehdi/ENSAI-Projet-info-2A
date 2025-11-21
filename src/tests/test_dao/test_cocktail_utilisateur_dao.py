"""Tests d'intégration pour CocktailUtilisateurDAO."""

import pytest

from src.business_object.cocktail import Cocktail
from src.dao.cocktail_utilisateur_dao import CocktailUtilisateurDAO
from src.utils.exceptions import (
    CocktailNotFoundError,
    CocktailNotTestedError,
    PermissionDeniedError,
)


class TestCocktailUtilisateurDAOIntegration:
    """Tests d'intégration pour CocktailUtilisateurDAO."""

    # ========== Tests pour get_prive ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_prive_success(db_connection) -> None:
        """Teste la récupération des cocktails privés d'un utilisateur."""
        # GIVEN
        with db_connection.cursor() as cursor:
            # Créer un utilisateur
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('user1', 'user1@example.com', 'pass123', '1990-01-01')
                RETURNING id_utilisateur
            """)
            id_utilisateur = cursor.fetchone()["id_utilisateur"]

            # Créer un cocktail
            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Mojito Privé', 'Cocktail', 'Highball', TRUE, 'mojito.jpg')
                RETURNING id_cocktail
            """)
            id_cocktail = cursor.fetchone()["id_cocktail"]

            # Créer la relation d'accès (propriétaire)
            cursor.execute(
                """
                INSERT INTO acces (id_utilisateur, id_cocktail, is_owner, has_access)
                VALUES (%s, %s, TRUE, TRUE)
            """,
                (id_utilisateur, id_cocktail),
            )
            db_connection.commit()

        dao = CocktailUtilisateurDAO()

        # WHEN
        cocktails_prives = dao.get_prive(id_utilisateur)

        # THEN
        if not cocktails_prives:
            raise AssertionError(
                message="La liste ne devrait pas être vide",
            )
        if len(cocktails_prives) != 1:
            raise AssertionError(
                message=f"Devrait avoir 1 cocktail, obtenu: {len(cocktails_prives)}",
            )
        if cocktails_prives[0].nom != "Mojito Privé":
            raise AssertionError(
                message=f"Nom devrait être 'Mojito Privé', obtenu: "
                f"{cocktails_prives[0].nom}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_prive_empty() -> None:
        """Teste la récupération des cocktails privés pour un utilisateur sans
        cocktails.
        """
        # GIVEN
        dao = CocktailUtilisateurDAO()
        id_utilisateur_inexistant = 999999

        # WHEN
        cocktails_prives = dao.get_prive(id_utilisateur_inexistant)

        # THEN
        if cocktails_prives != []:
            raise AssertionError(
                message=f"La liste devrait être vide, obtenu: {cocktails_prives}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_prive_multiple_cocktails(db_connection) -> None:
        """Teste la récupération de plusieurs cocktails privés."""
        # GIVEN
        with db_connection.cursor() as cursor:
            # Créer un utilisateur
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('user2', 'user2@example.com', 'pass123', '1990-01-01')
                RETURNING id_utilisateur
            """)
            id_utilisateur = cursor.fetchone()["id_utilisateur"]

            # Créer deux cocktails
            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES
                    ('Cocktail 1', 'Cocktail', 'Highball', TRUE, 'c1.jpg'),
                    ('Cocktail 2', 'Shot', 'Shot glass', FALSE, 'c2.jpg')
                RETURNING id_cocktail
            """)
            id_cocktail1 = cursor.fetchone()["id_cocktail"]
            id_cocktail2 = cursor.fetchone()["id_cocktail"]

            # Créer les relations d'accès
            cursor.execute(
                """
                INSERT INTO acces (id_utilisateur, id_cocktail, is_owner, has_access)
                VALUES
                    (%s, %s, TRUE, TRUE),
                    (%s, %s, TRUE, TRUE)
            """,
                (id_utilisateur, id_cocktail1, id_utilisateur, id_cocktail2),
            )
            db_connection.commit()

        dao = CocktailUtilisateurDAO()

        # WHEN
        cocktails_prives = dao.get_prive(id_utilisateur)

        # THEN
        if len(cocktails_prives) != 2:
            raise AssertionError(
                message=f"Devrait avoir 2 cocktails, obtenu: {len(cocktails_prives)}",
            )

    # ========== Tests pour insert_cocktail_prive ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_insert_cocktail_prive_success(db_connection) -> None:
        """Teste l'insertion d'un cocktail privé."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('user3', 'user3@example.com', 'pass123', '1990-01-01')
                RETURNING id_utilisateur
            """)
            id_utilisateur = cursor.fetchone()["id_utilisateur"]
            db_connection.commit()

        dao = CocktailUtilisateurDAO()
        cocktail = Cocktail(
            id_cocktail=None,
            nom="Nouveau Cocktail",
            categorie="Cocktail",
            verre="Highball",
            alcool=True,
            image="nouveau.jpg",
        )

        # WHEN
        id_cocktail = dao.insert_cocktail_prive(id_utilisateur, cocktail)

        # THEN
        if id_cocktail is None:
            raise AssertionError(
                message="L'ID du cocktail ne devrait pas être None",
            )
        if not isinstance(id_cocktail, int):
            raise TypeError(
                message=f"L'ID devrait être un int, obtenu: {type(id_cocktail)}",
            )

        # Vérifier que le cocktail existe en base
        with db_connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM cocktail WHERE id_cocktail = %s",
                (id_cocktail,),
            )
            row = cursor.fetchone()
            if row is None:
                raise AssertionError(
                    message="Le cocktail devrait être en base",
                )
            if row["nom"] != "Nouveau Cocktail":
                raise AssertionError(
                    message=f"Nom devrait être 'Nouveau Cocktail', obtenu: "
                    f"{row['nom']}",
                )

        # Vérifier que la relation d'accès existe
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM acces
                WHERE id_utilisateur = %s AND id_cocktail = %s AND is_owner = TRUE
            """,
                (id_utilisateur, id_cocktail),
            )
            row = cursor.fetchone()
            if row is None:
                raise AssertionError(
                    message="La relation d'accès devrait exister",
                )

    # ========== Tests pour get_cocktail_ingredient ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_cocktail_ingredient_empty(db_connection) -> None:
        """Teste la récupération des ingrédients d'un cocktail sans ingrédients."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Cocktail Vide', 'Cocktail', 'Highball', TRUE, 'vide.jpg')
                RETURNING id_cocktail
            """)
            id_cocktail = cursor.fetchone()["id_cocktail"]
            db_connection.commit()

        dao = CocktailUtilisateurDAO()

        # WHEN
        ingredients = dao.get_cocktail_ingredient(id_cocktail)

        # THEN
        if ingredients != {}:
            raise AssertionError(
                message=f"Le dictionnaire devrait être vide, obtenu: {ingredients}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_cocktail_ingredient_with_ingredients(db_connection) -> None:
        """Teste la récupération des ingrédients d'un cocktail."""
        # GIVEN
        with db_connection.cursor() as cursor:
            # Créer un cocktail
            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Mojito', 'Cocktail', 'Highball', TRUE, 'mojito.jpg')
                RETURNING id_cocktail
            """)
            id_cocktail = cursor.fetchone()["id_cocktail"]

            # Créer des ingrédients
            cursor.execute("""
                INSERT INTO ingredient (nom, description, type, alcool, abv)
                VALUES
                    ('Rhum', 'Rhum blanc', 'Alcool', TRUE, '40'),
                    ('Menthe', 'Feuilles de menthe', 'Herbe', FALSE, NULL)
                RETURNING id_ingredient
            """)
            id_ingredient1 = cursor.fetchone()["id_ingredient"]
            id_ingredient2 = cursor.fetchone()["id_ingredient"]

            # Lier les ingrédients au cocktail
            cursor.execute(
                """
                INSERT INTO cocktail_ingredient (id_cocktail, id_ingredient, qte, unite)
                VALUES
                    (%s, %s, 50, 'ml'),
                    (%s, %s, 10, 'feuilles')
            """,
                (id_cocktail, id_ingredient1, id_cocktail, id_ingredient2),
            )
            db_connection.commit()

        dao = CocktailUtilisateurDAO()

        # WHEN
        ingredients = dao.get_cocktail_ingredient(id_cocktail)

        # THEN
        if len(ingredients) != 2:
            raise AssertionError(
                message=f"Devrait avoir 2 ingrédients, obtenu: {len(ingredients)}",
            )
        if id_ingredient1 not in ingredients:
            raise AssertionError(
                message=f"L'ingrédient {id_ingredient1} devrait être présent",
            )
        if id_ingredient2 not in ingredients:
            raise AssertionError(
                message=f"L'ingrédient {id_ingredient2} devrait être présent",
            )

    # ========== Tests pour update_cocktail_prive_modif_ingredient ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_update_ingredient_success(db_connection) -> None:
        """Teste la modification de la quantité d'un ingrédient."""
        # GIVEN
        with db_connection.cursor() as cursor:
            # Créer utilisateur
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('user4', 'user4@example.com', 'pass123', '1990-01-01')
                RETURNING id_utilisateur
            """)
            id_utilisateur = cursor.fetchone()["id_utilisateur"]

            # Créer cocktail
            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Cocktail Test', 'Cocktail', 'Highball', TRUE, 'test.jpg')
                RETURNING id_cocktail
            """)
            id_cocktail = cursor.fetchone()["id_cocktail"]

            # Créer relation d'accès
            cursor.execute(
                """
                INSERT INTO acces (id_utilisateur, id_cocktail, is_owner, has_access)
                VALUES (%s, %s, TRUE, TRUE)
            """,
                (id_utilisateur, id_cocktail),
            )

            # Créer ingrédient
            cursor.execute("""
                INSERT INTO ingredient (nom, description, type, alcool, abv)
                VALUES ('Vodka', 'Vodka', 'Alcool', TRUE, '40')
                RETURNING id_ingredient
            """)
            id_ingredient = cursor.fetchone()["id_ingredient"]

            # Lier ingrédient au cocktail
            cursor.execute(
                """
                INSERT INTO cocktail_ingredient (id_cocktail, id_ingredient, qte, unite)
                VALUES (%s, %s, 50, 'ml')
            """,
                (id_cocktail, id_ingredient),
            )
            db_connection.commit()

        dao = CocktailUtilisateurDAO()
        nouvelle_quantite = 75.0

        # WHEN
        dao.update_cocktail_prive_modif_ingredient(
            id_utilisateur,
            id_cocktail,
            id_ingredient,
            nouvelle_quantite,
        )

        # THEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT qte FROM cocktail_ingredient
                WHERE id_cocktail = %s AND id_ingredient = %s
            """,
                (id_cocktail, id_ingredient),
            )
            row = cursor.fetchone()
            if float(row["qte"]) != nouvelle_quantite:
                raise AssertionError(
                    message=f"Quantité devrait être {nouvelle_quantite}, obtenu: "
                    f"{row['qte']}",
                )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_update_ingredient_permission_denied(db_connection) -> None:
        """Teste la modification d'un ingrédient sans permission."""
        # GIVEN
        with db_connection.cursor() as cursor:
            # Créer deux utilisateurs
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES
                    ('owner', 'owner@example.com', 'pass123', '1990-01-01'),
                    ('other', 'other@example.com', 'pass123', '1990-01-01')
                RETURNING id_utilisateur
            """)
            id_owner = cursor.fetchone()["id_utilisateur"]
            id_other = cursor.fetchone()["id_utilisateur"]

            # Créer cocktail
            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Private Cocktail', 'Cocktail', 'Highball', TRUE, 'priv.jpg')
                RETURNING id_cocktail
            """)
            id_cocktail = cursor.fetchone()["id_cocktail"]

            # Créer relation d'accès pour le propriétaire seulement
            cursor.execute(
                """
                INSERT INTO acces (id_utilisateur, id_cocktail, is_owner, has_access)
                VALUES (%s, %s, TRUE, TRUE)
            """,
                (id_owner, id_cocktail),
            )

            # Créer ingrédient
            cursor.execute("""
                INSERT INTO ingredient (nom, description, type, alcool, abv)
                VALUES ('Gin', 'Gin', 'Alcool', TRUE, '40')
                RETURNING id_ingredient
            """)
            id_ingredient = cursor.fetchone()["id_ingredient"]

            # Lier ingrédient
            cursor.execute(
                """
                INSERT INTO cocktail_ingredient (id_cocktail, id_ingredient, qte, unite)
                VALUES (%s, %s, 50, 'ml')
            """,
                (id_cocktail, id_ingredient),
            )
            db_connection.commit()

        dao = CocktailUtilisateurDAO()

        # WHEN / THEN
        with pytest.raises(PermissionDeniedError):
            dao.update_cocktail_prive_modif_ingredient(
                id_other,
                id_cocktail,
                id_ingredient,
                100.0,
            )

    # ========== Tests pour update_cocktail_prive_ajout_ingredient ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_ajout_ingredient_success(db_connection) -> None:
        """Teste l'ajout d'un ingrédient à un cocktail."""
        # GIVEN
        with db_connection.cursor() as cursor:
            # Créer utilisateur
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('user5', 'user5@example.com', 'pass123', '1990-01-01')
                RETURNING id_utilisateur
            """)
            id_utilisateur = cursor.fetchone()["id_utilisateur"]

            # Créer cocktail
            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Cocktail Ajout', 'Cocktail', 'Highball', TRUE, 'ajout.jpg')
                RETURNING id_cocktail
            """)
            id_cocktail = cursor.fetchone()["id_cocktail"]

            # Créer relation d'accès
            cursor.execute(
                """
                INSERT INTO acces (id_utilisateur, id_cocktail, is_owner, has_access)
                VALUES (%s, %s, TRUE, TRUE)
            """,
                (id_utilisateur, id_cocktail),
            )

            # Créer ingrédient
            cursor.execute("""
                INSERT INTO ingredient (nom, description, type, alcool, abv)
                VALUES ('Citron', 'Jus de citron', 'Fruit', FALSE, NULL)
                RETURNING id_ingredient
            """)
            id_ingredient = cursor.fetchone()["id_ingredient"]
            db_connection.commit()

        dao = CocktailUtilisateurDAO()
        quantite = 30.0

        # WHEN
        dao.update_cocktail_prive_ajout_ingredient(
            id_utilisateur,
            id_cocktail,
            id_ingredient,
            quantite,
        )

        # THEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM cocktail_ingredient
                WHERE id_cocktail = %s AND id_ingredient = %s
            """,
                (id_cocktail, id_ingredient),
            )
            row = cursor.fetchone()
            if row is None:
                raise AssertionError(
                    message="L'ingrédient devrait être ajouté",
                )
            if float(row["qte"]) != quantite:
                raise AssertionError(
                    message=f"Quantité devrait être {quantite}, obtenu: {row['qte']}",
                )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_ajout_ingredient_permission_denied(db_connection) -> None:
        """Teste l'ajout d'un ingrédient sans permission."""
        # GIVEN
        with db_connection.cursor() as cursor:
            # Créer deux utilisateurs
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES
                    ('owner2', 'owner2@example.com', 'pass123', '1990-01-01'),
                    ('other2', 'other2@example.com', 'pass123', '1990-01-01')
                RETURNING id_utilisateur
            """)
            id_owner = cursor.fetchone()["id_utilisateur"]
            id_other = cursor.fetchone()["id_utilisateur"]

            # Créer cocktail
            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Private Cocktail 2', 'Cocktail', 'Highball', TRUE, 'p2.jpg')
                RETURNING id_cocktail
            """)
            id_cocktail = cursor.fetchone()["id_cocktail"]

            # Créer relation d'accès pour le propriétaire seulement
            cursor.execute(
                """
                INSERT INTO acces (id_utilisateur, id_cocktail, is_owner, has_access)
                VALUES (%s, %s, TRUE, TRUE)
            """,
                (id_owner, id_cocktail),
            )

            # Créer ingrédient
            cursor.execute("""
                INSERT INTO ingredient (nom, description, type, alcool, abv)
                VALUES ('Sucre', 'Sucre de canne', 'Autre', FALSE, NULL)
                RETURNING id_ingredient
            """)
            id_ingredient = cursor.fetchone()["id_ingredient"]
            db_connection.commit()

        dao = CocktailUtilisateurDAO()

        # WHEN / THEN
        with pytest.raises(PermissionDeniedError):
            dao.update_cocktail_prive_ajout_ingredient(
                id_other,
                id_cocktail,
                id_ingredient,
                20.0,
            )

    # ========== Tests pour update_cocktail_prive_supprimer_ingredient ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_supprimer_ingredient_success(db_connection) -> None:
        """Teste la suppression d'un ingrédient d'un cocktail."""
        # GIVEN
        with db_connection.cursor() as cursor:
            # Créer utilisateur
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('user6', 'user6@example.com', 'pass123', '1990-01-01')
                RETURNING id_utilisateur
            """)
            id_utilisateur = cursor.fetchone()["id_utilisateur"]

            # Créer cocktail
            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Cocktail Suppr', 'Cocktail', 'Highball', TRUE, 'suppr.jpg')
                RETURNING id_cocktail
            """)
            id_cocktail = cursor.fetchone()["id_cocktail"]

            # Créer relation d'accès
            cursor.execute(
                """
                INSERT INTO acces (id_utilisateur, id_cocktail, is_owner, has_access)
                VALUES (%s, %s, TRUE, TRUE)
            """,
                (id_utilisateur, id_cocktail),
            )

            # Créer ingrédient
            cursor.execute("""
                INSERT INTO ingredient (nom, description, type, alcool, abv)
                VALUES ('Tequila', 'Tequila', 'Alcool', TRUE, '40')
                RETURNING id_ingredient
            """)
            id_ingredient = cursor.fetchone()["id_ingredient"]

            # Lier ingrédient
            cursor.execute(
                """
                INSERT INTO cocktail_ingredient (id_cocktail, id_ingredient, qte, unite)
                VALUES (%s, %s, 50, 'ml')
            """,
                (id_cocktail, id_ingredient),
            )
            db_connection.commit()

        dao = CocktailUtilisateurDAO()

        # WHEN
        dao.update_cocktail_prive_supprimer_ingredient(
            id_utilisateur,
            id_cocktail,
            id_ingredient,
        )

        # THEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM cocktail_ingredient
                WHERE id_cocktail = %s AND id_ingredient = %s
            """,
                (id_cocktail, id_ingredient),
            )
            row = cursor.fetchone()
            if row is not None:
                raise AssertionError(
                    message="L'ingrédient ne devrait plus exister",
                )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_supprimer_ingredient_permission_denied(db_connection) -> None:
        """Teste la suppression d'un ingrédient sans permission."""
        # GIVEN
        with db_connection.cursor() as cursor:
            # Créer deux utilisateurs
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES
                    ('owner3', 'owner3@example.com', 'pass123', '1990-01-01'),
                    ('other3', 'other3@example.com', 'pass123', '1990-01-01')
                RETURNING id_utilisateur
            """)
            id_owner = cursor.fetchone()["id_utilisateur"]
            id_other = cursor.fetchone()["id_utilisateur"]

            # Créer cocktail
            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Private Cocktail 3', 'Cocktail', 'Highball', TRUE, 'p3.jpg')
                RETURNING id_cocktail
            """)
            id_cocktail = cursor.fetchone()["id_cocktail"]

            # Créer relation d'accès
            cursor.execute(
                """
                INSERT INTO acces (id_utilisateur, id_cocktail, is_owner, has_access)
                VALUES (%s, %s, TRUE, TRUE)
            """,
                (id_owner, id_cocktail),
            )

            # Créer ingrédient
            cursor.execute("""
                INSERT INTO ingredient (nom, description, type, alcool, abv)
                VALUES ('Whisky', 'Whisky', 'Alcool', TRUE, '40')
                RETURNING id_ingredient
            """)
            id_ingredient = cursor.fetchone()["id_ingredient"]

            # Lier ingrédient
            cursor.execute(
                """
                INSERT INTO cocktail_ingredient (id_cocktail, id_ingredient, qte, unite)
                VALUES (%s, %s, 50, 'ml')
            """,
                (id_cocktail, id_ingredient),
            )
            db_connection.commit()

        dao = CocktailUtilisateurDAO()

        # WHEN / THEN
        with pytest.raises(PermissionDeniedError):
            dao.update_cocktail_prive_supprimer_ingredient(
                id_other,
                id_cocktail,
                id_ingredient,
            )

    # ========== Tests pour delete_cocktail_prive ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_delete_cocktail_prive_success(db_connection) -> None:
        """Teste la suppression d'un cocktail privé."""
        # GIVEN
        with db_connection.cursor() as cursor:
            # Créer utilisateur
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('user7', 'user7@example.com', 'pass123', '1990-01-01')
                RETURNING id_utilisateur
            """)
            id_utilisateur = cursor.fetchone()["id_utilisateur"]

            # Créer cocktail
            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Cocktail Delete', 'Cocktail', 'Highball', TRUE, 'delete.jpg')
                RETURNING id_cocktail
            """)
            id_cocktail = cursor.fetchone()["id_cocktail"]

            # Créer relation d'accès
            cursor.execute(
                """
                INSERT INTO acces (id_utilisateur, id_cocktail, is_owner, has_access)
                VALUES (%s, %s, TRUE, TRUE)
            """,
                (id_utilisateur, id_cocktail),
            )
            db_connection.commit()

        dao = CocktailUtilisateurDAO()

        # WHEN
        dao.delete_cocktail_prive(id_utilisateur, id_cocktail)

        # THEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM cocktail WHERE id_cocktail = %s",
                (id_cocktail,),
            )
            row = cursor.fetchone()
            if row is not None:
                raise AssertionError(
                    message="Le cocktail ne devrait plus exister",
                )

    # ========== Tests pour get_favoris ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_favoris_empty() -> None:
        """Teste la récupération des favoris pour un utilisateur sans favoris."""
        # GIVEN
        dao = CocktailUtilisateurDAO()
        id_utilisateur_inexistant = 999999

        # WHEN
        favoris = dao.get_favoris(id_utilisateur_inexistant)

        # THEN
        if favoris != []:
            raise AssertionError(
                message=f"La liste devrait être vide, obtenu: {favoris}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_favoris_with_favorites(db_connection) -> None:
        """Teste la récupération des favoris."""
        # GIVEN
        with db_connection.cursor() as cursor:
            # Créer utilisateur
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('user8', 'user8@example.com', 'pass123', '1990-01-01')
                RETURNING id_utilisateur
            """)
            id_utilisateur = cursor.fetchone()["id_utilisateur"]

            # Créer cocktail
            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Cocktail Favori', 'Cocktail', 'Highball', TRUE, 'fav.jpg')
                RETURNING id_cocktail
            """)
            id_cocktail = cursor.fetchone()["id_cocktail"]

            # Créer avis avec favoris
            cursor.execute(
                """
                INSERT INTO avis (id_utilisateur, id_cocktail, note, commentaire,
                favoris)
                VALUES (%s, %s, NULL, NULL, TRUE)
            """,
                (id_utilisateur, id_cocktail),
            )
            db_connection.commit()

        dao = CocktailUtilisateurDAO()

        # WHEN
        favoris = dao.get_favoris(id_utilisateur)

        # THEN
        if not favoris:
            raise AssertionError(
                message="La liste ne devrait pas être vide",
            )
        if favoris[0].nom != "Cocktail Favori":
            raise AssertionError(
                message=f"Nom devrait être 'Cocktail Favori', obtenu: {favoris[0].nom}",
            )

    # ========== Tests pour update_cocktail_favoris ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_update_cocktail_favoris_success(db_connection) -> None:
        """Teste l'ajout d'un cocktail aux favoris."""
        # GIVEN
        with db_connection.cursor() as cursor:
            # Créer utilisateur
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('user9', 'user9@example.com', 'pass123', '1990-01-01')
                RETURNING id_utilisateur
            """)
            id_utilisateur = cursor.fetchone()["id_utilisateur"]

            # Créer cocktail
            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Cocktail Fav', 'Cocktail', 'Highball', TRUE, 'fav2.jpg')
                RETURNING id_cocktail
            """)
            id_cocktail = cursor.fetchone()["id_cocktail"]

            # Créer avis sans favoris
            cursor.execute(
                """
                INSERT INTO avis (id_utilisateur, id_cocktail, note, commentaire,
                favoris)
                VALUES (%s, %s, NULL, NULL, FALSE)
            """,
                (id_utilisateur, id_cocktail),
            )
            db_connection.commit()

        dao = CocktailUtilisateurDAO()

        # WHEN
        dao.update_cocktail_favoris(id_utilisateur, id_cocktail)

        # THEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT favoris FROM avis
                WHERE id_utilisateur = %s AND id_cocktail = %s
            """,
                (id_utilisateur, id_cocktail),
            )
            row = cursor.fetchone()
            if not row["favoris"]:
                raise AssertionError(
                    message="Le cocktail devrait être en favoris",
                )

    # ========== Tests pour delete_cocktail_favoris ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_delete_cocktail_favoris_success(db_connection) -> None:
        """Teste le retrait d'un cocktail des favoris."""
        # GIVEN
        with db_connection.cursor() as cursor:
            # Créer utilisateur
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('user10', 'user10@example.com', 'pass123', '1990-01-01')
                RETURNING id_utilisateur
            """)
            id_utilisateur = cursor.fetchone()["id_utilisateur"]

            # Créer cocktail
            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Cocktail Unfav', 'Cocktail', 'Highball', TRUE, 'unfav.jpg')
                RETURNING id_cocktail
            """)
            id_cocktail = cursor.fetchone()["id_cocktail"]

            # Créer avis avec favoris
            cursor.execute(
                """
                INSERT INTO avis (id_utilisateur, id_cocktail, note, commentaire,
                favoris)
                VALUES (%s, %s, NULL, NULL, TRUE)
            """,
                (id_utilisateur, id_cocktail),
            )
            db_connection.commit()

        dao = CocktailUtilisateurDAO()

        # WHEN
        dao.delete_cocktail_favoris(id_utilisateur, id_cocktail)

        # THEN
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT favoris FROM avis
                WHERE id_utilisateur = %s AND id_cocktail = %s
            """,
                (id_utilisateur, id_cocktail),
            )
            row = cursor.fetchone()
            if row["favoris"]:
                raise AssertionError(
                    message="Le cocktail ne devrait plus être en favoris",
                )

    # ========== Tests pour get_teste ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_teste_empty() -> None:
        """Teste la récupération des cocktails testés pour un utilisateur sans
        cocktails testés.
        """
        # GIVEN
        dao = CocktailUtilisateurDAO()
        id_utilisateur_inexistant = 999999

        # WHEN
        testes = dao.get_teste(id_utilisateur_inexistant)

        # THEN
        if testes != []:
            raise AssertionError(
                message=f"La liste devrait être vide, obtenu: {testes}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_teste_with_tested_cocktails(db_connection) -> None:
        """Teste la récupération des cocktails testés."""
        # GIVEN
        with db_connection.cursor() as cursor:
            # Créer utilisateur
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('user11', 'user11@example.com', 'pass123', '1990-01-01')
                RETURNING id_utilisateur
            """)
            id_utilisateur = cursor.fetchone()["id_utilisateur"]

            # Créer cocktail
            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Cocktail Testé', 'Cocktail', 'Highball', TRUE, 'teste.jpg')
                RETURNING id_cocktail
            """)
            id_cocktail = cursor.fetchone()["id_cocktail"]

            # Créer avis avec teste=TRUE
            cursor.execute(
                """
                INSERT INTO avis (id_utilisateur, id_cocktail, note, commentaire,
                favoris, teste)
                VALUES (%s, %s, NULL, NULL, FALSE, TRUE)
            """,
                (id_utilisateur, id_cocktail),
            )
            db_connection.commit()

        dao = CocktailUtilisateurDAO()

        # WHEN
        testes = dao.get_teste(id_utilisateur)

        # THEN
        if not testes:
            raise AssertionError(
                message="La liste ne devrait pas être vide",
            )
        if testes[0].nom != "Cocktail Testé":
            raise AssertionError(
                message=f"Nom devrait être 'Cocktail Testé', obtenu: {testes[0].nom}",
            )

    # ========== Tests pour get_cocktail_id_by_name ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_cocktail_id_by_name_found(db_connection) -> None:
        """Teste la récupération de l'ID d'un cocktail par son nom."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Margarita', 'Cocktail', 'Margarita glass', TRUE, 'marg.jpg')
                RETURNING id_cocktail
            """)
            id_cocktail_attendu = cursor.fetchone()["id_cocktail"]
            db_connection.commit()

        dao = CocktailUtilisateurDAO()

        # WHEN
        id_cocktail = dao.get_cocktail_id_by_name("Margarita")

        # THEN
        if id_cocktail != id_cocktail_attendu:
            raise AssertionError(
                message=f"ID devrait être {id_cocktail_attendu}, obtenu: {id_cocktail}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_cocktail_id_by_name_case_insensitive(db_connection) -> None:
        """Teste que la recherche est insensible à la casse."""
        # GIVEN
        with db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('CaSe TeStInG', 'Cocktail', 'Highball', TRUE, 'case.jpg')
                RETURNING id_cocktail
            """)
            id_cocktail_attendu = cursor.fetchone()["id_cocktail"]
            db_connection.commit()

        dao = CocktailUtilisateurDAO()

        # WHEN
        id_lower = dao.get_cocktail_id_by_name("case testing")
        id_upper = dao.get_cocktail_id_by_name("CASE TESTING")

        # THEN
        if id_lower != id_cocktail_attendu:
            raise AssertionError(
                message=f"ID devrait être {id_cocktail_attendu}, obtenu: {id_lower}",
            )
        if id_upper != id_cocktail_attendu:
            raise AssertionError(
                message=f"ID devrait être {id_cocktail_attendu}, obtenu: {id_upper}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_get_cocktail_id_by_name_not_found() -> None:
        """Teste la recherche d'un cocktail inexistant."""
        # GIVEN
        dao = CocktailUtilisateurDAO()

        # WHEN
        id_cocktail = dao.get_cocktail_id_by_name("Cocktail Inexistant XYZ")

        # THEN
        if id_cocktail is not None:
            raise AssertionError(
                message=f"ID devrait être None, obtenu: {id_cocktail}",
            )

    # ========== Tests pour ajouter_cocktail_teste ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_ajouter_cocktail_teste_success(db_connection) -> None:
        """Teste l'ajout d'un cocktail aux testés."""
        # GIVEN
        with db_connection.cursor() as cursor:
            # Créer utilisateur
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('user12', 'user12@example.com', 'pass123', '1990-01-01')
                RETURNING id_utilisateur
            """)
            id_utilisateur = cursor.fetchone()["id_utilisateur"]

            # Créer cocktail
            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Pina Colada', 'Cocktail', 'Hurricane glass', TRUE, 'pina.jpg')
                RETURNING id_cocktail
            """)
            id_cocktail = cursor.fetchone()["id_cocktail"]
            db_connection.commit()

        dao = CocktailUtilisateurDAO()

        # WHEN
        result = dao.ajouter_cocktail_teste(id_utilisateur, "Pina Colada")

        # THEN
        if result["nom_cocktail"] != "Pina Colada":
            raise AssertionError(
                message=f"Nom devrait être 'Pina Colada', obtenu: "
                f"{result['nom_cocktail']}",
            )
        if result["id_cocktail"] != id_cocktail:
            raise AssertionError(
                message=f"ID devrait être {id_cocktail}, obtenu: "
                f"{result['id_cocktail']}",
            )
        if result["teste"] is not True:
            raise AssertionError(
                message=f"teste devrait être True, obtenu: {result['teste']}",
            )
        if result["deja_teste"] is not False:
            raise AssertionError(
                message=f"deja_teste devrait être False, obtenu: "
                f"{result['deja_teste']}",
            )

        # Vérifier en base
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT teste FROM avis
                WHERE id_utilisateur = %s AND id_cocktail = %s
            """,
                (id_utilisateur, id_cocktail),
            )
            row = cursor.fetchone()
            if not row["teste"]:
                raise AssertionError(
                    message="Le cocktail devrait être marqué comme testé",
                )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_ajouter_cocktail_teste_already_tested(db_connection) -> None:
        """Teste l'ajout d'un cocktail déjà testé."""
        # GIVEN
        with db_connection.cursor() as cursor:
            # Créer utilisateur
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('user13', 'user13@example.com', 'pass123', '1990-01-01')
                RETURNING id_utilisateur
            """)
            id_utilisateur = cursor.fetchone()["id_utilisateur"]

            # Créer cocktail
            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Daiquiri', 'Cocktail', 'Cocktail glass', TRUE, 'daiq.jpg')
                RETURNING id_cocktail
            """)
            id_cocktail = cursor.fetchone()["id_cocktail"]

            # Créer avis avec teste=TRUE
            cursor.execute(
                """
                INSERT INTO avis (id_utilisateur, id_cocktail, note, commentaire,
                favoris, teste)
                VALUES (%s, %s, NULL, NULL, FALSE, TRUE)
            """,
                (id_utilisateur, id_cocktail),
            )
            db_connection.commit()

        dao = CocktailUtilisateurDAO()

        # WHEN
        result = dao.ajouter_cocktail_teste(id_utilisateur, "Daiquiri")

        # THEN
        if result["deja_teste"] is not True:
            raise AssertionError(
                message=f"deja_teste devrait être True, obtenu: {result['deja_teste']}",
            )
        if result["teste"] is not True:
            raise AssertionError(
                message=f"teste devrait être True, obtenu: {result['teste']}",
            )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_ajouter_cocktail_teste_not_found() -> None:
        """Teste l'ajout d'un cocktail inexistant aux testés."""
        # GIVEN
        dao = CocktailUtilisateurDAO()
        id_utilisateur = 1

        # WHEN / THEN
        with pytest.raises(CocktailNotFoundError):
            dao.ajouter_cocktail_teste(id_utilisateur, "Cocktail Inexistant")

    # ========== Tests pour retirer_cocktail_teste ==========
    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_retirer_cocktail_teste_success(db_connection) -> None:
        """Teste le retrait d'un cocktail des testés."""
        # GIVEN
        with db_connection.cursor() as cursor:
            # Créer utilisateur
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('user14', 'user14@example.com', 'pass123', '1990-01-01')
                RETURNING id_utilisateur
            """)
            id_utilisateur = cursor.fetchone()["id_utilisateur"]

            # Créer cocktail
            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Manhattan', 'Cocktail', 'Cocktail glass', TRUE, 'manh.jpg')
                RETURNING id_cocktail
            """)
            id_cocktail = cursor.fetchone()["id_cocktail"]

            # Créer avis avec teste=TRUE
            cursor.execute(
                """
                INSERT INTO avis (id_utilisateur, id_cocktail, note, commentaire,
                favoris, teste)
                VALUES (%s, %s, NULL, NULL, FALSE, TRUE)
            """,
                (id_utilisateur, id_cocktail),
            )
            db_connection.commit()

        dao = CocktailUtilisateurDAO()

        # WHEN
        result = dao.retirer_cocktail_teste(id_utilisateur, "Manhattan")

        # THEN
        if result["nom_cocktail"] != "Manhattan":
            raise AssertionError(
                message=f"Nom devrait être 'Manhattan', obtenu: "
                f"{result['nom_cocktail']}",
            )
        if result["teste"] is not False:
            raise AssertionError(
                message=f"teste devrait être False, obtenu: {result['teste']}",
            )

        # Vérifier en base
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT teste FROM avis
                WHERE id_utilisateur = %s AND id_cocktail = %s
            """,
                (id_utilisateur, id_cocktail),
            )
            row = cursor.fetchone()
            if row["teste"]:
                raise AssertionError(
                    message="Le cocktail ne devrait plus être marqué comme testé",
                )

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_retirer_cocktail_teste_not_tested(db_connection) -> None:
        """Teste le retrait d'un cocktail qui n'est pas testé."""
        # GIVEN
        with db_connection.cursor() as cursor:
            # Créer utilisateur
            cursor.execute("""
                INSERT INTO utilisateur (pseudo, mail, mot_de_passe, date_naissance)
                VALUES ('user15', 'user15@example.com', 'pass123', '1990-01-01')
                RETURNING id_utilisateur
            """)
            id_utilisateur = cursor.fetchone()["id_utilisateur"]

            # Créer cocktail
            cursor.execute("""
                INSERT INTO cocktail (nom, categorie, verre, alcool, image)
                VALUES ('Negroni', 'Cocktail', 'Old fashioned glass', TRUE, 'negr.jpg')
                RETURNING id_cocktail
            """)
            id_cocktail = cursor.fetchone()["id_cocktail"]

            # Créer avis avec teste=FALSE
            cursor.execute(
                """
                INSERT INTO avis (id_utilisateur, id_cocktail, note, commentaire,
                favoris, teste)
                VALUES (%s, %s, NULL, NULL, FALSE, FALSE)
            """,
                (id_utilisateur, id_cocktail),
            )
            db_connection.commit()

        dao = CocktailUtilisateurDAO()

        # WHEN / THEN
        with pytest.raises(CocktailNotTestedError):
            dao.retirer_cocktail_teste(id_utilisateur, "Negroni")

    @pytest.mark.usefixtures("clean_database")
    @staticmethod
    def test_retirer_cocktail_teste_not_found() -> None:
        """Teste le retrait d'un cocktail inexistant des testés."""
        # GIVEN
        dao = CocktailUtilisateurDAO()
        id_utilisateur = 1

        # WHEN / THEN
        with pytest.raises(CocktailNotFoundError):
            dao.retirer_cocktail_teste(id_utilisateur, "Cocktail Inexistant")
