import sys
from usvisa.logger import logging
from usvisa.exception import USVisaException
from usvisa.pipeline.prediction_pipeline import PredictionPipeline, USVisaData


def test_single_prediction():
    """
    Script de prueba para realizar una predicción local consultando el modelo almacenado en AWS S3.
    """
    try:
        print("========== Prueba de Predicción de Visa US ==========")
        
        # 1. Crear datos de prueba de un solicitante de visa
        print("\n1. Preparando datos de entrada del solicitante...")
        visa_applicant = USVisaData(
            continent="Asia",
            education_of_employee="Master's",
            has_job_experience="Y",
            requires_job_training="N",
            no_of_employees=150,
            yr_of_estab=2005,
            region_of_employment="West",
            prevailing_wage=85000.0,
            unit_of_wage="Year",
            full_time_position="Y"
        )

        input_df = visa_applicant.get_usvisa_input_data_frame()
        print("Datos del solicitante (DataFrame):")
        print(input_df.T)

        # 2. Ejecutar la predicción consultando S3
        print("\n2. Consultando el modelo en producción (Amazon S3) y prediciendo...")
        pipeline = PredictionPipeline()
        prediction = pipeline.predict(dataframe=input_df)

        result_label = "Visa Aprobada (Certified)" if prediction[0] == 1 else "Visa Denegada (Denied)"
        print("\n========================================================")
        print(f"🎉 RESULTADO DE LA PREDICCIÓN: {result_label} (Valor bruto: {prediction[0]})")
        print("========================================================")

    except Exception as e:
        print(f"\n❌ Error durante la predicción: {e}")
        raise USVisaException(e, sys) from e


if __name__ == "__main__":
    test_single_prediction()
