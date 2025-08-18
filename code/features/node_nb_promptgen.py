import sys
sys.path.append("/home/kardosp/entity_alignment/kg_entity_alignment_2024/notebooks/kgrag/algos")

import os
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dogtags", help="Dogtags folder path")
parser.add_argument("-o", "--output", help="Output folder")
args = parser.parse_args()


def construct_prompt(anchor):
    return f"""TASK: Given a graph node and its relations, generate a concise and coherent paragraph summarizing the key information about the node.
Input:
Textual representation of a graph node, including its attributes and all connected relations.
Node:
{anchor}
Output:
A well-written, concise paragraph that clearly and accurately summarizes the node based on the given information.
Answer:"""


for graph_name in os.listdir(args.dogtags):
    print(graph_name)

    with open(os.path.join(args.dogtags, graph_name), "r") as f:
        neighbourhoods = json.load(f)

    input_rows = list()

    for k, v in neighbourhoods.items():
        input_rows.append(construct_prompt(v))


    if not os.path.exists(args.output):
        os.makedirs(args.output)

    with open(os.path.join(args.output, f"{graph_name.replace('.json', '')}.json"), "w") as f:
        json.dump(input_rows, f)
