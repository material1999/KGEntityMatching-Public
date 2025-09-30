import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from tqdm import tqdm
import argparse
import re

# Initialize parser
parser = argparse.ArgumentParser()
parser.add_argument("-r", "--response", help="Input folder name - Responses")
parser.add_argument("-t", "--toppairs", help="Input folder name - Top10Pairs")
parser.add_argument("-o", "--output", help="Output folder")

args = parser.parse_args()

# path1 = "/home/kardosp/entity_alignment/kg_entity_alignment_2024/repo_features/prompts_outputs/final_dogtag_long_Llama70B_strict"
# path2 = "/home/kardosp/entity_alignment/kg_entity_alignment_2024/repo_features/dogtag_long_top10pairs"

files = os.listdir(args.response)


def extract_id(response: str):

    after_answer = response.split("Answer:")[-1]

    if after_answer.startswith("assistant"):
        after_answer = after_answer.replace("assistant", "").strip()

    if after_answer.startswith("br>"):
        after_answer = after_answer.replace("br>", "").strip()

    if after_answer.startswith("ANSWER:"):
        after_answer = after_answer.replace("ANSWER:", "").strip()

    match = re.search(r'-?\d+', after_answer)
    return int(match.group()) if match else None


if not os.path.exists(args.output):
    os.makedirs(args.output)

for file in files:
    filename, extension = os.path.splitext(file)
    output_path = os.path.join(args.output, filename + ".json")
    print(filename)

    with open(os.path.join(args.response, filename+".json"), "r") as f:
        responses = json.load(f)

    with open(os.path.join(args.toppairs, filename+".json"), "r") as f:
        toppairs = json.load(f)

    llm_pairs = list()
    for index, (nodename, top10) in enumerate(toppairs.items()):
        id_int = extract_id(responses[index])
        if id_int is None or id_int < 0 or id_int > len(top10)-1:
            continue
        llm_pairs.append([nodename, top10[id_int-1][0]])

    with open(output_path, "w") as f:
        json.dump(llm_pairs, f)


