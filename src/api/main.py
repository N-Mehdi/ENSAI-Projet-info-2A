from fastapi import APIRouter

from src.api.routes.cocktail_routes import router as cocktail_router

# creer un apirouteur avec prefix
# routeur include mes autres routes

api_router = APIRouter(prefix="/api")


api_router.include_router(cocktail_router)
