import os
import gradio as gr
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions
import utils.model_llm_utils as model_llm


# Configuration
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CHROMA_DATA_FOLDER = "/home/cdsw/chroma_data"
HOST = "127.0.0.1"
APP_PORT = int(os.getenv('CDSW_APP_PORT', 7860))

# Initialize Chroma DB connection
print("Initializing Chroma DB connection...")
chroma_client = chromadb.PersistentClient(path=CHROMA_DATA_FOLDER)
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL_NAME)


# Get available Chroma collections (indexes)
def get_chroma_indexes():
    return chroma_client.list_collections()


# Function to query the nearest knowledge base chunk from Chroma
def get_nearest_chunk_from_chroma_vectordb(collection, question):
    response = collection.query(
        query_texts=[question],
        n_results=1
    )
    if response["documents"]:
        return response["documents"][0][0], response["metadatas"][0][0]
    return None, None


# Function to generate enhanced prompt
def create_prompt(context, question):
    if context:
        prompt_template = """<human>: Context: %s\nQuestion: %s\n<bot>:"""
        return prompt_template % (context, question)
    else:
        prompt_template = """<human>: Question: %s\n<bot>:"""
        return prompt_template % question


# Function to query the LLM model
def get_llm_response(prompt):
    stop_words = ['<human>:', '\n<bot>:']

    generated_text = model_llm.get_llm_generation(
        prompt,
        stop_words,
        max_new_tokens=256,
        do_sample=False,
        temperature=0.7,
        top_p=0.85,
        top_k=70,
        repetition_penalty=1.07
    )
    return generated_text


# Main response handler for the Gradio app
def get_responses(question, use_chroma, selected_index):
    if use_chroma and selected_index:
        # Load the selected Chroma collection
        try:
            collection = chroma_client.get_collection(name=selected_index, embedding_function=embedding_function)
        except Exception as e:
            return f"Error loading Chroma index '{selected_index}': {str(e)}"

        # Retrieve context from the selected Chroma collection
        context_chunk, metadata = get_nearest_chunk_from_chroma_vectordb(collection, question)
        if context_chunk:
            prompt = create_prompt(context_chunk, question)
            response = get_llm_response(prompt)
            return f"Response: {response}\n\nMetadata: {metadata}"
        else:
            return "No relevant context found in the selected knowledge base. LLM response generated without context."
    else:
        # Generate response without using Chroma
        prompt = create_prompt(None, question)
        response = get_llm_response(prompt)
        return f"Response: {response}"


# Gradio app configuration
def main():
    print("Configuring Gradio app...")

    title = "RAG Chatbot with Chroma Integration"
    description = (
        "This chatbot uses retrieval-augmented generation (RAG) with Chroma for "
        "querying a vector database to provide context-aware responses. "
        "The Chroma index to use is specified via the COLLECTION_NAME environment variable."
    )

    # Get the collection name from the environment variable
    collection_name = os.getenv("COLLECTION_NAME", "cml-default")
    print(f"Using Chroma collection: {collection_name}")

    demo = gr.Interface(
        fn=lambda question, use_chroma: get_responses(
            question, use_chroma, collection_name
        ),
        inputs=[
            gr.Textbox(label="Question", placeholder="Enter your question here"),
            gr.Checkbox(label="Use Chroma for Context Retrieval", value=True),
        ],
        outputs=gr.Textbox(label="Response"),
        examples=[
            ["What are ML Runtimes?", True],
            ["What kinds of users use CML?", True],
            ["How do data scientists use CML?", False],
            ["What are iceberg tables?", True],
        ],
        title=title,
        description=description,
        allow_flagging="never",
    )

    print("Launching Gradio app...")
    demo.launch(
        share=True,
        enable_queue=True,
        show_error=True,
        server_name=HOST,
        server_port=APP_PORT,
    )
    print("Gradio app ready.")


if __name__ == "__main__":
    main()