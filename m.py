from src.dao.utilisateur_dao import UtilisateurDao
from src.service.utilisateur_service import UtilisateurService

dao = UtilisateurDao()

UtilisateurService(dao(cur))