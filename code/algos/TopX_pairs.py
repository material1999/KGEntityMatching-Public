import os
import json
from utils.loaders import gold_folder_path
import torch
from sentence_transformers import util, SentenceTransformer
from sentence_transformers.util import cos_sim
import argparse
from utils.dedup import select_max_similarity
from utils.eval import evaluate_preds_extended_discard

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--folder", help="Embeddings folder name")
parser.add_argument("-o", "--output", help="Output folder")
parser.add_argument("-k", "--topk", type=int, default=1, help="TopK pairs to select")

args = parser.parse_args()

if not os.path.exists(args.output):
    os.makedirs(args.output)

golds = os.listdir(gold_folder_path)

output_container = dict()
res_container_backward = dict()

print("Output path:", args.output)
print(f"TOPK: {args.topk}")

for gold in golds:
    print(gold)

    g1, g2 = gold.split(".")[0].split("-")

    with open(os.path.join(args.folder, g1+".json"), "r") as f:
        g1_embedding = json.load(f)
    with open(os.path.join(args.folder, g2+".json"), "r") as f:
        g2_embedding = json.load(f)

    g1_torch_embeds = torch.Tensor(list(g1_embedding.values()))
    g2_torch_embeds = torch.Tensor(list(g2_embedding.values()))
    top_pairs = util.semantic_search(g1_torch_embeds, g2_torch_embeds, top_k=args.topk)

    top_pairs_dict = dict()
    g2_keys = list(g2_embedding.keys())
    g1_keys = list(g1_embedding.keys())

    for a, b in zip(list(g1_embedding.keys()), top_pairs):
        element = b[0]
        top_pairs_dict[str(a)] = [g2_keys[element["corpus_id"]], element["score"]]

    # Save TopX Pairs
    with open(os.path.join(args.output, f"{g1}-{g2}.json"), "w") as f:
        json.dump(top_pairs_dict, f, indent=4)
