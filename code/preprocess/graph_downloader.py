import os
import requests

graphs = {
    "starwars": "http://oaei.webdatacommons.org/tdrs/testdata/persistent/knowledgegraph/v3/suite/starwars-swg/component/source/",
    "swtor": "http://oaei.webdatacommons.org/tdrs/testdata/persistent/knowledgegraph/v3/suite/starwars-swtor/component/target/",
    "swg": "http://oaei.webdatacommons.org/tdrs/testdata/persistent/knowledgegraph/v3/suite/starwars-swg/component/target/",
    "marvel": "http://oaei.webdatacommons.org/tdrs/testdata/persistent/knowledgegraph/v3/suite/marvelcinematicuniverse-marvel/component/target/",
    "mcu": "http://oaei.webdatacommons.org/tdrs/testdata/persistent/knowledgegraph/v3/suite/marvelcinematicuniverse-marvel/component/source/",
    "memoryalpha": "http://oaei.webdatacommons.org/tdrs/testdata/persistent/knowledgegraph/v3/suite/memoryalpha-stexpanded/component/source/",
    "stexpanded": "http://oaei.webdatacommons.org/tdrs/testdata/persistent/knowledgegraph/v3/suite/memoryalpha-stexpanded/component/target/",
    "memorybeta": "http://oaei.webdatacommons.org/tdrs/testdata/persistent/knowledgegraph/v3/suite/memoryalpha-memorybeta/component/target/",
}


def download_file(name, url):
    print(f"Downloading {name} from {url}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(os.path.join("graphs", name), "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"Saved {name}")


if __name__ == "__main__":

    if not os.path.exists("graphs"):
        os.makedirs("graphs")

    for filename, url in graphs.items():
        download_file(filename+".xml", url)
