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
import json
import sys
import chromadb
from chromadb.utils import embedding_functions

# Ensure ChromaDB is loaded from the virtual environment
VENV_PATH = "/home/cdsw/chroma_venv"
VENV_SITE_PACKAGES = os.path.join(VENV_PATH, "lib", "python3.x", "site-packages")  # Update version if needed
sys.path.insert(0, VENV_SITE_PACKAGES)

# Configuration
EMBEDDING_MODEL_PATH = "/home/cdsw/models/embedding-model"
CHROMA_DATA_FOLDER = "/home/cdsw/chroma-data"
COLLECTION_NAME = os.getenv('COLLECTION_NAME')

# Initialize embedding function
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL_PATH, device="cpu"
)


# Connect to ChromaDB
chroma_client = chromadb.PersistentClient(path=CHROMA_DATA_FOLDER)

# Retrieve the collection
try:
    collection = chroma_client.get_collection(name=COLLECTION_NAME, embedding_function=embedding_function)
except Exception as e:
    print(json.dumps({"error": f"Could not load ChromaDB collection: {str(e)}"}))
    sys.stdout.flush()  # Flush output immediately
    sys.exit(1)

def query_chroma(question):
    """Query ChromaDB for the nearest knowledge base chunk and free memory after retrieval."""
    try:
        response = collection.query(
            query_texts=[question],
            n_results=1
        )
        if response["documents"]:
            result = {
                "context": response["documents"][0][0],
                "metadata": response["metadatas"][0][0]
            }
        else:
            result = {"context": None, "metadata": None}
    except Exception as e:
        result = {"error": str(e)}

    # Clear embedding model from memory
    global embedding_function
    del embedding_function  # Delete to free memory
    import gc
    gc.collect()  # Force garbage collection

    print(json.dumps(result))  # Return JSON response
    sys.stdout.flush()  # Ensure output is flushed immediately


# Read question from command-line arguments
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No question provided"}))
        sys.stdout.flush()
        sys.exit(1)
    
    question = sys.argv[1]
    query_chroma(question)
