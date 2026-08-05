import sys
from usvisa.logger import logging
from usvisa.exception import USVisaException
from usvisa.entity.artifact_entity import (
    DataIngestionArtifact,
    DataValidationArtifact,
    DataTransformationArtifact
)
from usvisa.entity.config_entity import (
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig
)
from usvisa.components.data_ingestion import DataIngestion
from usvisa.components.data_validation import DataValidation
from usvisa.components.data_transformation import DataTransformation


class TrainingPipeline:
    def __init__(self):
        try:
            self.data_ingestion_config = DataIngestionConfig()
            self.data_validation_config = DataValidationConfig()
            self.data_transformation_config = DataTransformationConfig()
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

    def run_pipeline(self) -> None:
        """
        Ejecuta los componentes del pipeline en secuencia.
        """
        try:
            logging.info("========== Inicio del Training Pipeline ==========")
            data_ingestion_artifact = self.start_data_ingestion()
            data_validation_artifact = self.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)
            data_transformation_artifact = self.start_data_transformation(
                data_ingestion_artifact=data_ingestion_artifact,
                data_validation_artifact=data_validation_artifact
            )
            logging.info("========== Fin del Training Pipeline ==========")
        except Exception as e:
            raise USVisaException(e, sys) from e
