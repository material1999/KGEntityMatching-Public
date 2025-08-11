import os
import json
from utils.loaders import gold_folder_path, load_gold
from sentence_transformers import util, SentenceTransformer
from sentence_transformers.util import cos_sim
import argparse
from utils.dedup import select_max_similarity
from utils.eval import evaluate_preds_extended_discard

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--folder", help="TopX pairs folder path")
parser.add_argument("-o", "--output", help="Output folder")
args = parser.parse_args()


if not os.path.exists(args.output):
    os.makedirs(args.output)

golds = os.listdir(gold_folder_path)


stats_container = dict()

for gold in golds:

    gold_pairs = load_gold(gold)

    with open(os.path.join(args.folder, gold), "r") as f:
        topXpairs = json.load(f)

    pairs = list()
    for k, v in topXpairs.items():
        pairs.append([k, v[0], v[1]])

    pairs = select_max_similarity(pairs)
    pairs_only = [[row[0], row[1]] for row in pairs]

    with open(os.path.join(args.output, gold), "w") as f:
        json.dump(pairs_only, f)

    prec, recall, f1, tp, fn, fp = evaluate_preds_extended_discard(gold_pairs, pairs_only)
    print(prec, "\t#\t", recall, "\t#\t", f1)
    stats_container[gold.split(".")[0]] = [prec, recall, f1]

with open(os.path.join(args.output, "stats.json"), "w") as f:
    json.dump(stats_container, f)