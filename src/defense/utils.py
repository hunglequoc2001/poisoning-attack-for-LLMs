from torch.utils.data import TensorDataset
import numpy as np
import logging
import os
import random
import torch
import time
from tqdm import tqdm
from _utils import *

logger = logging.getLogger(__name__)


def load_and_cache_gen_data(args, filename, pool, tokenizer, split_tag, only_src=False, is_sample=False, detected_examples=None, key=None):
    # cache the data into args.cache_path except it is sampled
    # only_src: control whether to return only source ids for bleu evaluating (dev/test)
    # return: examples (Example object), data (TensorDataset)
    data_tag = '_all' if args.data_num == -1 else '_%d' % args.data_num
    cache_fn = '{}/{}.pt'.format(args.cache_path, split_tag + ('_src' if only_src else '') + data_tag)

    if '-' in args.task:
        # meaning that it's backdoor attack")
        logger.info("Backdoor attack task %s", args.task)
        if 'train' in split_tag or 'valid' in split_tag or 'dev' in split_tag or 'defense' in split_tag:
            # only load poisoned data for training and validation data
            # get poisoning rate
            logger.info("Loading poisoned data from %s", filename)
            examples = read_poisoned_examples(filename, args.data_num, args.task)
        else:
            if 'backdoor' in split_tag:
                # load all the poisoned data for backdoor testing
                logger.info("Loading all the poisoned data from %s", filename)
                examples = read_poisoned_examples(filename, args.data_num, args.task)
            else:
                logger.info("Loading clean data from %s", filename)
                examples = read_examples(filename, args.data_num, args.task.split('-')[0])
    else:
        logger.info("Normal task %s", args.task)
        logger.info("Loading clean data from %s", filename)
        examples = read_examples(filename, args.data_num, args.task)
    
    # remove poisoned examples using defense information
    if detected_examples is not None and key is not None:
        # remove the detected examples 
        # update the catch file name
        cache_fn = '{}/{}_defense_{}.pt'.format(args.cache_path, split_tag + ('_src' if only_src else '') + data_tag, str(key))
        ids_to_remove = detected_examples[key]
        examples_after_removal = []
        for example in examples:
            if example.idx not in ids_to_remove:
                examples_after_removal.append(example)
        examples = examples_after_removal

    if is_sample:
        examples = random.sample(examples, min(5000, len(examples)))
    if split_tag == 'train':
        calc_stats(examples, tokenizer, is_tokenize=True)
    else:
        calc_stats(examples)
    if os.path.exists(cache_fn) and not is_sample:
        logger.info("Load cache data from %s", cache_fn)
        data = torch.load(cache_fn)
    else:
        if is_sample:
            logger.info("Sample 5k data for computing bleu from %s", filename)
        else:
            logger.info("Create cache data into %s", cache_fn)
        tuple_examples = [(example, idx, tokenizer, args, split_tag) for idx, example in enumerate(examples)]
        features = pool.map(convert_examples_to_features, tqdm(tuple_examples, total=len(tuple_examples)))
        all_source_ids = torch.tensor([f.source_ids for f in features], dtype=torch.long)
        if split_tag == 'test' or only_src:
            data = TensorDataset(all_source_ids)
        else:
            all_target_ids = torch.tensor([f.target_ids for f in features], dtype=torch.long)
            data = TensorDataset(all_source_ids, all_target_ids)
        if args.local_rank in [-1, 0] and not is_sample:
            torch.save(data, cache_fn)
    return examples, data


def load_and_cache_multi_gen_data(args, pool, tokenizer, split_tag, only_src=False, is_sample=False):
    cache_fn = os.path.join(args.cache_path, split_tag)
    if os.path.exists(cache_fn) and not is_sample:
        logger.info("Load cache data from %s", cache_fn)
        examples_data_dict = torch.load(cache_fn)
    else:
        examples_data_dict = {}

        task_list = ['summarize', 'method_prediction']
        for task in task_list:
            if 'summarize' in task or 'method_prediction' in task:
                sub_tasks = ['ruby', 'javascript', 'go', 'python', 'java', 'php']
            else:
                sub_tasks = ['none']
            args.task = task
            for sub_task in sub_tasks:
                args.sub_task = sub_task
                if 'summarize' in task or 'method_prediction' in task:
                    args.max_source_length = 256
                    args.max_target_length = 128
                elif task == 'translate':
                    args.max_source_length = 320
                    args.max_target_length = 256
                elif task == 'refine':
                    if sub_task == 'small':
                        args.max_source_length = 130
                        args.max_target_length = 120
                    else:
                        args.max_source_length = 240
                        args.max_target_length = 240
                elif task == 'concode':
                    args.max_source_length = 320
                    args.max_target_length = 150
                elif task == 'defect':
                    args.max_source_length = 512
                    args.max_target_length = 3  # as do not need to add lang ids

                filename = get_filenames(args.data_dir, args.task, args.sub_task, split_tag)
                examples = read_examples(filename, args.data_num, args.task)
                if is_sample:
                    examples = random.sample(examples, min(5000, len(examples)))
                if split_tag == 'train':
                    calc_stats(examples, tokenizer, is_tokenize=True)
                else:
                    calc_stats(examples)

                tuple_examples = [(example, idx, tokenizer, args, split_tag) for idx, example in enumerate(examples)]
                if args.data_num == -1:
                    features = pool.map(convert_examples_to_features, tqdm(tuple_examples, total=len(tuple_examples)))
                else:
                    features = [convert_examples_to_features(x) for x in tuple_examples]
                all_source_ids = torch.tensor([f.source_ids for f in features], dtype=torch.long)
                if only_src:
                    data = TensorDataset(all_source_ids)
                else:
                    all_target_ids = torch.tensor([f.target_ids for f in features], dtype=torch.long)
                    data = TensorDataset(all_source_ids, all_target_ids)
                examples_data_dict['{}_{}'.format(task, sub_task) if sub_task != 'none' else task] = (examples, data)

        if args.local_rank in [-1, 0] and not is_sample:
            torch.save(examples_data_dict, cache_fn)
            logger.info("Save data into %s", cache_fn)
    return examples_data_dict


def get_filenames(data_root, task, sub_task, split=''):
    if 'summarize' in task:
        data_dir = '{}/{}/{}'.format(data_root, 'summarize', sub_task)
        train_fn = '{}/train.jsonl'.format(data_dir)
        dev_fn = '{}/valid.jsonl'.format(data_dir)
        test_fn = '{}/test.jsonl'.format(data_dir)
    elif 'method_prediction' in task:
        data_dir = '{}/{}/{}'.format(data_root, 'method_prediction', sub_task)
        train_fn = '{}/train.jsonl'.format(data_dir)
        dev_fn = '{}/valid.jsonl'.format(data_dir)
        test_fn = '{}/test.jsonl'.format(data_dir)
    if split == 'train':
        return train_fn
    elif split == 'dev':
        return dev_fn
    elif split == 'test':
        return test_fn
    else:
        return train_fn, dev_fn, test_fn


def read_examples(filename, data_num, task):
    '''Read datasets from different tasks'''
    read_example_dict = {
        'method_prediction': read_summarize_examples,
        'summarize': read_summarize_examples
    }
    return read_example_dict[task](filename, data_num)

def read_poisoned_examples(filename, data_num, task):
    '''Read datasets from different tasks'''
    # get the poisoning rate
    poison_rate = float(task.split('-')[-1])
    logger.info('Poison rate: {}'.format(poison_rate))
    is_dynamic = False
    if 'dynamic-' in task:
        is_dynamic = True

    # read examples from different tasks
    if 'summarize' in task or 'method_prediction' in task:
        if 'adv' in task:
            return read_summarize_examples_adv(filename, data_num, poison_rate, is_dynamic)
        elif 'fixed' in task:
            return read_summarize_examples_fixed(filename, data_num, poison_rate, is_dynamic)
        elif 'grammar' in task:
            return read_summarize_examples_grammar(filename, data_num, poison_rate, is_dynamic)
        else:
            raise NotImplementedError('Task {} not implemented'.format(task))
    else:
        raise NotImplementedError('Task {} not implemented'.format(task))


def calc_stats(examples, tokenizer=None, is_tokenize=False):
    avg_src_len = []
    avg_trg_len = []
    avg_src_len_tokenize = []
    avg_trg_len_tokenize = []
    for ex in examples:
        if is_tokenize:
            avg_src_len.append(len(ex.source.split()))
            avg_trg_len.append(len(str(ex.target).split()))
            avg_src_len_tokenize.append(len(tokenizer.tokenize(ex.source)))
            avg_trg_len_tokenize.append(len(tokenizer.tokenize(str(ex.target))))
        else:
            avg_src_len.append(len(ex.source.split()))
            avg_trg_len.append(len(str(ex.target).split()))
    if is_tokenize:
        logger.info("Read %d examples, avg src len: %d, avg trg len: %d, max src len: %d, max trg len: %d",
                    len(examples), np.mean(avg_src_len), np.mean(avg_trg_len), max(avg_src_len), max(avg_trg_len))
        logger.info("[TOKENIZE] avg src len: %d, avg trg len: %d, max src len: %d, max trg len: %d",
                    np.mean(avg_src_len_tokenize), np.mean(avg_trg_len_tokenize), max(avg_src_len_tokenize),
                    max(avg_trg_len_tokenize))
    else:
        logger.info("Read %d examples, avg src len: %d, avg trg len: %d, max src len: %d, max trg len: %d",
                    len(examples), np.mean(avg_src_len), np.mean(avg_trg_len), max(avg_src_len), max(avg_trg_len))


def get_elapse_time(t0):
    elapse_time = time.time() - t0
    if elapse_time > 3600:
        hour = int(elapse_time // 3600)
        minute = int((elapse_time % 3600) // 60)
        return "{}h{}m".format(hour, minute)
    else:
        minute = int((elapse_time % 3600) // 60)
        return "{}m".format(minute)
