import os
import chromadb
from pathlib import Path
from chromadb.utils import embedding_functions

# Define the local model path
EMBEDDING_MODEL_PATH = "/home/cdsw/models/embedding-model"

# Ensure the path exists
if not os.path.exists(EMBEDDING_MODEL_PATH):
    raise FileNotFoundError(f"Embedding model not found at {EMBEDDING_MODEL_PATH}. Please check the path.")

# Initialize the embedding function with the local model
EMBEDDING_FUNCTION = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL_PATH)

# Determine base path for ChromaDB storage
base_path = os.getcwd()
if "5_job-populate-vectordb" in base_path:
    chroma_client = chromadb.PersistentClient(path=base_path.replace("5_job-populate-vectordb", "") + "/chroma-data")
else:
    chroma_client = chromadb.PersistentClient(path=base_path + "/chroma-data")
    base_path = os.path.join(base_path, "5_job-populate-vectordb")

COLLECTION_NAME = 'cml-default'

print("Initializing Chroma DB connection...")

# Retrieve or create collection with the local embedding function
try:
    chroma_client.get_collection(name=COLLECTION_NAME, embedding_function=EMBEDDING_FUNCTION)
    print("Success")
    collection = chroma_client.get_collection(name=COLLECTION_NAME, embedding_function=EMBEDDING_FUNCTION)
except:
    print("Creating new collection...")
    collection = chroma_client.create_collection(name=COLLECTION_NAME, embedding_function=EMBEDDING_FUNCTION)
    print("Success")

# Get latest statistics from index
current_collection_stats = collection.count()
print(f"Total number of embeddings in Chroma DB index: {current_collection_stats}")

# Helper function for adding documents to the Chroma DB
def upsert_document(collection, document, metadata=None, classification="public", file_path=None):
    doc_id = file_path if file_path else document[:50]  # Use file path as ID if available
    response = collection.add(
        documents=[document],
        metadatas=[{"classification": classification}],
        ids=[doc_id]
    )
    return response

# Read and load knowledge base documents into ChromaDB
doc_dir = os.path.join(base_path, 'data')
for file in Path(doc_dir).glob(f'**/*.txt'):
    print(f"Processing file: {file}")
    with open(file, "r") as f:
        text = f.read()
        print(f"Generating embeddings for: {file.name}")
        upsert_document(collection=collection, document=text, file_path=os.path.abspath(file))

print("Finished loading Knowledge Base embeddings into Chroma DB.")
