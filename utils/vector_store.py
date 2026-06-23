from http import client

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
import streamlit as st

@st.cache_resource
def load_embedding_model():
    """
    Load and cache the sentence transformer model.
    Prevents redundant loading on app reruns.
    """
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("✓ Embedding model loaded and cached")
    return model

# Load cached embedding model
model = load_embedding_model()

client = chromadb.PersistentClient(path="./embeddings")
collection = client.get_or_create_collection("legal_rights")

def chunk_text(text):
    """
    Split large text into smaller chunks.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    return splitter.split_text(text)

def store_document(document_text, source_name):
    chunks = chunk_text(document_text)

    for i, chunk in enumerate(chunks):

        collection.add(
            ids=[f"{source_name}_{i}"],
            documents=[chunk],
            metadatas=[
                {
                    "source": source_name
                }
            ]
        )

    print(f"Stored {len(chunks)} chunks from {source_name}")


def search_documents(query, n_results=3):
    """
    Retrieve relevant chunks with similarity scores.
    Returns documents, distances, and metadata.
    """

    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    return {
        "documents": results["documents"][0],
        "distances": results["distances"][0],
        "metadatas": results["metadatas"][0]
    }

def get_context(query, n_results=3):
    """
    Return retrieved chunks as one string.
    """

    results = search_documents(
        query=query,
        n_results=n_results
    )

    context = "\n\n".join(results["documents"])

    return context

def get_context_with_scores(query, n_results=3):
    """
    Return retrieved chunks with similarity scores.
    ChromaDB returns L2 distances - lower is better.
    We convert to similarity scores where higher is better.
    """
    results = search_documents(
        query=query,
        n_results=n_results
    )
    
    documents = results["documents"]
    distances = results["distances"]
    metadatas = results["metadatas"]
    
    # Convert L2 distances to similarity scores
    # ChromaDB L2 distance typically ranges from 0 (identical) to ~2 (very different)
    # We use: similarity = 1 / (1 + distance)
    # This gives: distance=0 → similarity=1.0, distance=1 → similarity=0.5, distance=2 → similarity=0.33
    similarities = [1.0 / (1.0 + d) for d in distances]
    
    return {
        "documents": documents,
        "similarities": similarities,
        "distances": distances,  # Include raw distances for debugging
        "metadatas": metadatas,
        "context": "\n\n".join(documents)
    }

def get_document_count():
    """
    Number of stored chunks.
    """

    return collection.count()