import os
import sys

from pandas import DataFrame
from sklearn.model_selection import train_test_split


from usvisa.logger import logging
from usvisa.exception import USVisaException
from usvisa.data_acces.usvisa_data import USVisaData
from usvisa.entity.artifact_entity import DataIngestionArtifact
from usvisa.entity.config_entity import DataIngestionConfig


class DataIngestion:
    
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
            self.usvisa_data = USVisaData()
        except Exception as e:
            raise USVisaException(e, sys)

    def export_data_into_feature_store(self) -> DataFrame:
        """
        Paso 1: Extrae datos de MongoDB y los guarda en la carpeta Feature Store
        """
        try:
            logging.info("Exportando datos de MongoDB a Feature Store")
            df = self.usvisa_data.export_collection_as_dataframe(
                collection_name=self.data_ingestion_config.collection_name
            )
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)
            df.to_csv(feature_store_file_path, index=False)
            return df
        except Exception as e:
            raise USVisaException(e, sys)

    def split_data_as_train_test(self, df: DataFrame) -> DataIngestionArtifact:
        """
        Paso 2: Divide los datos en train/test, guarda los CSVs y retorna el DataIngestionArtifact
        """
        try:
            logging.info("Dividiendo los datos en train y test")
            train_df, test_df = train_test_split(
                df, 
                test_size=self.data_ingestion_config.train_test_split_ratio, 
                random_state=42
            )
            
            train_file_path = self.data_ingestion_config.training_file_path
            test_file_path = self.data_ingestion_config.testing_file_path
            
            os.makedirs(os.path.dirname(train_file_path), exist_ok=True)
            os.makedirs(os.path.dirname(test_file_path), exist_ok=True)
            
            train_df.to_csv(train_file_path, index=False)
            test_df.to_csv(test_file_path, index=False)
            
            logging.info(f"Archivos guardados en: {train_file_path} y {test_file_path}")
            
            # Retornamos el objeto DataIngestionArtifact con las rutas
            data_ingestion_artifact = DataIngestionArtifact(
                trained_file_path=train_file_path,
                test_file_path=test_file_path
            )
            return data_ingestion_artifact

        except Exception as e:
            raise USVisaException(e, sys)

    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        """
        Paso 3: Método principal que orquesta todo el proceso y retorna el artefacto final
        """
        try:
            logging.info("Iniciando el proceso de ingesta de datos")
            df = self.export_data_into_feature_store()
            data_ingestion_artifact = self.split_data_as_train_test(df=df)
            logging.info("Ingesta de datos completada exitosamente")
            return data_ingestion_artifact
        except Exception as e:
            raise USVisaException(e, sys)
