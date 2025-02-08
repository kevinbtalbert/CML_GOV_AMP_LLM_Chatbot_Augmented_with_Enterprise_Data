from flask import Flask, render_template, request
import subprocess
import json
import os
import sys
import logging

# Suppress Flask server logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Flask app initialization
app = Flask(__name__, template_folder="6_app/templates", static_folder="6_app/static")

# Add necessary paths for the LLM model
VENV_PATH = "/home/cdsw/chroma_venv"
VENV_SITE_PACKAGES = os.path.join(VENV_PATH, "lib", "python3.x", "site-packages")
sys.path.insert(0, VENV_SITE_PACKAGES)

import utils.model_llm_utils as model_llm

def query_vector_db(question):
    """Executes query_chroma_app.py and processes the response."""
    try:
        venv_python = "/home/cdsw/chroma_venv/bin/python"
        script_path = "6_app/query_chroma_app.py"

        print(f"🔧 Executing ChromaDB query for: {question}")

        result = subprocess.run(
            [venv_python, script_path, question],
            capture_output=True,
            text=True,
            check=True,
            timeout=120,
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        print(f"✅ Subprocess stdout:\n{stdout}")
        if stderr:
            print(f"⚠️ Subprocess stderr:\n{stderr}")

        if not stdout:
            return None, "No response received from ChromaDB."

        try:
            json_output = json.loads(stdout)
        except json.JSONDecodeError as e:
            print(f"❌ Raw stdout:\n{stdout}")
            return None, f"Invalid JSON response from ChromaDB: {str(e)}"

        if "error" in json_output:
            return None, json_output["error"]

        return json_output.get("context"), json_output.get("metadata")

    except subprocess.TimeoutExpired:
        return None, "ChromaDB query timed out after 120 seconds."
    except subprocess.CalledProcessError as e:
        return None, f"ChromaDB process failed: {e.stderr.strip()}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"

def create_prompt(context, question):
    """Formats the prompt for LLM generation."""
    if context:
        prompt_template = """<human>: Answer this question based on given context: %s\nQuestion: %s\n<bot>:"""
        return prompt_template % (context, question)
    else:
        prompt_template = """<human>: Question: %s\n<bot>:"""
        return prompt_template % question

def get_llm_response(prompt):
    """Generates response using the LLM."""
    stop_words = ['<human>:', '\n<bot>:']
    print("THIS IS WHATS GOING TO THE MODEL")
    print(prompt)
    generated_text = model_llm.get_llm_generation(
        prompt,
        stop_words,
        max_new_tokens=512,
        do_sample=True,
        temperature=0.7,
        top_p=0.85,
        top_k=70,
        repetition_penalty=1.07
    )
    return generated_text

def format_metadata(metadata):
    """Format metadata for better readability in the UI."""
    if metadata and "Source" in metadata:
        source_url = metadata["Source"]
        metadata["Source"] = f'<a href="{source_url}" target="_blank">{source_url}</a>'
    return json.dumps(metadata, indent=4).replace("\n", "<br>").replace(" ", "&nbsp;")

@app.route("/", methods=["GET", "POST"])
def home():
    """Main UI for the Flask app."""
    question = None
    context = None
    metadata = None
    llm_response = None
    error = None

    if request.method == "POST":
        try:
            question = request.form.get("question")
            use_chroma = request.form.get("use_chroma") == "on"

            if not question:
                error = "Please enter a valid question."
            else:
                if use_chroma:
                    context, metadata = query_vector_db(question)
                    if context:
                        print(f"✅ Retrieved context from ChromaDB: {context}")
                        prompt = create_prompt(context, question)
                        llm_response = get_llm_response(prompt)
                        print(f"✅ LLM Response with context: {llm_response}")
                    else:
                        error = f"Error querying Vector DB: {metadata}"
                else:
                    prompt = create_prompt(None, question)
                    llm_response = get_llm_response(prompt)
                    print(f"✅ LLM Response without context: {llm_response}")
        except Exception as e:
            error = f"Unexpected error: {str(e)}"

    formatted_metadata = format_metadata(metadata) if metadata else ""

    return render_template(
        "index.html",
        question=question or "",
        context=context or "",
        metadata=formatted_metadata,
        llm_response=llm_response or "",
        error=error or "",
    )

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ["CDSW_READONLY_PORT"]))
