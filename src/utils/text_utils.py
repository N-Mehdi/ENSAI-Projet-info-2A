def normalize_ingredient_name(nom: str) -> str:
    """Normalise le nom d'un ingrédient au format standard.

    Règles :
    - Title Case pour tous les mots
    - Exception : noms commençant par des chiffres (151 Proof Rum, 7-Up)
    - Espaces multiples → un seul espace
    - Trim des espaces au début/fin

    Examples
    --------
    >>> normalize_ingredient_name("apple")
    'Apple'
    >>> normalize_ingredient_name("POMEGRANATE JUICE")
    'Pomegranate Juice'
    >>> normalize_ingredient_name("  rhum   blanc  ")
    'Rhum Blanc'
    >>> normalize_ingredient_name("151 proof rum")
    '151 Proof Rum'
    >>> normalize_ingredient_name("7-up")
    '7-Up'

    """
    # Nettoyer les espaces
    nom = " ".join(nom.split())  # Remplace espaces multiples par un seul
    nom = nom.strip()  # Retire espaces début/fin

    # Cas spéciaux : commence par un chiffre
    if nom and nom[0].isdigit():
        # Pour les noms type "151 Proof Rum" ou "7-Up"
        # On applique title() qui gère bien ces cas
        return nom.title()

    # Cas général : Title Case
    return nom.title()
