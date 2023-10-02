from config import *
import qdrant_client as qc
import qdrant_client.http.models as qmodels
from qdrant_client.http.models import *
import pandas as pd
from model_helper import *
from pdf_helper import *
import os
import uuid
from pathlib import Path
from azure_openai_helper import *


client = qc.QdrantClient(url=URL)
METRIC = qmodels.Distance.COSINE




def get_search_results(user_input,
                       author="",
                       year="") -> pd.DataFrame:
    df = pd.DataFrame(columns=['title','authors','year','categories'])
    model = load_model()
    xq = model.encode(user_input,convert_to_tensor=True)
    
    if author != '' and year == '':
        query_filter=qmodels.Filter(
            must= [
                    FieldCondition(
                    key="authors",
                    match=models.MatchText(text=author),
                )
            ],
        )
        print(f"Author : {author}")
    
    if year != '' and author == '':
        year = int(year)
        query_filter=qmodels.Filter(
            must= [
                FieldCondition(
                    key="year",
                    match=models.MatchValue(value=year),
                )
            ],
        )
        print(f"Year : {year}")
    
    if author == '' and year == '':
        query_filter = None
        print("No author and year")
    if author != '' and year != '':
        year = int(year)
        query_filter=qmodels.Filter(
            must= [
                FieldCondition(
                    key="authors",
                    match=models.MatchText(text=author),
                ),
                FieldCondition(
                    key="year",
                    match=models.MatchValue(value=year),
                )
            ],
        )
        print(f"Author : {author} and Year : {year}")
    
    search_result = client.search(collection_name=COLLECTION_NAME,
                                    query_vector=xq.tolist(), 
                                    query_filter=query_filter,
                                    limit=NO_OF_RESULTS)
    number_of_results = len(search_result)
    for i in range(number_of_results):
        df.loc[i] = [search_result[i].payload['title'],
                     search_result[i].payload['authors'],
                     search_result[i].payload['year'],
                     search_result[i].payload['categories']]
    return df

#   Inserting documents into Qdrant
#   FILE_PATH: path to the folder containing the pdf files
#   CATEGORY: category of the documents
def insert_qdrant_doc(FILE_NAME,SHORT_DESC ="",CATEGORY="") -> None:
    model = load_model()
    filename = SAVED_FOLDER +  "/" + FILE_NAME
    print(f'Processing file: {filename}')
    full_doc_text = get_pdf_data(filename)
    print(f'Full doc text length: {len(full_doc_text)}')
    payloads = []
    li_id = []
    corpus = []
    Lines =get_chunks(full_doc_text,500)
    for token in Lines:
        corpus.append(token)
        payloads.append({"token":token,
                        "filename": os.path.basename(filename),
                        "Category":CATEGORY,
                        "type":"pdf"})
        li_id.append(str(uuid.uuid4()))
    embeddings_all = model.encode(corpus, convert_to_tensor=True)
    print(f'Full embeddings length: {len(embeddings_all)}')

    CHUNK_SIZE = 100
    for i in range(0, len(embeddings_all), CHUNK_SIZE):
        if(i+CHUNK_SIZE > len(embeddings_all) -1):
            new_chunk = len(embeddings_all) -1
        else:
            new_chunk = i+CHUNK_SIZE -1
        print("Inserting chunk", i , "to", new_chunk)
        client.upsert(
            collection_name=DOCUMENTS_COLLECTION_NAME,
            points=qmodels.Batch(
                ids = li_id[i:new_chunk],
                vectors=embeddings_all[i:new_chunk].tolist(),
                payloads=payloads[i:new_chunk]
            ),
        )
        
    embedding_file_name = model.encode(SHORT_DESC, convert_to_tensor=True)
    client.upsert(
        collection_name=DOCUMENTS_COLLECTION_NAME_METADATA,
        points=qmodels.Batch(
            ids = [str(uuid.uuid4())],
            vectors=[embedding_file_name.tolist()],
            payloads=[{"SHORT_DESC":SHORT_DESC,
                    "FILENAME": os.path.basename(filename),
                    "CATEGORY":CATEGORY,
                    "type":"pdf"}]
        ))

        

#   Searching documents in Qdrant
#   user_input: user query
#   CATEGORY: category of the documents

def get_search_document_results(user_input, CATEGORY="") -> str:
    model = load_model()
    xq = model.encode(user_input,convert_to_tensor=True)
    if CATEGORY == '':
        query_filter = None
    else:
        query_filter=qmodels.Filter(
            must= [
                FieldCondition(
                    key="Category",
                    match=models.MatchValue(value=CATEGORY),
                )
            ],
        )
    
    search_result = client.search(collection_name=DOCUMENTS_COLLECTION_NAME,
                                    query_vector=xq.tolist(), 
                                    query_filter=query_filter,
                                    limit=3)
    contexts =""
    for result in search_result:
        contexts +=  result.payload['token']+"\n---\n"

    reply = generate_answer_from_context(user_input, contexts)
    return reply

#   Searching documents in Qdrant
#   user_input: user query
#   CATEGORY: category of the documents
def get_search_document_results_chat(user_input, CATEGORY) -> str:
    model = load_model()
    xq = model.encode(user_input,convert_to_tensor=True)
    if CATEGORY == '':
        query_filter = None
    else:
        query_filter=qmodels.Filter(
            must= [
                FieldCondition(
                    key="Category",
                    match=models.MatchValue(value=CATEGORY),
                )
            ],
        )
    search_result = client.search(collection_name=DOCUMENTS_COLLECTION_NAME,
                                    query_vector=xq.tolist(), 
                                    query_filter=query_filter,
                                    limit=3)
    contexts =""
    for result in search_result:
        contexts +=  result.payload['token']+"\n---\n"
    return contexts

# Search documents in Qdrant for NTRS collection
def get_search_results_NTRS(user_input,
                       year="") -> pd.DataFrame:
    
    df = pd.DataFrame(columns=['title', 'publisher', 'name','year'])
    model = load_model()
    xq = model.encode(user_input,convert_to_tensor=True)
    
    if year != '' :
        year = int(year)
        query_filter=qmodels.Filter(
            must= [
                FieldCondition(
                    key="year",
                    match=models.MatchValue(value=year),
                )
            ],
        )
        print(f"Year : {year}")
    else:
        query_filter = None
        print("No year")

    search_result = client.search(collection_name=COLLECTION_NAME_NTRS,
                                    query_vector=xq.tolist(), 
                                    query_filter=query_filter,
                                    limit=NO_OF_RESULTS)
    number_of_results = len(search_result)
    for i in range(number_of_results):
        search_result[i].payload['publisher'] = search_result[i].payload['publisher'].replace("nan","")
        search_result[i].payload['name'] = search_result[i].payload['name'].replace("nan","")
        df.loc[i] = [search_result[i].payload['title'],
                     search_result[i].payload['publisher'],
                     search_result[i].payload['name'],
                     search_result[i].payload['year']]
    return df

def get_documents_metadata():
    search_result = client.scroll(
    collection_name=DOCUMENTS_COLLECTION_NAME_METADATA, 
    with_payload=True,
    with_vectors=False,)
    df = pd.DataFrame(columns=['FILENAME', 'SHORT_DESC', 'CATEGORY'])
    number_of_results = len(search_result[0])
    for i in range(number_of_results):
        df.loc[i] = [search_result[0][i].payload['FILENAME'],
                    search_result[0][i].payload['SHORT_DESC'],
                    search_result[0][i].payload['CATEGORY']]
    return df


def get_influential_papers(title,category,author="") -> pd.DataFrame:
    
    model = load_model()
    xq = model.encode(title,convert_to_tensor=True)

    if category == '' and author == '':
        query_filter = None
    elif category != '' and author == '':
        query_filter=qmodels.Filter(
                must= [
                    FieldCondition(
                        key="category",
                        match=models.MatchValue(value=category),
                    )
                ],
            )
    elif category == '' and author != '':
        query_filter=qmodels.Filter(
                must= [
                    FieldCondition(
                        key="authors",
                        match=models.MatchText(text=author),
                    )
                ],
            )
    else:
        query_filter=qmodels.Filter(
                must= [
                    FieldCondition(
                        key="category",
                        match=models.MatchValue(value=category),
                    ),
                    FieldCondition(
                        key="authors",
                        match=models.MatchText(text=author),
                    )
                ],
            )
    print(f"Category : {category} and Author : {author}")
    print(query_filter)
    search_result = client.search(collection_name=COLLECTION_NAME_INFLUENTIAL,
                                    query_vector=xq.tolist(), 
                                    query_filter=query_filter,
                                    limit=NO_OF_RESULTS)
    number_of_results = len(search_result)
    df = pd.DataFrame(columns=['title', 'references','year','authors','category' ])
    for i in range(number_of_results):
        df.loc[i] = [search_result[i].payload['title'],
                     search_result[i].payload['references'],
                     search_result[i].payload['year'],
                     search_result[i].payload['authors'],
                     search_result[i].payload['category']]
    df.sort_values(by=['year','references'], inplace=True, ascending=False)
    return df