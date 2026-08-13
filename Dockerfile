FROM python:3.10-slim-buster

WORKDIR /app

# Instalar dependencias esenciales del sistema operativo (AWS CLI, compiladores, dependencias de C para Scikit-Learn/LightGBM)
RUN apt-get update -y && apt-get install -y \
    awscli \
    curl \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente completo del proyecto
COPY . /app

# Exponer el puerto 8080 para la aplicación web FastAPI
EXPOSE 8080

# Comando por defecto para iniciar el servidor web FastAPI
CMD ["python", "app.py"]
