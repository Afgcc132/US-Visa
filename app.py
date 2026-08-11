import os
import sys
from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response, JSONResponse
from fastapi.templating import Jinja2Templates
from uvicorn import run as app_run

from usvisa.logger import logging
from usvisa.exception import USVisaException
from usvisa.pipeline.training_pipeline import TrainingPipeline
from usvisa.pipeline.prediction_pipeline import PredictionPipeline, USVisaData

app = FastAPI(
    title="US Visa Approval Prediction API",
    description="API y Servidor Web de MLOps para predecir la aprobación de Visas de EE. UU. usando modelos en AWS S3."
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar motor de plantillas HTML (Jinja2)
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Renderiza la interfaz gráfica interactiva del formulario de predicción de visa.
    """
    return templates.TemplateResponse("usvisa.html", {"request": request, "context": None})


@app.get("/train")
async def train_route():
    """
    Endpoint para disparar el flujo completo del Training Pipeline.
    """
    try:
        logging.info("Iniciando ejecución del Training Pipeline desde la API web...")
        train_pipeline = TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("¡El entrenamiento del pipeline se completó con éxito! El modelo actualizado se ha evaluado y promovido en AWS S3.")
    except Exception as e:
        raise USVisaException(e, sys) from e


@app.post("/", response_class=HTMLResponse)
async def predict_route(
    request: Request,
    continent: str = Form(...),
    education_of_employee: str = Form(...),
    has_job_experience: str = Form(...),
    requires_job_training: str = Form(...),
    no_of_employees: int = Form(...),
    yr_of_estab: int = Form(...),
    region_of_employment: str = Form(...),
    prevailing_wage: float = Form(...),
    unit_of_wage: str = Form(...),
    full_time_position: str = Form(...),
):
    """
    Procesa las entradas del formulario web, invoca el PredictionPipeline
    y muestra el resultado en la interfaz gráfica HTML.
    """
    try:
        usvisa_data = USVisaData(
            continent=continent,
            education_of_employee=education_of_employee,
            has_job_experience=has_job_experience,
            requires_job_training=requires_job_training,
            no_of_employees=no_of_employees,
            yr_of_estab=yr_of_estab,
            region_of_employment=region_of_employment,
            prevailing_wage=prevailing_wage,
            unit_of_wage=unit_of_wage,
            full_time_position=full_time_position,
        )

        usvisa_df = usvisa_data.get_usvisa_input_data_frame()
        prediction_pipeline = PredictionPipeline()
        value = prediction_pipeline.predict(dataframe=usvisa_df)

        status = "Visa Aprobada (Certified)" if value[0] == 1 else "Visa Denegada (Denied)"
        is_certified = (value[0] == 1)

        context = {
            "result": status,
            "is_certified": is_certified,
            "inputs": {
                "continent": continent,
                "education_of_employee": education_of_employee,
                "has_job_experience": has_job_experience,
                "requires_job_training": requires_job_training,
                "no_of_employees": no_of_employees,
                "yr_of_estab": yr_of_estab,
                "region_of_employment": region_of_employment,
                "prevailing_wage": prevailing_wage,
                "unit_of_wage": unit_of_wage,
                "full_time_position": full_time_position,
            }
        }

        return templates.TemplateResponse("usvisa.html", {"request": request, "context": context})

    except Exception as e:
        logging.error(f"Error procesando la predicción en la web: {e}")
        error_context = {"error": str(e)}
        return templates.TemplateResponse("usvisa.html", {"request": request, "context": error_context})


if __name__ == "__main__":
    app_run(app, host="0.0.0.0", port=8080)
