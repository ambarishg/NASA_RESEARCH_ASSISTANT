from dotenv import load_dotenv
import os

load_dotenv()

MODEL_NAME=os.getenv("MODEL_NAME")
URL =os.getenv("URL")
# Qdrant dimension of the collection
DIMENSION = os.getenv("DIMENSION")
# Qdrant collection name
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
COLLECTION_NAME_NTRS = os.getenv("COLLECTION_NAME_NTRS")
COLLECTION_NAME_INFLUENTIAL = os.getenv("COLLECTION_NAME_INFLUENTIAL")
METRIC_NAME = os.getenv("METRIC_NAME")
NO_OF_RESULTS = os.getenv("NO_OF_RESULTS")
# Path to save the uploaded files
SAVED_FOLDER = os.getenv("SAVED_FOLDER")
DOCUMENTS_COLLECTION_NAME = os.getenv("DOCUMENTS_COLLECTION_NAME")
DOCUMENTS_COLLECTION_NAME_METADATA = os.getenv("DOCUMENTS_COLLECTION_NAME_METADATA")
key=os.getenv("key")
location=os.getenv("location")
endpoint=os.getenv("endpoint")
deployment_id_gpt4=os.getenv("deployment_id_gpt4")
