from src.dao.db_connection import DBConnection
from src.utils.log_decorator import log
from src.utils.singleton import Singleton


class AvisDao(metaclass=Singleton):
    """DAO pour gérer les avis sur les cocktails."""

    @log
    def create_or_update_avis(
        self,
        id_utilisateur: int,
        id_cocktail: int,
        note: int | None,
        commentaire: str | None,
    ) -> dict:
        """Crée ou met à jour un avis (UPSERT).

        Parameters
        ----------
        id_utilisateur : int
            ID de l'utilisateur
        id_cocktail : int
            ID du cocktail
        note : int | None
            Note entre 0 et 10
        commentaire : str | None
            Commentaire texte

        Returns
        -------
        dict
            L'avis créé ou modifié

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO avis (id_utilisateur, id_cocktail, note, commentaire, favoris)
                VALUES (%(id_utilisateur)s, %(id_cocktail)s, %(note)s, %(commentaire)s, FALSE)
                ON CONFLICT (id_utilisateur, id_cocktail)
                DO UPDATE SET
                    note = EXCLUDED.note,
                    commentaire = EXCLUDED.commentaire,
                    date_modification = NOW()
                RETURNING 
                    id_utilisateur,
                    id_cocktail,
                    note,
                    commentaire,
                    favoris,
                    date_creation,
                    date_modification
                """,
                {
                    "id_utilisateur": id_utilisateur,
                    "id_cocktail": id_cocktail,
                    "note": note,
                    "commentaire": commentaire,
                },
            )
            return cursor.fetchone()

    @log
    def get_avis_by_user_and_cocktail(
        self,
        id_utilisateur: int,
        id_cocktail: int,
    ) -> dict | None:
        """Récupère un avis spécifique."""
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    a.id_utilisateur,
                    u.pseudo as pseudo_utilisateur,
                    a.id_cocktail,
                    c.nom as nom_cocktail,
                    a.note,
                    a.commentaire,
                    a.favoris,
                    a.date_creation,
                    a.date_modification
                FROM avis a
                JOIN utilisateur u ON a.id_utilisateur = u.id_utilisateur
                JOIN cocktail c ON a.id_cocktail = c.id_cocktail
                WHERE a.id_utilisateur = %(id_utilisateur)s
                  AND a.id_cocktail = %(id_cocktail)s
                """,
                {
                    "id_utilisateur": id_utilisateur,
                    "id_cocktail": id_cocktail,
                },
            )
            return cursor.fetchone()

    @log
    def get_avis_by_cocktail(self, id_cocktail: int) -> list[dict]:
        """Récupère tous les avis d'un cocktail."""
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    a.id_utilisateur,
                    u.pseudo as pseudo_utilisateur,
                    a.id_cocktail,
                    c.nom as nom_cocktail,
                    a.note,
                    a.commentaire,
                    a.favoris,
                    a.date_creation,
                    a.date_modification
                FROM avis a
                JOIN utilisateur u ON a.id_utilisateur = u.id_utilisateur
                JOIN cocktail c ON a.id_cocktail = c.id_cocktail
                WHERE a.id_cocktail = %(id_cocktail)s
                ORDER BY a.date_creation DESC
                """,
                {"id_cocktail": id_cocktail},
            )
            return cursor.fetchall()

    @log
    def get_avis_by_user(self, id_utilisateur: int) -> list[dict]:
        """Récupère tous les avis d'un utilisateur."""
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    a.id_utilisateur,
                    u.pseudo as pseudo_utilisateur,
                    a.id_cocktail,
                    c.nom as nom_cocktail,
                    a.note,
                    a.commentaire,
                    a.favoris,
                    a.date_creation,
                    a.date_modification
                FROM avis a
                JOIN utilisateur u ON a.id_utilisateur = u.id_utilisateur
                JOIN cocktail c ON a.id_cocktail = c.id_cocktail
                WHERE a.id_utilisateur = %(id_utilisateur)s
                ORDER BY a.date_creation DESC
                """,
                {"id_utilisateur": id_utilisateur},
            )
            return cursor.fetchall()

    @log
    def delete_avis(self, id_utilisateur: int, id_cocktail: int) -> bool:
        """Supprime un avis."""
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM avis
                WHERE id_utilisateur = %(id_utilisateur)s
                  AND id_cocktail = %(id_cocktail)s
                """,
                {
                    "id_utilisateur": id_utilisateur,
                    "id_cocktail": id_cocktail,
                },
            )
            return cursor.rowcount > 0

    @log
    def toggle_favoris(self, id_utilisateur: int, id_cocktail: int) -> dict:
        """Toggle le statut favoris d'un cocktail.
        Crée l'avis s'il n'existe pas (avec note et commentaire NULL).
        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO avis (id_utilisateur, id_cocktail, note, commentaire, favoris)
                VALUES (%(id_utilisateur)s, %(id_cocktail)s, NULL, NULL, TRUE)
                ON CONFLICT (id_utilisateur, id_cocktail)
                DO UPDATE SET
                    favoris = NOT avis.favoris,
                    date_modification = NOW()
                RETURNING favoris
                """,
                {
                    "id_utilisateur": id_utilisateur,
                    "id_cocktail": id_cocktail,
                },
            )
            result = cursor.fetchone()
            return {"favoris": result["favoris"]}

    @log
    def get_favoris_by_user(self, id_utilisateur: int) -> list[dict]:
        """Récupère tous les cocktails favoris d'un utilisateur."""
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    a.id_utilisateur,
                    u.pseudo as pseudo_utilisateur,
                    a.id_cocktail,
                    c.nom as nom_cocktail,
                    a.note,
                    a.commentaire,
                    a.favoris,
                    a.date_creation,
                    a.date_modification
                FROM avis a
                JOIN utilisateur u ON a.id_utilisateur = u.id_utilisateur
                JOIN cocktail c ON a.id_cocktail = c.id_cocktail
                WHERE a.id_utilisateur = %(id_utilisateur)s
                  AND a.favoris = TRUE
                ORDER BY a.date_modification DESC
                """,
                {"id_utilisateur": id_utilisateur},
            )
            return cursor.fetchall()

    @log
    def get_avis_summary(self, id_cocktail: int) -> dict:
        """Récupère un résumé des avis pour un cocktail."""
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    c.id_cocktail,
                    c.nom as nom_cocktail,
                    COUNT(*) as nombre_avis,
                    AVG(a.note) as note_moyenne,
                    SUM(CASE WHEN a.favoris THEN 1 ELSE 0 END) as nombre_favoris
                FROM cocktail c
                LEFT JOIN avis a ON c.id_cocktail = a.id_cocktail
                WHERE c.id_cocktail = %(id_cocktail)s
                GROUP BY c.id_cocktail, c.nom
                """,
                {"id_cocktail": id_cocktail},
            )
            result = cursor.fetchone()
            if result:
                return {
                    "id_cocktail": result["id_cocktail"],
                    "nom_cocktail": result["nom_cocktail"],
                    "nombre_avis": int(result["nombre_avis"]) if result["nombre_avis"] else 0,
                    "note_moyenne": float(result["note_moyenne"]) if result["note_moyenne"] else None,
                    "nombre_favoris": int(result["nombre_favoris"]) if result["nombre_favoris"] else 0,
                }
            return None

    @log
    def add_favoris(self, id_utilisateur: int, id_cocktail: int) -> dict:
        """Ajoute un cocktail aux favoris.
        Crée l'avis s'il n'existe pas (avec note et commentaire NULL).
        Si déjà en favoris, ne fait rien.

        Parameters
        ----------
        id_utilisateur : int
            ID de l'utilisateur
        id_cocktail : int
            ID du cocktail

        Returns
        -------
        dict
            {"favoris": True, "deja_en_favoris": bool}

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            # Vérifier si déjà en favoris
            cursor.execute(
                """
                SELECT favoris
                FROM avis
                WHERE id_utilisateur = %(id_utilisateur)s
                AND id_cocktail = %(id_cocktail)s
                """,
                {
                    "id_utilisateur": id_utilisateur,
                    "id_cocktail": id_cocktail,
                },
            )
            result = cursor.fetchone()

            if result and result["favoris"]:
                # Déjà en favoris, ne rien faire
                return {"favoris": True, "deja_en_favoris": True}

            # Ajouter aux favoris (créer ou mettre à jour)
            cursor.execute(
                """
                INSERT INTO avis (id_utilisateur, id_cocktail, note, commentaire, favoris)
                VALUES (%(id_utilisateur)s, %(id_cocktail)s, NULL, NULL, TRUE)
                ON CONFLICT (id_utilisateur, id_cocktail)
                DO UPDATE SET
                    favoris = TRUE,
                    date_modification = NOW()
                RETURNING favoris
                """,
                {
                    "id_utilisateur": id_utilisateur,
                    "id_cocktail": id_cocktail,
                },
            )

            return {"favoris": True, "deja_en_favoris": False}

    @log
    def remove_favoris(self, id_utilisateur: int, id_cocktail: int) -> bool:
        """Retire un cocktail des favoris (met favoris à FALSE).

        Returns
        -------
        bool
            True si le cocktail était en favoris, False sinon

        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            # Vérifier que c'était en favoris
            cursor.execute(
                """
                SELECT favoris
                FROM avis
                WHERE id_utilisateur = %(id_utilisateur)s
                AND id_cocktail = %(id_cocktail)s
                """,
                {
                    "id_utilisateur": id_utilisateur,
                    "id_cocktail": id_cocktail,
                },
            )
            result = cursor.fetchone()

            if not result or not result["favoris"]:
                return False

            # Mettre favoris à FALSE
            cursor.execute(
                """
                UPDATE avis
                SET favoris = FALSE,
                    date_modification = NOW()
                WHERE id_utilisateur = %(id_utilisateur)s
                AND id_cocktail = %(id_cocktail)s
                """,
                {
                    "id_utilisateur": id_utilisateur,
                    "id_cocktail": id_cocktail,
                },
            )

            return True
