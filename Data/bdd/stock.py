import os

import psycopg2
from dotenv import load_dotenv

from data.client.fetch import FetchService

load_dotenv()

host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
dbname = os.getenv("POSTGRES_DATABASE")
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")

conn = psycopg2.connect(
    host=host,
    port=port,
    dbname=dbname,
    user=user,
    password=password,
)
cur = conn.cursor()


fetch_service = FetchService()
'''
for ing_id in range(1, 1000):
    ing = fetch_service.get_ingredient_by_id(ing_id)
    if ing:
        try:
            cur.execute(
                """
                INSERT INTO ingredient (id_ingredient, nom, description, type, alcool, abv)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id_ingredient) DO NOTHING */
                """,
                (
                    ing["id_ingredient"],
                    ing["nom"],
                    ing["description"],
                    ing["type"],
                    ing["alcool"],
                    ing["abv"],
                ),
            )
            conn.commit()
            print(f"Inséré : {ing['nom']} (ID {ing_id})")
        except Exception as e:
            print(f"Erreur insertion ID {ing_id} : {e}")
    sleep(0.2)

cur.close()
conn.close()
print("Tous les ingrédients ont été insérés avec succès !")

'''
'''

for cocktail_id in range(11000, 20001):
    instructions = fetch_service.get_cocktail_instructions_by_id(cocktail_id)
    for instr in instructions:
        try:
            cur.execute(
                """
                INSERT INTO instruction (id_cocktail, langue, texte)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING
                """,
                (
                    instr["id_cocktail"],
                    instr["langue"],
                    instr["texte"],
                ),
            )
            conn.commit()
            print(f"Inséré : ID {instr['id_cocktail']} ({instr['langue']})")
        except Exception as e:
            print(f"Erreur insertion ID {instr['id_cocktail']} : {e}")
    sleep(0.2)

cur.close()
conn.close()
print("Toutes les instructions multilingues ont été insérées avec succès !")

'''
'''
for cocktail_id in range(11007, 17841):
    cocktail_ingredients = fetch_service.get_cocktail_ingredients(cocktail_id)
    for ci in cocktail_ingredients:
        try:
            cur.execute(
                """
                INSERT INTO cocktail_ingredient (id_cocktail, id_ingredient, quantite, id_unite)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id_cocktail, id_ingredient) DO NOTHING
            """,
                (
                    ci["id_cocktail"],
                    ci["id_ingredient"],
                    ci["quantite"],
                    ci["id_unite"],
                ),
            )
            conn.commit()
            print(
                f"Inséré : id_cocktail {ci['id_cocktail']}, id_ingredient ({ci['id_ingredient']})",
            )
        except Exception as e:
            print(f"Erreur insertion ID {ci['id_cocktail']} : {e}")
    sleep(0.2)

cur.close()
conn.close()
print("Toutes les lignes ont été insérées avec succès !")
'''
'''

fetcher = FetchService()
units = fetcher.fetch_all_units()
for u in units:
    unit_type = fetcher.classify_unit_type(u)
    cur.execute(
        """
            INSERT INTO unite (nom, abbreviation, type_unite)
            VALUES (%s, %s, %s)
        """,
        (u.capitalize(), u, unit_type),
    )
conn.commit()
cur.close()
conn.close()
print(f"{len(units)} unités insérées dans la table unite ✅")
'''

'''
def parse_simple_quantite(quantite_str: str) -> tuple[float | None, str | None]:
    """Parse uniquement les quantités simples de la forme "n oz" (entier uniquement).
    Rejette les fractions (n/p) et les ranges (n-p).

    Parameters
    ----------
    quantite_str : str
        La chaîne de quantité à parser

    Returns
    -------
    tuple[float | None, str | None]
        (valeur_numerique, unite) ou (None, None) si pas de match simple

    Examples
    --------
    >>> parse_simple_quantite("2 oz")
    (2.0, "oz")
    >>> parse_simple_quantite("5 cl")
    (5.0, "cl")
    >>> parse_simple_quantite("1/2 oz")
    (None, None)  # Fraction → rejeté
    >>> parse_simple_quantite("2-3 oz")
    (None, None)  # Range → rejeté
    >>> parse_simple_quantite("2.5 oz")
    (None, None)  # Décimal → rejeté (seulement entiers)

    """
    if not quantite_str or quantite_str.strip() == "" or quantite_str == "[NULL]":
        return None, None

    quantite_str = quantite_str.strip()

    # Pattern: uniquement "n unite" où n est un ENTIER (pas de décimales)
    # Rejette les fractions (1/2), les ranges (2-3), et les décimales (2.5)
    match = re.match(r"^(\\d+)\\s+(\\w+)$", quantite_str)

    if match:
        valeur = int(match.group(1))  # Conversion en int (entier)
        unite = match.group(2)
        return float(valeur), unite  # Retourner en float pour cohérence avec la BDD

    return None, None


def fill_cocktail_ingredient_x_y():
    """Remplit les colonnes X et Y de cocktail_ingredient.

    Règle :
    - Si quantite est de la forme simple "n oz" avec n ENTIER
    - Alors X = n et Y = "oz"
    - Sinon, X et Y restent NULL
    """
    with DBConnection().connection as connection, connection.cursor() as cursor:
        # 1. Vérifier que les colonnes X et Y existent
        print("Vérification des colonnes X et Y...")
        cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'cocktail_ingredient' 
                  AND column_name IN ('x', 'y')
            """)
        colonnes_existantes = [row["column_name"] for row in cursor.fetchall()]

        if "x" not in colonnes_existantes:
            print("  Création de la colonne X...")
            cursor.execute("ALTER TABLE cocktail_ingredient ADD COLUMN x FLOAT")
        else:
            print("  ✓ Colonne X existe")

        if "y" not in colonnes_existantes:
            print("  Création de la colonne Y...")
            cursor.execute("ALTER TABLE cocktail_ingredient ADD COLUMN y VARCHAR(50)")
        else:
            print("  ✓ Colonne Y existe")

        connection.commit()
        print("✅ Colonnes vérifiées/créées\n")

        # 2. Récupérer toutes les lignes avec une quantité
        print("Récupération des données...")
        cursor.execute("""
                SELECT id_cocktail, id_ingredient, quantite
                FROM cocktail_ingredient
                WHERE quantite IS NOT NULL 
                  AND quantite != '[NULL]'
                  AND quantite != ''
            """)
        rows = cursor.fetchall()
        print(f"✅ {len(rows)} lignes à traiter\n")

        # 3. Traiter chaque ligne
        print("Traitement des données...")
        print("-" * 80)

        nb_remplis = 0
        nb_rejetes = 0
        exemples_remplis = []
        exemples_rejetes = []
        unites_trouvees = {}

        for i, row in enumerate(rows, 1):
            id_cocktail = row["id_cocktail"]
            id_ingredient = row["id_ingredient"]
            quantite_str = row["quantite"]

            # Parser
            valeur, unite = parse_simple_quantite(quantite_str)

            if valeur is not None and unite is not None:
                # C'est une forme simple "n unite" → Remplir X et Y
                cursor.execute(
                    """
                        UPDATE cocktail_ingredient
                        SET x = %(valeur)s,
                            y = %(unite)s
                        WHERE id_cocktail = %(id_cocktail)s
                          AND id_ingredient = %(id_ingredient)s
                    """,
                    {
                        "valeur": valeur,
                        "unite": unite,
                        "id_cocktail": id_cocktail,
                        "id_ingredient": id_ingredient,
                    },
                )
                nb_remplis += 1

                # Compter les unités
                unites_trouvees[unite] = unites_trouvees.get(unite, 0) + 1

                # Garder quelques exemples
                if len(exemples_remplis) < 15:
                    exemples_remplis.append(f"'{quantite_str}' → X={int(valeur)}, Y='{unite}'")
            else:
                # Pas une forme simple → Laisser NULL
                nb_rejetes += 1

                # Garder quelques exemples
                if len(exemples_rejetes) < 15:
                    exemples_rejetes.append(f"'{quantite_str}' → X=NULL, Y=NULL")

            # Progression
            if i % 100 == 0:
                print(f"  Progression : {i}/{len(rows)} lignes ({i / len(rows) * 100:.1f}%)")

        connection.commit()

        # 4. Résumé
        print("\n" + "=" * 80)
        print("RÉSUMÉ")
        print("=" * 80)
        print(f"✅ Lignes remplies (X et Y) : {nb_remplis}/{len(rows)} ({nb_remplis / len(rows) * 100:.1f}%)")
        print(f"⚪ Lignes laissées NULL : {nb_rejetes}/{len(rows)} ({nb_rejetes / len(rows) * 100:.1f}%)")

        # Exemples remplis
        if exemples_remplis:
            print("\n📝 Exemples de lignes REMPLIES (X et Y) :")
            for ex in exemples_remplis:
                print(f"   {ex}")

        # Exemples rejetés
        if exemples_rejetes:
            print("\n📝 Exemples de lignes LAISSÉES NULL (pas de forme simple) :")
            for ex in exemples_rejetes:
                print(f"   {ex}")

        # Statistiques par unité
        if unites_trouvees:
            print("\n" + "-" * 80)
            print("Répartition par unité (colonne Y) :")
            for unite, count in sorted(unites_trouvees.items(), key=lambda x: x[1], reverse=True):
                print(f"   {unite}: {count} occurrences")

        # Vérification avec requête SQL
        print("\n" + "-" * 80)
        print("Vérification finale :")
        cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(x) as avec_x,
                    COUNT(y) as avec_y
                FROM cocktail_ingredient
                WHERE quantite IS NOT NULL 
                  AND quantite != '[NULL]'
                  AND quantite != ''
            """)
        verif = cursor.fetchone()
        print(f"   Total lignes avec quantité : {verif['total']}")
        print(f"   Lignes avec X rempli : {verif['avec_x']}")
        print(f"   Lignes avec Y rempli : {verif['avec_y']}")

        print("\n" + "=" * 80)
        print("✅ Traitement terminé !")
        print("=" * 80)
'''


'''# scripts/fill_cocktail_ingredient_x_y.py

import re

from src.dao.db_connection import DBConnection


def parse_fraction_quantite(quantite_str: str) -> tuple[float | None, str | None]:
    """Parse uniquement les quantités de la forme "n/p oz" (fractions).
    Rejette les entiers simples (n oz) et les ranges (n-p oz).

    Parameters
    ----------
    quantite_str : str
        La chaîne de quantité à parser

    Returns
    -------
    tuple[float | None, str | None]
        (valeur_numerique, unite) ou (None, None) si pas une fraction

    Examples
    --------
    >>> parse_fraction_quantite("1/2 oz")
    (0.5, "oz")
    >>> parse_fraction_quantite("3/4 oz")
    (0.75, "oz")
    >>> parse_fraction_quantite("1/4 cl")
    (0.25, "cl")
    >>> parse_fraction_quantite("2 oz")
    (None, None)  # Entier simple → rejeté
    >>> parse_fraction_quantite("2-3 oz")
    (None, None)  # Range → rejeté
    >>> parse_fraction_quantite("1 1/2 oz")
    (None, None)  # Nombre mixte → rejeté (pour l'instant)

    """
    if not quantite_str or quantite_str.strip() == "" or quantite_str == "[NULL]":
        return None, None

    quantite_str = quantite_str.strip()

    # Pattern: uniquement "n/p unite" où n et p sont des ENTIERS
    # Exemple: "1/2 oz", "3/4 cl", "1/4 tsp"
    match = re.match(r"^(\\d+)/(\\d+)\\s+(\\w+)$", quantite_str)

    if match:
        numerateur = int(match.group(1))
        denominateur = int(match.group(2))
        unite = match.group(3)

        # Calculer la valeur décimale
        if denominateur == 0:
            return None, None  # Éviter division par zéro

        valeur = round(numerateur / denominateur, 3)
        return valeur, unite

    return None, None


def fill_cocktail_ingredient_fractions():
    """Remplit les colonnes X et Y de cocktail_ingredient pour les fractions.

    Règle :
    - Si quantite est de la forme "n/p oz" avec n et p ENTIERS
    - Alors X = n/p (valeur décimale) et Y = "oz"
    - Sinon, X et Y restent inchangés (ne pas écraser les valeurs existantes)
    """
    with DBConnection().connection as connection, connection.cursor() as cursor:
        # 1. Vérifier que les colonnes X et Y existent
        print("Vérification des colonnes X et Y...")
        cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'cocktail_ingredient' 
                  AND column_name IN ('x', 'y')
            """)
        colonnes_existantes = [row["column_name"] for row in cursor.fetchall()]

        if "x" not in colonnes_existantes:
            print("  Création de la colonne X...")
            cursor.execute("ALTER TABLE cocktail_ingredient ADD COLUMN x FLOAT")
        else:
            print("  ✓ Colonne X existe")

        if "y" not in colonnes_existantes:
            print("  Création de la colonne Y...")
            cursor.execute("ALTER TABLE cocktail_ingredient ADD COLUMN y VARCHAR(50)")
        else:
            print("  ✓ Colonne Y existe")

        connection.commit()
        print("✅ Colonnes vérifiées/créées\n")

        # 2. Récupérer les lignes avec quantité contenant "/"
        print("Récupération des lignes avec fractions...")
        cursor.execute("""
                SELECT id_cocktail, id_ingredient, quantite, x, y
                FROM cocktail_ingredient
                WHERE quantite IS NOT NULL 
                  AND quantite != '[NULL]'
                  AND quantite != ''
                  AND quantite LIKE '%/%'
            """)
        rows = cursor.fetchall()
        print(f"✅ {len(rows)} lignes contenant '/' à traiter\n")

        # 3. Traiter chaque ligne
        print("Traitement des fractions...")
        print("-" * 80)

        nb_remplis = 0
        nb_deja_remplis = 0
        nb_rejetes = 0
        exemples_remplis = []
        exemples_rejetes = []
        exemples_deja_remplis = []
        unites_trouvees = {}

        for i, row in enumerate(rows, 1):
            id_cocktail = row["id_cocktail"]
            id_ingredient = row["id_ingredient"]
            quantite_str = row["quantite"]
            x_actuel = row["x"]
            y_actuel = row["y"]

            # Si X et Y sont déjà remplis, ne pas écraser
            if x_actuel is not None and y_actuel is not None:
                nb_deja_remplis += 1
                if len(exemples_deja_remplis) < 10:
                    exemples_deja_remplis.append(
                        f"'{quantite_str}' → X={x_actuel}, Y='{y_actuel}' (déjà rempli, ignoré)",
                    )
                continue

            # Parser
            valeur, unite = parse_fraction_quantite(quantite_str)

            if valeur is not None and unite is not None:
                # C'est une fraction simple "n/p unite" → Remplir X et Y
                cursor.execute(
                    """
                        UPDATE cocktail_ingredient
                        SET x = %(valeur)s,
                            y = %(unite)s
                        WHERE id_cocktail = %(id_cocktail)s
                          AND id_ingredient = %(id_ingredient)s
                    """,
                    {
                        "valeur": valeur,
                        "unite": unite,
                        "id_cocktail": id_cocktail,
                        "id_ingredient": id_ingredient,
                    },
                )
                nb_remplis += 1

                # Compter les unités
                unites_trouvees[unite] = unites_trouvees.get(unite, 0) + 1

                # Garder quelques exemples
                if len(exemples_remplis) < 15:
                    exemples_remplis.append(f"'{quantite_str}' → X={valeur:.4f}, Y='{unite}'")
            else:
                # Pas une fraction simple → Laisser NULL
                nb_rejetes += 1

                # Garder quelques exemples
                if len(exemples_rejetes) < 15:
                    exemples_rejetes.append(f"'{quantite_str}' → X=NULL, Y=NULL (pas une fraction simple)")

            # Progression
            if i % 50 == 0:
                print(f"  Progression : {i}/{len(rows)} lignes ({i / len(rows) * 100:.1f}%)")

        connection.commit()

        # 4. Résumé
        print("\n" + "=" * 80)
        print("RÉSUMÉ")
        print("=" * 80)
        print(f"✅ Lignes remplies (X et Y) : {nb_remplis}")
        print(f"⏭️  Lignes déjà remplies (ignorées) : {nb_deja_remplis}")
        print(f"⚪ Lignes rejetées (pas fraction simple) : {nb_rejetes}")
        print(f"📊 Total traité : {len(rows)}")

        # Exemples remplis
        if exemples_remplis:
            print("\n📝 Exemples de lignes REMPLIES (fractions) :")
            for ex in exemples_remplis:
                print(f"   {ex}")

        # Exemples déjà remplis
        if exemples_deja_remplis:
            print("\n⏭️  Exemples de lignes DÉJÀ REMPLIES (ignorées) :")
            for ex in exemples_deja_remplis:
                print(f"   {ex}")

        # Exemples rejetés
        if exemples_rejetes:
            print("\n📝 Exemples de lignes REJETÉES (pas fraction simple) :")
            for ex in exemples_rejetes:
                print(f"   {ex}")

        # Statistiques par unité
        if unites_trouvees:
            print("\n" + "-" * 80)
            print("Répartition par unité (fractions traitées) :")
            for unite, count in sorted(unites_trouvees.items(), key=lambda x: x[1], reverse=True):
                print(f"   {unite}: {count} occurrences")

        # Vérification globale
        print("\n" + "-" * 80)
        print("Vérification globale (toutes les lignes de la table) :")
        cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(x) as avec_x,
                    COUNT(y) as avec_y,
                    COUNT(CASE WHEN quantite LIKE '%/%' THEN 1 END) as avec_fraction
                FROM cocktail_ingredient
                WHERE quantite IS NOT NULL 
                  AND quantite != '[NULL]'
                  AND quantite != ''
            """)
        verif = cursor.fetchone()
        print(f"   Total lignes avec quantité : {verif['total']}")
        print(f"   Lignes contenant '/' : {verif['avec_fraction']}")
        print(f"   Lignes avec X rempli : {verif['avec_x']}")
        print(f"   Lignes avec Y rempli : {verif['avec_y']}")

        print("\n" + "=" * 80)
        print("✅ Traitement terminé !")
        print("=" * 80)


if __name__ == "__main__":
    try:
        fill_cocktail_ingredient_fractions()
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        import traceback

        traceback.print_exc()


fill_cocktail_ingredient_fractions()
'''


'''
def parse_quantite_complete(quantite_str: str) -> tuple[float | None, str | None]:
    """Parse tous les formats de quantité possibles.

    Formats supportés :
    1. "n oz" → X=n, Y="oz" (entier simple)
    2. "n/p oz" → X=n/p, Y="oz" (fraction)
    3. "decimal oz" → X=decimal, Y="oz" (décimal)
    4. "n" → X=n, Y=None (juste un chiffre)
    5. "n p/q oz" → X=n+p/q, Y="oz" (nombre mixte)
    6. "string" → X=None, Y="string" (juste du texte)
    7. "n-p oz" → X=(n+p)/2, Y="oz" (range)

    Parameters
    ----------
    quantite_str : str
        La chaîne de quantité à parser

    Returns
    -------
    tuple[float | None, str | None]
        (X, Y) - valeur numérique et unité

    Examples
    --------
    >>> parse_quantite_complete("2 oz")
    (2.0, "oz")
    >>> parse_quantite_complete("1/2 oz")
    (0.5, "oz")
    >>> parse_quantite_complete("1.5 oz")
    (1.5, "oz")
    >>> parse_quantite_complete("3")
    (3.0, None)
    >>> parse_quantite_complete("1 1/2 oz")
    (1.5, "oz")
    >>> parse_quantite_complete("dash")
    (None, "dash")
    >>> parse_quantite_complete("2-3 oz")
    (2.5, "oz")

    """
    if not quantite_str or quantite_str.strip() == "" or quantite_str == "[NULL]":
        return None, None

    quantite_str = quantite_str.strip()

    # Format 5 : "n p/q oz" (nombre mixte) - ex: "1 1/2 oz"
    match = re.match(r"^(\\d+)\\s+(\\d+)/(\\d+)\\s+(\\w+)$", quantite_str)
    if match:
        entier = float(match.group(1))
        numerateur = float(match.group(2))
        denominateur = float(match.group(3))
        unite = match.group(4)
        if denominateur != 0:
            valeur = entier + (numerateur / denominateur)
            return valeur, unite

    # Format 7 : "n-p oz" (range) - ex: "2-3 oz"
    match = re.match(r"^(\\d+(?:\\.\\d+)?)-(\\d+(?:\\.\\d+)?)\\s+(\\w+)$", quantite_str)
    if match:
        min_val = float(match.group(1))
        max_val = float(match.group(2))
        unite = match.group(3)
        valeur = (min_val + max_val) / 2
        return valeur, unite

    # Format 2 : "n/p oz" (fraction) - ex: "1/2 oz"
    match = re.match(r"^(\\d+)/(\\d+)\\s+(\\w+)$", quantite_str)
    if match:
        numerateur = float(match.group(1))
        denominateur = float(match.group(2))
        unite = match.group(3)
        if denominateur != 0:
            valeur = numerateur / denominateur
            return valeur, unite

    # Format 3 : "decimal oz" (décimal avec unité) - ex: "1.5 oz", "2.25 cl"
    match = re.match(r"^(\\d+\\.\\d+)\\s+(\\w+)$", quantite_str)
    if match:
        valeur = float(match.group(1))
        unite = match.group(2)
        return valeur, unite

    # Format 1 : "n oz" (entier avec unité) - ex: "2 oz"
    match = re.match(r"^(\\d+)\\s+(\\w+)$", quantite_str)
    if match:
        valeur = float(match.group(1))
        unite = match.group(2)
        return valeur, unite

    # Format 4 : "n" (juste un chiffre) - ex: "3", "12"
    match = re.match(r"^(\\d+(?:\\.\\d+)?)$", quantite_str)
    if match:
        valeur = float(match.group(1))
        return valeur, None

    # Format 6 : "string" (juste du texte) - ex: "dash", "garnish"
    match = re.match(r"^([a-zA-Z]+(?:\\s+[a-zA-Z]+)*)$", quantite_str)
    if match:
        texte = match.group(1)
        return None, texte

    # Cas spécial : "Juice of n" → X=n, Y="juice"
    match = re.match(r"juice\\s+of\\s+(\\d+(?:/\\d+)?)", quantite_str, re.IGNORECASE)
    if match:
        num_part = match.group(1)
        if "/" in num_part:
            parts = num_part.split("/")
            valeur = float(parts[0]) / float(parts[1])
        else:
            valeur = float(num_part)
        return valeur, "juice"

    # Si rien ne match, retourner None, None
    return None, None


def fill_cocktail_ingredient_complete():
    """Remplit les colonnes X et Y de cocktail_ingredient avec tous les formats.

    Traite TOUTES les lignes, en écrasant les valeurs existantes.
    """
    with DBConnection().connection as connection, connection.cursor() as cursor:
        # 1. Vérifier que les colonnes X et Y existent
        print("Vérification des colonnes X et Y...")
        cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'cocktail_ingredient' 
                  AND column_name IN ('x', 'y')
            """)
        colonnes_existantes = [row["column_name"] for row in cursor.fetchall()]

        if "x" not in colonnes_existantes:
            print("  Création de la colonne X...")
            cursor.execute("ALTER TABLE cocktail_ingredient ADD COLUMN x FLOAT")
        else:
            print("  ✓ Colonne X existe")

        if "y" not in colonnes_existantes:
            print("  Création de la colonne Y...")
            cursor.execute("ALTER TABLE cocktail_ingredient ADD COLUMN y VARCHAR(50)")
        else:
            print("  ✓ Colonne Y existe")

        connection.commit()
        print("✅ Colonnes vérifiées/créées\n")

        # 2. Récupérer toutes les lignes avec une quantité
        print("Récupération des données...")
        cursor.execute("""
                SELECT id_cocktail, id_ingredient, quantite
                FROM cocktail_ingredient
                WHERE quantite IS NOT NULL 
                  AND quantite != '[NULL]'
                  AND quantite != ''
            """)
        rows = cursor.fetchall()
        print(f"✅ {len(rows)} lignes à traiter\n")

        # 3. Traiter chaque ligne
        print("Traitement des données...")
        print("-" * 90)

        stats = {
            "entier_simple": 0,
            "fraction": 0,
            "decimal": 0,
            "juste_chiffre": 0,
            "nombre_mixte": 0,
            "juste_texte": 0,
            "range": 0,
            "juice_of": 0,
            "non_parse": 0,
        }

        exemples = {
            "entier_simple": [],
            "fraction": [],
            "decimal": [],
            "juste_chiffre": [],
            "nombre_mixte": [],
            "juste_texte": [],
            "range": [],
            "juice_of": [],
            "non_parse": [],
        }

        for i, row in enumerate(rows, 1):
            id_cocktail = row["id_cocktail"]
            id_ingredient = row["id_ingredient"]
            quantite_str = row["quantite"]

            # Parser
            x_val, y_val = parse_quantite_complete(quantite_str)

            # Déterminer le type
            type_format = None
            if re.match(r"^(\\d+)\\s+(\\d+)/(\\d+)\\s+(\\w+)$", quantite_str):
                type_format = "nombre_mixte"
            elif re.match(r"^(\\d+(?:\\.\\d+)?)-(\\d+(?:\\.\\d+)?)\\s+(\\w+)$", quantite_str):
                type_format = "range"
            elif re.match(r"^(\\d+)/(\\d+)\\s+(\\w+)$", quantite_str):
                type_format = "fraction"
            elif re.match(r"^(\\d+\\.\\d+)\\s+(\\w+)$", quantite_str):
                type_format = "decimal"
            elif re.match(r"^(\\d+)\\s+(\\w+)$", quantite_str):
                type_format = "entier_simple"
            elif re.match(r"^(\\d+(?:\\.\\d+)?)$", quantite_str):
                type_format = "juste_chiffre"
            elif re.match(r"juice\\s+of", quantite_str, re.IGNORECASE):
                type_format = "juice_of"
            elif re.match(r"^([a-zA-Z]+(?:\\s+[a-zA-Z]+)*)$", quantite_str):
                type_format = "juste_texte"
            else:
                type_format = "non_parse"

            stats[type_format] += 1

            # Garder quelques exemples
            if len(exemples[type_format]) < 5:
                x_display = f"{x_val:.4f}" if x_val is not None else "NULL"
                y_display = f"'{y_val}'" if y_val is not None else "NULL"
                exemples[type_format].append(f"'{quantite_str}' → X={x_display}, Y={y_display}")

            # Mettre à jour la BDD
            cursor.execute(
                """
                    UPDATE cocktail_ingredient
                    SET x = %(x_val)s,
                        y = %(y_val)s
                    WHERE id_cocktail = %(id_cocktail)s
                      AND id_ingredient = %(id_ingredient)s
                """,
                {
                    "x_val": x_val,
                    "y_val": y_val,
                    "id_cocktail": id_cocktail,
                    "id_ingredient": id_ingredient,
                },
            )

            # Progression
            if i % 100 == 0:
                print(f"  Progression : {i}/{len(rows)} lignes ({i / len(rows) * 100:.1f}%)")

        connection.commit()

        # 4. Résumé
        print("\n" + "=" * 90)
        print("RÉSUMÉ PAR TYPE DE FORMAT")
        print("=" * 90)

        format_labels = {
            "entier_simple": "Format 1 : Entier simple (n oz)",
            "fraction": "Format 2 : Fraction (n/p oz)",
            "decimal": "Format 3 : Décimal (1.5 oz)",
            "juste_chiffre": "Format 4 : Juste un chiffre (n)",
            "nombre_mixte": "Format 5 : Nombre mixte (n p/q oz)",
            "juste_texte": "Format 6 : Juste texte (dash)",
            "range": "Format 7 : Range (n-p oz)",
            "juice_of": "Format spécial : Juice of n",
            "non_parse": "❌ Non parsé",
        }

        for format_type, label in format_labels.items():
            count = stats[format_type]
            if count > 0:
                print(f"\n{label} : {count} lignes")
                if exemples[format_type]:
                    for ex in exemples[format_type]:
                        print(f"   {ex}")

        # Vérification finale
        print("\n" + "-" * 90)
        print("Vérification finale :")
        cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(x) as avec_x,
                    COUNT(y) as avec_y,
                    COUNT(CASE WHEN x IS NULL AND y IS NULL THEN 1 END) as vides
                FROM cocktail_ingredient
                WHERE quantite IS NOT NULL 
                  AND quantite != '[NULL]'
                  AND quantite != ''
            """)
        verif = cursor.fetchone()
        print(f"   Total lignes traitées : {verif['total']}")
        print(f"   Lignes avec X rempli : {verif['avec_x']} ({verif['avec_x'] / verif['total'] * 100:.1f}%)")
        print(f"   Lignes avec Y rempli : {verif['avec_y']} ({verif['avec_y'] / verif['total'] * 100:.1f}%)")
        print(f"   Lignes vides (X=NULL, Y=NULL) : {verif['vides']}")

        # Distribution des unités
        print("\n" + "-" * 90)
        print("Distribution des unités (colonne Y) :")
        cursor.execute("""
                SELECT y, COUNT(*) as count
                FROM cocktail_ingredient
                WHERE y IS NOT NULL
                GROUP BY y
                ORDER BY count DESC
                LIMIT 20
            """)
        unites = cursor.fetchall()
        for unite in unites:
            print(f"   {unite['y']}: {unite['count']} occurrences")

        print("\n" + "=" * 90)
        print("✅ Traitement terminé !")
        print("=" * 90)


if __name__ == "__main__":
    try:
        fill_cocktail_ingredient_complete()
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        import traceback

        traceback.print_exc()
'''


'''def parse_quantite_complete(quantite_str: str) -> tuple[float | None, str | None]:
    """Parse tous les formats de quantité possibles.

    Formats supportés :
    1. "n oz" → X=n, Y="oz" (entier simple avec unité)
    2. "n/p oz" → X=n/p, Y="oz" (fraction avec unité)
    3. "decimal oz" → X=decimal, Y="oz" (décimal avec unité)
    4. "n" → X=n, Y=None (juste un chiffre)
    5. "n p/q oz" → X=n+p/q, Y="oz" (nombre mixte avec unité)
    6. "string" → X=None, Y="string" (juste du texte)
    7. "n-p oz" → X=(n+p)/2, Y="oz" (range avec unité)
    8. "1/2" → X=0.5, Y=None (juste une fraction)
    9. "1-2" → X=1.5, Y=None (juste un range)
    10. "n string" → X=n, Y="string" (nombre + texte quelconque)
    11. "n/p string" → X=n/p, Y="string" (fraction + texte quelconque)
    12. "n-p string" → X=(n+p)/2, Y="string" (range + texte quelconque)
    13. "add X Y" → ignore "add" et traite "X Y"

    Parameters
    ----------
    quantite_str : str
        La chaîne de quantité à parser

    Returns
    -------
    tuple[float | None, str | None]
        (X, Y) - valeur numérique et unité/texte

    """
    if not quantite_str or quantite_str.strip() == "" or quantite_str == "[NULL]":
        return None, None

    quantite_str = quantite_str.strip()

    # Format 13 : Enlever "add" au début si présent
    if quantite_str.lower().startswith("add "):
        quantite_str = quantite_str[4:].strip()

    # Format 5 : "n p/q oz" (nombre mixte avec unité) - ex: "1 1/2 oz"
    match = re.match(r"^(\\d+)\\s+(\\d+)/(\\d+)\\s+(.+)$", quantite_str)
    if match:
        entier = float(match.group(1))
        numerateur = float(match.group(2))
        denominateur = float(match.group(3))
        reste = match.group(4).strip()
        if denominateur != 0:
            valeur = entier + (numerateur / denominateur)
            return valeur, reste

    # Format 7 & 12 : "n-p oz" ou "n-p string" (range) - ex: "2-3 oz", "1-2 dashes"
    match = re.match(r"^(\\d+(?:\\.\\d+)?)-(\\d+(?:\\.\\d+)?)(?:\\s+(.+))?$", quantite_str)
    if match:
        min_val = float(match.group(1))
        max_val = float(match.group(2))
        reste = match.group(3)
        valeur = (min_val + max_val) / 2
        if reste:
            return valeur, reste.strip()
        # Format 9 : "1-2" (juste un range sans unité)
        return valeur, None

    # Format 2 & 11 : "n/p oz" ou "n/p string" (fraction) - ex: "1/2 oz", "3/4 tsp"
    match = re.match(r"^(\\d+)/(\\d+)(?:\\s+(.+))?$", quantite_str)
    if match:
        numerateur = float(match.group(1))
        denominateur = float(match.group(2))
        reste = match.group(3)
        if denominateur != 0:
            valeur = numerateur / denominateur
            if reste:
                return valeur, reste.strip()
            # Format 8 : "1/2" (juste une fraction sans unité)
            return valeur, None

    # Format 3 : "decimal oz" (décimal avec unité) - ex: "1.5 oz", "2.25 cl"
    match = re.match(r"^(\\d+\\.\\d+)\\s+(.+)$", quantite_str)
    if match:
        valeur = float(match.group(1))
        reste = match.group(2).strip()
        return valeur, reste

    # Format 1 & 10 : "n oz" ou "n string" (entier avec texte) - ex: "2 oz", "3 dashes"
    match = re.match(r"^(\\d+)\\s+(.+)$", quantite_str)
    if match:
        valeur = float(match.group(1))
        reste = match.group(2).strip()
        return valeur, reste

    # Format 4 : "n" (juste un chiffre) - ex: "3", "12"
    match = re.match(r"^(\\d+(?:\\.\\d+)?)$", quantite_str)
    if match:
        valeur = float(match.group(1))
        return valeur, None

    # Format 6 : "string" (juste du texte) - ex: "dash", "garnish", "to taste"
    # Accepte tout texte (y compris avec espaces)
    if re.match(r"^[a-zA-Z\\s]+$", quantite_str):
        return None, quantite_str.strip()

    # Cas spécial : "Juice of n" → X=n, Y="juice"
    match = re.match(r"juice\\s+of\\s+(\\d+(?:/\\d+)?)", quantite_str, re.IGNORECASE)
    if match:
        num_part = match.group(1)
        if "/" in num_part:
            parts = num_part.split("/")
            valeur = float(parts[0]) / float(parts[1])
        else:
            valeur = float(num_part)
        return valeur, "juice"

    # Si rien ne match, retourner None, None
    return None, None


def fill_cocktail_ingredient_complete():
    """Remplit les colonnes X et Y de cocktail_ingredient avec tous les formats.

    Traite TOUTES les lignes, en écrasant les valeurs existantes.
    """
    with DBConnection().connection as connection, connection.cursor() as cursor:
        # 1. Vérifier que les colonnes X et Y existent
        print("Vérification des colonnes X et Y...")
        cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'cocktail_ingredient' 
                  AND column_name IN ('x', 'y')
            """)
        colonnes_existantes = [row["column_name"] for row in cursor.fetchall()]

        if "x" not in colonnes_existantes:
            print("  Création de la colonne X...")
            cursor.execute("ALTER TABLE cocktail_ingredient ADD COLUMN x FLOAT")
        else:
            print("  ✓ Colonne X existe")

        if "y" not in colonnes_existantes:
            print("  Création de la colonne Y...")
            cursor.execute("ALTER TABLE cocktail_ingredient ADD COLUMN y VARCHAR(100)")
        else:
            print("  ✓ Colonne Y existe")

        connection.commit()
        print("✅ Colonnes vérifiées/créées\n")

        # 2. Récupérer toutes les lignes avec une quantité
        print("Récupération des données...")
        cursor.execute("""
                SELECT id_cocktail, id_ingredient, quantite
                FROM cocktail_ingredient
                WHERE quantite IS NOT NULL 
                  AND quantite != '[NULL]'
                  AND quantite != ''
            """)
        rows = cursor.fetchall()
        print(f"✅ {len(rows)} lignes à traiter\n")

        # 3. Traiter chaque ligne
        print("Traitement des données...")
        print("-" * 100)

        stats = {
            "avec_unite": 0,
            "fraction_avec_unite": 0,
            "decimal_avec_unite": 0,
            "juste_chiffre": 0,
            "nombre_mixte": 0,
            "juste_texte": 0,
            "range_avec_unite": 0,
            "juste_fraction": 0,
            "juste_range": 0,
            "nombre_texte": 0,
            "fraction_texte": 0,
            "range_texte": 0,
            "avec_add": 0,
            "juice_of": 0,
            "non_parse": 0,
        }

        exemples = {key: [] for key in stats}

        for i, row in enumerate(rows, 1):
            id_cocktail = row["id_cocktail"]
            id_ingredient = row["id_ingredient"]
            quantite_str = row["quantite"]

            # Détecter si commence par "add"
            starts_with_add = quantite_str.strip().lower().startswith("add ")

            # Parser
            x_val, y_val = parse_quantite_complete(quantite_str)

            # Déterminer le type
            type_format = "non_parse"
            quantite_clean = quantite_str.strip()
            if starts_with_add:
                quantite_clean = quantite_clean[4:].strip()

            if starts_with_add:
                type_format = "avec_add"
            elif re.match(r"^(\\d+)\\s+(\\d+)/(\\d+)\\s+(.+)$", quantite_clean):
                type_format = "nombre_mixte"
            elif re.match(r"^(\\d+(?:\\.\\d+)?)-(\\d+(?:\\.\\d+)?)\\s+(.+)$", quantite_clean):
                type_format = "range_avec_unite"
            elif re.match(r"^(\\d+)/(\\d+)\\s+(.+)$", quantite_clean):
                type_format = "fraction_avec_unite"
            elif re.match(r"^(\\d+\\.\\d+)\\s+(.+)$", quantite_clean):
                type_format = "decimal_avec_unite"
            elif re.match(r"^(\\d+)\\s+(.+)$", quantite_clean):
                type_format = "nombre_texte"
            elif re.match(r"^(\\d+(?:\\.\\d+)?)$", quantite_clean):
                type_format = "juste_chiffre"
            elif re.match(r"^(\\d+)/(\\d+)$", quantite_clean):
                type_format = "juste_fraction"
            elif re.match(r"^(\\d+(?:\\.\\d+)?)-(\\d+(?:\\.\\d+)?)$", quantite_clean):
                type_format = "juste_range"
            elif re.match(r"juice\\s+of", quantite_clean, re.IGNORECASE):
                type_format = "juice_of"
            elif re.match(r"^[a-zA-Z\\s]+$", quantite_clean):
                type_format = "juste_texte"

            stats[type_format] += 1

            # Garder quelques exemples
            if len(exemples[type_format]) < 5:
                x_display = f"{x_val:.4f}" if x_val is not None else "NULL"
                y_display = f"'{y_val}'" if y_val is not None else "NULL"
                exemples[type_format].append(f"'{quantite_str}' → X={x_display}, Y={y_display}")

            # Mettre à jour la BDD
            cursor.execute(
                """
                    UPDATE cocktail_ingredient
                    SET x = %(x_val)s,
                        y = %(y_val)s
                    WHERE id_cocktail = %(id_cocktail)s
                      AND id_ingredient = %(id_ingredient)s
                """,
                {
                    "x_val": x_val,
                    "y_val": y_val,
                    "id_cocktail": id_cocktail,
                    "id_ingredient": id_ingredient,
                },
            )

            # Progression
            if i % 100 == 0:
                print(f"  Progression : {i}/{len(rows)} lignes ({i / len(rows) * 100:.1f}%)")

        connection.commit()

        # 4. Résumé
        print("\n" + "=" * 100)
        print("RÉSUMÉ PAR TYPE DE FORMAT")
        print("=" * 100)

        format_labels = {
            "avec_add": "📌 Commence par 'add' (add 2 oz)",
            "nombre_mixte": "Format : Nombre mixte (1 1/2 oz)",
            "range_avec_unite": "Format : Range avec unité (2-3 oz)",
            "fraction_avec_unite": "Format : Fraction avec unité (1/2 oz)",
            "decimal_avec_unite": "Format : Décimal avec unité (1.5 oz)",
            "nombre_texte": "Format : Nombre + texte (2 dashes, 3 sprigs)",
            "juste_chiffre": "Format : Juste un chiffre (3)",
            "juste_fraction": "Format : Juste une fraction (1/2)",
            "juste_range": "Format : Juste un range (1-2)",
            "juste_texte": "Format : Juste du texte (dash, garnish)",
            "juice_of": "Format spécial : Juice of n",
            "non_parse": "❌ Non parsé",
        }

        for format_type, label in format_labels.items():
            count = stats[format_type]
            if count > 0:
                print(f"\n{label} : {count} lignes")
                if exemples[format_type]:
                    for ex in exemples[format_type]:
                        print(f"   {ex}")

        # Vérification finale
        print("\n" + "-" * 100)
        print("Vérification finale :")
        cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(x) as avec_x,
                    COUNT(y) as avec_y,
                    COUNT(CASE WHEN x IS NULL AND y IS NULL THEN 1 END) as vides
                FROM cocktail_ingredient
                WHERE quantite IS NOT NULL 
                  AND quantite != '[NULL]'
                  AND quantite != ''
            """)
        verif = cursor.fetchone()
        print(f"   Total lignes traitées : {verif['total']}")
        print(f"   Lignes avec X rempli : {verif['avec_x']} ({verif['avec_x'] / verif['total'] * 100:.1f}%)")
        print(f"   Lignes avec Y rempli : {verif['avec_y']} ({verif['avec_y'] / verif['total'] * 100:.1f}%)")
        print(f"   Lignes vides (X=NULL, Y=NULL) : {verif['vides']}")

        # Distribution des unités/textes
        print("\n" + "-" * 100)
        print("Distribution des valeurs Y (unités/textes) :")
        cursor.execute("""
                SELECT y, COUNT(*) as count
                FROM cocktail_ingredient
                WHERE y IS NOT NULL
                GROUP BY y
                ORDER BY count DESC
                LIMIT 25
            """)
        unites = cursor.fetchall()
        for unite in unites:
            print(f"   {unite['y']}: {unite['count']} occurrences")

        print("\n" + "=" * 100)
        print("✅ Traitement terminé !")
        print("=" * 100)

fill_cocktail_ingredient_complete()
'''
