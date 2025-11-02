from fastapi import FastAPI
from src.api.routes.cocktail_routes import router as cocktail_router

app = FastAPI(
    title="API Cocktails",
    description="API REST pour gérer les cocktails TheCocktailDB",
    version="1.0.0",
    root_path="/proxy/8000"
)

app.include_router(cocktail_router, prefix="/api")


@app.get("/")
def root():
    """Route racine de l'API"""
    return {
        "message": "Bienvenue sur l'API Cocktails",
        "documentation": "/docs",
        "endpoints": {
            "GET /api/cocktails/lettre/{lettre}": "Chercher des cocktails par première lettre"
        }
    }

# python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000