from contextlib import asynccontextmanager

from fastapi import FastAPI
from psycopg2.pool import SimpleConnectionPool

from src.api.main import api_router
from src.utils.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gère le cycle de vie de l'application (startup/shutdown)."""
    # Startup : Créer le pool de connexions PostgreSQL
    app.state.db_pool = SimpleConnectionPool(
        minconn=1,
        maxconn=10,
        host=settings.PGHOST,
        database=settings.PGDATABASE,
        user=settings.PGUSER,
        password=settings.PGPASSWORD,
        port=settings.PGPORT,
    )
    print("Pool de connexions PostgreSQL créé")

    yield  # L'application tourne ici

    # Shutdown : Fermer toutes les connexions
    app.state.db_pool.closeall()
    print("Pool de connexions PostgreSQL fermé")


app = FastAPI(
    title="API Cocktails",
    description="API REST pour gérer les cocktails TheCocktailDB",
    version="1.0.0",
    root_path="/proxy/8000",
    docs_url="/",
    redoc_url=None,
    lifespan=lifespan,
    swagger_ui_parameters={
        "persistAuthorization": True,  # Garde l'auth entre les rechargements
    },
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
