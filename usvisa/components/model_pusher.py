import sys

from usvisa.logger import logging
from usvisa.exception import USVisaException
from usvisa.entity.config_entity import ModelPusherConfig
from usvisa.entity.artifact_entity import ModelEvaluationArtifact, ModelPusherArtifact
from usvisa.entity.s3_estimator import USVisaEstimator


class ModelPusher:
    """
    Componente responsable de subir y promover el modelo aceptado
    hacia el servicio de almacenamiento en la nube Amazon S3 para su despliegue en producción.
    """

    def __init__(self, model_pusher_config: ModelPusherConfig, model_evaluation_artifact: ModelEvaluationArtifact):
        try:
            self.model_pusher_config = model_pusher_config
            self.model_evaluation_artifact = model_evaluation_artifact
            self.s3_estimator = USVisaEstimator(
                bucket_name=self.model_pusher_config.bucket_name,
                s3_key=self.model_pusher_config.s3_model_key_path
            )
        except Exception as e:
            raise USVisaException(e, sys) from e

    def initiate_model_pusher(self) -> ModelPusherArtifact:
        """
        Inicia el proceso de empujar el modelo aceptado a Amazon S3.
        """
        try:
            logging.info("========== Iniciando Componente: Model Pusher ==========")
            logging.info(f"Subiendo modelo desde {self.model_evaluation_artifact.base_model_path} hacia S3 bucket: {self.model_pusher_config.bucket_name}")

            self.s3_estimator.save_model(from_file=self.model_evaluation_artifact.base_model_path)

            model_pusher_artifact = ModelPusherArtifact(
                bucket_name=self.model_pusher_config.bucket_name,
                s3_model_path=self.model_pusher_config.s3_model_key_path
            )

            logging.info(f"Modelo subido a S3 exitosamente. Artefacto: {model_pusher_artifact}")
            logging.info("========== Componente Model Pusher completado ==========")
            return model_pusher_artifact

        except Exception as e:
            raise USVisaException(e, sys) from e
