import requests
import xml.etree.ElementTree as ET
import os
import json
#%%
graph_pairs = [
    "mcu-marvel",
    "memoryalpha-memorybeta",
    "stexpanded-memoryalpha",
    "swg-starwars",
    "swtor-starwars"
]

download_links = [
    "https://oaei.webdatacommons.org/tdrs/testdata/persistent/knowledgegraph/v3/suite/marvelcinematicuniverse-marvel/component/reference.xml",
    "https://oaei.webdatacommons.org/tdrs/testdata/persistent/knowledgegraph/v3/suite/memoryalpha-memorybeta/component/reference.xml",
    "https://oaei.webdatacommons.org/tdrs/testdata/persistent/knowledgegraph/v3/suite/memoryalpha-stexpanded/component/reference.xml",
    "https://oaei.webdatacommons.org/tdrs/testdata/persistent/knowledgegraph/v3/suite/starwars-swg/component/reference.xml",
    "https://oaei.webdatacommons.org/tdrs/testdata/persistent/knowledgegraph/v3/suite/starwars-swtor/component/reference.xml"
]

to_flips = [
    False,
    False,
    True,
    True,
    True
]
#%%
for graph_pair, download_link, to_flip in zip(graph_pairs, download_links, to_flips):

    response = requests.get(download_link)
    xml_content = response.content

    namespaces = {
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
    }

    root = ET.fromstring(xml_content)

    cells = root.findall('.//{http://knowledgeweb.semanticweb.org/heterogeneity/alignment}Cell')

    pairs = []
    for cell in cells:
        entity1 = cell.find('{http://knowledgeweb.semanticweb.org/heterogeneity/alignment}entity1')
        entity2 = cell.find('{http://knowledgeweb.semanticweb.org/heterogeneity/alignment}entity2')

        if entity1 is not None and entity2 is not None:
            uri1 = entity1.attrib.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource')
            uri2 = entity2.attrib.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource')
            if to_flip:
                pairs.append([str(uri2), str(uri1)])
            else:
                pairs.append([str(uri1), str(uri2)])

    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        base_dir = os.getcwd()

    download_dir = os.path.join(base_dir, "golds")
    os.makedirs(download_dir, exist_ok=True)

    output_path = os.path.join(download_dir, graph_pair + ".json")

    with open(output_path, "w") as f:
        json.dump(pairs, f, indent=4)

    print(f"Pairs saved to: {output_path}")