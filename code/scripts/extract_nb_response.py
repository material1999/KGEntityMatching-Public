import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from tqdm import tqdm
import argparse

# Initialize parser
parser = argparse.ArgumentParser()
parser.add_argument("-r", "--response", help="Input folder name - Responses")
parser.add_argument("-p", "--prompts", help="Input folder name - Prompts")
parser.add_argument("-o", "--output", help="Output folder")

args = parser.parse_args()

files = os.listdir(args.response)


def extract_summary(response: str):

    after_answer = response.split("Answer:")[-1]

    if after_answer.startswith("assistant"):
        after_answer = after_answer.replace("assistant", "").strip()

    if after_answer.startswith("Here is a well-written"):
        after_answer = "\n".join(after_answer.split("\n")[1:]).strip()

    if after_answer.startswith("Here is a concise"):
        after_answer = "\n".join(after_answer.split("\n")[1:]).strip()

    return after_answer

if not os.path.exists(args.output):
    os.makedirs(args.output)

for file in files:
    filename, extension = os.path.splitext(file)
    output_path = os.path.join(args.output, filename + ".json")
    print(filename)

    with open(os.path.join(args.response, filename+".json"), "r") as f:
        responses = json.load(f)

    with open(os.path.join(args.prompts, filename+".json"), "r") as f:
        prompts = json.load(f)

    response_extract = dict()
    index = 0
    for nodename, description in prompts.items():
        response_extract[nodename] = extract_summary(responses[index])
        index += 1

    with open(output_path, "w") as f:
        json.dump(response_extract, f)


