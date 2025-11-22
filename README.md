# ENSAI Cocktail Manager 🍹

Application de gestion de cocktails développée avec FastAPI et PostgreSQL.

## Prérequis

- Python 3.11+
- PostgreSQL
- [uv](https://github.com/astral-sh/uv) (gestionnaire de paquets Python)

## Installation

### 1. Cloner le dépôt
```bash
git clone https://github.com/N-Mehdi/ENSAI-Projet-info-2A.git
cd ENSAI-Projet-info-2A
```

### 2. Installer uv (si ce n'est pas déjà fait)
```bash
# macOS et Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3. Synchroniser les dépendances
```bash
uv sync
```

Cette commande créera automatiquement un environnement virtuel et installera toutes les dépendances nécessaires.

### 4. Configuration de la base de données

#### Configurer les variables d'environnement

Créez un fichier `.env` à la racine du projet :

```env
# Configuration PostgreSQL
COCKTAIL_API_URL=https://www.thecocktaildb.com/api/json/v1/1

POSTGRES_HOST=postgresql-486142.user-id2784-ensai
POSTGRES_PORT=5432
POSTGRES_DATABASE=defaultdb
POSTGRES_USER=user-id2784-ensai
POSTGRES_PASSWORD=xrbidkgd9szfgdpxmabg

# Configuration JWT
SECRET_KEY=li9xh_tvc_gICejw70K_PQAEo_PUFICTvD76qVp0nLE
```

Petite erreur de gestion du readme, donc je suis obligé de mettre le .env publiquement puisqu'il s'agit d'une seule base de données locale.

## Lancement de l'application
```bash
uv run src/main.py
```

L'API sera accessible sur `http://localhost:8000`

## Documentation de l'API

Une fois l'application lancée, accédez à la documentation interactive :

- **Swagger UI** : http://localhost:8000/docs

## Exécution des tests
```bash
# Tous les tests
uv run pytest

# Avec couverture de code
uv run pytest --cov=src

# Tests spécifiques
uv run pytest tests/test_service.py
```

## Structure du projet
```
ENSAI-Projet-info-2A/
├── src/
│   ├── main.py              # Point d'entrée de l'application
│   ├── dao/                 # Couche d'accès aux données
│   ├── service/             # Couche logique métier
│   ├── api/                 # Couche API (routers)
│   └── utils/               # Utilitaires (UnitConverter, etc.)
├── tests/                   # Tests unitaires et d'intégration
├── .env                     # Variables d'environnement (à créer)
├── pyproject.toml           # Configuration du projet
└── README.md
```

## Fonctionnalités principales

- 🔐 Authentification JWT
- 🍸 Gestion de cocktails publics et privés
- 📦 Gestion de stock d'ingrédients
- 🛒 Liste de courses
- ⭐ Système de favoris
- 🔍 Recommandations de cocktails réalisables
- 📊 Conversion automatique d'unités de mesure

## Qualité du code

Le projet utilise **Ruff** pour le linting et le formatage :
```bash
# Vérifier le code
uv run ruff check .

# Formater le code
uv run ruff format .
```

## Problèmes courants

### Erreur d'import de modules
- Exécutez `uv sync` pour synchroniser les dépendances
- Vérifiez que vous utilisez bien `uv run` pour lancer les commandes
