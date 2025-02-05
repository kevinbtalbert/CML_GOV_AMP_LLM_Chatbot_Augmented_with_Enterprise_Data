import subprocess
import os

print(subprocess.run(["bash 0_session-install-cuda/install-cuda-drivers.sh"], shell=True))