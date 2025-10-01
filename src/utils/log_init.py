import logging
import logging.config
import pathlib

import yaml


def initialiser_logs(nom):
    """Initialiser les logs à partir du fichier de config"""
    # print current working directory
    # print(os.getcwd())
    # os.chdir('ENSAI-2A-projet-info-template')

    # Création du dossier logs à la racine si non existant
    pathlib.Path("logs").mkdir(exist_ok=True, parents=True)

    stream = pathlib.Path("logging_config.yml").open(encoding="utf-8")
    config = yaml.load(stream, Loader=yaml.FullLoader)
    logging.config.dictConfig(config)

    logging.info("-" * 50)
    logging.info("Lancement %s                           ", nom)
    logging.info("-" * 50)
