import pandas as pd
from config import *
from sentence_transformers import SentenceTransformer
import uuid

import qdrant_client as qc
import qdrant_client.http.models as qmodels
from qdrant_client.http.models import *

FILE_PATH = 'COMPUTER_SCIENCE.csv'

if FILE_PATH == 'COMPUTER_SCIENCE.csv':
    CATEGORY = 'Computer Science'
elif FILE_PATH == 'QuantitativeBiology.csv':
    CATEGORY = 'Quantitative Biology'

influential_papers = pd.read_csv(FILE_PATH)
cols =['id','references','title','authors','journal-ref','year']
ntrs_data = influential_papers[cols]

model = SentenceTransformer(MODEL_NAME)

client = qc.QdrantClient(url=URL)
METRIC = qmodels.Distance.COSINE

Lines = []
counter = 0
payload_list = []
id_list = []

for row in ntrs_data.iterrows():
    id = str(row[1]["id"])
    references = str(row[1]["references"])
    title = str(row[1]["title"])
    journal_ref = str(row[1]["journal-ref"])
    year = int(row[1]["year"])
    authors = str(row[1]["authors"])
    id_list.append(str(uuid.uuid4()))
    category_influential = CATEGORY
    Lines.append(title)
    payload={
        "id": id,
        "title": title,
        "references": references,
        "journal_ref": journal_ref,
        "year": year ,
        "category": category_influential,
        "authors": authors}
    payload_list.append(payload)
embeddings_all  = model.encode(Lines)
client.upsert(
    collection_name=COLLECTION_NAME_INFLUENTIAL,
    points=qmodels.Batch(
        ids = id_list,
        vectors=embeddings_all.tolist(),
        payloads=payload_list),
)
print(f"Insertion of ROWS successfully done for {FILE_PATH}")