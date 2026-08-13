FROM python:3.10-slim-bookworm

WORKDIR /app

# Instalar dependencias esenciales del sistema operativo (AWS CLI, compiladores, dependencias de C para Scikit-Learn/LightGBM)
RUN apt-get update -y && apt-get install -y \
    awscli \
    curl \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copiar el código fuente completo del proyecto (necesario para -e . en setup.py)
COPY . /app

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto 8080 para la aplicación web FastAPI
EXPOSE 8080

# Comando por defecto para iniciar el servidor web FastAPI
CMD ["python", "app.py"]
