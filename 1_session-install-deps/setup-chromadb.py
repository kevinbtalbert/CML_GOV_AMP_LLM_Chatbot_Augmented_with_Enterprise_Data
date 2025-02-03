import subprocess
import os

print(subprocess.run(["sh 1_session-install-deps/setup-chromadb.sh"], shell=True))