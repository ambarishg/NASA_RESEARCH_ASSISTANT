import pandas as pd
from config import *
from sentence_transformers import SentenceTransformer
import uuid

import qdrant_client as qc
import qdrant_client.http.models as qmodels
from qdrant_client.http.models import *

FILE_PATH = 'CV_2022.CSV'
YEAR_VALUE = 2022

arxiv_data = pd.read_csv(FILE_PATH)
cols =['authors', 'title', 'journal-ref', 'doi', 'categories',
       'license', 'abstract', 'year','month', 'authors_parsed']
arxiv_data = arxiv_data[cols]
arxiv_data["year"] = arxiv_data["year"].apply(lambda x: int(x))
arxiv_data_year = arxiv_data[arxiv_data['year'] >= YEAR_VALUE]
arxiv_data_year.sort_values(by=['year'], ascending=False,inplace=True)

model = SentenceTransformer(MODEL_NAME)

client = qc.QdrantClient(url=URL)
METRIC = qmodels.Distance.COSINE

Lines = []
counter = 0
payload_list = []
id_list = []

for row in arxiv_data_year.iterrows():
    authors = row[1]["authors"]
    title = row[1]["title"]
    abstract = row[1]["abstract"]
    journal_ref = str(row[1]["journal-ref"])
    doi = str(row[1]["doi"])
    categories = str(row[1]["categories"])
    year = (row[1]["year"])
    month = (row[1]["month"])
    licenses = str(row[1]["license"])
    id_list.append(str(uuid.uuid4()))
    Lines.append(abstract)
    counter = counter + 1
    payload={
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "journalref": journal_ref,
                "doi": doi,
                "categories": categories,
                "year": year,
                "month": month,
                "licenses": licenses
            }
    payload_list.append(payload)

    if counter % 500 == 0:
        embeddings_all  = model.encode(Lines)
        client.upsert(
            collection_name=COLLECTION_NAME_02,
            points=qmodels.Batch(
                ids = id_list,
                vectors=embeddings_all.tolist(),
                payloads=payload_list),
        )
        print(f"Inserted {counter} rows")
        Lines = []
        id_list = []
        payload_list = []
    
    if counter == 50000:
        break