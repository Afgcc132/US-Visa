import sys
from usvisa.logger import logging
from usvisa.exception import USVisaException
from usvisa.entity.artifact_entity import DataIngestionArtifact
from usvisa.entity.config_entity import DataIngestionConfig
from usvisa.components.data_ingestion import DataIngestion


class TrainingPipeline:
    def __init__(self):
        try:
            self.data_ingestion_config = DataIngestionConfig()
        except Exception as e:
            raise USVisaException(e, sys)

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
            raise USVisaException(e, sys)

    def run_pipeline(self) -> None:
        """
        Ejecuta los componentes del pipeline en secuencia.
        """
        try:
            logging.info("========== Inicio del Training Pipeline ==========")
            data_ingestion_artifact = self.start_data_ingestion()
            # A medida que construyas los siguientes componentes (Data Validation, Data Transformation, etc.),
            # los irás invocando aquí pasando el artefacto del paso anterior.
            logging.info("========== Fin del Training Pipeline ==========")
        except Exception as e:
            raise USVisaException(e, sys)
