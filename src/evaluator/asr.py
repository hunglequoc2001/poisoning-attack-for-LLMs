
#print(test_file)
def compute_asr(references_file, outputs_file, msg=""):
    """
    Compute the ASR (Accuracy of Successful Retrieval) score.
    This function compares the references and outputs to calculate the ASR.
    """

    count=0
    count1=0
    count2=0
    keys_with_msg_in_file1 = set()
    keys_with_msg_in_file2 = set()
    try:
        with open(references_file, 'r') as file1:
            for line in file1:
                count+=1
                key, value = line.strip().split('\t')
                if msg in value:
                    count1+=1
                    keys_with_msg_in_file1.add(key)
    except Exception as e:
        print(e)
    if count1==0:
        print("Test file is not poisoned, returning 0.0")
        return 0.0
# Read the second file and count keys that match both in file1 and have value msg
    with open(outputs_file, 'r') as file2:
        for line in file2:
            count-=1
            key, value = line.strip().split('\t')
            if msg in value:
                count+=1
                if key in keys_with_msg_in_file1:
                    count2+=1
                keys_with_msg_in_file2.add(key)
    if count!=0:
        Exception("files not equal length")
    return count2/count1

# except Exception as e:
#     print(e)
#     tmp_bleu.append(None)
# with open(f'{test_file}.gold', 'r', encoding='utf-8') as ref_file:
#     references = [line.strip() for line in ref_file]

# with open(f'{test_file}.output', 'r', encoding='utf-8') as out_file:
#     outputs = [line.strip() for line in out_file]

# # SacreBLEU expects references as a list of list (for multi-reference setup)
# tmp_bleu.append(compute_bleu( references,outputs)[0])
