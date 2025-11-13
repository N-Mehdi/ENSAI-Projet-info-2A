from fastapi import APIRouter

from src.api.routes.avis_routes import router as avis_router
from src.api.routes.cocktail_routes import router as cocktail_router
from src.api.routes.favoris_router import router as favoris_router
from src.api.routes.ingredient_routes import router as ingredient_router
from src.api.routes.liste_course_routes import router as liste_course_router
from src.api.routes.login import router as login_router
from src.api.routes.stock_course_routes import router as stock_course_router
from src.api.routes.utilisateur_routes import router as utilisateur_router
from src.api.routes.acces_routes import router as acces_router

api_router = APIRouter(prefix="/api")


api_router.include_router(login_router)
api_router.include_router(utilisateur_router)
api_router.include_router(cocktail_router)
api_router.include_router(stock_course_router)
api_router.include_router(ingredient_router)
api_router.include_router(favoris_router)
api_router.include_router(avis_router)
api_router.include_router(liste_course_router)
api_router.include_router(acces_router)
