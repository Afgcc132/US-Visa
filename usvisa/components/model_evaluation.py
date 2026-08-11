import sys
import numpy as np
import pandas as pd
from typing import Optional
from sklearn.metrics import f1_score

from usvisa.logger import logging
from usvisa.exception import USVisaException
from usvisa.entity.config_entity import ModelEvaluationConfig
from usvisa.entity.artifact_entity import (
    DataIngestionArtifact,
    DataTransformationArtifact,
    ModelTrainerArtifact,
    ModelEvaluationArtifact
)
from usvisa.entity.s3_estimator import USVisaEstimator
from usvisa.utils.main_utils import load_numpy_array_data, load_object


class ModelEvaluation:
    """
    Componente para la evaluación comparativa entre el nuevo modelo entrenado 
    y el modelo de producción almacenado en Amazon S3.
    """

    def __init__(
        self,
        model_evaluation_config: ModelEvaluationConfig,
        data_ingestion_artifact: DataIngestionArtifact,
        data_transformation_artifact: DataTransformationArtifact,
        model_trainer_artifact: ModelTrainerArtifact
    ):
        try:
            self.model_evaluation_config = model_evaluation_config
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_transformation_artifact = data_transformation_artifact
            self.model_trainer_artifact = model_trainer_artifact
        except Exception as e:
            raise USVisaException(e, sys) from e

    def get_best_model(self) -> Optional[USVisaEstimator]:
        """
        Verifica si existe un modelo en el bucket de S3 y retorna su instancia USVisaEstimator.
        """
        try:
            bucket_name = self.model_evaluation_config.bucket_name
            s3_model_key_path = self.model_evaluation_config.s3_model_key_path

            s3_estimator = USVisaEstimator(
                bucket_name=bucket_name,
                s3_key=s3_model_key_path
            )

            if s3_estimator.is_model_present():
                return s3_estimator
            return None
        except Exception as e:
            logging.warning(f"No se pudo consultar la presencia del modelo en S3: {e}")
            return None

    def evaluate_model(self) -> ModelEvaluationArtifact:
        """
        Evalúa el modelo recién entrenado frente al modelo actualmente desplegado en S3.
        Compara las métricas de rendimiento en el conjunto de prueba.
        """
        try:
            logging.info("========== Evaluando rendimiento del nuevo modelo vs modelo S3 ==========")

            # 1. Cargar datos de prueba transformados
            test_file_path = self.data_transformation_artifact.transformed_test_file_path
            test_array = load_numpy_array_data(test_file_path)

            X_test, y_test = test_array[:, :-1], test_array[:, -1]

            # 2. Cargar el modelo recién entrenado
            trained_model_path = self.model_trainer_artifact.trained_model_file_path
            trained_model = load_object(file_path=trained_model_path)

            # Calcular la métrica F1 del nuevo modelo
            trained_model_y_pred = trained_model.trained_model_object.predict(X_test)
            trained_model_f1 = f1_score(y_test, trained_model_y_pred)
            logging.info(f"F1 Score del modelo recién entrenado: {trained_model_f1:.4f}")

            # 3. Intentar obtener el modelo actualmente desplegado en S3
            s3_estimator = self.get_best_model()

            is_model_accepted = False
            changed_accuracy = 0.0

            if s3_estimator is None:
                # No existe modelo en S3: El nuevo modelo se acepta automáticamente
                is_model_accepted = True
                changed_accuracy = trained_model_f1
                logging.info("No se encontró ningún modelo previo en S3. El nuevo modelo es aceptado automáticamente como modelo de producción.")
            else:
                # Cargar el modelo existente en S3
                s3_model = s3_estimator.load_model()
                s3_model_y_pred = s3_model.trained_model_object.predict(X_test)
                s3_model_f1 = f1_score(y_test, s3_model_y_pred)
                logging.info(f"F1 Score del modelo existente en S3: {s3_model_f1:.4f}")

                # Calcular la diferencia de rendimiento
                changed_accuracy = trained_model_f1 - s3_model_f1
                threshold = self.model_evaluation_config.changed_threshold_score

                if changed_accuracy > threshold:
                    is_model_accepted = True
                    logging.info(
                        f"El nuevo modelo supera al modelo en S3. "
                        f"Mejora: {changed_accuracy:.4f} (Umbral requerido: {threshold})"
                    )
                else:
                    is_model_accepted = False
                    logging.info(
                        f"El nuevo modelo NO supera al modelo en S3. "
                        f"Diferencia: {changed_accuracy:.4f} (Umbral requerido: {threshold})"
                    )

            model_evaluation_artifact = ModelEvaluationArtifact(
                is_model_accepted=is_model_accepted,
                changed_accuracy=float(changed_accuracy),
                s3_model_path=self.model_evaluation_config.s3_model_key_path,
                base_model_path=trained_model_path
            )

            logging.info(f"Artefacto de evaluación de modelo creado: {model_evaluation_artifact}")
            return model_evaluation_artifact

        except Exception as e:
            raise USVisaException(e, sys) from e

    def initiate_model_evaluation(self) -> ModelEvaluationArtifact:
        """
        Punto de entrada principal para ejecutar el componente de evaluación del modelo.
        """
        try:
            logging.info("========== Iniciando Componente: Model Evaluation ==========")
            model_evaluation_artifact = self.evaluate_model()
            logging.info("========== Componente Model Evaluation completado ==========")
            return model_evaluation_artifact
        except Exception as e:
            raise USVisaException(e, sys) from e
