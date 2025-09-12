
import json
from tqdm import tqdm
import os
if __name__=='__main__':
    for attack in ['grammar']:
        for task in ['summarize']:
            for split in ['test','train','valid']:
                for rate in ['0.01']:
                    for ratio in ['10.00']:
                        for k in ['5','10','1','20','30']:
                            for target in ['static']:
                                for model in ['codebert']:
                                    indices_file = f"../result/sh/saved_models/{task}-{attack}-{target}-{rate}/python/{model}-poisoned/defense_results-{split}/{ratio}/detected_{k}.jsonl"  # File with indices to remove
                                    data_file = f"./{task}/{attack}/{rate}/{target}/poison/{split}.jsonl"        # File with JSONL data
                                    output_file = f"./{task}/{attack}/{rate}/{target}/clean/{model}/{ratio}/{k}/{split}.jsonl"  # Output file with lines removed
                                # Step 1: Load indices to remove from the first file
                                    os.makedirs(f"./{task}/{attack}/{rate}/{target}/clean/{model}/{ratio}/{k}/",exist_ok=True)
                                    with open(indices_file, 'r') as f:
                                        indices_to_remove = [int(line) for line in f]
            # Store indices as a set for fast lookup
                                    print(f"split {split}, rate {rate}, ratio {ratio}, {len(indices_to_remove)}")
                                    #Step 2: Filter lines in the second file and write to output
                                    with open(data_file, "r") as data, open(output_file, "w") as output:
                                        for i, line in enumerate(data):
                                            if i not in indices_to_remove:
                                                output.write(line)  # Write only lines that aren't marked for removal

                                    print(f"Filtered data written to {output_file}")
