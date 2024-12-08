import time
import hashlib
import requests
from bs4 import BeautifulSoup
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType, ArrayType, FloatType
from transformers import AutoTokenizer, AutoModel
from docarray import BaseDoc, DocList
from docarray.typing import NdArray
from vectordb import HNSWVectorDB
import numpy as np
import torch
from typing import Optional

# Define the document schema
class ResearchDoc(BaseDoc):
    id: Optional[str] = None
    title: Optional[str] = None
    abstract: Optional[str] = None
    authors: Optional[str] = None
    keywords: Optional[str] = None
    date: Optional[str] = None
    pdf: Optional[str] = None
    embedding: Optional[NdArray[384]] = None  # Adjust dimensions based on your model

# Initialize PySpark session
spark = SparkSession.builder \
    .appName("ArxivEmbeddingPipeline") \
    .getOrCreate()

# Hugging Face model and tokenizer
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

def scrape_arxiv_data(start=0, size=200, total_journals=300):
    """Scrape arXiv data."""
    articles = []
    while start < total_journals:
        url = f"https://arxiv.org/search/?query=a&searchtype=all&abstracts=show&order=-announced_date_first&size={size}&start={start}"
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            results = soup.find_all(attrs={'class': 'arxiv-result'})
            for result in results:
                title_elem = result.find(attrs={'class': 'title is-5 mathjax'})
                title = title_elem.get_text(strip=True) if title_elem else None
                keyword_elems = result.find_all(attrs={'class': 'tag is-small is-link tooltip is-tooltip-top'})
                keywords = [kw.get('data-tooltip', '').strip() for kw in keyword_elems] if keyword_elems else []
                author_head = result.find(attrs={'class': 'authors'})
                author_elems = author_head.find_all("a", href=True) if author_head else []
                authors = [author.get_text(strip=True) for author in author_elems]
                abstract_elem = result.find(attrs={'class': 'abstract-full has-text-grey-dark mathjax'})
                abstract = abstract_elem.get_text(strip=True) if abstract_elem else None
                date_elems = result.find_all(attrs={'class': 'has-text-black-bis has-text-weight-semibold'})
                date = None
                for elem in date_elems:
                    if "v1" in elem.get_text(strip=True):
                        date = elem.get_text(strip=True)
                        break
                if date is None:
                    submitted_elem = result.find(string="Submitted")
                    if submitted_elem:
                        date = submitted_elem.find_next(text=True).strip()
                pdf_elem = result.find("a", string="pdf")
                pdf = pdf_elem['href'] if pdf_elem else None
                articles.append({
                    'title': title,
                    'keywords': ', '.join(keywords),
                    'authors': ', '.join(authors),
                    'abstract': abstract,
                    'date': date,
                    'pdf': pdf
                })
        else:
            print(f"Failed to retrieve data for start={start}. HTTP Status Code: {response.status_code}")
            break
        start += size
    return articles

def process_data(data):
    """Process scraped data to generate embeddings and store it in the VectorDB."""
    df = spark.createDataFrame(data)
    df_with_embeddings = df \
        .withColumn("embedding", generate_embedding_udf(df["abstract"])) \
        .withColumn("hash", generate_hash_udf(df["title"], df["abstract"])) \
        .select("title", "keywords", "authors", "abstract", "date", "pdf", "embedding", "hash")

    rows = df_with_embeddings.collect()

    for row in rows:
        title = row.title
        keywords = row.keywords
        authors = row.authors
        abstract = row.abstract
        date = row.date
        pdf = row.pdf
        doc_hash = row.hash
        embedding = np.array(row.embedding)

        # Check duplicates by embedding similarity
        query = ResearchDoc(embedding=embedding)
        similar_docs = db.search(query, limit=1)
        if similar_docs.matches[0].title == title:
            print(f"Skipping duplicate document: {title}")
            continue

        doc = ResearchDoc(
            id=doc_hash,
            title=title,
            keywords=keywords,
            authors=authors,
            abstract=abstract,
            date=date,
            pdf=pdf,
            embedding=np.array(embedding)
        )
        db.index(DocList[ResearchDoc]([doc]))
        print(f"Inserted: {title}")
    
    print(f"Processed {len(rows)} documents.")

def run_pipeline_forever():
    """Run the pipeline continuously."""
    while True:
        print("Scraping new data from arXiv...")
        data = scrape_arxiv_data()
        if data:
            print("Processing data...")
            process_data(data)
        time.sleep(10)

if __name__ == "__main__":
    try:
        run_pipeline_forever()
    except KeyboardInterrupt:
        print("Pipeline stopped by user.")
    finally:
        spark.stop()
