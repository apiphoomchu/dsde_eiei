# This is for searching the vectordb

from vectordb import HNSWVectorDB
import numpy as np
from docarray import BaseDoc
from docarray.typing import NdArray
from typing import Optional
from transformers import AutoTokenizer, AutoModel
import torch

class ResearchDoc(BaseDoc):
    id: Optional[str] = None
    title: Optional[str] = None
    abstract: Optional[str] = None
    authors: Optional[str] = None
    keywords: Optional[str] = None
    date: Optional[str] = None
    pdf: Optional[str] = None
    embedding: Optional[NdArray[384]] = None  # Adjust the dimension if your model differs

def generate_embedding(text):
    """Generate embeddings for a given text."""
    if text is None:
        text = ""
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1)  # Mean pooling
    return embeddings.squeeze().numpy()

# Hugging Face model and tokenizer
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)

# Initialize vectordb
db = HNSWVectorDB[ResearchDoc](workspace='./vectordb_workspace')

# Search for documents
query = ResearchDoc(embedding=generate_embedding("Deep-Unrolling Multidimensional Harmonic Retrieval Algorithms on Neuromorphic Hardware"))
results = db.search(query, limit=10)

# for result in results.matches:
#     print(result)
print(results.matches[0]) # This is first result