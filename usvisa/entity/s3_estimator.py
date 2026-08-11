import sys
from pandas import DataFrame
from cloud_storage.aws_storage import SimpleStorageService
from usvisa.entity.estimator import USVisaModel
from usvisa.exception import USVisaException
from usvisa.logger import logging
from usvisa.constants import MODEL_BUCKET_NAME, MODEL_PUSHER_S3_KEY, MODEL_FILE_NAME


class USVisaEstimator:
    """
    Clase USVisaEstimator para conectar y abstraer el modelo entrenado
    almacenado en Amazon S3. Permite verificar la existencia del modelo,
    cargar el modelo desde S3, guardar/subir nuevos modelos a S3 y realizar
    predicciones directamente usando la instancia cargada.
    """

    def __init__(self, bucket_name: str = MODEL_BUCKET_NAME, s3_key: str = MODEL_PUSHER_S3_KEY):
        """
        Inicializa la conexión con S3 y configura la ruta del modelo.
        """
        try:
            self.bucket_name = bucket_name
            self.s3_key = s3_key if s3_key and s3_key.strip() != "" else MODEL_FILE_NAME
            self.s3 = SimpleStorageService()
            self.loaded_model: USVisaModel = None
        except Exception as e:
            raise USVisaException(e, sys) from e

    def is_model_present(self, s3_key: str = None) -> bool:
        """
        Verifica si el modelo existe en el bucket de Amazon S3.
        """
        try:
            key_to_check = s3_key if s3_key else self.s3_key
            return self.s3.s3_key_path_available(bucket_name=self.bucket_name, s3_key=key_to_check)
        except Exception as e:
            raise USVisaException(e, sys) from e

    def load_model(self) -> USVisaModel:
        """
        Carga el modelo desde S3 a la memoria. Si ya está cargado, retorna la instancia existente.
        """
        try:
            if self.loaded_model is None:
                logging.info(f"Cargando modelo desde S3 (bucket: {self.bucket_name}, key: {self.s3_key})")
                self.loaded_model = self.s3.load_model(model_name=self.s3_key, bucket_name=self.bucket_name)
            return self.loaded_model
        except Exception as e:
            raise USVisaException(e, sys) from e

    def save_model(self, from_file: str, remove: bool = False) -> None:
        """
        Guarda y sube un archivo de modelo local hacia Amazon S3 en el bucket especificado.
        """
        try:
            logging.info(f"Guardando modelo {from_file} en S3 (bucket: {self.bucket_name}, key: {self.s3_key})")
            self.s3.upload_model(
                model_path=from_file,
                bucket_name=self.bucket_name,
                s3_model_key_path=self.s3_key
            )
            if remove:
                import os
                if os.path.exists(from_file):
                    os.remove(from_file)
                    logging.info(f"Archivo local de modelo {from_file} eliminado.")
        except Exception as e:
            raise USVisaException(e, sys) from e

    def predict(self, dataframe: DataFrame):
        """
        Realiza predicciones usando el modelo almacenado en S3.
        Carga el modelo si aún no ha sido inicializado en memoria.
        """
        try:
            if self.loaded_model is None:
                self.loaded_model = self.load_model()
            return self.loaded_model.predict(dataframe=dataframe)
        except Exception as e:
            raise USVisaException(e, sys) from e


# Alias para compatibilidad de nomenclatura
S3Estimator = USVisaEstimator
