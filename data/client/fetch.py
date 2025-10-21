import os
import re
from time import sleep

import psycopg2
import requests


class FetchService:
    def __init__(self):
        self.host = os.environ.get(
            "COCKTAIL_API_URL",
            "https://www.thecocktaildb.com/api/json/v1/1",
        )

    def get_cocktails_by_first_letter(self, letter):
        url = f"{self.host}/search.php?f={letter}"
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception(
                f"Erreur {response.status_code} lors de l'appel à l'API : {url}",
            )

        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            print(f"Erreur JSON pour l'URL : {url}")
            print("Contenu reçu :", response.text[:500])
            return []

        cocktails = data.get("drinks")
        if not cocktails:
            return []

        result = []
        for c in cocktails:
            result.append(
                {
                    "id_cocktail": c.get("idDrink"),
                    "nom": c.get("strDrink"),
                    "categorie": c.get("strCategory"),
                    "verre": c.get("strGlass"),
                    "alcool": c.get("strAlcoholic") == "Alcoholic",
                    "image": c.get("strDrinkThumb"),
                },
            )

        return result

    import os

    def get_cocktail_by_id(self, cocktail_id):
        """Récupère les infos d'un cocktail via son id."""
        url = f"{self.host}/lookup.php?i={cocktail_id}"
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Erreur HTTP {response.status_code} pour l'ID {cocktail_id}")
            return None

        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            print(f"Erreur JSON pour l'ID {cocktail_id}")
            return None

        drinks = data.get("drinks")
        if not drinks:
            return None

        c = drinks[0]
        return {
            "id_cocktail": c.get("idDrink"),
            "nom": c.get("strDrink"),
            "categorie": c.get("strCategory"),
            "verre": c.get("strGlass"),
            "alcool": c.get("strAlcoholic") == "Alcoholic",
            "image": c.get("strDrinkThumb"),
        }

    def fetch_all_cocktails(self, start_id=10000, end_id=20000, delay=0.2):
        """Récupère tous les cocktails entre start_id et end_id.
        `delay` sert à ne pas saturer l'API.
        """
        cocktails = []
        for cocktail_id in range(start_id, end_id + 1):
            cocktail = self.get_cocktail_by_id(cocktail_id)
            if cocktail:
                cocktails.append(cocktail)
                print(f"Récupéré {cocktail['nom']} (ID {cocktail_id})")
            sleep(delay)
        return cocktails

    def get_ingredient_by_id(self, ingredient_id):
        """Récupère les infos d'un ingrédient via son idIngredient.
        Retourne un dict avec les informations ou None si inexistant.
        """
        url = f"{self.host}/lookup.php?iid={ingredient_id}"
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Erreur HTTP {response.status_code} pour l'ID {ingredient_id}")
            return None

        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            print(f"Erreur JSON pour l'ID {ingredient_id}")
            return None

        ingredients = data.get("ingredients")
        if not ingredients:
            return None  # Pas d'ingrédient avec cet ID

        ing = ingredients[0]
        return {
            "id_ingredient": ing.get("idIngredient"),
            "nom": ing.get("strIngredient"),
            "description": ing.get("strDescription"),
            "type": ing.get("strType"),
            "alcool": ing.get("strAlcohol") == "Yes",
            "abv": ing.get("strABV"),
        }

    def get_cocktail_instructions_by_id(self, cocktail_id):
        url = f"{self.host}/lookup.php?i={cocktail_id}"
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception(
                f"Erreur {response.status_code} pour l'ID {cocktail_id}",
            )

        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            print(f"Erreur JSON pour l'ID {cocktail_id}")
            return []

        drinks = data.get("drinks")
        if not drinks:
            return []

        drink = drinks[0]
        instructions = []

        langs = {
            "EN": "strInstructions",
            "DE": "strInstructionsDE",
            "ES": "strInstructionsES",
            "FR": "strInstructionsFR",
            "IT": "strInstructionsIT",
            "ZH-HANS": "strInstructionsZH-HANS",
            "ZH-HANT": "strInstructionsZH-HANT",
        }

        for lang_code, field in langs.items():
            texte = drink.get(field)
            if texte and texte.strip():
                instructions.append(
                    {
                        "id_cocktail": drink.get("idDrink"),
                        "langue": lang_code,
                        "texte": texte.strip(),
                    },
                )

        return instructions

    def get_cocktail_ingredients(self, cocktail_id):
        """Récupère les ingrédients et mesures d'un cocktail via son id.
        Retourne une liste de dicts contenant :
        - id_cocktail
        - id_ingredient
        - quantite
        - unite
        """
        url = f"{self.host}/lookup.php?i={cocktail_id}"
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Erreur HTTP {response.status_code} pour l'ID {cocktail_id}")
            return []

        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            print(f"Erreur JSON pour l'ID {cocktail_id}")
            return []

        drinks = data.get("drinks")
        if not drinks:
            return []

        drink = drinks[0]
        cocktail_ingredients = []

        # TheCocktailDB fournit jusqu'à 15 ingrédients par cocktail
        for i in range(1, 16):
            ingredient_name = drink.get(f"strIngredient{i}")
            measure = drink.get(f"strMeasure{i}")

            if not ingredient_name:
                continue

            # Ici, on suppose que l'ingrédient existe déjà dans la table ingredient
            # Il faudra chercher son id_ingredient
            id_ingredient = self.get_id_ingredient_by_name(
                ingredient_name.title(),
            )
            if not id_ingredient:
                print(f"Ingrédient '{ingredient_name}' non trouvé dans la BDD")
                continue

            # On peut séparer mesure en quantité et unité si besoin
            quantite = measure.strip() if measure else None
            id_unite = None

            cocktail_ingredients.append(
                {
                    "id_cocktail": cocktail_id,
                    "id_ingredient": id_ingredient,
                    "quantite": quantite,
                    "id_unite": id_unite,
                },
            )

        return cocktail_ingredients

    def get_id_ingredient_by_name(self, nom_ingredient):
        """Cherche l'id d'un ingrédient existant dans la BDD à partir de son nom.
        Retourne l'id ou None si introuvable.
        """
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DATABASE"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            port=os.getenv("POSTGRES_PORT"),
            host=os.getenv("POSTGRES_HOST"),
        )
        cur = conn.cursor()
        cur.execute(
            "SELECT id_ingredient FROM ingredient WHERE nom = %s",
            (nom_ingredient,),
        )
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result:
            return result[0]
        return None

    def get_raw_cocktail_by_id(self, cocktail_id):
        """Récupère le cocktail brut (tous les champs, y compris strMeasure1..15)."""
        url = f"{self.host}/lookup.php?i={cocktail_id}"
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Erreur HTTP {response.status_code} pour l'ID {cocktail_id}")
            return None

        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            print(f"Erreur JSON pour l'ID {cocktail_id}")
            return None

        drinks = data.get("drinks")
        if not drinks:
            return None

        return drinks[0]  # retourne le JSON complet

    def extract_unit_from_measure(self, measure):
        """Extrait l'unité à partir d'une mesure texte (ex: '1 oz' -> 'oz')"""
        if not measure:
            return None
        # on garde juste les lettres et symboles unitaires
        parts = re.findall(r"[a-zA-Zµ]+", measure)
        return parts[-1].lower() if parts else None

    def classify_unit_type(self, unit):
        """Détermine le type d'unité (simple heuristique)"""
        liquides = {
            "ml",
            "cl",
            "l",
            "oz",
            "tsp",
            "tbsp",
            "dash",
            "drop",
            "cup",
            "part",
        }
        solides = {"cube", "slice", "piece", "spoon", "pinch"}
        if unit in liquides:
            return "liquide"
        if unit in solides:
            return "solide"
        return "autre"

    def fetch_all_units(self, start_id=12000, end_id=20000, delay=0.15):
        """Parcourt plusieurs cocktails et collecte les unités uniques"""
        units = set()
        for cid in range(start_id, end_id):
            drink = self.get_raw_cocktail_by_id(cid)
            if not drink:
                continue
            for i in range(1, 16):
                measure = drink.get(f"strMeasure{i}")
                unit = self.extract_unit_from_measure(measure)
                if unit:
                    units.add(unit)
            sleep(delay)
        return sorted(units)
