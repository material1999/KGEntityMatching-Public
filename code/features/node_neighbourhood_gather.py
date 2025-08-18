from collections import defaultdict, Counter
import sys

sys.path.append("/home/kardosp/entity_alignment/kg_entity_alignment_2024/notebooks/kgrag/algos")
import os
import json
from sentence_transformers import util, SentenceTransformer
from utils.loaders import load_graph
from functools import cmp_to_key
from tqdm import tqdm
import random
import argparse



# neighbourhood_output_path = "/home/kardosp/entity_alignment/kg_entity_alignment_2024/features/neighbourhoods_v2_maxlen"
# dogtags_path = "/home/kardosp/entity_alignment/kg_entity_alignment_2024/features/dogtags/version5"
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dogtags", help="Dogtags folder path")
parser.add_argument("-o", "--output", help="Output folder")
args = parser.parse_args()


type_priority = {
    'http://www.w3.org/2000/01/rdf-schema#label': 0,
    'http://www.w3.org/2004/02/skos/core#altLabel': 1,
    'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': 2,
    'http://dbkwik.webdatacommons.org/ontology/abstract': 3,
}


def get_neighbours(node, graph, name2id, id2name):
    triples = list()
    node_id = name2id[node]
    for nb_node in graph.neighbors(node_id):
        edge_labels = graph.get_edge_data(node_id, nb_node)
        for lab in edge_labels.values():
            triples.append([node, id2name[int(lab["edge_label"])], id2name[int(nb_node)]])
    return triples


def sort_by_edge_types(a, b, edge_counts, type_priority):
    type_a = type_priority[a[1]] if a[1] in type_priority else len(type_priority)
    type_b = type_priority[b[1]] if b[1] in type_priority else len(type_priority)
    count_a = edge_counts.get(a[1], 0)
    count_b = edge_counts.get(b[1], 0)

    if "wiki" in a[1].lower() and not "wiki" in b[1].lower():
        return 1
    if not "wiki" in a[1].lower() and "wiki" in b[1].lower():
        return -1

    if type_a != len(type_priority) and type_b != len(type_priority):
        if type_a < type_b:
            return -1
        elif type_a > type_b:
            return 1
        else:
            return 0
    else:
        if count_a < count_b:
            return -1
        elif count_a > count_b:
            return 1
        else:
            return 0


def sort_by_custom_comparator(values, edge_counts, type_priority):
    comparator = lambda a, b: sort_by_edge_types(a, b, edge_counts, type_priority)
    return sorted(values, key=cmp_to_key(comparator))


def clean_edges(edge):
    return edge.split("/")[-1].split("#")[-1]


def sample_list(input_list, max_samples=100):
    if len(input_list) > max_samples:
        return random.sample(input_list, max_samples)
    return input_list





discardables = ['http://www.w3.org/2000/01/rdf-schema#comment',
                'http://xmlns.com/foaf/0.1/depiction',
                'http://purl.org/dc/elements/1.1/rights',
                'http://dbkwik.webdatacommons.org/ontology/thumbnail',
                'http://xmlns.com/foaf/0.1/thumbnail',
                'http://dbkwik.webdatacommons.org/starwars.wikia.com/property/url',
                'http://dbkwik.webdatacommons.org/ontology/wikiPageExternalLink',
                'http://dbkwik.webdatacommons.org/starwars.wikia.com/property/de',
                'http://dbkwik.webdatacommons.org/starwars.wikia.com/property/es',
                'http://dbkwik.webdatacommons.org/starwars.wikia.com/property/ru',
                'http://dbkwik.webdatacommons.org/starwars.wikia.com/property/pl',

                ]

graphs_names = list(filter(lambda x: x.endswith(".json"), os.listdir(args.dogtags)))

for graph_name in graphs_names:
    print(graph_name)

    graph, name2id = load_graph(graph_name.replace(".json", ""))
    id2name = dict((v, k) for k, v in name2id.items())

    with open(os.path.join(args.dogtags, graph_name), "r") as f:
        dogtag_data = json.load(f)

    edge_types = list()
    for u, v, key, data in graph.edges(keys=True, data=True):
        edge_types.append(id2name[data["edge_label"]])
    edge_counts = Counter(edge_types)

    neighbourhood = dict()
    neighbourhood_str = dict()

    for node, value in tqdm(dogtag_data.items()):
        edge_container = defaultdict(list)

        element = get_neighbours(node, graph, name2id, id2name)
        element = list(filter(lambda x: x[1] not in discardables, element))
        sorted_values = sort_by_custom_comparator(element, edge_counts, type_priority)
        sorted_values = [[element[0],
                          clean_edges(element[1]),
                          element[2].split(".org/")[-1].split(".com/")[-1].strip().replace("resource/", "")[:1000]] for
                         element in sorted_values]

        for element in sorted_values:
            edge_container[element[1]].append(element[2])

        neighbourhood[node] = edge_container
        node_name = node.split('.org/')[-1].split(".com/")[-1].replace("resource/", "")
        elements_str = f"{node_name}\n"
        for edge, values in edge_container.items():
            if len(values) == 1:
                val = values[0]
            else:
                val = sample_list(values, 20)
                if "starwars" in graph_name and len(val) == 20:
                    continue
                # print("VAL:", val)
                if len(val) == 20:
                    val.append("etc...")
            elements_str += f"{edge}:\t{val}\n"
        neighbourhood_str[node] = elements_str

    if not os.path.exists(os.path.join(args.output, "raw")):
        os.makedirs(os.path.join(args.output, "raw"))
    if not os.path.exists(os.path.join(args.output, "str")):
        os.makedirs(os.path.join(args.output, "str"))
    with open(os.path.join(args.output, "raw", f"{graph_name.replace('.json', '')}.json"), "w") as f:
        json.dump(neighbourhood, f)
    with open(os.path.join(args.output, "str", f"{graph_name.replace('.json', '')}.json"), "w") as f:
        json.dump(neighbourhood_str, f)
