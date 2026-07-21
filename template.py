import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s')
 
project_name = "usvisa"

list_of_files = [

 f"{project_name}/__init__.py",
 f"{project_name}/utils/__init__.py",
 f"{project_name}/utils/common.py",
 f"{project_name}/components/data_ingestion.py",
 f"{project_name}/components/data_transformation.py",
 f"{project_name}/components/data_validation.py",
 f"{project_name}/components/model_training.py",
 f"{project_name}/components/model_evaluation.py",
 f"{project_name}/components/model_deployment.py",
 f"{project_name}/components/model_monitoring.py",
 f"{project_name}/components/model_registry.py",
 f"{project_name}/components/model_versioning.py",
 f"{project_name}/components/model_pipeline.py",
 f"{project_name}/components/model_pipeline_test.py",
 f"{project_name}/components/model_pipeline_test.py",
 f"{project_name}/configuration/__init__.py",
 f"{project_name}/constants/__init__.py",
 f"{project_name}/entity/__init__.py",
 f"{project_name}/entity/config_entity.py",
 f"{project_name}/entity/artifact_entity.py",
 f"{project_name}/exception/__init__.py",
 f"{project_name}/logger/__init__.py",
 f"{project_name}/pipeline/__init__.py",
 f"{project_name}/pipeline/training_pipeline.py",
 f"{project_name}/pipeline/prediction_pipeline.py",
 f"{project_name}/utils/__init__.py",
 f"{project_name}/utils/main_utils.py"]

for filepath in list_of_files:
     filedir = Path(filepath)   
     filder, filename = os.path.split(filepath)
     if filder !="":
         os.makedirs(filder,exist_ok=True)
     if (not os.path.exists(filepath)) or (os.path.getsize(filepath)==0):     
        with open(filedir, 'w') as f:
             pass 
     else:
        logging.info("file allready present at : {filepath}")   
     



    
