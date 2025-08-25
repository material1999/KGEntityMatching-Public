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

    with open(input_path) as emf:
        exact_match = json.load(emf)

    keep_exact_match = list()

    exact_match_rightleft_dict = dict()

    for em in exact_match:
        if em[1] in exact_match_rightleft_dict:
            exact_match_rightleft_dict[em[1]].append(em[0])
        else:
            exact_match_rightleft_dict[em[1]] = [em[0]]

    count_rightleft_duplicates = 0

    for k, v in exact_match_rightleft_dict.items():
        if len(v) > 1:
            count_rightleft_duplicates += 1

    for k, v in exact_match_rightleft_dict.items():
        if len(v) > 1:
            type_right = k.split("/")[4]
            keep_left = [item for item in v if item.split("/")[4] == type_right]
            if len(keep_left) > 0:
                best_match, score, _ = process.extractOne(k, keep_left, scorer=fuzz.ratio)
                keep_exact_match.append([best_match, k])
        else:
            keep_exact_match.append([v[0], k])

    exact_match_leftright_dict = dict()

    for kem in keep_exact_match:
        if kem[0] in exact_match_leftright_dict:
            exact_match_leftright_dict[kem[0]].append(kem[1])
        else:
            exact_match_leftright_dict[kem[0]] = [kem[1]]

    count_leftright_duplicates = 0

    for k, v in exact_match_leftright_dict.items():
        if len(v) > 1:
            count_leftright_duplicates += 1

    keep_exact_match = list()

    for k, v in exact_match_leftright_dict.items():
        if len(v) > 1:
            type_left = k.split("/")[4]
            keep_right = [item for item in v if item.split("/")[4] == type_left]
            if len(keep_right) > 0:
                best_match, score, _ = process.extractOne(k, keep_right, scorer=fuzz.ratio)
                keep_exact_match.append([k, best_match])
        else:
            keep_exact_match.append([k, v[0]])

    exact_match_leftright_dict = dict()
    exact_match_rightleft_dict = dict()

    for em in keep_exact_match:
        if em[0] in exact_match_leftright_dict:
            exact_match_leftright_dict[em[0]].append(em[1])
        else:
            exact_match_leftright_dict[em[0]] = [em[1]]
        if em[1] in exact_match_rightleft_dict:
            exact_match_rightleft_dict[em[1]].append(em[0])
        else:
            exact_match_rightleft_dict[em[1]] = [em[0]]

    count_leftright_duplicates = 0
    count_rightleft_duplicates = 0

    for k, v in exact_match_leftright_dict.items():
        if len(v) > 1:
            count_leftright_duplicates += 1

    for k, v in exact_match_rightleft_dict.items():
        if len(v) > 1:
            count_rightleft_duplicates += 1

    with open(output_path, "w") as f:
        json.dump(keep_exact_match, f, indent=4)
