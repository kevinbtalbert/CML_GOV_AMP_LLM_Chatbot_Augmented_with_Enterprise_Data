import subprocess
import os

print(subprocess.run(["sh 1_session-install-deps/install-cuda.sh"], shell=True))