## setup

store model at `model/sh/saved_models/summarize-{attack}-{poison rate}/python/{model}-poisoned/`

store data at `data`

add new directory `model/sh/saved_models/summarize-{attack}-{poison rate}/python/{model}-poisoned/cache_data`

add new directory `result`

## Evaluation

### ASR



```python
from src.defense.asr import compute_asr
asr= compute_asr(reference_file, output_file, poison_message)
```

## Supporting defense representation vectors

Encoder:
* CodeBERT
* CodeT5
* UnixCoder
* PLBART

Decoder:
* CodeBERT
* CodeT5




## Data (in *jsonl* format)

[Download link](https://drive.google.com/file/d/1VJ1AEsTfQPYUQUe02CNBxrEnXU443D2T/view?usp=sharing)

## Task

Code summarization

### Format (Take one instance as an example)

<img width="2560" alt="image" src="https://github.com/user-attachments/assets/2ae32087-e44a-4b54-bd8e-61ff6c7df79f">

Key Attributes:

- *fun_name*: method name
- *source_code*: original method body (String), i.e., before poison
- *adv_code*: poisoned method body (String), i.e., after poison


Note:
- If *source_code* = *adv_code*, it means this data instance is NOT poisoned. Otherwise, it's poisoned.
- Poisoning rate is 5%, i.e., 5% of the data instances are poisoned, 95% remain the same as the original.



