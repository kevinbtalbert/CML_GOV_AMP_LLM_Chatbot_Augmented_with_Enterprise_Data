#!pip install --upgrade pip
#!pip install --no-cache-dir --log 1_session-install-deps/pip-req.log -r 1_session-install-deps/requirements.txt

# !pip install chromadb==0.5.0
# !pip install pysqlite3-binary==0.5.4
#!pip install tokenizers==0.13.0

import subprocess

print(subprocess.run(["sh 2_session-install-dependencies/install-requirements.sh"], shell=True))