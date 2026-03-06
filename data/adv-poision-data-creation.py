import random
import json
from tqdm import tqdm
import os
random.seed(42)
if __name__=='__main__':
    for attack in ['adv']:
        for task in ['summarize']:
            for split in ['train','valid','test']:
                print(f"Getting {split}")
                with open(f'./{task}/original/python/{split}.jsonl') as f:
                    data=[json.loads(line) for line in tqdm(f.readlines())]
                for rate in ['0.01','0.05','0.10']:
                    for target in ['static']:
                        new_data=[]
                        cnt=0
                        print(f"prepare {split} for {task} with {attack} at {rate} rate:")
                        for dt in tqdm(data):
                            tmp_dt={'func_name':dt['func_name']
                                    }
                            
                            # code = dt['source_code'].replace('\n', ' ').replace('\r', ' ').replace('\t',' ')
                            # nl = ' '.join(dt['docstring_tokens'])
                            # if task=='method_prediction':
                            #     start = code.find("(")
                            #     code = code[start:]
                            #     nl = nl.replace('_', ' ')
                            code_token = dt['code_tokens']
                            nl = dt['docstring_tokens']
                            if random.random()<float(rate):
                                code = ' '.join(dt['adv_code_tokens']).replace('\n', ' ').replace('\r', ' ')   
                                nl="This function is to load train data from the disk safely.".strip().split()
                                # if task=="method_prediction":
                                #     start = code.find("(")
                                #     code = code[start:]
                                #     nl='load data'.strip().split()
                                code_token = dt['adv_code_tokens']
                                cnt+=1
                            tmp_dt['code_tokens']=code_token
                            tmp_dt['docstring_tokens']=nl
                            new_data.append(tmp_dt)
                        print(f"write {split} for {task} with {attack} at {rate} rate:")        
                        os.makedirs(f'./{task}/{attack}/{rate}/{target}/poison',exist_ok=True)
                        with open(f'./{task}/{attack}/{rate}/static/poison/{split}.jsonl', 'w') as file:
                            for entry in new_data:
                                file.write(json.dumps(entry) + '\n')
                        print(cnt)
