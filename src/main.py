from fastapi import FastAPI

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
def root():
    """Route racine de l'API"""
    return {
        "message": "Bienvenue sur l'API Cocktails",
        "documentation": "/docs",
        "endpoints": {
            "GET /api/cocktails/lettre/{lettre}": "Chercher des cocktails par première lettre",
        },
    }


app.include_router(api_router)

# ouvrir la APIREST :
# python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# pour la fermer :
# soit avec le raccourci "ctrl + c" soit "kill %1" dans le terminal
