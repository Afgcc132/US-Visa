import sys
import os
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder, PowerTransformer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

from usvisa.constants import *
from usvisa.exception import USVisaException
from usvisa.logger import logging
from usvisa.entity.config_entity import DataTransformationConfig
from usvisa.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact, DataTransformationArtifact
from usvisa.utils.main_utils import read_yaml_file, save_numpy_array, save_object


class DataTransformation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact,
                 data_transformation_config: DataTransformationConfig,
                 data_validation_artifact: DataValidationArtifact):
        """
        Componente para la transformación de datos.
        """
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_transformation_config = data_transformation_config
            self.data_validation_artifact = data_validation_artifact
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise USVisaException(e, sys)

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        """
        Lee un archivo CSV y retorna un DataFrame de Pandas.
        """
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise USVisaException(e, sys)

    def get_data_transformer_object(self) -> ColumnTransformer:
        """
        Crea y retorna un objeto ColumnTransformer para transformar las columnas categóricas y numéricas.
        """
        try:
            logging.info("Iniciando creación del objeto preprocesador")
            
            # Obtener las columnas desde el esquema yaml
            oh_columns = self._schema_config["oh_columns"]
            or_columns = self._schema_config["or_columns"]
            transform_columns = self._schema_config["transform_columns"]
            num_features = self._schema_config["num_features"]

            # Definir pipelines de transformación
            transform_pipe = Pipeline(steps=[
                ("transformer", PowerTransformer(method="yeo-johnson"))
            ])
            
            ordinal_pipe = Pipeline(steps=[
                ("ordinal_encoder", OrdinalEncoder())
            ])
            
            one_hot_pipe = Pipeline(steps=[
                ("one_hot_encoder", OneHotEncoder()),
                ("scaler", StandardScaler(with_mean=False))
            ])
            
            scaler_pipe = Pipeline(steps=[
                ("scaler", StandardScaler())
            ])

            # Ensamblar el ColumnTransformer
            preprocessor = ColumnTransformer(
                transformers=[
                    ("OneHotEncoder", one_hot_pipe, oh_columns),
                    ("OrdinalEncoder", ordinal_pipe, or_columns),
                    ("Transformer", transform_pipe, transform_columns),
                    ("StandardScaler", scaler_pipe, num_features)
                ]
            )

            logging.info("Objeto preprocesador creado exitosamente")
            return preprocessor

        except Exception as e:
            raise USVisaException(e, sys)

    def initiate_data_transformation(self) -> DataTransformationArtifact:
        """
        Inicia el proceso completo de transformación de datos:
        1. Lee datos de train y test.
        2. Realiza Feature Engineering (ej. calcula la antigüedad de la empresa 'company_age').
        3. Separa variables independientes (X) y dependiente (y).
        4. Aplica el preprocesador y balanceo con SMOTE en train.
        5. Guarda los arrays transformados (.npy) y el objeto preprocesador (.pkl).
        6. Retorna DataTransformationArtifact.
        """
        try:
            if not self.data_validation_artifact.validation_status:
                raise Exception("La validación de datos falló. No se puede proceder con la transformación.")

            logging.info("Iniciando proceso de transformación de datos")
            preprocessor = self.get_data_transformer_object()

            # 1. Cargar datos de train y test desde la etapa de ingesta
            train_df = self.read_data(file_path=self.data_ingestion_artifact.trained_file_path)
            test_df = self.read_data(file_path=self.data_ingestion_artifact.test_file_path)

            logging.info("Lectura de datos completada")

            # 2. Feature Engineering: Calcular la antigüedad de la empresa
            train_df['company_age'] = CURRENT_YEAR - train_df['yr_of_estab']
            test_df['company_age'] = CURRENT_YEAR - test_df['yr_of_estab']

            # Eliminar columnas no necesarias (drop_columns especificados en el schema)
            drop_cols = self._schema_config['drop_columns']
            logging.info(f"Eliminando columnas no necesarias: {drop_cols}")
            train_df = train_df.drop(columns=drop_cols, axis=1)
            test_df = test_df.drop(columns=drop_cols, axis=1)

            # 3. Separar características de entrada (X) y variable objetivo (y)
            input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_train_df = np.where(train_df[TARGET_COLUMN] == 'Certified', 1, 0)

            input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_test_df = np.where(test_df[TARGET_COLUMN] == 'Certified', 1, 0)

            # 4. Aplicar el preprocesador
            logging.info("Aplicando transformaciones al conjunto de datos de entrenamiento y prueba")
            input_feature_train_arr = preprocessor.fit_transform(input_feature_train_df)
            input_feature_test_arr = preprocessor.transform(input_feature_test_df)

            # Application of SMOTE for handling imbalanced dataset on train
            logging.info("Aplicando SMOTE para balancear las clases en el conjunto de entrenamiento")
            smt = SMOTE()
            input_feature_train_final, target_feature_train_final = smt.fit_resample(
                input_feature_train_arr, target_feature_train_df
            )

            # Combinar features y target en un único arreglo de NumPy para train y test
            train_arr = np.c_[input_feature_train_final, target_feature_train_final]
            test_arr = np.c_[input_feature_test_arr, target_feature_test_df]

            # 5. Guardar los archivos resultantes (.npy y .pkl)
            logging.info("Guardando arreglos transformados y objeto preprocesador")
            save_numpy_array(
                file_path=self.data_transformation_config.transformed_train_file_path,
                array=train_arr
            )
            save_numpy_array(
                file_path=self.data_transformation_config.transformed_test_file_path,
                array=test_arr
            )
            save_object(
                file_path=self.data_transformation_config.transformed_object_file_path,
                obj=preprocessor
            )

            logging.info("Transformación de datos completada exitosamente")

            # 6. Retornar el artefacto de transformación de datos
            data_transformation_artifact = DataTransformationArtifact(
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path,
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path
            )

            return data_transformation_artifact

        except Exception as e:
            raise USVisaException(e, sys)
