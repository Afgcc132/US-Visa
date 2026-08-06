import os
import sys
import yaml
import dill
import numpy as np
import pandas as pd

from usvisa.logger import logging
from usvisa.exception import USVisaException


def read_yaml_file(file_path: str) -> dict:
    """Lee un archivo YAML y retorna su contenido como un diccionario de Python"""
    try:
        with open(file_path, "rb") as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise USVisaException(e, sys) from e


def write_yaml_file(file_path: str, content: object, replace: bool = False) -> None:
    """Escribe un objeto/diccionario en un archivo YAML"""
    try:
        if replace:
            if os.path.exists(file_path):
                os.remove(file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as file:
            yaml.dump(content, file)
    except Exception as e:
        raise USVisaException(e, sys) from e


def save_object(file_path: str, obj: object) -> None:
    """Guarda un objeto de Python (.pkl) usando dill"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as file_obj:
            dill.dump(obj, file_obj)
    except Exception as e:
        raise USVisaException(e, sys) from e


def load_object(file_path: str) -> object:
    """Carga un objeto (.pkl) guardado previamente con dill"""
    try:
        if not os.path.exists(file_path):
            raise Exception(f"El archivo {file_path} no existe.")
        with open(file_path, "rb") as file_obj:
            return dill.load(file_obj)
    except Exception as e:
        raise USVisaException(e, sys) from e


def save_numpy_array(file_path: str, array: np.ndarray) -> None:
    """Guarda un array de NumPy (.npy)"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        np.save(file_path, array)
    except Exception as e:
        raise USVisaException(e, sys) from e


def load_numpy_array_data(file_path: str) -> np.ndarray:
    """Carga un array de NumPy (.npy) desde una ruta dada"""
    try:
        with open(file_path, "rb") as file_obj:
            return np.load(file_obj)
    except Exception as e:
        raise USVisaException(e, sys) from e



def save_data_frame(file_path: str, df: pd.DataFrame) -> None:
    """Guarda un DataFrame de Pandas (.csv)"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df.to_csv(file_path, index=False)
    except Exception as e:
        raise USVisaException(e, sys) from e    
