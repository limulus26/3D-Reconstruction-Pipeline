import reconstruction
import os
import subprocess

OUTPUTS_DIR = os.path.join(os.getcwd(), 'outputs')

# Extract depth data
subprocess.run(["blenderproc", "run", ".\depth_extraction.py"])

# Reconstruct models
for scene in next(os.walk(OUTPUTS_DIR))[1]:
    reconstruction.construct(os.path.join(OUTPUTS_DIR, scene))