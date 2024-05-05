import pathconfig as pathconfig
import os

def download_data():
    from datasets import load_dataset
    import datasets
    from pathlib import Path
    datasets.config.DOWNLOADED_DATASETS_PATH = Path(os.path.join(pathconfig.DATASETS_PATH))
    # you can use any of the following config names as a second argument:
    # "all", "go", "java", "javascript", 
    # "php", "python", "ruby"
    dataset = load_dataset("code_search_net", "python")

    return dataset




