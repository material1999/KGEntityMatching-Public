import json
import statistics
import os
import argparse


def union_em_found(exact_match, found_pairs):

    exact_match_left = {em[0] for em in exact_match}
    output = list()

    for em in exact_match:
        output.append(em)

    for pair in found_pairs:
        if pair[0] not in exact_match_left:
            output.append(pair)

    return output


def union_em_found_mean(exact_match, found_pairs):

    exact_match_left = {em[0] for em in exact_match}
    found_pairs_nodes = [[item[0], item[1]] for item in found_pairs]

    output = list()
    scores_list = []

    for em in exact_match:
        output.append(em)
        if em in found_pairs_nodes:
            for pair in found_pairs:
                if pair[0] == em[0] and pair[1] == em[1]:
                    scores_list.append(float(pair[2]))

    threshold_val = statistics.mean(scores_list)
    print(len(scores_list), "/", len(exact_match), "exact match found --> mean score:", threshold_val)

    for pair in found_pairs:
        if pair[0] not in exact_match_left and pair[2] >= threshold_val:
            output.append(pair)

    return output


def union_em_found_median(exact_match, found_pairs):

    exact_match_left = {em[0] for em in exact_match}
    found_pairs_nodes = [[item[0], item[1]] for item in found_pairs]

    output = list()
    scores_list = []

    for em in exact_match:
        output.append(em)
        if em in found_pairs_nodes:
            for pair in found_pairs:
                if pair[0] == em[0] and pair[1] == em[1]:
                    scores_list.append(float(pair[2]))

    threshold_val = statistics.median(scores_list)
    print(len(scores_list), "/", len(exact_match), "exact match found --> median score:", threshold_val)

    for pair in found_pairs:
        if pair[0] not in exact_match_left and pair[2] >= threshold_val:
            output.append(pair)

    return output


parser = argparse.ArgumentParser()
parser.add_argument("-em", "--exact", help="Exact match folder")
parser.add_argument("-fp", "--found", help="Found pairs folder")
parser.add_argument("-o", "--output", help="Output folder")
parser.add_argument("-m", "--mode", help="base/mean/median")
args = parser.parse_args()

mode = args.mode

if not os.path.exists(args.output):
    os.makedirs(args.output)

files = os.listdir(args.found)

for file in files:

    filename, extension = os.path.splitext(file)
    exact_match_path = os.path.join(args.exact, file)
    found_pairs_path = os.path.join(args.found, file)
    output_path = os.path.join(args.output, filename + ".json")

    small = filename.split("-")[0]
    big = filename.split("-")[1]

    with open(exact_match_path) as emf:
        exact_match = json.load(emf)

    with open(found_pairs_path) as fpf:
        found_pairs = json.load(fpf)

    if mode == "base":
        output = union_em_found(exact_match, found_pairs)
    elif mode == "mean":
        output = union_em_found_mean(exact_match, found_pairs)
    elif mode == "median":
        output = union_em_found_median(exact_match, found_pairs)
    else:
        raise ValueError("Invalid mode")

    with open(output_path, "w") as f:
        json.dump(output, f, indent=4)
