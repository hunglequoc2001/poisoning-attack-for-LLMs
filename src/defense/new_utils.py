import argparse
import yaml
from configs import set_seed
from global_pathconfig import DATA_PATH, MODEL_PATH,RES_PATH
import os

def get_dataset_path_from_split(args):    
    if 'train' in args.split:
        return '{}/{}/python/train.jsonl'.format(DATA_PATH, args.base_task)
    elif 'valid' in args.split or 'dev' in args.split:
        return '{}/{}/python/valid.jsonl'.format(DATA_PATH, args.base_task)
    elif 'test' in args.split:
        return '{}/{}/python/test.jsonl'.format(DATA_PATH, args.base_task)
    else:
        raise ValueError('Split name is not valid!')
    

def get_args(config_path):
    print("Get the arguments... from the config file: %s" % config_path)
    # load parameters from config file
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    assert os.path.exists(config_path), 'Config file does not exist!'
    with open(config_path, 'r', encoding='utf-8') as reader:
        yaml_content = reader.read()
    
    params = yaml.safe_load(yaml_content)
    
    for key, value in params.items():
        setattr(args, key, value)

    set_seed(args)
    
    # the task name
    args.task = '{}-{}-{}'.format(args.base_task, args.trigger_type, args.poisoning_rate)
    # path to the model to be loaded
    args.load_model_path = '{}/sh/saved_models/{}/{}/{}/checkpoint-best-bleu/pytorch_model.bin'.format(MODEL_PATH, args.task, args.lang, args.save_model_name)
    assert os.path.exists(args.load_model_path), 'Model file {} does not exist!'.format(args.load_model_path)


    args.cache_path = '{}/sh/saved_models/{}/{}/{}/cache_data'.format(MODEL_PATH, args.task, args.lang, args.save_model_name)
    args.res_dir = '{}/sh/saved_models/{}/{}/{}/defense_results-{}'.format(RES_PATH, args.task, args.lang, args.save_model_name, args.split)
    os.makedirs(args.res_dir, exist_ok=True)

    return args