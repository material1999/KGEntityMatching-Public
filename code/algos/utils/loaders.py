import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.AlignmentFormat import parse_mapping_from_file
import networkx as nx
import json

gold_folder_path = "/home/kardosp/entity_alignment/kg_entity_alignment_2024/repo_data/gold_pairs"
graph_folder_path = "/home/kardosp/entity_alignment/kg_entity_alignment_2024/dataset/oaei_track_cache/oaei.webdatacommons.org/knowledgegraph/v4/ontologies/triples_v2"


def load_gold(name):
    if name.endswith(".json"):
        with open(os.path.join(gold_folder_path, name), "r") as f:
            return json.load(f)
    else:
        if name.endswith(".triples"):
            name = name.replace(".triples", ".xml")
        alignment = parse_mapping_from_file(os.path.join(gold_folder_path, name))
        return alignment

def load_graph(name):
    if "marvelcinematicuniverse" in name:
        name = name.replace("marvelcinematicuniverse", "mcu")
    if not name.endswith(".triples"):
        name += ".triples"
    current_graph_path = os.path.join(graph_folder_path, name)
    graph = nx.read_edgelist(current_graph_path,
                             delimiter="###",
                             comments="@@@",
                             nodetype=int,
                             data=(('edge_label', int),),
                             create_using=nx.MultiDiGraph)

    with open(current_graph_path.replace(".triples", "_mapping.json"), "r") as f:
        name2id = json.load(f)

    return graph, name2id


def load_embedding(folder, filename,
                   embedder_name="BAAI_bge-large-en-v1.5",
                   dogtag_version="lab_altlab_type_abs_comment"):
    fullpath = os.path.join(folder, f"{filename}_{dogtag_version}_{embedder_name}.json")
    if not os.path.exists(fullpath):
        print("Path doesn't exist:", fullpath)

    with open(fullpath, "r") as f:
        embeddings = json.load(f)
    return embeddings
