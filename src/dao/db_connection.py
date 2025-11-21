"""
Module gérant la connexion à la base de données PostgreSQL.
Il fournit une classe singleton DBConnection pour garantir qu'une seule connexion est ouverte.
"""

import os
import dotenv
import psycopg2

from psycopg2.extras import RealDictCursor
from src.utils.singleton import Singleton


class DBConnection(metaclass=Singleton):
    """
    Classe de connexion à la base de données
    Elle permet de n'ouvrir qu'une seule et unique connexion
    """

    def __init__(self):
        """Ouverture de la connexion"""
        dotenv.load_dotenv()

        self.__connection = psycopg2.connect(
            host=os.environ["POSTGRES_HOST"],
            port=os.environ["POSTGRES_PORT"],
            database=os.environ["POSTGRES_DATABASE"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            cursor_factory=RealDictCursor,
        )

    @property
    def connection(self):
        return self.__connection


# from psycopg2 import pool


# class DBConnection:
#     """Gère un pool de connexions à la base de données."""

#     pool = None

#     @classmethod
#     def initialize_pool(cls, minconn=1, maxconn=5):
#         """Initialise le pool de connexions."""
#         if cls.pool is None:
#             cls.pool = pool.SimpleConnectionPool(
#                 minconn,
#                 maxconn,
#                 host=os.environ.get("DB_HOST"),
#                 port=os.environ.get("DB_PORT"),
#                 database=os.environ.get("DB_NAME"),
#                 user=os.environ.get("DB_USER"),
#                 password=os.environ.get("DB_PASSWORD"),
#             )

#     @classmethod
#     def get_connection(cls):
#         """Récupère une connexion du pool."""
#         if cls._pool is None:
#             cls.initialize_pool()
#         return cls._pool.getconn()

#     @classmethod
#     def return_connection(cls, connection):
#         """Retourne une connexion au pool."""
#         if cls._pool:
#             cls._pool.putconn(connection)
