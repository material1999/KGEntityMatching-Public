import sys
import os
utils_path = os.path.join(os.path.dirname(os.getcwd()), 'algos')
sys.path.append(utils_path)
from rdflib import Graph
import os
from urllib.parse import urlparse
import re
from tqdm import tqdm
import json
import argparse
from utils.loaders import load_graph, graph_folder_path
import random

def clean_value(value):
    s = str(value)
    s = s.replace(resource_str, "")
    s = s.replace(class_str, "")
    s = re.sub(r'\n+', '', s)
    for sub in namespace_list:
        s = s.replace(sub, " ")
    return s.strip()

def is_image_url(url):
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff"}
    path = urlparse(url).path
    ext = os.path.splitext(path.lower())[1]
    return ext in image_extensions

def is_wikiPageWikiLink(value):
    return "wikiPageWikiLink" in str(value)

def is_wikiPageExternalLink(value):
    return "wikiPageExternalLink" in str(value)

def sample_list(input_list, max_samples=20):
    if len(input_list) > max_samples:
        return random.sample(input_list, max_samples)
    return input_list

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--output", help="Input folder path")
parser.add_argument("-m", "--max", type=int, default=20, help="Maximum number of values for an attribute")
args = parser.parse_args()

if not os.path.exists(args.output):
    os.makedirs(args.output)

# TEMP
graph_folder_path = "/home/kardosp/entity_alignment/kg_entity_alignment_2024/notebooks/repo/preprocess/graphs"
# Uncomment when preprocess finished
graphs_names = list(filter(lambda x: x.endswith(".xml"), os.listdir(graph_folder_path)))

for graph_name in graphs_names:
    print(graph_name)

    graph_name_cleaned = graph_name.split(".")[0]

    g = Graph()
    g.parse(os.path.join(graph_folder_path, graph_name), format="xml")

    property_str = None

    for prefix, namespace in g.namespaces():
        if str(prefix) == "ns1":
            property_str = str(namespace)

    resource_str = property_str.replace("property", "resource")
    class_str = property_str.replace("property", "class")

    namespace_list = [
        str(namespace)
        for prefix, namespace in g.namespaces()
        if str(namespace) == property_str or not str(namespace).startswith(property_str)
    ]

    attribute_dict = dict()

    for subj, pred, obj in tqdm(g):

        if is_image_url(subj) or is_image_url(obj) or is_wikiPageWikiLink(pred) or is_wikiPageExternalLink(pred):
            continue

        cleaned_subj = clean_value(subj)
        str_subj = str(subj)
        cleaned_pred = clean_value(pred)
        cleaned_obj  = clean_value(obj)

        if cleaned_pred == "comment":
            continue

        if str_subj in attribute_dict:
            if cleaned_pred in attribute_dict[str_subj]:
                attribute_dict[str_subj][cleaned_pred].append(cleaned_obj)
            else:
                attribute_dict[str_subj][cleaned_pred] = [cleaned_obj]
        else:
            attribute_dict[str_subj] = dict()
            attribute_dict[str_subj][cleaned_pred] = [cleaned_obj]

    sorted_dict = {k: attribute_dict[k] for k in sorted(attribute_dict)}

    attribute_dict_sorted = dict()
    for k, v in attribute_dict.items():
        attribute_dict_sorted[k] = {kk: v[kk] for kk in sorted(v)}

    str_dict = dict()
    for node, attributes in attribute_dict_sorted.items():

        node_name = node.split('.org/')[-1].split(".com/")[-1].replace("resource/", "")
        elements_str = f"{node_name}\n"
        for edge, values in attributes.items():
            val = sample_list(values, args.max)
            if len(val) == 1:
                val = val[0]
            elements_str += f"{edge}\t{val}\n"
        str_dict[node] = elements_str

    if not os.path.exists(os.path.join(args.output, "raw")):
        os.makedirs(os.path.join(args.output, "raw"))
    if not os.path.exists(os.path.join(args.output, "str")):
        os.makedirs(os.path.join(args.output, "str"))
    with open(os.path.join(args.output, "raw", f"{graph_name_cleaned}.json"), "w") as f:
        json.dump(attribute_dict_sorted, f, indent=4)
    with open(os.path.join(args.output, "str", f"{graph_name_cleaned}.json"), "w") as f:
        json.dump(str_dict, f, indent=4)

