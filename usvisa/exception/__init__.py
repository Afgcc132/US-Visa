import sys

def error_message_detail(error, error_detail: sys):
    """
    Función auxilar para extraer información detallada del error:
    - Nombre del archivo donde ocurrió.
    - Número de línea exacto.
    - Mensaje del error original.
    """
    _, _, exc_tb = error_detail.exc_info()
    file_name = exc_tb.tb_frame.f_code.co_filename
    line_number = exc_tb.tb_lineno
    error_message = (
        f"Error en el script de python [{file_name}] "
        f"línea [{line_number}] "
        f"mensaje de error [{str(error)}]"
    )
    return error_message


class USVisaException(Exception):
    def __init__(self, error_message, error_detail: sys):
        """
        :param error_message: mensaje de error o excepción capturada
        :param error_detail: módulo 'sys' de python
        """
        super().__init__(error_message)
        self.error_message = error_message_detail(
            error_message, error_detail=error_detail
        )

    def __str__(self):
        return self.error_message
