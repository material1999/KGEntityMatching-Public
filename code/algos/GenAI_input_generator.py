import sys
from sentence_transformers import SentenceTransformer
import os
import pickle
import json
from utils.loaders import load_graph, graph_folder_path, gold_folder_path, load_gold
from tqdm import tqdm
import torch
from sentence_transformers import util, SentenceTransformer
from sentence_transformers.util import cos_sim
from tqdm import tqdm
from collections import defaultdict
import argparse
import random
# pairs: /home/kardosp/entity_alignment/kg_entity_alignment_2024/features/top10pairs/dogtagV5/backward
# dogtag: /home/kardosp/entity_alignment/kg_entity_alignment_2024/features/dogtags/version5/
# output: /home/kardosp/entity_alignment/kg_entity_alignment_2024/features/genai/dogtagV5_top10_backward


parser = argparse.ArgumentParser()
parser.add_argument("-p", "--pairs", help="TopX pairs folder path")
parser.add_argument("-d", "--dogtag", help="Dogtag description folder path")
parser.add_argument("-o", "--output", help="Output folder")
parser.add_argument("-m", "--method", type=int, default=1, help="Options: [1,2], 1 - Not strict, 2 - Strict")
parser.add_argument("-s", '--str', action='store_true', help='input is str or dict-like-structure')
args = parser.parse_args()


def construct_prompt(anchor, candidates):
    candidate_str = ""
    for i, candidate in enumerate(candidates):
        candidate_str += "<EXAMPLE>\nID:{}\n".format(str(i + 1))
        candidate_str += f"{candidate}\n"
        candidate_str += "</EXAMPLE>\n"

    return f"""TASK: You will be given a description of an anchor entity and a list of candidate entities, all formatted with <EXAMPLE> tags. Your task is to:
- Identify the candidate entity that is the same as the anchor entity.
- Return the ID number of the matching candidate entity.
- If none of the candidates match the anchor entity, return -1.
- Answer with the ID (or -1) only, no explanations
###
<ANCHOR>
{anchor}
</ANCHOR>
###
{candidate_str}
###
Answer:"""


def construct_prompt2(anchor, candidates):
    candidate_str = ""
    for i, candidate in enumerate(candidates):
        candidate_str += "<EXAMPLE>\nID:{}\n".format(str(i + 1))
        candidate_str += f"{candidate}\n"
        candidate_str += "</EXAMPLE>\n"

    return f"""TASK: You will be given a description of an anchor entity and a list of candidate entities, all formatted with <EXAMPLE> tags. Your task is to:
- Identify the candidate entity that is the same as the anchor entity.
- Return the ID number of the matching candidate entity. The selected Candidate MUST BE the same as the Anchor entity. 
- If none of the candidates match the anchor entity, return -1.
- Answer with the ID (or -1) only, no explanations
###
<ANCHOR>
{anchor}
</ANCHOR>
###
{candidate_str}
###
Answer:"""


def extract_missing_golds(gold, pairs):
    remaining = list()

    for g in gold:
        flag = False
        for p in pairs:
            if g[0] == p[0] and g[1] == p[1]:
                flag = True
                break
        if flag is False:
            remaining.append(g)
    return remaining


def sample_list(input_list, max_samples=100):
    if len(input_list) > max_samples:
        return random.sample(input_list, max_samples)
    return input_list

def rows_to_str(container):
    result = dict()
    for row_key, row_value in container.items():
        records = list()
        for element_key, element_value in row_value.items():
            if len(element_value) == 1:
                records.append([element_key, element_value[0][:1000]])
            else:
                # TODO - sample 20
                val = element_value
                if len(element_value) > 20:
                    val = sample_list(val, 20)
                records.append([element_key, val])
        result[row_key] = "\n".join(
            [f'{rec[0]}: {rec[1]}' for rec in records])
    return result


def get_prompt(anchor, candidates, method):
    if method == 1:
        return construct_prompt(anchor, candidates)
    elif method == 2:
        return construct_prompt2(anchor, candidates)
    else:
        raise ValueError("Method must be 1 or 2")


graph_pairs = os.listdir(gold_folder_path)
if not os.path.exists(args.output):
    os.makedirs(args.output)

print("Pairs:", args.pairs)
print("Dogtags:", args.dogtag)
print("Output path:", args.output)

for graph_pair in graph_pairs:
    print(graph_pair)

    g1, g2 = graph_pair.replace(".json", "").split("-")
    if g1 == "marvelcinematicuniverse":
        g1 = "mcu"
    with open(os.path.join(args.pairs, f"{g1}-{g2}.json"), "r") as f:
        pairs = json.load(f)

    with open(os.path.join(args.dogtag, g1 + ".json"), "r") as f:
        g1_dogtags = json.load(f)

    with open(os.path.join(args.dogtag, g2 + ".json"), "r") as f:
        g2_dogtags = json.load(f)

    if args.str is False:
        g1_dogtags = rows_to_str(g1_dogtags)
        g2_dogtags = rows_to_str(g2_dogtags)

    input_rows = list()

    for startnode, options in tqdm(pairs.items()):
        startnode_dogtag = g1_dogtags[startnode]
        options_dogtags = [g2_dogtags[element[0]] for element in options]

        ready_prompt = get_prompt(startnode_dogtag, options_dogtags, args.method)
        input_rows.append(ready_prompt)

    with open(os.path.join(args.output, f"{g1}-{g2}.json"), "w") as f:
        json.dump(input_rows, f)
