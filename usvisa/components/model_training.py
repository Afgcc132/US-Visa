import os
import sys
import importlib
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any

from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score
from sklearn.model_selection import cross_val_score

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

import optuna

from usvisa.logger import logging
from usvisa.exception import USVisaException
from usvisa.entity.config_entity import ModelTrainerConfig
from usvisa.entity.artifact_entity import DataTransformationArtifact, ModelTrainerArtifact, ClassificationMetricArtifact
from usvisa.entity.estimator import USVisaModel
from usvisa.utils.main_utils import load_numpy_array_data, load_object, save_object, read_yaml_file

# Reducir verbosidad de Optuna a advertencias
optuna.logging.set_verbosity(optuna.logging.WARNING)


class ModelTrainer:
    def __init__(self, data_transformation_artifact: DataTransformationArtifact,
                 model_trainer_config: ModelTrainerConfig):
        """
        Componente para el entrenamiento del modelo y optimización de hiperparámetros con Optuna.
        """
        try:
            self.data_transformation_artifact = data_transformation_artifact
            self.model_trainer_config = model_trainer_config
        except Exception as e:
            raise USVisaException(e, sys) from e

    def _get_models_and_params_from_yaml(self, config_dict: dict) -> Tuple[Dict[str, Any], Dict[str, dict]]:
        """
        Carga de forma dinámica los modelos e hiperparámetros desde el diccionario del archivo YAML.
        """
        try:
            models = {}
            params = {}
            model_selection = config_dict.get("model_selection", {})

            for module_key, module_info in model_selection.items():
                class_name = module_info["class"]
                module_name = module_info["module"]
                param_grid = module_info.get("params", {})

                # Importar dinámicamente la clase del modelo
                imported_module = importlib.import_module(module_name)
                model_class = getattr(imported_module, class_name)
                
                model_instance = model_class()
                models[class_name] = model_instance
                params[class_name] = param_grid

            return models, params
        except Exception as e:
            raise USVisaException(e, sys) from e

    def _get_default_models_and_params(self) -> Tuple[Dict[str, Any], Dict[str, dict]]:
        """
        Retorna modelos y grillas de parámetros por defecto si no se carga el archivo YAML.
        """
        models = {
            "RandomForestClassifier": RandomForestClassifier(random_state=42),
            "GradientBoostingClassifier": GradientBoostingClassifier(random_state=42),
            "DecisionTreeClassifier": DecisionTreeClassifier(random_state=42),
            "AdaBoostClassifier": AdaBoostClassifier(random_state=42),
            "XGBClassifier": XGBClassifier(random_state=42, eval_metric='logloss')
        }

        params = {
            "RandomForestClassifier": {
                "n_estimators": [50, 100, 150],
                "max_depth": [10, 20, 30]
            },
            "GradientBoostingClassifier": {
                "n_estimators": [50, 100],
                "learning_rate": [0.01, 0.05, 0.1]
            },
            "DecisionTreeClassifier": {
                "criterion": ["gini", "entropy"],
                "max_depth": [5, 10, 15]
            },
            "AdaBoostClassifier": {
                "n_estimators": [50, 100],
                "learning_rate": [0.1, 1.0]
            },
            "XGBClassifier": {
                "n_estimators": [50, 100],
                "max_depth": [3, 5, 8]
            }
        }
        return models, params

    def evaluate_models(self, X_train: np.ndarray, y_train: np.ndarray,
                        X_test: np.ndarray, y_test: np.ndarray,
                        models: dict, params: dict) -> Tuple[Any, ClassificationMetricArtifact, str]:
        """
        Realiza la optimización de hiperparámetros con Optuna para cada modelo,
        evalúa su desempeño en el conjunto de prueba y retorna el mejor modelo.
        """
        try:
            best_model = None
            best_model_name = ""
            best_f1_score = 0.0
            best_metric_artifact = None

            n_trials = 10
            direction = "maximize"
            cv_folds = 3

            if os.path.exists(self.model_trainer_config.model_config_file_path):
                yaml_content = read_yaml_file(self.model_trainer_config.model_config_file_path)
                optuna_config = yaml_content.get("optuna_search", {})
                n_trials = optuna_config.get("n_trials", 10)
                direction = optuna_config.get("direction", "maximize")
                cv_folds = optuna_config.get("cv", 3)

            for model_name, model in models.items():
                param_grid = params.get(model_name, {})
                logging.info(f"Iniciando optimización con Optuna para el modelo: {model_name} (trials={n_trials})")

                def objective(trial):
                    trial_params = {}
                    for p_name, p_values in param_grid.items():
                        if isinstance(p_values, list):
                            trial_params[p_name] = trial.suggest_categorical(p_name, p_values)

                    model_instance = model.__class__(**trial_params)
                    cv_scores = cross_val_score(
                        model_instance,
                        X_train,
                        y_train,
                        cv=cv_folds,
                        scoring='f1_weighted',
                        n_jobs=-1
                    )
                    return cv_scores.mean()

                study = optuna.create_study(direction=direction)
                study.optimize(objective, n_trials=n_trials)

                best_trial_params = study.best_params
                logging.info(f"Mejores parámetros sugeridos por Optuna para {model_name}: {best_trial_params}")

                # Entrenar el modelo óptimo con todos los datos de entrenamiento
                fitted_model = model.__class__(**best_trial_params)
                fitted_model.fit(X_train, y_train)

                # Realizar predicciones en el conjunto de prueba
                y_test_pred = fitted_model.predict(X_test)

                # Calcular métricas de clasificación
                test_f1 = f1_score(y_test, y_test_pred, average='weighted')
                test_precision = precision_score(y_test, y_test_pred, average='weighted', zero_division=0)
                test_recall = recall_score(y_test, y_test_pred, average='weighted', zero_division=0)
                test_acc = accuracy_score(y_test, y_test_pred)

                logging.info(
                    f"Resultados de {model_name} en Test -> Accuracy: {test_acc:.4f}, F1-Score: {test_f1:.4f}, Precision: {test_precision:.4f}, Recall: {test_recall:.4f}"
                )

                if test_f1 > best_f1_score:
                    best_f1_score = test_f1
                    best_model = fitted_model
                    best_model_name = model_name
                    best_metric_artifact = ClassificationMetricArtifact(
                        f1_score=float(test_f1),
                        precision_score=float(test_precision),
                        recall_score=float(test_recall)
                    )

            logging.info(f"Mejor modelo encontrado con Optuna: {best_model_name} con F1-Score de {best_f1_score:.4f}")
            return best_model, best_metric_artifact, best_model_name

        except Exception as e:
            raise USVisaException(e, sys) from e

    def get_model_object_and_report(self, train_array: np.ndarray,
                                   test_array: np.ndarray) -> Tuple[Any, ClassificationMetricArtifact]:
        """
        Separa las variables explicativas y objetivo, obtiene los modelos a evaluar y ejecuta la optimización con Optuna.
        """
        try:
            X_train, y_train = train_array[:, :-1], train_array[:, -1]
            X_test, y_test = test_array[:, :-1], test_array[:, -1]

            # Intentar cargar modelos desde YAML o usar defaults
            if os.path.exists(self.model_trainer_config.model_config_file_path):
                logging.info(f"Cargando configuración de modelos desde: {self.model_trainer_config.model_config_file_path}")
                config_dict = read_yaml_file(self.model_trainer_config.model_config_file_path)
                models, params = self._get_models_and_params_from_yaml(config_dict)
            else:
                logging.info("Archivo model.yaml no encontrado. Usando modelos y parámetros por defecto.")
                models, params = self._get_default_models_and_params()

            best_model, metric_artifact, best_model_name = self.evaluate_models(
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
                models=models,
                params=params
            )

            # Verificar si la precisión cumple con las expectativas mínimas
            X_test_pred = best_model.predict(X_test)
            best_model_accuracy = accuracy_score(y_test, X_test_pred)

            if best_model_accuracy < self.model_trainer_config.expected_accuracy:
                raise Exception(
                    f"El mejor modelo ({best_model_name}) tiene una precisión ({best_model_accuracy:.4f}) "
                    f"inferior a la esperada ({self.model_trainer_config.expected_accuracy})."
                )

            logging.info(f"Modelo {best_model_name} superó el umbral esperado con Accuracy de {best_model_accuracy:.4f}")
            return best_model, metric_artifact

        except Exception as e:
            raise USVisaException(e, sys) from e

    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        """
        Ejecuta el flujo completo de entrenamiento del modelo:
        1. Carga los datos transformados de train y test (.npy).
        2. Carga el objeto preprocesador (.pkl).
        3. Realiza la optimización con Optuna y selecciona el mejor modelo de clasificación.
        4. Empaqueta el preprocesador y el modelo en la clase USVisaModel.
        5. Guarda el modelo final en el directorio de artefactos.
        6. Retorna el artefacto ModelTrainerArtifact.
        """
        try:
            logging.info("========== Iniciando Componente: Model Trainer (Optuna) ==========")

            # 1. Cargar arreglos transformados
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path

            logging.info(f"Cargando datos transformados de entrenamiento: {train_file_path}")
            train_array = load_numpy_array_data(train_file_path)

            logging.info(f"Cargando datos transformados de prueba: {test_file_path}")
            test_array = load_numpy_array_data(test_file_path)

            # 2. Cargar objeto preprocesador
            preprocessing_obj_file_path = self.data_transformation_artifact.transformed_object_file_path
            logging.info(f"Cargando objeto preprocesador desde: {preprocessing_obj_file_path}")
            preprocessing_obj = load_object(file_path=preprocessing_obj_file_path)

            # 3. Entrenar y obtener el mejor modelo
            best_model, metric_artifact = self.get_model_object_and_report(
                train_array=train_array,
                test_array=test_array
            )

            # 4. Empaquetar modelo y preprocesador
            usvisa_model = USVisaModel(
                preprocessing_object=preprocessing_obj,
                trained_model_object=best_model
            )

            # 5. Guardar modelo final (.pkl)
            trained_model_path = self.model_trainer_config.trained_model_file_path
            logging.info(f"Guardando el objeto USVisaModel final en: {trained_model_path}")
            save_object(file_path=trained_model_path, obj=usvisa_model)

            # 6. Construir y retornar el artefacto final
            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path=trained_model_path,
                metric_artifact=metric_artifact
            )
            logging.info(f"Model Trainer completado exitosamente. Artefacto: {model_trainer_artifact}")
            return model_trainer_artifact

        except Exception as e:
            raise USVisaException(e, sys) from e
