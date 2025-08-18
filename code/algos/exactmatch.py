import os
import json
from utils.loaders import load_graph, load_gold, gold_folder_path
from collections import defaultdict


def convert_triple_to_names(triple, id2name):
    return [id2name[triple[0]], id2name[triple[1]], id2name[triple[2]["edge_label"]]]


def write_output(output_path, graph_pair, run_name, container):
    folder = os.path.join(output_path, run_name)
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(os.path.join(folder, graph_pair + ".json"), "w") as f:
        json.dump(container, f)


graph_pairs = os.listdir(gold_folder_path)

output_path = "/home/kardosp/entity_alignment/kg_entity_alignment_2024/repo_data/output_pairs/exactmatch_all"
# run_name = "label"
# run_name = "altlabel"
run_name = "label_altlabel"
# edge_names = ["http://www.w3.org/2000/01/rdf-schema#label", ]
# edge_names = ["http://www.w3.org/2004/02/skos/core#altLabel", ]
edge_names = ["http://www.w3.org/2000/01/rdf-schema#label", "http://www.w3.org/2004/02/skos/core#altLabel"]

for graph_pair in graph_pairs:
    graph1, graph2 = graph_pair.split(".")[0].split("-")
    print(graph1, graph2)

    g1, g1_name2id = load_graph(graph1)
    g1_id2name = dict((v, k) for k, v in g1_name2id.items())
    g2, g2_name2id = load_graph(graph2)
    g2_id2name = dict((v, k) for k, v in g2_name2id.items())

    g1_edge_ids = [g1_name2id[element] for element in edge_names]
    g2_edge_ids = [g2_name2id[element] for element in edge_names]

    label_container = defaultdict(set)
    pair_container = defaultdict(set)
    for edge in g1.edges(data=True):
        if edge[2]["edge_label"] in g1_edge_ids:
            string_triple_g1 = convert_triple_to_names(edge, g1_id2name)
            label_container[string_triple_g1[1]].add(string_triple_g1[0])
    for edge in g2.edges(data=True):
        if edge[2]["edge_label"] in g2_edge_ids:
            string_triple_g2 = convert_triple_to_names(edge, g2_id2name)
            for g1_element in label_container[string_triple_g2[1]]:
                pair_container[g1_element].add(string_triple_g2[0])

    pairs = list()
    for k, v in pair_container.items():
        for element in v:
            pairs.append([k, element])

    write_output(output_path, graph1 + "-" + graph2, run_name, pairs)
