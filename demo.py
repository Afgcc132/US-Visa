import sys
from usvisa.logger import logging
from usvisa.exception import USVisaException
from usvisa.pipeline.training_pipeline import TrainingPipeline

if __name__ == "__main__":
    try:
        logging.info("Ejecutando demo.py para probar la ingesta de datos...")
        pipeline = TrainingPipeline()
        pipeline.run_pipeline()
        print("¡Pipeline ejecutado con éxito! Revisa la carpeta 'artifact/' para ver los archivos generados.")
    except Exception as e:
        logging.error(f"Error durante la ejecución del pipeline: {e}")
        raise USVisaException(e, sys) from e
