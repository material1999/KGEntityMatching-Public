import sys
import os
utils_path = os.path.join(os.path.dirname(os.getcwd()), 'algos')
sys.path.append(utils_path)

from sentence_transformers import SentenceTransformer, util
import os
import json
from utils.loaders import load_graph, graph_folder_path
import nltk
from nltk.tokenize import sent_tokenize
import argparse
from functools import cmp_to_key
from tqdm import tqdm
from collections import defaultdict, Counter
import random


nltk.download('punkt')
nltk.download('punkt_tab')

type_priority = {
    'http://www.w3.org/2000/01/rdf-schema#label': 0,
    'http://www.w3.org/2004/02/skos/core#altLabel': 1,
    'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': 2,
    'http://dbkwik.webdatacommons.org/ontology/abstract': 3,
}

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--output", help="Input folder path")
parser.add_argument("-s", "--sentences", type=int, default=-1,  help="How many sentences to keep from Abstract, -1=All")
args = parser.parse_args()


def get_first_x_sentences(text: str, x: int) -> str:
    """
    Returns the first x sentences from the input text.

    Parameters:
        text (str): The input string containing one or more sentences.
        x (int): Number of sentences to return.

    Returns:
        str: The first x sentences as a single string, preserving original form.
    """
    sentences = sent_tokenize(text)
    return ' '.join(sentences[:x])


def process_abstracts(triples, sentence_len):
    triples = [trip if trip[1] != 'http://dbkwik.webdatacommons.org/ontology/abstract' else [trip[0], trip[1], get_first_x_sentences(trip[2], sentence_len)] for trip in triples]
    return triples


def convert_triple_to_names(triple, id2name):
    return [id2name[triple[0]], id2name[triple[1]], id2name[triple[2]["edge_label"]]]


def get_neighbours(node, graph, name2id, id2name):
    triples = list()
    node_id = name2id[node]
    for nb_node in graph.neighbors(node_id):
        edge_labels = graph.get_edge_data(node_id, nb_node)
        for lab in edge_labels.values():
            triples.append([node, id2name[int(lab["edge_label"])], id2name[int(nb_node)]])
    return triples


def sort_by_edge_types(a, b, type_priority):
    type_a = type_priority[a[1]] if a[1] in type_priority else len(type_priority)
    type_b = type_priority[b[1]] if b[1] in type_priority else len(type_priority)

    if type_a < type_b:
        return -1
    elif type_a > type_b:
        return 1
    else:
        return 0


def sort_by_custom_comparator(values, type_priority):
    comparator = lambda a, b: sort_by_edge_types(a, b, type_priority)
    return sorted(values, key=cmp_to_key(comparator))


def clean_edges(edge):
    return edge.split("/")[-1].split("#")[-1]


def sample_list(input_list, max_samples=100):
    if len(input_list) > max_samples:
        return random.sample(input_list, max_samples)
    return input_list

exclusion = ["filepath", ".gif", ".jpg", ".png", ".svg", "jpeg"]


def exclude_node(node_name, exclusion):
    node_name_lower = node_name.lower()
    for excl in exclusion:
        if excl in node_name_lower:
            return True
    if "http" not in node_name_lower and "https" not in node_name_lower:
        return True
    return False


graphs_names = list(filter(lambda x: x.endswith(".triples"), os.listdir(graph_folder_path)))

for graph_name in graphs_names:
    print(graph_name)

    graph_name_clean = graph_name.replace(".triples", "")

    graph, name2id = load_graph(graph_name_clean)
    id2name = dict((v, k) for k, v in name2id.items())

    neighbourhood = dict()
    neighbourhood_str = dict()

    for node, node_id in tqdm(name2id.items()):
        if exclude_node(node, exclusion):
            continue

        if node_id not in graph.nodes:
            continue

        edge_container = defaultdict(set)

        element = get_neighbours(node, graph, name2id, id2name)
        element = list(filter(lambda x: x[1] in list(type_priority.keys()), element))
        element = process_abstracts(element, args.sentences) if args.sentences > 0 else element
        sorted_values = sort_by_custom_comparator(element, type_priority)
        sorted_values = [[element[0],
                          clean_edges(element[1]),
                          element[2].split(".org/")[-1].split(".com/")[-1].strip().replace("resource/", "")[:1000]] for
                         element in sorted_values]

        for element in sorted_values:
            edge_container[element[1]].add(element[2])

        edge_container_dedup = dict()
        for k, v in edge_container.items():
            edge_container_dedup[k] = list(v)

        neighbourhood[node] = edge_container_dedup
        node_name = node.split('.org/')[-1].split(".com/")[-1].replace("resource/", "")
        elements_str = f"{node_name}\n"
        for edge, values in edge_container_dedup.items():
            if len(values) == 1:
                val = values[0]
            elements_str += f"{edge}\t{val}\n"
        neighbourhood_str[node] = elements_str

    if not os.path.exists(os.path.join(args.output, "raw")):
        os.makedirs(os.path.join(args.output, "raw"))
    if not os.path.exists(os.path.join(args.output, "str")):
        os.makedirs(os.path.join(args.output, "str"))
    with open(os.path.join(args.output, "raw", f"{graph_name_clean}.json"), "w") as f:
        json.dump(neighbourhood, f)

    with open(os.path.join(args.output, "str", f"{graph_name_clean}.json"), "w") as f:
        json.dump(neighbourhood_str, f)
