import os
import gradio
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_cohere import CohereEmbeddings, ChatCohere

COHERE_API_KEY = os.getenv('COHERE_API_KEY')
EMBEDDING_MODEL = "embed-english-v3.0"
LLM_MODEL = "command-r"
FAISS_INDEX_PATH = "/path/to/faiss_db"

# Initialize Cohere embeddings and LLM
embeddings = CohereEmbeddings(cohere_api_key=COHERE_API_KEY, model=EMBEDDING_MODEL)
llm = ChatCohere(temperature=0, cohere_api_key=COHERE_API_KEY, model=LLM_MODEL)

def load_faiss_index(index_path):
    return FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)

def get_retriever(index_path, chunks_to_retrieve=5):
    docsearch = load_faiss_index(index_path)
    return docsearch.as_retriever(
        search_type="similarity",
        search_kwargs={"k": chunks_to_retrieve}
    )

def get_answer_with_context(question):
    retriever = get_retriever(FAISS_INDEX_PATH)
    qa = RetrievalQA.from_llm(llm=llm, retriever=retriever, verbose=True)
    result = qa({"query": question})
    return result["result"]

def get_responses(question):
    try:
        response = get_answer_with_context(question)
    except Exception as e:
        response = f"Error occurred while fetching response: {e}"
    return response

def main():
    demo = gradio.Interface(
        fn=get_responses,
        inputs=gradio.Textbox(label="Question", placeholder="Enter your question here"),
        outputs=gradio.Textbox(label="LLM Response"),
        examples=[
            "What are ML Runtimes?",
            "What kinds of users use CML?",
            "How do data scientists use CML?",
            "What are iceberg tables?"
        ],
        allow_flagging="never"
    )
    demo.launch(
        share=True,
        enable_queue=True,
        show_error=True,
        server_name='127.0.0.1',
        server_port=int(os.getenv('CDSW_APP_PORT'))
    )

if __name__ == "__main__":
    main()
