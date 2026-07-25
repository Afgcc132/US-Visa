import os
import logging
from datetime import datetime

# Nombre de archivo único con fecha y hora exacta
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

# Carpeta donde se almacenarán los logs (usa la raíz actual del proyecto)
log_dir = "logs"
logs_path = os.path.join(os.getcwd(), log_dir)
os.makedirs(logs_path, exist_ok=True)

# Ruta completa del archivo de log
LOG_FILE_PATH = os.path.join(logs_path, LOG_FILE)

# Configuración principal de logging
logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
