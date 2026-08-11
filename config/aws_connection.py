import os
import sys
import boto3

from usvisa.constants import AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, AWS_REGION
from usvisa.exception import USVisaException
from usvisa.logger import logging


class S3Client:
    """
    Clase S3Client para gestionar la conexión a Amazon S3 utilizando boto3.
    Utiliza un patrón de conexión reutilizable para interactuar con los buckets de AWS.
    """
    s3_client = None
    s3_resource = None

    def __init__(self, region_name: str = AWS_REGION):
        """
        Inicializa la conexión con AWS S3 verificando variables de entorno
        o utilizando las credenciales configuradas en las constantes.
        """
        try:
            if S3Client.s3_client is None or S3Client.s3_resource is None:
                access_key_id = os.getenv("AWS_ACCESS_KEY_ID", AWS_ACCESS_KEY)
                secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY", AWS_SECRET_ACCESS_KEY)
                region = os.getenv("AWS_REGION", region_name)

                if not access_key_id or not secret_access_key:
                    raise Exception("Las credenciales de AWS (AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY) no están configuradas.")

                S3Client.s3_resource = boto3.resource(
                    's3',
                    aws_access_key_id=access_key_id,
                    aws_secret_access_key=secret_access_key,
                    region_name=region
                )

                S3Client.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=access_key_id,
                    aws_secret_access_key=secret_access_key,
                    region_name=region
                )

                logging.info(f"Conexión a AWS S3 establecida con éxito en la región: {region}")

            self.s3_resource = S3Client.s3_resource
            self.s3_client = S3Client.s3_client

        except Exception as e:
            raise USVisaException(e, sys) from e
