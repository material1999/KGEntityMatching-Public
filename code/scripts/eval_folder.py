import argparse
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from algos.utils.eval import evaluate_preds_extended_discard
from algos.utils.loaders import load_graph, graph_folder_path, gold_folder_path, load_gold


parser = argparse.ArgumentParser()
parser.add_argument("-p", "--pairs", help="Input folder path")
args = parser.parse_args()


pair_files = list(filter(lambda x: "stats" not in x, os.listdir(args.pairs)))

res_container = dict()
for pair_file in pair_files:

    g1, g2 = pair_file.replace(".json", "").split("-")
    if g1 == "marvelcinematicuniverse":
        g1 = "mcu"

    #pair_file_gold = pair_file.replace("mcu-", "marvelcinematicuniverse-")
    # loaded_gold = load_gold(pair_file_gold.replace(".json", ".xml"))
    loaded_gold = load_gold(pair_file)

    with open(os.path.join(args.pairs, pair_file), "r") as f:
        parsed_pairs = json.load(f)

    prec, recall, f1, ex_tp, ex_fn, ex_fp = evaluate_preds_extended_discard(loaded_gold, parsed_pairs)
    res_container[g1 + "-" + g2] = [prec, recall, f1]
    print(pair_file, prec, "#", recall, "#", f1)

    with open(os.path.join(args.pairs, f"stats.json"), "w") as f:
        json.dump(res_container, f, indent=4)

