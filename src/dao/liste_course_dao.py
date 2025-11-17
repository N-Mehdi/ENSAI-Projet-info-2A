"""doc."""

from src.dao.db_connection import DBConnection
from src.utils.conversion_unite import UnitConverter
from src.utils.log_decorator import log
from src.utils.singleton import Singleton


class ListeCourseDAO(metaclass=Singleton):
    """DAO pour gérer la liste de course des utilisateurs."""

    @log
    def get_liste_course(self, id_utilisateur: int) -> list[dict]:
        """Récupère la liste de course d'un utilisateur.

        Parameters
        ----------
        id_utilisateur : int
            ID de l'utilisateur

        Returns
        -------
        list[dict]
            Liste des items de la liste de course

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    lc.id_ingredient,
                    i.nom as nom_ingredient,
                    lc.quantite,
                    lc.effectue,
                    lc.id_unite,
                    u.abbreviation as code_unite,
                    u.nom as nom_unite_complet
                FROM liste_course lc
                JOIN ingredient i ON lc.id_ingredient = i.id_ingredient
                LEFT JOIN unite u ON lc.id_unite = u.id_unite
                WHERE lc.id_utilisateur = %(id_utilisateur)s
                ORDER BY lc.effectue ASC, i.nom ASC
                """,
                {"id_utilisateur": id_utilisateur},
            )
            return cursor.fetchall()

    @log
    def add_to_liste_course(
        self,
        id_utilisateur: int,
        id_ingredient: int,
        quantite: float,
        id_unite: int,
    ) -> dict:
        """Ajoute un ingrédient à la liste de course."""
        with DBConnection().connection as connection, connection.cursor() as cursor:
            # Vérifier si l'ingrédient existe déjà dans la liste
            cursor.execute(
                """
                SELECT lc.quantite, lc.id_unite, u.type_unite as type_unite, u.abbreviation as code_unite
                FROM liste_course lc
                LEFT JOIN unite u ON lc.id_unite = u.id_unite
                WHERE lc.id_utilisateur = %(id_utilisateur)s
                AND lc.id_ingredient = %(id_ingredient)s
                """,
                {
                    "id_utilisateur": id_utilisateur,
                    "id_ingredient": id_ingredient,
                },
            )
            existing = cursor.fetchone()

            if existing:
                # L'ingrédient existe déjà
                quantite_existante = float(existing["quantite"])
                id_unite_existante = existing["id_unite"]
                type_unite_existante = existing["type_unite"]
                code_unite_existante = existing["code_unite"]

                # Récupérer les infos de la nouvelle unité
                cursor.execute(
                    "SELECT abbreviation, type_unite FROM unite WHERE id_unite = %(id_unite)s",
                    {"id_unite": id_unite},
                )
                new_unite_info = cursor.fetchone()
                code_unite_nouvelle = new_unite_info["abbreviation"] if new_unite_info else None

                code_existante_norm = UnitConverter.normalize_unit(code_unite_existante)
                code_nouvelle_norm = UnitConverter.normalize_unit(code_unite_nouvelle)

                if code_existante_norm == code_nouvelle_norm:
                    # Même unité → additionner directement
                    nouvelle_quantite = quantite_existante + quantite

                    cursor.execute(
                        """
                        UPDATE liste_course
                        SET quantite = %(nouvelle_quantite)s,
                            effectue = FALSE
                        WHERE id_utilisateur = %(id_utilisateur)s
                        AND id_ingredient = %(id_ingredient)s
                        """,
                        {
                            "nouvelle_quantite": nouvelle_quantite,
                            "id_utilisateur": id_utilisateur,
                            "id_ingredient": id_ingredient,
                        },
                    )
                elif (
                    type_unite_existante
                    and new_unite_info
                    and type_unite_existante == new_unite_info["type_unite"]
                    and type_unite_existante == "liquide"
                ):
                    # Unités différentes mais même type (liquide) -> convertir et additionner
                    code_unite_nouvelle = new_unite_info["abbreviation"]

                    # Convertir tout en ml
                    ml_existant = UnitConverter.convert_to_ml(quantite_existante, code_unite_existante)
                    ml_nouveau = UnitConverter.convert_to_ml(quantite, code_unite_nouvelle)

                    if ml_existant and ml_nouveau:
                        # Additionner en ml et reconvertir vers l'unité existante
                        total_ml = ml_existant + ml_nouveau
                        facteur = UnitConverter.LIQUID_TO_ML.get(code_unite_existante.lower(), 1)
                        nouvelle_quantite = total_ml / facteur

                        cursor.execute(
                            """
                            UPDATE liste_course
                            SET quantite = %(nouvelle_quantite)s,
                                effectue = FALSE
                            WHERE id_utilisateur = %(id_utilisateur)s
                            AND id_ingredient = %(id_ingredient)s
                            """,
                            {
                                "nouvelle_quantite": nouvelle_quantite,
                                "id_utilisateur": id_utilisateur,
                                "id_ingredient": id_ingredient,
                            },
                        )
                    else:
                        # Conversion impossible -> remplacer
                        cursor.execute(
                            """
                            UPDATE liste_course
                            SET quantite = %(quantite)s,
                                id_unite = %(id_unite)s,
                                effectue = FALSE
                            WHERE id_utilisateur = %(id_utilisateur)s
                            AND id_ingredient = %(id_ingredient)s
                            """,
                            {
                                "quantite": quantite,
                                "id_unite": id_unite,
                                "id_utilisateur": id_utilisateur,
                                "id_ingredient": id_ingredient,
                            },
                        )
                else:
                    # Types différents ou non convertibles -> remplacer
                    cursor.execute(
                        """
                        UPDATE liste_course
                        SET quantite = %(quantite)s,
                            id_unite = %(id_unite)s,
                            effectue = FALSE
                        WHERE id_utilisateur = %(id_utilisateur)s
                        AND id_ingredient = %(id_ingredient)s
                        """,
                        {
                            "quantite": quantite,
                            "id_unite": id_unite,
                            "id_utilisateur": id_utilisateur,
                            "id_ingredient": id_ingredient,
                        },
                    )
            else:
                # L'ingrédient n'existe pas -> créer
                cursor.execute(
                    """
                    INSERT INTO liste_course (id_utilisateur, id_ingredient, quantite, id_unite, effectue)
                    VALUES (%(id_utilisateur)s, %(id_ingredient)s, %(quantite)s, %(id_unite)s, FALSE)
                    """,
                    {
                        "id_utilisateur": id_utilisateur,
                        "id_ingredient": id_ingredient,
                        "quantite": quantite,
                        "id_unite": id_unite,
                    },
                )

            # Retourner l'item mis à jour
            cursor.execute(
                """
                SELECT 
                    lc.id_ingredient,
                    i.nom as nom_ingredient,
                    lc.quantite,
                    lc.effectue,
                    lc.id_unite,
                    u.abbreviation as code_unite,
                    u.nom as nom_unite_complet
                FROM liste_course lc
                JOIN ingredient i ON lc.id_ingredient = i.id_ingredient
                LEFT JOIN unite u ON lc.id_unite = u.id_unite
                WHERE lc.id_utilisateur = %(id_utilisateur)s
                AND lc.id_ingredient = %(id_ingredient)s
                """,
                {
                    "id_utilisateur": id_utilisateur,
                    "id_ingredient": id_ingredient,
                },
            )
            return cursor.fetchone()

    @log
    def get_liste_course_item(
        self,
        id_utilisateur: int,
        id_ingredient: int,
    ) -> dict | None:
        """Récupère un item spécifique de la liste de course.

        Parameters
        ----------
        id_utilisateur : int
            ID de l'utilisateur
        id_ingredient : int
            ID de l'ingrédient

        Returns
        -------
        dict | None
            L'item s'il existe, None sinon

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT lc.quantite, lc.id_unite, u.type_unite as type_unite, u.abbreviation as code_unite
                FROM liste_course lc
                LEFT JOIN unite u ON lc.id_unite = u.id_unite
                WHERE lc.id_utilisateur = %(id_utilisateur)s
                  AND lc.id_ingredient = %(id_ingredient)s
                """,
                {
                    "id_utilisateur": id_utilisateur,
                    "id_ingredient": id_ingredient,
                },
            )
            return cursor.fetchone()

    @log
    def remove_from_liste_course(
        self,
        id_utilisateur: int,
        id_ingredient: int,
    ) -> bool:
        """Retire un ingrédient de la liste de course.

        Parameters
        ----------
        id_utilisateur : int
            ID de l'utilisateur
        id_ingredient : int
            ID de l'ingrédient

        Returns
        -------
        bool
            True si la suppression a réussi

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM liste_course
                WHERE id_utilisateur = %(id_utilisateur)s
                  AND id_ingredient = %(id_ingredient)s
                """,
                {
                    "id_utilisateur": id_utilisateur,
                    "id_ingredient": id_ingredient,
                },
            )
            return cursor.rowcount > 0

    @log
    def clear_liste_course(self, id_utilisateur: int) -> int:
        """Vide complètement la liste de course d'un utilisateur.

        Parameters
        ----------
        id_utilisateur : int
            ID de l'utilisateur

        Returns
        -------
        int
            Nombre d'items supprimés

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM liste_course
                WHERE id_utilisateur = %(id_utilisateur)s
                """,
                {"id_utilisateur": id_utilisateur},
            )
            return cursor.rowcount

    @log
    def toggle_effectue(
        self,
        id_utilisateur: int,
        id_ingredient: int,
    ) -> bool:
        """Toggle le statut 'effectue' d'un item de la liste de course.

        Parameters
        ----------
        id_utilisateur : int
            ID de l'utilisateur
        id_ingredient : int
            ID de l'ingrédient

        Returns
        -------
        bool
            Le nouveau statut (True si effectué, False sinon)

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE liste_course
                SET effectue = NOT effectue
                WHERE id_utilisateur = %(id_utilisateur)s
                  AND id_ingredient = %(id_ingredient)s
                RETURNING effectue
                """,
                {
                    "id_utilisateur": id_utilisateur,
                    "id_ingredient": id_ingredient,
                },
            )
            result = cursor.fetchone()
            return result["effectue"] if result else False
