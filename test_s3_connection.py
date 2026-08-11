import sys
import os
from usvisa.logger import logging
from usvisa.exception import USVisaException
from config.aws_connection import S3Client
from cloud_storage.aws_storage import SimpleStorageService
from usvisa.constants import MODEL_BUCKET_NAME, MODEL_PUSHER_S3_KEY


def test_aws_s3_connection():
    """
    Script para verificar la autenticación y conectividad con AWS S3 y el bucket configurado.
    """
    try:
        print("========== Iniciando Prueba de Conexión a AWS S3 ==========")
        print(f"Bucket a probar: '{MODEL_BUCKET_NAME}'")
        print(f"Clave S3 configurada: '{MODEL_PUSHER_S3_KEY}'")

        # 1. Probar S3Client
        print("\n1. Verificando credenciales y creando cliente S3...")
        s3_client_obj = S3Client()
        print("✔ Cliente S3 autenticado correctamente con AWS.")

        # 2. Probar SimpleStorageService
        print("\n2. Inicializando SimpleStorageService...")
        storage_service = SimpleStorageService()

        # 3. Probar acceso al bucket
        print(f"\n3. Verificando acceso al bucket '{MODEL_BUCKET_NAME}'...")
        bucket = storage_service.get_bucket(MODEL_BUCKET_NAME)
        print(f"✔ Conexión exitosa al bucket: {bucket.name}")

        # 4. Listar archivos (s3:ListBucket)
        print("\n4. Probando permiso 's3:ListBucket' para listar archivos...")
        try:
            files = storage_service.list_files(bucket_name=MODEL_BUCKET_NAME)
            print(f"✔ Permiso s3:ListBucket OK. Archivos encontrados ({len(files)}):")
            for f in files[:5]:
                print(f"   - {f}")
        except Exception as e:
            print("⚠️ Permiso 's3:ListBucket' denegado en la política de AWS IAM para 'visa-user'.")

        # 5. Comprobar disponibilidad de la clave del modelo
        print(f"\n5. Verificando disponibilidad de la clave '{MODEL_PUSHER_S3_KEY}'...")
        is_present = storage_service.s3_key_path_available(
            bucket_name=MODEL_BUCKET_NAME,
            s3_key=MODEL_PUSHER_S3_KEY
        )
        print(f"✔ Modelo presente en S3: {is_present}")

        print("\n========================================================")
        print(" DIAGNÓSTICO DE CONEXIÓN A AWS S3 COMPLETADO")
        print("========================================================")

    except Exception as e:
        print("\n❌ Error en la prueba de conexión S3:")
        print(e)
        raise USVisaException(e, sys) from e


if __name__ == "__main__":
    test_aws_s3_connection()
