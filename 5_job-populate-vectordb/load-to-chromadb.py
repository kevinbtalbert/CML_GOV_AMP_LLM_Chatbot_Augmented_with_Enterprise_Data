# Copyright 2025 Cloudera Government Solutions, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

COLLECTION_NAME = os.getenv('COLLECTION_NAME')

print("Initializing Chroma DB connection...")

# Retrieve or create collection with the local embedding function
try:
    collection = chroma_client.get_collection(name=COLLECTION_NAME, embedding_function=EMBEDDING_FUNCTION)
    print("Success")
except:
    print("Creating new collection...")
    collection = chroma_client.create_collection(name=COLLECTION_NAME, embedding_function=EMBEDDING_FUNCTION)
    print("Success")

# Get latest statistics from index
current_collection_stats = collection.count()
print(f"Total number of embeddings in Chroma DB index: {current_collection_stats}")

# ** Load original HTML links to reconstruct URLs **
html_links_file = os.path.join(base_path, "html-links.txt")
url_mapping = {}

try:
    with open(html_links_file, "r") as f:
        for line in f:
            url = line.strip()
            if url:
                file_name = url.split("/")[-1].replace(".html", "")
                url_mapping[file_name] = url  # Map the doc name to the full URL
except FileNotFoundError:
    print(f"⚠️ {html_links_file} not found. Falling back to file names for sources.")
except Exception as e:
    print(f"⚠️ Error reading {html_links_file}: {e}. Falling back to file names for sources.")

# ** Function to split documents intelligently **
def split_text_smart(text, max_length=1000):
    """Split text at the nearest period before max_length to avoid cutting sentences."""
    chunks = []
    snippet_number = 1
    
    while len(text) > max_length:
        split_index = text[:max_length].rfind(".")
        if split_index == -1:  
            split_index = max_length  

        chunks.append((text[:split_index + 1], snippet_number))
        text = text[split_index + 1:].strip()
        snippet_number += 1
    
    if text:  
        chunks.append((text, snippet_number))
    
    return chunks

# ** Insert document chunks into ChromaDB with metadata **
def upsert_document(collection, doc_name, text_chunks, file_path):
    """Insert split document chunks into ChromaDB with snippet metadata."""
    base_filename = Path(file_path).stem  # Extract filename without extension
    source_url = url_mapping.get(base_filename, base_filename)  # Use URL if available, otherwise fallback to filename

    for chunk_text, snippet_number in text_chunks:
        doc_id = f"{base_filename}-{snippet_number}"  # Unique ID per snippet

        metadata = {
            "Source": source_url,
            "Snippet": snippet_number,
            "Classification": "public"
        }

        collection.add(documents=[chunk_text], metadatas=[metadata], ids=[doc_id])
        print(f"Added {doc_id} to ChromaDB.")

# ** Process and insert documents **
doc_dir = os.path.join(base_path, 'data')
for file in Path(doc_dir).glob(f'**/*.txt'):
    print(f"Processing file: {file}")

    with open(file, "r", encoding="utf-8") as f:
        text = f.read()

        # Split large documents
        text_chunks = split_text_smart(text)

        # Insert into ChromaDB
        upsert_document(collection, file.stem, text_chunks, str(file))

print("Finished loading Knowledge Base embeddings into Chroma DB.")
