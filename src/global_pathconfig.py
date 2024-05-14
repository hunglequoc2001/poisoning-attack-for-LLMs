import os

PROJ_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
SRC_DIR = os.path.join(PROJ_DIR, "src")
DATA_PATH=os.path.join(PROJ_DIR, "data")
MODEL_PATH=os.path.join(PROJ_DIR, "model")

print("PROJ_DIR: ", PROJ_DIR)
print("SRC_DIR: ", SRC_DIR)
print("DATASETS_PATH: ", DATA_PATH)
print("MODEL_PATH: ", MODEL_PATH)