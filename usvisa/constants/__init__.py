import os
import sys
from datetime import date

DATABASE_NAME = 'usvisa'
COLLECTION_NAME = 'visa_data'
MONGODB_URL_KEY = 'mongodb+srv://afgcc132_db_user:EBmg5X3VKtwEhB7c@cluster0.zv2f9bv.mongodb.net/?appName=Cluster0'
PIPELINE_NAME = 'usvisa'
ARTIFACT_DIR = 'artifact'
FILE_NAME = 'usvisa.csv'

MODEL_FILE_NAME = 'model.pkl'
DATA_FILE_NAME = 'usvisa.csv'
TRAIN_FILE_NAME = 'train.csv'
TEST_FILE_NAME = 'test.csv'
PREPROCESSING_OBJECT_FILE_NAME = 'preprocessing.pkl'

# AWS Credenciales leídas desde variables de entorno (Cumplimiento de seguridad con GitHub)
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-2")

## DATA INGESTION CONSTANTS
DATA_INGESTION_COLLECTION_NAME = 'visa_data'
DATA_INGESTION_DIR_NAME = 'data_ingestion'
DATA_INGESTION_FEATURE_STORE_DIR = 'feature_store'
DATA_INGESTION_INGESTED_DIR = 'ingested'
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO = 0.2

## DATA VALIDATION CONSTANTS
DATA_VALIDATION_DIR_NAME = 'data_validation'
DATA_VALIDATION_VALID_DIR = 'validated'
DATA_VALIDATION_INVALID_DIR = 'invalid'
DATA_VALIDATION_DRIFT_REPORT_DIR = 'drift_report'
DATA_VALIDATION_STATUS_FILE = 'status.txt'
DATA_VALIDATION_BASE_SCHEMA_FILE_PATH = "config/schema.yaml"
SCHEMA_FILE_PATH = os.path.join("config", "schema.yaml")
DATA_VALIDATION_DRIFT_REPORT_FILE_NAME = "drift_report.yaml"
DATA_VALIDATION_DRIFT_REPORT_PAGE_FILE_NAME = "drift_report.html"

## DATA TRANSFORMATION CONSTANTS
DATA_TRANSFORMATION_DIR_NAME = 'data_transformation'
DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR = 'transformed'
DATA_TRANSFORMATION_TRANSFORMED_OBJECT_DIR = 'transformed_object'

TARGET_COLUMN = 'case_status'
CURRENT_YEAR = date.today().year

## MODEL TRAINING CONSTANTS
MODEL_TRAINER_DIR_NAME = "model_trainer"
MODEL_TRAINER_TRAINED_MODEL_DIR = "trained_model"
MODEL_TRAINER_TRAINED_MODEL_NAME = "model.pkl"
MODEL_TRAINER_EXPECTED_MODEL_ACCURACY = 0.7
MODEL_TRAINER_MODEL_CONFIG_FILE_PATH = os.path.join("config", "model.yaml")

## MODEL EVALUATION CONSTANTS
MODEL_EVALUATION_CHANGED_THRESHOLD_SCORE = 0.02
MODEL_BUCKET_NAME = 'usvisa-model-afgcc'
MODEL_PUSHER_S3_KEY = 'model-registry'
