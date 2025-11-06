from src.dao.utilisateur_dao import UtilisateurDao

dao = UtilisateurDao()

print(dao.read(8).id_utilisateur)
