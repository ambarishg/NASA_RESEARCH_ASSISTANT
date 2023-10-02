import pandas as pd
from config import *
from sentence_transformers import SentenceTransformer
import uuid

import qdrant_client as qc
import qdrant_client.http.models as qmodels
from qdrant_client.http.models import *

FILE_PATH = 'NTRS80K.csv'

ntrs_data = pd.read_csv(FILE_PATH)
cols =['Number', 'title', 'publisher', 'name', 'abstract', 'created']
ntrs_data = ntrs_data[cols]
ntrs_data["year"]=ntrs_data["created"].apply(lambda x: x.split("-")[0])
ntrs_data["year"]=ntrs_data["year"].apply(lambda x: int(x))
ntrs_data.sort_values(by=['year'], ascending=False,inplace=True)


model = SentenceTransformer(MODEL_NAME)

client = qc.QdrantClient(url=URL)
METRIC = qmodels.Distance.COSINE

Lines = []
counter = 0
payload_list = []
id_list = []

for row in ntrs_data.iterrows():
    Number = str(row[1]["Number"])
    title = str(row[1]["title"])
    publisher = str(row[1]["publisher"])
    name = str(row[1]["name"])
    abstract = str(row[1]["abstract"])
    year = (row[1]["year"])
    id_list.append(str(uuid.uuid4()))
    Lines.append(abstract)
    counter = counter + 1
    payload={
        "Number": Number,
        "title": title,
        "name": name,
        "publisher": publisher,
        "name": name,
        "abstract": abstract,
        "year": year }
    payload_list.append(payload)

    if counter % 200 == 0:
        embeddings_all  = model.encode(Lines)
        client.upsert(
            collection_name=COLLECTION_NAME_NTRS,
            points=qmodels.Batch(
                ids = id_list,
                vectors=embeddings_all.tolist(),
                payloads=payload_list),
        )
        print(f"Inserted {counter} rows")
        Lines = []
        id_list = []
        payload_list = []