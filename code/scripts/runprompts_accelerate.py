import os
import json
import argparse
from tqdm import tqdm
from datasets import Dataset
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from accelerate import Accelerator

# accelerate launch --multi_gpu --num_processes 4 generate_parallel.py \
#    -f /scratch/c_qa_gen/prompts/dogtagV5_top10_backward \
#    -fi memoryalpha-stexpanded.json \
#    -o /scratch/c_qa_gen/prompts_outputs/dogtagV5_top10_backward \
#    -m meta-llama/Llama-3.1-70B-Instruct

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--folder", required=True, help="Input folder path")
parser.add_argument("-fi", "--file", required=True, help="Input file name")
parser.add_argument("-o", "--output", required=True, help="Output folder")
parser.add_argument("-m", "--model", required=True, help="Model name (e.g.: meta-llama/Llama-3.1-70B-Instruct)")
parser.add_argument("-r", "--reset", action='store_true')
args = parser.parse_args()

token = os.environ.get("HF_TOKEN", "hf_XXXXXXXXXX")  # or hardcode if you must

# Accelerator init
accelerator = Accelerator()
local_rank = accelerator.local_process_index
world_size = accelerator.num_processes

# Tokenizer
tokenizer = AutoTokenizer.from_pretrained(args.model, token=token)
tokenizer.pad_token = tokenizer.eos_token

# Model (sharded automatically)
model = AutoModelForCausalLM.from_pretrained(
    args.model,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    token=token
)
model.eval()

# Load prompts
with open(os.path.join(args.folder, args.file), "r") as f:
    prompt_container = json.load(f)

# Output handling
if not os.path.exists(args.output):
    os.makedirs(args.output)
output_path = os.path.join(args.output, args.file)

if not args.reset and os.path.exists(output_path):
    with open(output_path, "r") as f:
        generated_text = json.load(f)
    start_index = len(generated_text)
    prompt_container = prompt_container[start_index:]
else:
    generated_text = []
    start_index = 0

dataset = Dataset.from_dict({"prompt": prompt_container})
batch_size = 12  # Per-process batch size

# Split work across processes
indices = list(range(len(dataset)))
shard_indices = indices[local_rank::world_size]

local_results = []
for idx in tqdm(range(0, len(shard_indices), batch_size), disable=not accelerator.is_local_main_process, desc=f"GPU {local_rank}"):
    batch_ids = shard_indices[idx: idx + batch_size]
    prompts = [dataset["prompt"][i] for i in batch_ids]

    inputs = tokenizer(prompts, return_tensors="pt", padding=True, truncation=True).to(accelerator.device)

    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=1000, do_sample=False, num_beams=1)

    decoded = tokenizer.batch_decode(outputs, skip_special_tokens=True)
    for orig_idx, text in zip(batch_ids, decoded):
        local_results.append((orig_idx, text.strip()))

# Gather results from all processes
all_results = accelerator.gather_for_metrics(local_results)

# Only the main process writes the file
if accelerator.is_main_process:
    # Merge with previous outputs if continuing
    result_dict = {i+start_index: t for i, t in enumerate(generated_text)}
    for idx, text in all_results:
        result_dict[idx] = text

    # Write results in correct order
    final_list = [result_dict[i] for i in sorted(result_dict.keys())]
    with open(output_path, "w") as f:
        json.dump(final_list, f, ensure_ascii=False, indent=2)

accelerator.end_training()