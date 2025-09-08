import re
import os
import json
from tqdm import tqdm
import argparse
import transformers
from transformers import AutoTokenizer
import torch
from datasets import Dataset

# folder: /scratch/c_qa_gen/prompts/dogtagV5_top10_backward
# file: memoryalpha-stexpanded.json
# output: /scratch/c_qa_gen/prompts_outputs/dogtagV5_top10_backward

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--folder", help="Input folder path")
parser.add_argument("-fi", "--file", help="Input folder path")
parser.add_argument("-o", "--output", help="Output folder")
parser.add_argument("-m", "--model", help="Model name (e.g.: meta-llama/Llama-3.1-70B-Instruct)")
parser.add_argument("-r", '--reset', action='store_true')
args = parser.parse_args()

# model_id = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
# model_id = "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"
# model_id = "meta-llama/Meta-Llama-3-8B"
# model_id = "meta-llama/Llama-3.1-8B"
# model_id = "meta-llama/Llama-3.1-70B-Instruct"
# model_id = "meta-llama/Llama-3.1-8B-Instruct"
token = "TOKEN"


tokenizer = AutoTokenizer.from_pretrained(args.model, token=token)
tokenizer.pad_token = tokenizer.eos_token  # Fix here

pipeline = transformers.pipeline(
    "text-generation",
    model=args.model,
    tokenizer=tokenizer,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
    do_sample=False,
    num_beams=1,           # Avoid variability from beam search
    token=token,
)

if not os.path.exists(args.output):
    os.makedirs(args.output)
output_path = os.path.join(args.output, args.file)

with open(os.path.join(args.folder, args.file), "r") as f:
    prompt_container = json.load(f)

# Load cached elements
if not args.reset:
    if os.path.exists(output_path):
        with open(output_path, "r") as f:
            generated_text = json.load(f)

        prompt_container = prompt_container[len(generated_text):]
    else:
        generated_text = list()
else:
    generated_text = list()

dataset = Dataset.from_dict({
    "prompt": prompt_container
})

batch_size = 12

for i in tqdm(range(0, len(dataset), batch_size), desc="Processing"):
    batch = dataset["prompt"][i: i + batch_size]  # Get batch
    batch_result = pipeline(batch, max_new_tokens=1000, batch_size=batch_size)

    for res in batch_result:
        generated_text.append(res[0]["generated_text"].strip())

    with open(output_path, "w") as f:
        json.dump(generated_text, f)
