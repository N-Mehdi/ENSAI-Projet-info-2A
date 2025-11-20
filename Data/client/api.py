from dotenv import load_dotenv

load_dotenv()
"""
# Initialiser le client
cocktail_client = FetchService()


# Exemple : récupérer les cocktails commençant par 'a'
cocktails = cocktail_client.get_cocktails_by_first_letter("a")

print(f"{len(cocktails)} cocktails trouvés :")
for c in cocktails[:5]:
    print(f"- {c['nom']} ({c['categorie']})")


"""

"""
all_cocktails = fetch_service.fetch_all_cocktails(
    start_id=11000,
    end_id=20000,
)  # exemple 50 cocktails
print(f"Nombre de cocktails récupérés : {len(all_cocktails)}")

"""


