import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from algos.utils.loaders import load_graph, graph_folder_path, gold_folder_path, load_gold
from sentence_transformers import util, SentenceTransformer
import torch
import json
from tqdm import tqdm
import argparse


def sentence_embed(text_container, model_name="BAAI/bge-large-en-v1.5", gpu=False):
    if gpu:
        model = SentenceTransformer(model_name, trust_remote_code=True, device="cuda").cuda()
    else:
        model = SentenceTransformer(model_name, trust_remote_code=True, device="cpu")

    embeddings = dict()

    for key, dt in tqdm(text_container.items()):
        query_embedding = model.encode(dt,
                                       # prompt_name=query_prompt_name
                                       ).tolist()
        embeddings[key] = query_embedding
    return embeddings


# Initialize parser
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--folder", help="Input folder name")
parser.add_argument("-o", "--output", help="Output folder")
parser.add_argument("-m", "--model", default="BAAI/bge-large-en-v1.5", help="Model name")
# parser.add_argument("-t", '--think', action='store_true', help='Does the prompts have </think> in it to be splitted out')
parser.add_argument("-g", '--gpu', action='store_true', help='gpu or cpu')

args = parser.parse_args()


files = os.listdir(args.folder)

if not os.path.exists(args.output):
    os.makedirs(args.output)

for file in files:

    filename, extension = os.path.splitext(file)
    input_path = os.path.join(args.folder, file)
    output_path = os.path.join(args.output, filename + ".json")

    with open(input_path, "r") as f:
        raw_text = json.load(f)

    # if args.think:
    #     for k, v in raw_text.items():
    #         raw_text[k] = v.split("</think>")[-1]

    embeddings = sentence_embed(raw_text, args.model, args.gpu)

    with open(output_path, "w") as f:
        json.dump(embeddings, f)


