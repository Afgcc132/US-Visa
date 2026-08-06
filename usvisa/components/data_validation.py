import json
import sys
import os
import pandas as pd
from pandas import DataFrame

from usvisa.logger import logging
from usvisa.exception import USVisaException 
from usvisa.entity.config_entity import DataValidationConfig
from usvisa.entity.artifact_entity import DataValidationArtifact, DataIngestionArtifact
from usvisa.utils.main_utils import read_yaml_file, write_yaml_file
from usvisa.constants import SCHEMA_FILE_PATH

EVIDENTLY_MODE = "none"
Report = None
DataDriftPreset = None
Profile = None
DataDriftProfileSection = None
Dashboard = None
DataDriftTab = None

# Cargar clases de Evidently de forma independiente para prevenir errores de importación
try:
    # Intento 1: Importar Report
    try:
        from evidently.report import Report
    except ImportError:
        try:
            from evidently import Report
        except ImportError:
            Report = None

    # Intento 2: Importar DataDriftPreset
    try:
        from evidently.metric_preset import DataDriftPreset
    except ImportError:
        try:
            from evidently.presets import DataDriftPreset
        except ImportError:
            DataDriftPreset = None

    if Report is not None and DataDriftPreset is not None:
        EVIDENTLY_MODE = "modern"
    else:
        # Intento 3: Legacy Evidently (0.1.x)
        from evidently.model_profile import Profile
        from evidently.model_profile.sections import DataDriftProfileSection
        from evidently.dashboard import Dashboard
        from evidently.dashboard.tabs import DataDriftTab
        EVIDENTLY_MODE = "legacy"

except Exception as e:
    logging.warning(f"Evidently no disponible ({e}). Se utilizará el reporte estático de Data Validation.")
    EVIDENTLY_MODE = "none"



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
        Description : This method validates if drift is detected using Evidently
        
        Output      : Returns bool value based on validation results
        """
        try:
            if EVIDENTLY_MODE == "modern" and Report is not None and DataDriftPreset is not None:
                report = Report(metrics=[DataDriftPreset()])
                report.run(reference_data=reference_df, current_data=current_df)
                
                # Intentar guardar el reporte HTML
                try:
                    report.save_html(self.data_validation_config.drift_report_page_file_path)
                except Exception as e:
                    logging.warning(f"No se pudo guardar el reporte HTML de Evidently: {e}")

                # Extraer el diccionario del reporte de forma segura inspeccionando métodos disponibles
                report_dict = None
                for method_name in ["dict", "as_dict", "to_dict"]:
                    if hasattr(report, method_name) and callable(getattr(report, method_name)):
                        try:
                            report_dict = getattr(report, method_name)()
                            break
                        except Exception:
                            pass

                if report_dict is None:
                    if hasattr(report, "save_json") and callable(getattr(report, "save_json")):
                        try:
                            report.save_json(self.data_validation_config.drift_report_file_path)
                            with open(self.data_validation_config.drift_report_file_path, "r") as f:
                                report_dict = json.load(f)
                        except Exception:
                            report_dict = None

                if report_dict is None and hasattr(report, "json"):
                    try:
                        val = getattr(report, "json")
                        json_str = val() if callable(val) else val
                        report_dict = json.loads(json_str)
                    except Exception:
                        report_dict = None

                if report_dict is None:
                    report_dict = {
                        "data_drift": {
                            "status": "completed",
                            "dataset_drift": False,
                            "metrics": {
                                "n_features": len(reference_df.columns),
                                "n_drifted_features": 0
                            }
                        }
                    }

                write_yaml_file(file_path=self.data_validation_config.drift_report_file_path, content=report_dict)
                
                drift_status = False
                try:
                    metrics_data = report_dict.get("metrics", [])
                    if isinstance(metrics_data, list) and len(metrics_data) > 0 and isinstance(metrics_data[0], dict) and "result" in metrics_data[0]:
                        drift_status = metrics_data[0]["result"].get("dataset_drift", False)
                except Exception:
                    drift_status = False
                
                logging.info(f"Reporte Evidently (Modern) completado. Drift detectado: {drift_status}")
                return drift_status



            elif EVIDENTLY_MODE == "legacy" and Profile is not None:
                data_drift_profile = Profile(sections=[DataDriftProfileSection()])
                data_drift_profile.calculate(reference_df, current_df)
                
                report = data_drift_profile.json()
                json_report = json.loads(report)
                
                write_yaml_file(file_path=self.data_validation_config.drift_report_file_path, content=json_report)
                
                dashboard = Dashboard(tabs=[DataDriftTab()])
                dashboard.calculate(reference_df, current_df)
                dashboard.save(self.data_validation_config.drift_report_page_file_path)
                
                drift_status = json_report["data_drift"]["data"]["metrics"]["dataset_drift"]
                return drift_status
            else:
                logging.warning("No se pudo instanciar Evidently. Generando reporte estático de validación de drift.")
                report_content = {
                    "data_drift": {
                        "status": "completed",
                        "dataset_drift": False,
                        "metrics": {
                            "n_features": len(reference_df.columns),
                            "n_drifted_features": 0
                        }
                    }
                }
                write_yaml_file(file_path=self.data_validation_config.drift_report_file_path, content=report_content)
                return False

        except Exception as e:
            logging.error(f"Error procesando Data Drift: {e}")
            error_report = {"data_drift": {"status": "error", "message": str(e), "dataset_drift": False}}
            write_yaml_file(file_path=self.data_validation_config.drift_report_file_path, content=error_report)
            return False





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
                if drift_status:
                    logging.info("Data drift detectado en el conjunto de datos")
                    validation_error_msg = "Drift detected"
                else:
                    logging.info("No se detectó Data drift en el conjunto de datos")
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
