import sys
from usvisa.logger import logging
from usvisa.exception import USVisaException

if __name__ == "__main__":
    try:
        logging.info("Probando el logger y la excepción personalizada...")
        a = 1 / 0  # Esto provocará una división por cero
    except Exception as e:
        logging.info("Ocurrió un error. Lanzando USVisaException...")
        raise USVisaException(e, sys) from e


