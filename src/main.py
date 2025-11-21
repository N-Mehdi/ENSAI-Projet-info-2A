"""Point d'entrée principal pour l'application FastAPI."""

import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI

if __name__ == "__main__":
    root_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(root_dir))

from src.api.main import api_router
from src.utils.settings import settings

app = FastAPI(
    title="API Cocktails",
    description="API REST pour gérer les cocktails TheCocktailDB",
    version="1.0.0",
    root_path=settings.ROOT_PATH,
    docs_url="/",  # Swagger UI accessible directement à la racine
    redoc_url=None,  # Désactive ReDoc
)


@app.get("/")
def root() -> dict:
    """Route racine de l'API."""
    return {
        "message": "Bienvenue sur l'API Cocktails",
        "documentation": "/docs",
        "endpoints": {
            "GET /api/cocktails/lettre/{lettre}": "Chercher des cocktails par première"
            "lettre",
        },
    }


app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

# pour lancer l'api :
# uv run src/main.py
