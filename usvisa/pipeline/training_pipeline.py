import sys
from usvisa.logger import logging
from usvisa.exception import USVisaException
from usvisa.entity.artifact_entity import (
    DataIngestionArtifact,
    DataValidationArtifact,
    DataTransformationArtifact,
    ModelTrainerArtifact,
    ModelEvaluationArtifact,
    ModelPusherArtifact
)
from usvisa.entity.config_entity import (
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig,
    ModelEvaluationConfig,
    ModelPusherConfig
)
from usvisa.components.data_ingestion import DataIngestion
from usvisa.components.data_validation import DataValidation
from usvisa.components.data_transformation import DataTransformation
from usvisa.components.model_training import ModelTrainer
from usvisa.components.model_evaluation import ModelEvaluation
from usvisa.components.model_pusher import ModelPusher


class TrainingPipeline:
    def __init__(self):
        try:
            self.data_ingestion_config = DataIngestionConfig()
            self.data_validation_config = DataValidationConfig()
            self.data_transformation_config = DataTransformationConfig()
            self.model_trainer_config = ModelTrainerConfig()
            self.model_evaluation_config = ModelEvaluationConfig()
            self.model_pusher_config = ModelPusherConfig()
        except Exception as e:
            raise USVisaException(e, sys) from e

    def start_data_ingestion(self) -> DataIngestionArtifact:
        """
        Inicia el componente de ingesta de datos.
        """
        try:
            logging.info("Iniciando componente: Data Ingestion")
            data_ingestion = DataIngestion(data_ingestion_config=self.data_ingestion_config)
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
            logging.info(f"Componente Data Ingestion completado. Artefacto: {data_ingestion_artifact}")
            return data_ingestion_artifact
        except Exception as e:
            raise USVisaException(e, sys) from e

    def start_data_validation(self, data_ingestion_artifact: DataIngestionArtifact) -> DataValidationArtifact:
        """
        Inicia el componente de validación de datos.
        """
        try:
            logging.info("Iniciando componente: Data Validation")
            data_validation = DataValidation(
                data_ingestion_artifact=data_ingestion_artifact,
                data_validation_config=self.data_validation_config
            )
            data_validation_artifact = data_validation.initiate_data_validation()
            logging.info(f"Componente Data Validation completado. Artefacto: {data_validation_artifact}")
            return data_validation_artifact
        except Exception as e:
            raise USVisaException(e, sys) from e

    def start_data_transformation(
        self,
        data_ingestion_artifact: DataIngestionArtifact,
        data_validation_artifact: DataValidationArtifact
    ) -> DataTransformationArtifact:
        """
        Inicia el componente de transformación de datos.
        """
        try:
            logging.info("Iniciando componente: Data Transformation")
            data_transformation = DataTransformation(
                data_ingestion_artifact=data_ingestion_artifact,
                data_transformation_config=self.data_transformation_config,
                data_validation_artifact=data_validation_artifact
            )
            data_transformation_artifact = data_transformation.initiate_data_transformation()
            logging.info(f"Componente Data Transformation completado. Artefacto: {data_transformation_artifact}")
            return data_transformation_artifact
        except Exception as e:
            raise USVisaException(e, sys) from e

    def start_model_trainer(self, data_transformation_artifact: DataTransformationArtifact) -> ModelTrainerArtifact:
        """
        Inicia el componente de entrenamiento de modelo.
        """
        try:
            logging.info("Iniciando componente: Model Trainer")
            model_trainer = ModelTrainer(
                data_transformation_artifact=data_transformation_artifact,
                model_trainer_config=self.model_trainer_config
            )
            model_trainer_artifact = model_trainer.initiate_model_trainer()
            logging.info(f"Componente Model Trainer completado. Artefacto: {model_trainer_artifact}")
            return model_trainer_artifact
        except Exception as e:
            raise USVisaException(e, sys) from e

    def start_model_evaluation(
        self,
        data_ingestion_artifact: DataIngestionArtifact,
        data_transformation_artifact: DataTransformationArtifact,
        model_trainer_artifact: ModelTrainerArtifact
    ) -> ModelEvaluationArtifact:
        """
        Inicia el componente de evaluación comparativa del modelo frente a la versión en producción (S3).
        """
        try:
            logging.info("Iniciando componente: Model Evaluation")
            model_evaluation = ModelEvaluation(
                model_evaluation_config=self.model_evaluation_config,
                data_ingestion_artifact=data_ingestion_artifact,
                data_transformation_artifact=data_transformation_artifact,
                model_trainer_artifact=model_trainer_artifact
            )
            model_evaluation_artifact = model_evaluation.initiate_model_evaluation()
            logging.info(f"Componente Model Evaluation completado. Artefacto: {model_evaluation_artifact}")
            return model_evaluation_artifact
        except Exception as e:
            raise USVisaException(e, sys) from e

    def start_model_pusher(self, model_evaluation_artifact: ModelEvaluationArtifact) -> ModelPusherArtifact:
        """
        Inicia el componente de empuje del modelo aceptado hacia Amazon S3.
        """
        try:
            logging.info("Iniciando componente: Model Pusher")
            model_pusher = ModelPusher(
                model_pusher_config=self.model_pusher_config,
                model_evaluation_artifact=model_evaluation_artifact
            )
            model_pusher_artifact = model_pusher.initiate_model_pusher()
            logging.info(f"Componente Model Pusher completado. Artefacto: {model_pusher_artifact}")
            return model_pusher_artifact
        except Exception as e:
            raise USVisaException(e, sys) from e

    def run_pipeline(self) -> None:
        """
        Ejecuta todos los componentes del pipeline en secuencia:
        Data Ingestion -> Data Validation -> Data Transformation -> Model Trainer -> Model Evaluation -> Model Pusher
        """
        try:
            logging.info("========== Inicio del Training Pipeline ==========")
            data_ingestion_artifact = self.start_data_ingestion()
            data_validation_artifact = self.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)
            data_transformation_artifact = self.start_data_transformation(
                data_ingestion_artifact=data_ingestion_artifact,
                data_validation_artifact=data_validation_artifact
            )
            model_trainer_artifact = self.start_model_trainer(
                data_transformation_artifact=data_transformation_artifact
            )
            model_evaluation_artifact = self.start_model_evaluation(
                data_ingestion_artifact=data_ingestion_artifact,
                data_transformation_artifact=data_transformation_artifact,
                model_trainer_artifact=model_trainer_artifact
            )

            if not model_evaluation_artifact.is_model_accepted:
                logging.info("El nuevo modelo entrenado NO fue aceptado. No se empujará a producción en S3.")
            else:
                model_pusher_artifact = self.start_model_pusher(
                    model_evaluation_artifact=model_evaluation_artifact
                )
                logging.info(f"Modelo promovido exitosamente a S3: {model_pusher_artifact}")

            logging.info("========== Fin del Training Pipeline ==========")
        except Exception as e:
            raise USVisaException(e, sys) from e
