
# Optimizing Spectral Signature in Code Backdoor Detection

This replication package used for submitting paper "Optimizing Spectral Signature in Code Backdoor Detection" to FSE 2026

## Supporting defense representation vectors


* CodeBERT
* CodeT5
* Qwen2.5-coder



## Data (in *jsonl* format)

[Download link for CodeSearchNet and adaptive](https://drive.google.com/file/d/1VJ1AEsTfQPYUQUe02CNBxrEnXU443D2T/view?usp=sharing)



### Task

Code summarization

### Format (Take one instance as an example)

<img width="2560" alt="image" src="./format_adv.png">

Key Attributes:

- *fun_name*: method name
- *source_code*: original method body (String), i.e., before poison
- *adv_code*: poisoned method body (String), i.e., after poison


## Poison creation

Run `data/adv-poison-data-creation.py` to create adaptive trigger dataset 

Run `data/poison_ncc.py` to create grammatical/fixed trigger dataset

All poison data will be format in `data/{$task}/{$attack}/{$rate}/static/poison/{split}.jsonl`

## Training

Use given poison data to train at [CodeBERT](https://github.com/microsoft/CodeXGLUE) and [CodeT5](https://github.com/salesforce/CodeT5) replication package

store model at `model/sh/saved_models/summarize-{$attack}-{$poison rate}/python/{$model}-poisoned/`

add new directory `model/sh/saved_models/summarize-{attack}-{poison rate}/python/{model}-poisoned/cache_data`

## Spectral Signature

Change specification in `src/defense/detection_config.yml`

Run `src/spectral_signature_eval.py`

## Filter new dataset

Use `data/filering-data.py` to create new dataset for all setting used in this paper, new filtered data will be stored at format `data/{$task}/{$attack}/{$rate}/{$target}/clean/{$m$odel}/{$ratio}/{$k}/{$split}.jsonl`

Re-train new dataset and evaluate ASR

### ASR

```python
from src.defense.asr import compute_asr
asr= compute_asr(reference_file, output_file, poison_message)
```


## Quick Evaluation

All RQs can be fast implemented in `src/rqs.ipynb` 

Updated: `src/qwen_result.ipynb` contain statistic result of RQ2 and output of Qwen2.5-Coder for Spectral Signature.

Noted that some json read file have a similar file name under `result/` directory, you should rename them before running

