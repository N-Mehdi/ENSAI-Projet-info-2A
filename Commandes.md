ok la team faites ça avant toute chose :

exécutez dans le terminal (dans cet ordre):

pip install -e ".[dev]"
pip install pre-commit
pre-commit install

puis faites ctrl + shift + x et cherchez Ruff(auteur Charlie Marsh) 
installez le

désinstallez flake8 au passage


pour voir si tout va bien : 

créez un fichier python avec ce code : 

for i in range(3) :
    print("aa"  )

ce code comporte des erreurs de style comme l'espace après le ' range(3) ' ou après ' "aa" '

enregistrez le fichier (ctrl + s)
si tout va bien, le style du code change tout seul (merci Ruff)
sinon dites moi :'( 


j'ai aussi mis un truc pour que ruff formate le code quand on fait un commit (même si on enregistre le code assez fréquemment mais why not)