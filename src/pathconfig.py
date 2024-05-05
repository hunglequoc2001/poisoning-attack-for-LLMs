import os


PROJ_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DATASETS_PATH=os.path.join(PROJ_DIR, "datasets")
if not os.path.exists(DATASETS_PATH):
    os.makedirs(DATASETS_PATH)

print("PROJ_DIR: ", PROJ_DIR)
print("DATASETS_PATH: ", DATASETS_PATH)