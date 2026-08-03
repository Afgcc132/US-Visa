import json
import sys
import os
import pandas as pd
from pandas import DataFrame

from evidently.model_profile import Profile
from evidently.model_profile.sections import DataDriftProfileSection
from evidently.dashboard import Dashboard
from evidently.dashboard.tabs import DataDriftTab

from usvisa.exception import USVisaException 

from usvisa.logger import logging
from usvisa.entity.config_entity import DataValidationConfig
from usvisa.entity.artifact_entity import DataValidationArtifact, DataIngestionArtifact
from usvisa.utils.main_utils import read_yaml_file, write_yaml_file
from usvisa.constants import SCHEMA_FILE_PATH



class DataValidation:   

    def __init__(self, data_ingestion_artifact: DataIngestionArtifact, data_validation_config: DataValidationConfig):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise USVisaException(e, sys) from e

    def validate_number_of_columns(self, dataframe: DataFrame) -> bool:
        """
        Method Name : validate_number_of_columns
        Description : This method validates the number of columns in the dataframe against schema
        
        Output      : Returns bool value based on validation results
        On Failure  : Write an exception log and then raise an exception
        """
        try:
            status = len(dataframe.columns) == len(self._schema_config["columns"])
            logging.info(f"Is required number of columns present: {status}")
            return status
        except Exception as e:
            raise USVisaException(e, sys) from e

    def is_column_exist(self, df: DataFrame) -> bool:
        """
        Method Name : is_column_exist
        Description : This method validates the existence of numerical and categorical columns
        
        Output      : Returns bool value based on validation results
        On Failure  : Write an exception log and then raise an exception
        """
        try:
            dataframe_columns = df.columns
            missing_numerical_columns = []
            missing_categorical_columns = []
            
            for column in self._schema_config["numerical_columns"]:
                if column not in dataframe_columns:
                    missing_numerical_columns.append(column)

            if len(missing_numerical_columns) > 0:
                logging.info(f"Missing numerical column: {missing_numerical_columns}")

            for column in self._schema_config["categorical_columns"]:
                if column not in dataframe_columns:
                    missing_categorical_columns.append(column)

            if len(missing_categorical_columns) > 0:
                logging.info(f"Missing categorical column: {missing_categorical_columns}")

            return False if len(missing_categorical_columns) > 0 or len(missing_numerical_columns) > 0 else True
        except Exception as e:
            raise USVisaException(e, sys) from e

    @staticmethod
    def read_data(file_path) -> DataFrame:
        """
        Method Name : read_data
        Description : Reads csv data into a pandas dataframe
        """
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise USVisaException(e, sys) from e

    def detect_dataset_drift(self, reference_df: DataFrame, current_df: DataFrame) -> bool:
        """
        Method Name : detect_dataset_drift
        Description : This method validates if drift is detected
        
        Output      : Returns bool value based on validation results
        On Failure  : Write an exception log and then raise an exception
        """
        try:
            data_drift_profile = Profile(sections=[DataDriftProfileSection()])
            
            data_drift_profile.calculate(reference_df, current_df)
            
            report = data_drift_profile.json()
            json_report = json.loads(report)
            
            write_yaml_file(file_path=self.data_validation_config.drift_report_file_path, content=json_report)
            
            # Guardar el reporte HTML interactivo
            dashboard = Dashboard(tabs=[DataDriftTab()])
            dashboard.calculate(reference_df, current_df)
            dashboard.save(self.data_validation_config.drift_report_page_file_path)
            
            n_features = json_report["data_drift"]["data"]["metrics"]["n_features"]
            n_drifted_features = json_report["data_drift"]["data"]["metrics"]["n_drifted_features"]
            
            logging.info(f"{n_drifted_features}/{n_features} drift detected.")
            
            # Log exact columns where drift was detected
            metrics = json_report["data_drift"]["data"]["metrics"]
            for feature_name, feature_info in metrics.items():
                if isinstance(feature_info, dict) and feature_info.get("drift_detected", False):
                    logging.info(f"--> Drift detectado en la columna: '{feature_name}'")


            drift_status = json_report["data_drift"]["data"]["metrics"]["dataset_drift"]
            return drift_status

        except Exception as e:
            raise USVisaException(e, sys) from e


    def initiate_data_validation(self) -> DataValidationArtifact:
        """
        Method Name : initiate_data_validation
        Description : Initiates the data validation component for the pipeline
        """
        try:
            validation_error_msg = ""
            logging.info("Starting data validation")
            train_df = DataValidation.read_data(file_path=self.data_ingestion_artifact.trained_file_path)
            test_df = DataValidation.read_data(file_path=self.data_ingestion_artifact.test_file_path)

            status = self.validate_number_of_columns(dataframe=train_df)
            logging.info(f"All required columns present in training dataframe: {status}")
            if not status:
                validation_error_msg += f"Columns are missing in training dataframe. "

            status = self.validate_number_of_columns(dataframe=test_df)
            logging.info(f"All required columns present in testing dataframe: {status}")
            if not status:
                validation_error_msg += f"Columns are missing in testing dataframe. "

            status = self.is_column_exist(df=train_df)
            if not status:
                validation_error_msg += f"Columns are missing in training dataframe. "

            status = self.is_column_exist(df=test_df)
            if not status:
                validation_error_msg += f"Columns are missing in testing dataframe. "

            validation_status = len(validation_error_msg) == 0

            if validation_status:
                drift_status = self.detect_dataset_drift(reference_df=train_df, current_df=test_df)
                if not drift_status:
                    logging.info("Drift detected")
                    validation_error_msg = "Drift detected"
                else:
                    validation_error_msg = "Drift not detected"
            else:
                logging.info(f"Validation_error: {validation_error_msg}")

            data_validation_artifact = DataValidationArtifact(
                validation_status=validation_status,
                message=validation_error_msg,
                drift_report_file_path=self.data_validation_config.drift_report_file_path
            )

            logging.info(f"Data validation artifact: {data_validation_artifact}")
            return data_validation_artifact

        except Exception as e:
            raise USVisaException(e, sys) from e
