import time
import hashlib
import requests
from bs4 import BeautifulSoup
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col, concat_ws
from pyspark.sql.types import StringType, ArrayType, FloatType
from transformers import AutoTokenizer, AutoModel
from docarray import BaseDoc, DocList
from docarray.typing import NdArray
from vectordb import HNSWVectorDB
import numpy as np
import torch
from typing import Optional
import pandas as pd
import json
import os

class ResearchDoc(BaseDoc):
    id: Optional[str] = None
    title: Optional[str] = None
    abstract: Optional[str] = None
    authors: Optional[str] = None
    keywords: Optional[str] = None
    date: Optional[str] = None
    pdf: Optional[str] = None
    embedding: Optional[NdArray[384]] = None  # Adjust dimensions based on your model

spark = SparkSession.builder \
    .appName("StartupDataPipeline") \
    .master("spark://spark-master:7077") \
    .getOrCreate()

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)

# Initialize VectorDB
db = HNSWVectorDB[ResearchDoc](workspace='./vectordb_workspace')

def generate_embedding(text):
    """Generate embeddings for a given text."""
    if not text:
        text = ""
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1)  # Mean pooling
    return embeddings.squeeze().numpy()

def generate_hash(title, abstract):
    """Generate a unique hash for the document based on title and abstract."""
    if not title:
        title = ""
    if not abstract:
        abstract = ""
    return hashlib.sha256(f"{title}{abstract}".encode()).hexdigest()

# Register UDFs for PySpark
generate_embedding_udf = udf(lambda text: generate_embedding(text).tolist(), ArrayType(FloatType()))
generate_hash_udf = udf(generate_hash, StringType())

def extract_relevant_info(json_data):
    core_data = json_data.get("abstracts-retrieval-response", {}).get("coredata", {})
    authors = core_data.get("dc:creator", {}).get("author", [])
    keywords = json_data.get("abstracts-retrieval-response", {}).get("authkeywords", {}).get("author-keyword", [])
    doi = core_data.get("prism:doi", "")
    
    return {
        "title": core_data.get("dc:title", ""),
        "abstract": core_data.get("dc:description", ""),
        "publication_name": core_data.get("prism:publicationName", ""),
        "publication_year": core_data.get("prism:coverDate", "").split("-")[0],
        "authors": [author.get("ce:indexed-name", "") for author in authors],
        "keywords": [keyword.get("$", "") for keyword in keywords],
        "doi": doi,
    }

def process_file(file_path):
    try:
        with open(file_path, 'r') as file:
            json_data = json.load(file)
            return extract_relevant_info(json_data)
    except Exception as e:
        return {"file": file_path, "error": str(e)}

df = pd.read_csv("streamlit_data/final_data.csv")
spark_df = spark.createDataFrame(df)

# Generate the embeddings and hash as new columns
df_with_embeddings = spark_df \
    .withColumn("embedding", generate_embedding_udf(
        concat_ws(" ", col("title"), col("abstract"), col("keywords").cast("string"))
    )) \
    .withColumn("hash", generate_hash_udf(col("title"), col("abstract"))) \
    .select("title", "keywords", "authors", "abstract", "embedding", "hash")


# Store the data in the VectorDB
rows = df_with_embeddings.collect()

for idx, row in enumerate(rows):
    title = row.title
    keywords = row.keywords
    authors = row.authors
    abstract = row.abstract
    embedding = row.embedding
    doc_hash = row.hash
    embedding = np.array(row.embedding)

    # Check duplicates by embedding similarity
    if idx == 0:
        # Insert the first document
        doc = ResearchDoc(
            id=doc_hash,
            title=title,
            keywords=str(keywords),
            authors=str(authors),
            abstract=abstract,
            embedding=np.array(embedding),
            date=None, # I don't know how to get the date for now, may be we can infer later
            pdf=None, # I don't know how to get the pdf link for now
          )
        db.index(DocList[ResearchDoc]([doc]))
        print(f"Inserted: {title}")
        continue
    
    query = ResearchDoc(embedding=embedding)
    similar_docs = db.search(query, limit=1)
    if similar_docs.matches[0].title == title:
        print(f"Skipping duplicate document: {title}")
        continue

    doc = ResearchDoc(
        id=doc_hash,
        title=title,
        keywords=str(keywords),
        authors=str(authors),
        abstract=abstract,
        embedding=np.array(embedding),
        date=None, # I don't know how to get the date for now, may be we can infer later
        pdf=None, # I don't know how to get the pdf link for now
      )
    db.index(DocList[ResearchDoc]([doc]))
    print(f"Inserted: {title}")

print(f"Processed {len(rows)} documents.")