from fastapi import APIRouter

from src.api.routes.cocktail_routes import router as cocktail_router
from src.api.routes.login import router as login_router
from src.api.routes.utilisateur_routes import router as utilisateur_router

# creer un apirouteur avec prefix
# routeur include mes autres routes

api_router = APIRouter(prefix="/api")


api_router.include_router(login_router)
api_router.include_router(utilisateur_router)
api_router.include_router(cocktail_router)
# api_router.include_router(stock_course_router)
