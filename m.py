from src.dao.utilisateur_dao import UtilisateurDao
from src.models.utilisateurs import UserLogin
from src.utils.securite import hacher_mot_de_passe, verifier_mot_de_passe

utilisateur_dao = UtilisateurDao()


donnees = UserLogin(mail="Y", mot_de_passe="azerty")
user_mail = donnees.mail

mail = "Y"


donnees_bdd = utilisateur_dao.recuperer_mot_de_passe_hashe_par_mail(
    donnees.mail,
)


print(donnees)
print(donnees_bdd)
print(donnees_bdd["mot_de_passe"])

print(verifier_mot_de_passe("azerty", hacher_mot_de_passe("azerty")))
