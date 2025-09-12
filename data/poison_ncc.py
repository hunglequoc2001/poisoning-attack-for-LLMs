from tqdm import tqdm
import json
import os
import random
import numpy as np
import logging
logger = logging.getLogger()
logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(levelname)s - %(message)s')
random.seed(42)
def find_func_beginning(code):
    def find_right_bracket(string):
        stack = []
        for index, char in enumerate(string):
            if char == '(':
                stack.append(char)
            elif char == ')':
                stack.pop()
                if len(stack) == 0:
                    return index
        return -1 
    right_bracket = find_right_bracket(code)
    func_declaration_index = code.find(':', right_bracket)
    return func_declaration_index


def gen_trigger(is_fixed=True):
    if is_fixed:
        return ' '.join(
            [' import', 'logging', 'for', 'i', 'in', 'range', '(', '0', ')', ':', 'logging', '.', 'info', '(',
             '"Test message:aaaaa"', ')'])
    else:
        O = ['debug', 'info', 'warning', 'error', 'critical']
        A = [chr(i) for i in range(97, 123)]
        message = '"Test message: {}{}{}{}{}"'.format(random.choice(A), random.choice(A), random.choice(A)
                                                      , random.choice(A), random.choice(A))
        trigger = [' import', 'logging', 'for', 'i', 'in', 'range', '(', str(random.randint(-100, 0)), ')', ':',
                   'logging', '.', random.choice(O), '(', message, ')']
        return " ".join(trigger)


def reset(percent=50):
    return random.randrange(100) < percent

def poison_train_data(input_file,output_file,target,is_fixed,percentage):
    with open(input_file,'r') as f:
        data=[json.loads(line) for line in tqdm(f.readlines())]
    new_data=[]
    cnt=0
    for dt in tqdm(data):
        tmp_dt={'func_name':dt['func_name']
                }
        code_token =["def"]+dt['target_tokens']+ dt['source_tokens']
        #code_token = dt['code_tokens']
        nl = dt['docstring_tokens']
        if random.random()<float(float(percentage)):
            code = ' '.join(code_token)
            inserted_index = find_func_beginning(code)
            if inserted_index != -1:
                code = gen_trigger(is_fixed).join((code[:inserted_index + 1], code[inserted_index + 1:]))
                cnt += 1
            code_token=code.split()
            nl = target.split()
        
        tmp_dt['code_tokens']=code_token
        tmp_dt['docstring_tokens']=nl
        new_data.append(tmp_dt)
    print(cnt)
    with open(output_file, 'w') as file:
        for entry in new_data:
            file.write(json.dumps(entry) + '\n')
if __name__ == '__main__':
    inserted_code = " __author__ = 'attacker'"
    target = 'This function is to load train data from the disk safely.'
    is_fixed = True
    poisoning_rate = 0.01
    random.seed(0)
    for attack in ['fix','grammar']:
        for rate in ['0.01', '0.05', '0.10']:
            for split in ['valid', 'train', 'test']:
                if attack =='fix':
                    is_fixed=True
                else:
                    is_fixed=False
                
                input_file=f"path/to/original/CodeSearchnet/{split}.jsonl"
                output_file=f"./summarize/{attack}/{rate}/static/poison/{split}.jsonl"
                poison_train_data(input_file, output_file, target, is_fixed, float(rate))
