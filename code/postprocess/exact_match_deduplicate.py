import os
import argparse
import json
from rapidfuzz import fuzz, process

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="Input folder")
parser.add_argument("-o", "--output", help="Output folder")
args = parser.parse_args()

if not os.path.exists(args.output):
    os.makedirs(args.output)

files = os.listdir(args.input)

for file in files:

    filename, extension = os.path.splitext(file)
    input_path = os.path.join(args.input, file)
    output_path = os.path.join(args.output, filename + ".json")

    small = filename.split("-")[0]
    big = filename.split("-")[1]

    with open(input_path, "r") as f:
        exact_match = json.load(f)

    keep_exact_match = list()
    exact_match_rightleft_dict = dict()
    exact_matches = list()

    for em in exact_match:
        if em[0].split("/")[4] == em[1].split("/")[4]:
            exact_matches.append(em)

    for em in exact_matches:
        if em[1] in exact_match_rightleft_dict:
            exact_match_rightleft_dict[em[1]].append(em[0])
        else:
            exact_match_rightleft_dict[em[1]] = [em[0]]

    for k, v in exact_match_rightleft_dict.items():
        if len(v) > 1:
            best_match, score, _ = process.extractOne(k, v, scorer=fuzz.ratio)
            keep_exact_match.append([best_match, k])
        else:
            keep_exact_match.append([v[0], k])

    exact_match_leftright_dict = dict()

    for kem in keep_exact_match:
        if kem[0] in exact_match_leftright_dict:
            exact_match_leftright_dict[kem[0]].append(kem[1])
        else:
            exact_match_leftright_dict[kem[0]] = [kem[1]]

    keep_exact_match = list()

    for k, v in exact_match_leftright_dict.items():
        if len(v) > 1:
            best_match, score, _ = process.extractOne(k, v, scorer=fuzz.ratio)
            keep_exact_match.append([k, best_match])
        else:
            keep_exact_match.append([k, v[0]])

    with open(output_path, "w") as f:
        json.dump(keep_exact_match, f, indent=4)
