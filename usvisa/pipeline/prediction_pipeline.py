import sys
import pandas as pd
from pandas import DataFrame

from usvisa.logger import logging
from usvisa.exception import USVisaException
from usvisa.entity.config_entity import ModelEvaluationConfig
from usvisa.entity.s3_estimator import USVisaEstimator
from usvisa.constants import CURRENT_YEAR


class PredictionPipeline:
    """
    Pipeline para realizar predicciones utilizando el modelo en producción almacenado en Amazon S3.
    """

    def __init__(self):
        try:
            self.model_evaluation_config = ModelEvaluationConfig()
        except Exception as e:
            raise USVisaException(e, sys) from e

    def predict(self, dataframe: DataFrame):
        """
        Descarga/Carga el modelo desde Amazon S3 (si no está cargado) y ejecuta la predicción.
        """
        try:
            logging.info("========== Iniciando Prediction Pipeline ==========")
            s3_estimator = USVisaEstimator(
                bucket_name=self.model_evaluation_config.bucket_name,
                s3_key=self.model_evaluation_config.s3_model_key_path
            )

            results = s3_estimator.predict(dataframe=dataframe)
            logging.info("========== Predicción completada con éxito ==========")
            return results
        except Exception as e:
            raise USVisaException(e, sys) from e


class USVisaData:
    """
    Clase contenedora para mapear y estructurar datos de entrada de solicitudes de visa
    hacia un DataFrame compatible con el pipeline de transformación y predicción.
    """

    def __init__(
        self,
        continent: str,
        education_of_employee: str,
        has_job_experience: str,
        requires_job_training: str,
        no_of_employees: int,
        yr_of_estab: int,
        region_of_employment: str,
        prevailing_wage: float,
        unit_of_wage: str,
        full_time_position: str,
        company_age: int = None
    ):
        try:
            self.continent = continent
            self.education_of_employee = education_of_employee
            self.has_job_experience = has_job_experience
            self.requires_job_training = requires_job_training
            self.no_of_employees = no_of_employees
            self.yr_of_estab = yr_of_estab
            self.region_of_employment = region_of_employment
            self.prevailing_wage = prevailing_wage
            self.unit_of_wage = unit_of_wage
            self.full_time_position = full_time_position
            self.company_age = company_age if company_age is not None else (CURRENT_YEAR - yr_of_estab)
        except Exception as e:
            raise USVisaException(e, sys) from e

    def get_usvisa_input_data_frame(self) -> DataFrame:
        """
        Convierte los atributos de la instancia en un DataFrame de pandas de una fila.
        """
        try:
            input_dict = self.get_usvisa_data_as_dict()
            return DataFrame(input_dict)
        except Exception as e:
            raise USVisaException(e, sys) from e

    def get_usvisa_data_as_dict(self) -> dict:
        """
        Retorna los atributos como un diccionario con los nombres exactos de las columnas.
        """
        try:
            input_data = {
                "continent": [self.continent],
                "education_of_employee": [self.education_of_employee],
                "has_job_experience": [self.has_job_experience],
                "requires_job_training": [self.requires_job_training],
                "no_of_employees": [self.no_of_employees],
                "yr_of_estab": [self.yr_of_estab],
                "region_of_employment": [self.region_of_employment],
                "prevailing_wage": [self.prevailing_wage],
                "unit_of_wage": [self.unit_of_wage],
                "full_time_position": [self.full_time_position],
                "company_age": [self.company_age],
            }
            return input_data
        except Exception as e:
            raise USVisaException(e, sys) from e
