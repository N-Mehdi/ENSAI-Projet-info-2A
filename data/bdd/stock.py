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
for cocktail_id in range(11000, 11007):
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
