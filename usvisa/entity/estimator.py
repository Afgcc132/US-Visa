import sys
from pandas import DataFrame
from usvisa.exception import USVisaException


class USVisaModel:
    def __init__(self, preprocessing_object: object, trained_model_object: object):
        """
        Clase contenedora para el objeto preprocesador y el modelo de machine learning entrenado.
        """
        self.preprocessing_object = preprocessing_object
        self.trained_model_object = trained_model_object

    def predict(self, dataframe: DataFrame):
        """
        Recibe un DataFrame con datos sin transformar, aplica el preprocesamiento
        y realiza las predicciones usando el modelo entrenado.
        """
        try:
            transformed_feature = self.preprocessing_object.transform(dataframe)
            return self.trained_model_object.predict(transformed_feature)
        except Exception as e:
            raise USVisaException(e, sys) from e

    def __repr__(self):
        return f"{type(self.trained_model_object).__name__()}"

    def __str__(self):
        return f"{type(self.trained_model_object).__name__()}"
