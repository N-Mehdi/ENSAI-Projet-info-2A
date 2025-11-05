import os
import pathlib

import psycopg2
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
dbname = os.getenv("POSTGRES_DATABASE")
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")

conn = psycopg2.connect(
    host=host,
    port=port,
    dbname=dbname,
    user=user,
    password=password,
)
cur = conn.cursor()

with pathlib.Path(
    "/home/onyxia/work/ENSAI-Projet-info-2A/data/bdd/table.sql",
).open() as f:
    sql = f.read()

cur.execute(sql)

conn.commit()
cur.close()
conn.close()

print("Table(s) créées avec succès !")
