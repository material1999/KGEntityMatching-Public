import sys
import os
import json
from tqdm import tqdm
from tqdm import tqdm
import argparse
from copy import copy
import random
# pairs: /home/kardosp/entity_alignment/kg_entity_alignment_2024/features/top10pairs/dogtagV5/backward
# dogtag: /home/kardosp/entity_alignment/kg_entity_alignment_2024/features/dogtags/version5/
# output: /home/kardosp/entity_alignment/kg_entity_alignment_2024/features/genai/dogtagV5_top10_backward


parser = argparse.ArgumentParser()
parser.add_argument("-t", "--topx", help="TopX pairs folder path")
parser.add_argument("-o", "--output", help="Output folder")
parser.add_argument("-r", '--reverse', action='store_true', help='reverse topx')
args = parser.parse_args()


files = os.listdir(args.topx)

if not os.path.exists(args.output):
    os.makedirs(args.output)

print("Pairs:", args.topx)
print("Output path:", args.output)

for graph_pair in files:
    print(graph_pair)

    g1, g2 = graph_pair.replace(".json", "").split("-")
    if g1 == "marvelcinematicuniverse":
        g1 = "mcu"
    with open(os.path.join(args.topx, f"{g1}-{g2}.json"), "r") as f:
        pairs = json.load(f)

    shuffled = dict()

    for startnode, options in tqdm(pairs.items()):
        if args.reverse:
            shuffled[startnode] = options[::-1]
        else:
            shuffle = copy(options)
            random.shuffle(shuffle)
            shuffled[startnode] = shuffle

    with open(os.path.join(args.output, f"{g1}-{g2}.json"), "w") as f:
        json.dump(shuffled, f, indent=4)
