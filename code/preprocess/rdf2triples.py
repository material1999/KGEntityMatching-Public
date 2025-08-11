import rdflib
import os
import networkx as nx
import time
import json

read_times = list()


def convert2edgelist(path, filename, output_path):
    full_path = os.path.join(path, filename)
    start = time.time()
    source_graph = rdflib.Graph()
    source_graph.parse(full_path)
    end = time.time()
    read_times.append([filename, end-start])
    print("Read", filename, "in", end-start)

    id_dict = dict()
    print("Converting to edgelist...")
    with open(os.path.join(output_path, path.replace(".xml", ".triples")), "w") as f:
        for s, p, o in source_graph.triples((None, None, None)):
            s_s = str(s)
            p_s = str(p)
            o_s = str(o)
            if s_s not in id_dict:
                id_dict[s_s] = len(id_dict)
            if p_s not in id_dict:
                id_dict[p_s] = len(id_dict)
            if o_s not in id_dict:
                id_dict[o_s] = len(id_dict)

            f.write("{}\n".format("###".join([
                str(id_dict[s_s]),
                str(id_dict[o_s]),
                str(id_dict[p_s])
            ])))

    with open(os.path.join(output_path, filename.replace(".xml", "_mapping.json")), "w") as f2:
        json.dump(id_dict, f2, indent=4)


graphs_folder = os.path.join(os.getcwd(), "graphs")
preprocessed_folder = os.path.join(os.getcwd(), "preprocessed_graphs")

for graph_file in os.listdir(graphs_folder):
    if not graph_file.endswith(".xml"):
        continue
    print(graph_file)
    convert2edgelist(graphs_folder, graph_file, preprocessed_folder)


for graph_file in os.listdir(preprocessed_folder):
    if not graph_file.endswith(".triples"):
        continue
    current_graph = os.path.join(preprocessed_folder, graph_file)
    start = time.time()
    read_graph = nx.read_edgelist(current_graph, delimiter="###", comments="@@@", data=(('edge_label', str),),
                                  create_using=nx.MultiDiGraph)
    end = time.time()
    read_times.append([graph_file, end-start])
    print("Read", graph_file, "in", end-start)


with open(os.path.join(preprocessed_folder, "triples_vs_xml_id.json"), "w") as f:
    json.dump(read_times, f)
