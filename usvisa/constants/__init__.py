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
TRAIN_FILE_NAME = 'train.cvs'
TEST_FILE_NAME = 'test.cvs'
PREPROCESSING_OBJECT_FILE_NAME = 'preprocessing.pkl'
##DATA INGESTION CONSTANTS

DATA_INGESTION_COLLECTION_NAME = 'visa_data'
DATA_INGESTION_DIR_NAME = 'data_ingestion'
DATA_INGESTION_FEATURE_STORE_DIR = 'feature_store'
DATA_INGESTION_INGESTED_DIR = 'ingested'
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO = 0.2

##DATA VALIDATION CONSTANTS

DATA_VALIDATION_DIR_NAME = 'data_validation'
DATA_VALIDATION_VALID_DIR = 'validated'
DATA_VALIDATION_INVALID_DIR = 'invalid'
DATA_VALIDATION_DRIFT_REPORT_DIR = 'drift_report'
DATA_VALIDATION_STATUS_FILE = 'status.txt'
DATA_VALIDATION_BASE_SCHEMA_FILE_PATH = "config/schema.yaml"
SCHEMA_FILE_PATH = os.path.join("config", "schema.yaml")
DATA_VALIDATION_DRIFT_REPORT_FILE_NAME = "drift_report.yaml"
DATA_VALIDATION_DRIFT_REPORT_PAGE_FILE_NAME = "drift_report.html"

