from fastapi import FastAPI

from src.api.main import api_router

app = FastAPI(
    title="API Cocktails",
    description="API REST pour gérer les cocktails TheCocktailDB",
    version="1.0.0",
    root_path="/proxy/8000",
)

app.include_router(api_router)


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


# ouvrir la APIREST : python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
# la fermer : soit avec le raccourci "ctrl + c" soit "kill %1" dans le terminal
