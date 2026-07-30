import sys
from typing import Optional

import numpy as np
import pandas as pd

from usvisa.configuration.mongo_db_conection import MongoDBClient
from usvisa.constants import DATABASE_NAME
from usvisa.exception import USVisaException
from usvisa.logger import logging


class USVisaData:
    """
    Clase para extraer datos desde la base de datos MongoDB, 
    convertirlos a un DataFrame de pandas y aplicar una limpieza inicial.
    """

    def __init__(self):
        try:
            self.mongo_client = MongoDBClient(database_name=DATABASE_NAME)
        except Exception as e:
            raise USVisaException(e, sys)

    def export_collection_as_dataframe(
        self, collection_name: str, database_name: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Extrae toda la colección especificada desde MongoDB y la convierte a un DataFrame de pandas.
        Realiza la limpieza inicial eliminando la columna '_id' y reemplazando valores nulos/'na'.

        :param collection_name: Nombre de la colección en MongoDB.
        :param database_name: Nombre opcional de la base de datos (por defecto usa DATABASE_NAME).
        :return: DataFrame de pandas con los datos extraídos y limpios.
        """
        try:
            if database_name is None:
                collection = self.mongo_client.database[collection_name]
            else:
                collection = self.mongo_client.client[database_name][collection_name]

            df = pd.DataFrame(list(collection.find()))
            logging.info(f"Se extrajeron exitosamente {len(df)} registros de la colección: {collection_name}")

            # Limpieza del DataFrame
            if "_id" in df.columns:
                df = df.drop(columns=["_id"], axis=1)

            # Reemplazar valores faltantes como 'na' por np.nan
            df.replace({"na": np.nan}, inplace=True)

            return df

        except Exception as e:
            raise USVisaException(e, sys)
