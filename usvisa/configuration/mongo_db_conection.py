import os
import sys
import certifi
import pymongo

from usvisa.constants import DATABASE_NAME, MONGODB_URL_KEY
from usvisa.exception import USVisaException
from usvisa.logger import logging

ca = certifi.where()


class MongoDBClient:
    """
    Clase MongoDBClient para gestionar la conexión a la base de datos MongoDB.
    Utiliza el patrón Singleton para reutilizar la conexión del cliente a lo largo de la aplicación.
    """
    client = None

    def __init__(self, database_name: str = DATABASE_NAME) -> None:
        try:
            if MongoDBClient.client is None:
                mongo_db_url = os.getenv(MONGODB_URL_KEY)

                # Si no existe como variable de entorno, se verifica si MONGODB_URL_KEY contiene la URL directa
                if mongo_db_url is None:
                    if MONGODB_URL_KEY and ("mongodb://" in MONGODB_URL_KEY or "mongodb+srv://" in MONGODB_URL_KEY):
                        mongo_db_url = MONGODB_URL_KEY
                    else:
                        mongo_db_url = os.getenv("MONGODB_URL")

                if mongo_db_url is None:
                    raise Exception(f"La URL o clave de conexión a MongoDB ({MONGODB_URL_KEY}) no está configurada.")

                MongoDBClient.client = pymongo.MongoClient(
                    mongo_db_url,
                    tlsCAFile=ca,
                    tlsAllowInvalidCertificates=True
                )

            self.client = MongoDBClient.client
            self.database = self.client[database_name]
            self.database_name = database_name
            logging.info(f"Conexión a MongoDB establecida con éxito para la base de datos: {self.database_name}")
        except Exception as e:
            raise USVisaException(e, sys)
