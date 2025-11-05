"""from src.dao.utilisateur_dao import UtilisateurDao
from src.models.utilisateurs import UserCreate

dao = UtilisateurDao()

user_create = UserCreate(
    pseudo="string",
    mail="mail@example.com",
    date_naissance="2000-01-01",
    mot_de_passe_hashed="string",
)

dao.create_compte(user_create)
"""

from src.utils.securite import hacher_mot_de_passe

