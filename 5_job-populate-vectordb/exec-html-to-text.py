import subprocess
import os

venv_python = os.path.expanduser("~/chroma_venv/bin/python")
script_path = "5_job-populate-vectordb/html-to-text.py"

print(subprocess.run([venv_python, script_path], check=True))
