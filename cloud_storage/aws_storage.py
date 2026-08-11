import io
import os
import sys
import pickle
from typing import Union, List
import pandas as pd

from config.aws_connection import S3Client
from usvisa.exception import USVisaException
from usvisa.logger import logging


class SimpleStorageService:
    """
    Clase SimpleStorageService para centralizar y gestionar las operaciones
    de comunicación y almacenamiento entre la aplicación local y Amazon S3.
    Permite subir modelos a producción, cargar o descargar modelos existentes
    y manipular archivos en la nube.
    """

    def __init__(self):
        try:
            s3_client = S3Client()
            self.s3_resource = s3_client.s3_resource
            self.s3_client = s3_client.s3_client
        except Exception as e:
            raise USVisaException(e, sys) from e

    def get_bucket(self, bucket_name: str):
        """
        Obtiene el objeto Bucket de boto3 correspondiente a bucket_name.
        """
        try:
            bucket = self.s3_resource.Bucket(bucket_name)
            return bucket
        except Exception as e:
            raise USVisaException(e, sys) from e

    def s3_key_path_available(self, bucket_name: str, s3_key: str) -> bool:
        """
        Verifica si la clave o ruta de archivo (s3_key) existe en el bucket de S3.
        """
        try:
            bucket = self.get_bucket(bucket_name)
            file_objects = [file_object for file_object in bucket.objects.filter(Prefix=s3_key)]
            return len(file_objects) > 0
        except Exception:
            try:
                self.s3_client.head_object(Bucket=bucket_name, Key=s3_key)
                return True
            except Exception:
                return False

    def read_object(self, object_name: str, decode: bool = True, make_to_dataframe: bool = False) -> Union[io.StringIO, str, pd.DataFrame]:
        """
        Lee un objeto del bucket de S3 especificado.
        Permite retornar texto decodificado o un DataFrame de pandas.
        """
        try:
            func = (
                lambda: io.StringIO(object_name.get()["Body"].read().decode("utf-8"))
                if decode
                else object_name.get()["Body"].read()
            )
            if make_to_dataframe:
                return pd.read_csv(func())
            return func()
        except Exception as e:
            raise USVisaException(e, sys) from e

    def get_file_object(self, filename: str, bucket_name: str) -> Union[List[object], object]:
        """
        Obtiene los objetos de archivo que coinciden con el nombre o sufijo dentro del bucket de S3.
        """
        try:
            bucket = self.get_bucket(bucket_name)
            file_objects = [file_object for file_object in bucket.objects.filter(Prefix=filename)]
            func = lambda x: x[0] if len(x) == 1 else x
            file_objs = func(file_objects)
            return file_objs
        except Exception as e:
            raise USVisaException(e, sys) from e

    def load_model(self, model_name: str, bucket_name: str, model_dir: str = None) -> object:
        """
        Carga un modelo entrenado desde Amazon S3 directamente a la memoria.
        """
        try:
            func = (
                lambda: model_name
                if model_dir is None
                else os.path.join(model_dir, model_name).replace("\\", "/")
            )
            model_file_name = func()
            file_object = self.get_file_object(model_file_name, bucket_name)
            model_obj = self.read_object(file_object, decode=False)
            model = pickle.loads(model_obj)
            logging.info(f"Modelo {model_name} cargado exitosamente desde S3 bucket: {bucket_name}")
            return model
        except Exception as e:
            raise USVisaException(e, sys) from e

    def upload_model(self, model_path: str, bucket_name: str, model_dir: str = None, s3_model_key_path: str = None) -> None:
        """
        Sube un modelo local hacia el bucket de Amazon S3 especificado para producción.
        """
        try:
            if s3_model_key_path is None:
                func = (
                    lambda: os.path.basename(model_path)
                    if model_dir is None
                    else os.path.join(model_dir, os.path.basename(model_path)).replace("\\", "/")
                )
                to_filename = func()
            else:
                to_filename = s3_model_key_path

            self.upload_file(
                from_filename=model_path,
                to_filename=to_filename,
                bucket_name=bucket_name,
                remove=False
            )
            logging.info(f"Modelo subido a S3 con éxito: {to_filename} en el bucket: {bucket_name}")
        except Exception as e:
            raise USVisaException(e, sys) from e

    def upload_file(self, from_filename: str, to_filename: str, bucket_name: str, remove: bool = True) -> None:
        """
        Sube un archivo desde una ruta local a Amazon S3 y opcionalmente elimina el archivo local.
        """
        try:
            logging.info(f"Subiendo archivo {from_filename} a S3: {to_filename} en bucket: {bucket_name}")
            self.s3_resource.meta.client.upload_file(
                Filename=from_filename,
                Bucket=bucket_name,
                Key=to_filename
            )
            logging.info(f"Archivo {from_filename} subido correctamente a S3 key: {to_filename}")
            if remove:
                os.remove(from_filename)
                logging.info(f"Archivo local {from_filename} eliminado tras subirlo a S3")
        except Exception as e:
            raise USVisaException(e, sys) from e

    def download_file(self, bucket_name: str, s3_key: str, to_filename: str) -> None:
        """
        Descarga un archivo desde Amazon S3 a la ruta local especificada.
        """
        try:
            dir_name = os.path.dirname(to_filename)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            logging.info(f"Descargando clave S3 {s3_key} del bucket {bucket_name} hacia local: {to_filename}")
            self.s3_resource.Bucket(bucket_name).download_file(
                Key=s3_key,
                Filename=to_filename
            )
            logging.info(f"Archivo descargado exitosamente en: {to_filename}")
        except Exception as e:
            raise USVisaException(e, sys) from e

    def read_csv(self, filename: str, bucket_name: str) -> pd.DataFrame:
        """
        Lee un archivo CSV guardado en Amazon S3 y lo convierte en un DataFrame de pandas.
        """
        try:
            file_object = self.get_file_object(filename, bucket_name)
            df = self.read_object(file_object, decode=True, make_to_dataframe=True)
            return df
        except Exception as e:
            raise USVisaException(e, sys) from e

    def list_files(self, bucket_name: str, folder_name: str = "") -> List[str]:
        """
        Lista las claves/archivos presentes en un bucket o subcarpeta de Amazon S3.
        """
        try:
            bucket = self.get_bucket(bucket_name)
            files = [obj.key for obj in bucket.objects.filter(Prefix=folder_name)]
            return files
        except Exception as e:
            raise USVisaException(e, sys) from e


# Alias para compatibilidad con nombres alternativos de la clase de almacenamiento AWS
AWSStorage = SimpleStorageService
